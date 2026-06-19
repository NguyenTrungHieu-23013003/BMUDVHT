"""
main.py — AI WAF reverse proxy.

Flow per request:
  1. Skip static assets immediately → forward.
  2. Skip internal /waf-* routes → serve locally.
  3. Parse method, URL, query params, body, current_user_id.
  4. Call Claude classifier (sync via thread pool).
  5. Append to in-memory detection log.
  6. MODE=block  + action=block  → return 403 block page.
   MODE=detect + action=block  → log & forward (tag header injected).
  7. Forward to backend via httpx, stream response back.
"""
import asyncio
import json
import logging
import os
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from urllib.parse import parse_qs, urlencode

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse

from classifier import classify_request
from config import settings
from pages import block_page, dashboard_page
from test_console import test_console_page

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ai_waf")

# ── App + shared state ────────────────────────────────────────────────────────
app = FastAPI(docs_url=None, redoc_url=None)

# Keep at most 500 entries in memory (thread-safe deque)
_log: deque = deque(maxlen=500)

# Thread pool for synchronous Groq calls (avoids blocking the event loop)
_executor = ThreadPoolExecutor(max_workers=4)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _is_static(path: str) -> bool:
    _, ext = os.path.splitext(path.split("?")[0])
    return ext.lower() in settings.STATIC_EXTENSIONS


def _extract_body(raw: bytes, content_type: str) -> tuple[dict | str, str]:
    """Return (parsed_body, body_repr) from raw bytes."""
    ct = content_type.lower()
    if not raw:
        return {}, ""
    try:
        if "application/json" in ct:
            parsed = json.loads(raw)
            return parsed, json.dumps(parsed, ensure_ascii=False)[: settings.MAX_BODY_BYTES]
        if "application/x-www-form-urlencoded" in ct:
            parsed = {k: v[0] for k, v in parse_qs(raw.decode("utf-8", "replace")).items()}
            return parsed, json.dumps(parsed, ensure_ascii=False)
    except Exception:
        pass
    text = raw.decode("utf-8", "replace")[: settings.MAX_BODY_BYTES]
    return text, text


def _guess_user_id(params: dict, body) -> str:
    """Best-effort: extract current_user_id from URL or body."""
    for key in ("id", "user_id", "uid", "userId"):
        if key in params:
            return str(params[key])
        if isinstance(body, dict) and key in body:
            return str(body[key])
    return "unknown"


def _append_log(entry: dict) -> None:
    _log.append(entry)


# ── Internal dashboard / health routes ───────────────────────────────────────

@app.get("/waf-dashboard", include_in_schema=False)
async def dashboard():
    html = dashboard_page(
        log=list(_log),
        mode=settings.MODE,
        backend=settings.BACKEND_URL,
    )
    return HTMLResponse(html)


@app.get("/waf-status", include_in_schema=False)
async def status():
    log_list = list(_log)
    return JSONResponse({
        "mode":        settings.MODE,
        "backend":     settings.BACKEND_URL,
        "model":       settings.GROQ_MODEL,
        "total":       len(log_list),
        "blocked":     sum(1 for e in log_list if e["verdict"]["action"] == "block"),
        "recent":      log_list[-10:],
    })


@app.get("/waf-health", include_in_schema=False)
async def health():
    return {"status": "ok", "mode": settings.MODE}


@app.get("/waf-test", include_in_schema=False)
async def test_console():
    return HTMLResponse(test_console_page(settings.GROQ_MODEL, settings.MODE))


@app.post("/waf-probe", include_in_schema=False)
async def probe(request: Request):
    """Classify a request snapshot WITHOUT forwarding to backend. Demo/testing only."""
    data = await request.json()
    t0 = time.perf_counter()
    verdict = await asyncio.get_event_loop().run_in_executor(
        _executor,
        classify_request,
        data.get("method", "GET"),
        data.get("url", "/"),
        data.get("params", {}),
        data.get("body", {}),
        data.get("user_id", "unknown"),
    )
    elapsed_ms = int((time.perf_counter() - t0) * 1000)
    _append_log({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "method":    data.get("method", "GET"),
        "url":       data.get("url", "/"),
        "user_id":   data.get("user_id", "unknown"),
        "verdict":   verdict,
        "latency_ms": elapsed_ms,
        "probe":     True,
    })
    logger.info("PROBE → type=%s score=%s action=%s (%dms)",
                verdict["type"], verdict["score"], verdict["action"], elapsed_ms)
    return JSONResponse(verdict)


@app.post("/waf-attack", include_in_schema=False)
async def attack_proxy(request: Request):
    """Forward request directly to VulnApp (no WAF). Returns status + body snippet."""
    data = await request.json()
    method  = data.get("method", "POST")
    path    = data.get("path", "/index.php")
    params  = data.get("params", {})
    body    = data.get("body", {})
    target  = f"http://vulnapp:80{path}"
    if params:
        target += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    try:
        async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
            resp = await client.request(
                method=method, url=target,
                data=body if isinstance(body, dict) else None,
                content=body.encode() if isinstance(body, str) else None,
            )
        snippet = resp.text[:400]
        # Detect success signals in response body
        success_keywords = ["Chào mừng", "Đăng xuất", "admin", "Dashboard", "profile", "cookie"]
        hit = any(kw.lower() in snippet.lower() for kw in success_keywords)
        return JSONResponse({
            "status": resp.status_code,
            "success": hit and resp.status_code == 200,
            "snippet": snippet[:200],
        })
    except Exception as e:
        return JSONResponse({"status": 0, "success": False, "snippet": str(e)}, status_code=200)


@app.post("/waf-modsec", include_in_schema=False)
async def modsec_proxy(request: Request):
    """Forward request to ModSecurity WAF. Returns status + whether it was blocked."""
    data = await request.json()
    method  = data.get("method", "POST")
    path    = data.get("path", "/index.php")
    params  = data.get("params", {})
    body    = data.get("body", {})
    target  = f"http://modsec_waf:8080{path}"
    if params:
        target += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    try:
        async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
            resp = await client.request(
                method=method, url=target,
                data=body if isinstance(body, dict) else None,
                content=body.encode() if isinstance(body, str) else None,
            )
        return JSONResponse({
            "status": resp.status_code,
            "blocked": resp.status_code == 403,
        })
    except Exception as e:
        return JSONResponse({"status": 0, "blocked": False, "snippet": str(e)}, status_code=200)



# ── Main proxy catch-all ──────────────────────────────────────────────────────

@app.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
)
async def proxy(request: Request, path: str):
    raw_path = "/" + path
    full_url = str(request.url)

    # 1. Internal WAF routes — must be caught here too because the catch-all
    #    path param matches before FastAPI's fixed routes in some edge cases.
    if raw_path in ("/waf-dashboard", "/waf-status", "/waf-health", "/waf-test", "/waf-probe"):
        if raw_path == "/waf-dashboard":
            return HTMLResponse(dashboard_page(list(_log), settings.MODE, settings.BACKEND_URL))
        if raw_path == "/waf-status":
            log_list = list(_log)
            return JSONResponse({
                "mode": settings.MODE, "backend": settings.BACKEND_URL,
                "model": settings.GROQ_MODEL, "total": len(log_list),
                "blocked": sum(1 for e in log_list if e["verdict"]["action"] == "block"),
                "recent": log_list[-10:],
            })
        if raw_path == "/waf-test":
            return HTMLResponse(test_console_page(settings.GROQ_MODEL, settings.MODE))
        if raw_path == "/waf-probe":
            return JSONResponse({"error": "use POST /waf-probe"}, status_code=405)
        return JSONResponse({"status": "ok", "mode": settings.MODE})

    # 2. Static assets → forward directly, no classification
    if _is_static(raw_path):
        return await _forward(request, raw_path)

    # 2. Parse request data
    params       = dict(request.query_params)
    raw_body     = await request.body()
    content_type = request.headers.get("content-type", "")
    body, _      = _extract_body(raw_body, content_type)
    user_id      = _guess_user_id(params, body)

    # 3. Classify (run sync Claude call in thread pool to avoid blocking event loop)
    t0 = time.perf_counter()
    verdict = await asyncio.get_event_loop().run_in_executor(
        _executor,
        classify_request,
        request.method, full_url, params, body, user_id,
    )
    elapsed_ms = int((time.perf_counter() - t0) * 1000)

    # 4. Log
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "method":    request.method,
        "url":       full_url,
        "user_id":   user_id,
        "verdict":   verdict,
        "latency_ms": elapsed_ms,
    }
    _append_log(entry)

    logger.info(
        "%s %s → type=%s score=%s action=%s (%dms)",
        request.method, raw_path,
        verdict["type"], verdict["score"], verdict["action"], elapsed_ms,
    )

    # 5. Apply mode
    if verdict["action"] == "block":
        if settings.MODE == "block":
            logger.warning("BLOCKED: %s %s [%s score=%s]",
                           request.method, raw_path, verdict["type"], verdict["score"])
            return HTMLResponse(
                content=block_page(verdict, request.method, full_url),
                status_code=403,
                headers={
                    "X-WAF-Action":    "block",
                    "X-WAF-Type":      verdict["type"],
                    "X-WAF-Score":     str(verdict["score"]),
                },
            )
        else:  # detect mode — log but let through
            logger.warning("DETECTED (allowed): %s %s [%s score=%s]",
                           request.method, raw_path, verdict["type"], verdict["score"])

    # 6. Forward
    extra_headers = {
        "X-WAF-Action": verdict["action"],
        "X-WAF-Type":   verdict["type"],
        "X-WAF-Score":  str(verdict["score"]),
    }
    return await _forward(request, raw_path, raw_body=raw_body, extra_req_headers=extra_headers)


# ── Forward helper ────────────────────────────────────────────────────────────

_HOP_BY_HOP = {
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailers", "transfer-encoding", "upgrade",
    "content-encoding",  # let httpx handle encoding
}


async def _forward(
    request: Request,
    path: str,
    raw_body: bytes | None = None,
    extra_req_headers: dict | None = None,
) -> Response:
    # Re-read body if not already consumed
    if raw_body is None:
        raw_body = await request.body()

    # Build upstream URL
    upstream = settings.BACKEND_URL.rstrip("/") + path
    if request.url.query:
        upstream += "?" + request.url.query

    # Filter request headers
    req_headers = {
        k: v
        for k, v in request.headers.items()
        if k.lower() not in _HOP_BY_HOP and k.lower() != "host"
    }
    if extra_req_headers:
        req_headers.update(extra_req_headers)

    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.request(
                method=request.method,
                url=upstream,
                headers=req_headers,
                content=raw_body,
            )

        # Filter response headers
        resp_headers = {
            k: v
            for k, v in resp.headers.items()
            if k.lower() not in _HOP_BY_HOP
        }

        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=resp_headers,
        )

    except httpx.ConnectError:
        logger.error("Cannot connect to backend: %s", settings.BACKEND_URL)
        return HTMLResponse(
            "<h1>502 Bad Gateway</h1><p>AI WAF cannot reach the backend application.</p>",
            status_code=502,
        )
    except Exception as exc:
        logger.error("Forward error: %s", exc)
        return HTMLResponse("<h1>500 Internal Server Error</h1>", status_code=500)
