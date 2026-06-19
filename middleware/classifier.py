"""
classifier.py — Sends the HTTP request snapshot to Groq and parses the JSON verdict.
"""
import json
import logging
from groq import Groq
from config import settings

logger = logging.getLogger("ai_waf.classifier")

# ── Prompt template ───────────────────────────────────────────────────────────
_PROMPT = """\
You are a request security classifier for a web app demo (OWASP-based).
Given ONE HTTP request, output ONLY compact JSON — no prose, no markdown, no explanation.

Vulnerability types (pick the single best match):
- sqli         : SQL injection — quote breaks ('), OR 1=1, UNION SELECT, --, #, /*, ;, SLEEP, WAITFOR
- xss_stored   : HTML/JS payload meant to persist — <script>, on*=, javascript:, data:, %3Cscript%3E
- idor         : resource ID in URL/body that does NOT match current_user_id (id enumeration / object hijack)
- auth_plaintext: login/register/reset payload exposing password in cleartext body
- none         : no clear threat

score  : 0-100 (confidence the request is malicious)
action : "block" if score >= {threshold}, else "allow"

Output strictly this JSON shape, nothing else:
{{"type":"sqli|xss_stored|idor|auth_plaintext|none","score":0,"action":"block|allow"}}

Request:
method           : {method}
url              : {url}
query_params     : {params}
body             : {body}
current_user_id  : {current_user_id}
"""

# ── Default safe verdict when classification cannot be obtained ───────────────
_SAFE = {"type": "none", "score": 0, "action": "allow"}


def classify_request(
    method: str,
    url: str,
    params: dict,
    body,
    current_user_id: str,
) -> dict:
    """
    Call Groq to classify the request.
    Returns a dict with keys: type, score, action.
    Never raises — falls back to _SAFE on any error.
    """
    if not settings.GROQ_API_KEY:
        logger.warning("GROQ_API_KEY not set — skipping classification")
        return _SAFE

    try:
        body_repr = (
            json.dumps(body, ensure_ascii=False)
            if isinstance(body, dict)
            else str(body)[: settings.MAX_BODY_BYTES]
        )

        prompt = _PROMPT.format(
            threshold=settings.BLOCK_THRESHOLD,
            method=method,
            url=url,
            params=json.dumps(params, ensure_ascii=False),
            body=body_repr,
            current_user_id=current_user_id,
        )

        client = Groq(api_key=settings.GROQ_API_KEY)
        completion = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            max_tokens=120,
            temperature=0,          # deterministic — no creative JSON
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a JSON-only security classifier. "
                        "Output only valid compact JSON, no explanation."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )

        raw = completion.choices[0].message.content.strip()
        logger.debug("Groq raw response: %s", raw)

        result = json.loads(raw)

        # Validate expected keys exist
        if not all(k in result for k in ("type", "score", "action")):
            raise ValueError(f"Unexpected shape: {result}")

        # Re-apply threshold locally in case the model drifts
        result["action"] = (
            "block" if int(result["score"]) >= settings.BLOCK_THRESHOLD else "allow"
        )
        return result

    except json.JSONDecodeError as exc:
        logger.error("JSON parse error from Groq: %s", exc)
        return _SAFE
    except Exception as exc:
        logger.error("Classifier error: %s", exc)
        return _SAFE
