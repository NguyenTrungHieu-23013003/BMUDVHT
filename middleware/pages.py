"""
pages.py — HTML templates for the 403 block page and the WAF dashboard.
"""
from datetime import datetime

# ── Type → display label mapping ─────────────────────────────────────────────
VULN_LABELS = {
    "sqli":           ("SQL Injection",        "#ef4444", "🧬"),
    "xss_stored":     ("Stored XSS",           "#f97316", "💉"),
    "idor":           ("IDOR",                 "#eab308", "🔓"),
    "auth_plaintext": ("Plaintext Auth",       "#8b5cf6", "🔑"),
    "none":           ("Clean",                "#22c55e", "✅"),
}


def block_page(verdict: dict, method: str, url: str) -> str:
    vtype  = verdict.get("type", "none")
    score  = verdict.get("score", 0)
    label, color, icon = VULN_LABELS.get(vtype, ("Unknown", "#6b7280", "❓"))
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>403 — Blocked by AI WAF</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&family=JetBrains+Mono:wght@400;700&display=swap');
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --bg:      #0a0a0f;
      --surface: #111118;
      --border:  #1e1e2e;
      --muted:   #6b7280;
      --red:     {color};
    }}

    body {{
      background: var(--bg);
      color: #e2e8f0;
      font-family: 'Inter', sans-serif;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
    }}

    /* Animated grid background */
    body::before {{
      content: '';
      position: fixed;
      inset: 0;
      background-image:
        linear-gradient(var(--border) 1px, transparent 1px),
        linear-gradient(90deg, var(--border) 1px, transparent 1px);
      background-size: 40px 40px;
      opacity: .4;
      animation: grid-pan 20s linear infinite;
    }}
    @keyframes grid-pan {{ to {{ background-position: 40px 40px; }} }}

    /* Red glow orb */
    body::after {{
      content: '';
      position: fixed;
      top: -200px; left: 50%;
      transform: translateX(-50%);
      width: 600px; height: 600px;
      background: radial-gradient(circle, {color}22 0%, transparent 70%);
      animation: pulse 3s ease-in-out infinite;
    }}
    @keyframes pulse {{
      0%, 100% {{ opacity: .6; transform: translateX(-50%) scale(1); }}
      50%       {{ opacity: 1;  transform: translateX(-50%) scale(1.1); }}
    }}

    .card {{
      position: relative;
      z-index: 10;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 48px 56px;
      max-width: 640px;
      width: 90%;
      box-shadow: 0 0 0 1px {color}33, 0 32px 80px #00000088;
      animation: slide-up .5s cubic-bezier(.16,1,.3,1);
    }}
    @keyframes slide-up {{
      from {{ opacity: 0; transform: translateY(30px); }}
      to   {{ opacity: 1; transform: translateY(0); }}
    }}

    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: {color}1a;
      border: 1px solid {color}55;
      border-radius: 999px;
      padding: 6px 16px;
      font-size: .75rem;
      font-weight: 600;
      letter-spacing: .08em;
      text-transform: uppercase;
      color: {color};
      margin-bottom: 24px;
    }}

    .code {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 5rem;
      font-weight: 900;
      line-height: 1;
      color: {color};
      text-shadow: 0 0 40px {color}66;
      margin-bottom: 8px;
    }}

    h1 {{
      font-size: 1.5rem;
      font-weight: 700;
      color: #f8fafc;
      margin-bottom: 8px;
    }}
    .sub {{
      color: var(--muted);
      font-size: .9rem;
      line-height: 1.6;
      margin-bottom: 32px;
    }}

    .meta {{
      background: #0a0a0f;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px 24px;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
      margin-bottom: 32px;
    }}
    .meta-item label {{
      display: block;
      font-size: .7rem;
      text-transform: uppercase;
      letter-spacing: .08em;
      color: var(--muted);
      margin-bottom: 4px;
    }}
    .meta-item span {{
      font-family: 'JetBrains Mono', monospace;
      font-size: .85rem;
      color: #cbd5e1;
      word-break: break-all;
    }}
    .meta-item.full {{ grid-column: 1 / -1; }}

    .score-bar {{
      background: var(--border);
      border-radius: 999px;
      height: 6px;
      overflow: hidden;
      margin-top: 8px;
    }}
    .score-fill {{
      height: 100%;
      width: {score}%;
      background: linear-gradient(90deg, {color}88, {color});
      border-radius: 999px;
      transition: width .8s cubic-bezier(.16,1,.3,1);
    }}

    .footer {{
      font-size: .75rem;
      color: var(--muted);
      text-align: center;
    }}
    .footer a {{
      color: {color};
      text-decoration: none;
      font-weight: 600;
    }}
    .footer a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="badge">{icon} AI WAF — Request Blocked</div>
    <div class="code">403</div>
    <h1>Access Denied</h1>
    <p class="sub">
      This request was classified as potentially malicious and has been
      blocked by the AI-powered WAF before reaching the application.
    </p>

    <div class="meta">
      <div class="meta-item">
        <label>Threat type</label>
        <span style="color:{color}">{label}</span>
      </div>
      <div class="meta-item">
        <label>Confidence score</label>
        <span>{score} / 100</span>
        <div class="score-bar"><div class="score-fill"></div></div>
      </div>
      <div class="meta-item">
        <label>Method</label>
        <span>{method}</span>
      </div>
      <div class="meta-item">
        <label>Timestamp</label>
        <span>{ts}</span>
      </div>
      <div class="meta-item full">
        <label>Requested URL</label>
        <span>{url}</span>
      </div>
    </div>

    <div class="footer">
      <a href="/waf-dashboard">View WAF Dashboard</a>
      &nbsp;·&nbsp; Powered by Claude AI + OWASP ModSecurity CRS
    </div>
  </div>
</body>
</html>"""


def dashboard_page(log: list, mode: str, backend: str) -> str:
    total   = len(log)
    blocked = sum(1 for e in log if e["verdict"]["action"] == "block")
    allowed = total - blocked

    type_counts: dict = {}
    for e in log:
        t = e["verdict"]["type"]
        type_counts[t] = type_counts.get(t, 0) + 1

    # Build threat breakdown pills
    pills_html = ""
    for vtype, cnt in sorted(type_counts.items(), key=lambda x: -x[1]):
        label, color, icon = VULN_LABELS.get(vtype, ("?", "#6b7280", "❓"))
        pills_html += f"""
        <div class="pill" style="--c:{color}">
          <span class="pill-icon">{icon}</span>
          <span class="pill-label">{label}</span>
          <span class="pill-count">{cnt}</span>
        </div>"""

    # Build table rows (newest first, max 50)
    rows_html = ""
    for e in reversed(log[-50:]):
        v     = e["verdict"]
        vtype = v["type"]
        score = v["score"]
        action= v["action"]
        label, color, icon = VULN_LABELS.get(vtype, ("?", "#6b7280", "❓"))
        action_badge = (
            f'<span class="tag tag-block">BLOCK</span>'
            if action == "block"
            else '<span class="tag tag-allow">ALLOW</span>'
        )
        rows_html += f"""
        <tr>
          <td class="mono small muted">{e['timestamp']}</td>
          <td><span class="method">{e['method']}</span></td>
          <td class="mono small url-cell">{e['url'][:60]}{'…' if len(e['url'])>60 else ''}</td>
          <td><span style="color:{color};font-weight:600;text-shadow:0 0 10px {color}44">{icon} {label}</span></td>
          <td class="mono font-bold" style="color:{color}">{score}</td>
          <td>{action_badge}</td>
        </tr>"""

    mode_color = "#10b981" if mode == "detect" else "#ef4444"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <meta http-equiv="refresh" content="5"/>
  <title>AI WAF — Dashboard</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600;700&display=swap');
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --bg: #07080f;
      --surface: rgba(18, 18, 32, 0.65);
      --panel: rgba(22, 22, 40, 0.45);
      --border: rgba(255, 255, 255, 0.08);
      --muted: #64748b;
      --text: #f1f5f9;
      --glass-blur: blur(16px);
    }}

    body {{
      background: var(--bg);
      background-image: radial-gradient(circle at top right, rgba(139,92,246,0.15), transparent 60%),
                        radial-gradient(circle at bottom left, rgba(56,189,248,0.1), transparent 50%);
      color: var(--text);
      font-family: 'Inter', sans-serif;
      min-height: 100vh;
    }}

    ::-webkit-scrollbar {{ width: 6px; }}
    ::-webkit-scrollbar-thumb {{ background: rgba(255,255,255,0.1); border-radius: 10px; }}

    header {{
      position: sticky; top: 0; z-index: 100;
      background: rgba(10, 10, 15, 0.7);
      backdrop-filter: var(--glass-blur);
      border-bottom: 1px solid var(--border);
      padding: 16px 32px;
      display: flex; align-items: center; gap: 16px;
      box-shadow: 0 4px 30px rgba(0,0,0,0.4);
    }}
    .logo {{
      font-size: 1.2rem; font-weight: 800;
      background: linear-gradient(135deg, #c084fc, #38bdf8);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      letter-spacing: -0.02em;
    }}
    .live-dot {{
      width: 8px; height: 8px; border-radius: 50%;
      background: #10b981; box-shadow: 0 0 12px #10b981;
      animation: pulse 2s infinite;
    }}
    @keyframes pulse {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} }}
    .hdr-right {{ margin-left: auto; display: flex; align-items: center; gap: 14px; font-size: .8rem; color: var(--muted); }}
    .code-badge {{
      font-family: 'JetBrains Mono', monospace;
      color: #38bdf8; background: rgba(56,189,248,0.1);
      padding: 4px 8px; border-radius: 6px; border: 1px solid rgba(56,189,248,0.2);
    }}
    .mode-badge {{
      padding: 4px 12px; border-radius: 999px;
      font-weight: 700; font-size: .7rem; letter-spacing: .08em; text-transform: uppercase;
      background: {mode_color}1a; border: 1px solid {mode_color}44; color: {mode_color};
      box-shadow: 0 0 15px {mode_color}22;
    }}

    main {{ max-width: 1280px; margin: 0 auto; padding: 40px 32px; }}

    /* ── Stats ── */
    .stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 32px; }}
    .stat {{
      background: var(--surface);
      backdrop-filter: var(--glass-blur);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 28px 32px;
      position: relative; overflow: hidden;
      box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    }}
    .stat::before {{
      content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%;
    }}
    .stat.total::before {{ background: #8b5cf6; box-shadow: 0 0 15px #8b5cf6; }}
    .stat.blocked::before {{ background: #ef4444; box-shadow: 0 0 15px #ef4444; }}
    .stat.allowed::before {{ background: #10b981; box-shadow: 0 0 15px #10b981; }}
    
    .stat label {{ font-size: .75rem; font-weight: 600; text-transform: uppercase; letter-spacing: .1em; color: var(--muted); display: block; margin-bottom: 12px; }}
    .stat .val {{ font-size: 2.8rem; font-weight: 700; line-height: 1; text-shadow: 0 4px 15px rgba(0,0,0,0.3); }}
    .stat.total .val {{ color: #a78bfa; }}
    .stat.blocked .val {{ color: #f87171; }}
    .stat.allowed .val {{ color: #34d399; }}

    /* ── Pills ── */
    .section-title {{ font-size: .8rem; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: .1em; margin-bottom: 16px; display: flex; align-items: center; gap: 12px; }}
    .section-title::after {{ content: ''; flex: 1; height: 1px; background: var(--border); }}
    
    .pills {{ display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 40px; }}
    .pill {{
      display: flex; align-items: center; gap: 10px;
      background: color-mix(in srgb, var(--c) 15%, var(--panel));
      border: 1px solid color-mix(in srgb, var(--c) 40%, transparent);
      border-radius: 12px;
      padding: 8px 18px;
      font-size: .9rem;
      box-shadow: 0 4px 15px rgba(0,0,0,0.1);
      backdrop-filter: blur(8px);
    }}
    .pill-label {{ color: var(--text); font-weight: 600; letter-spacing: -0.01em; }}
    .pill-count {{
      background: color-mix(in srgb, var(--c) 25%, transparent);
      color: var(--c);
      border-radius: 999px; padding: 2px 10px;
      font-size: .8rem; font-weight: 700;
      font-family: 'JetBrains Mono', monospace;
    }}

    /* ── Table ── */
    .table-wrap {{
      background: var(--surface);
      backdrop-filter: var(--glass-blur);
      border: 1px solid var(--border);
      border-radius: 20px;
      overflow: hidden;
      box-shadow: 0 10px 40px rgba(0,0,0,0.25);
    }}
    table {{ width: 100%; border-collapse: collapse; }}
    thead th {{
      background: rgba(0,0,0,0.2);
      padding: 16px 20px; text-align: left;
      font-size: .75rem; font-weight: 700;
      text-transform: uppercase; letter-spacing: .1em;
      color: var(--muted); border-bottom: 1px solid var(--border);
    }}
    tbody tr {{ border-bottom: 1px solid var(--border); transition: background .2s; }}
    tbody tr:last-child {{ border-bottom: none; }}
    tbody tr:hover {{ background: rgba(255,255,255,0.03); }}
    td {{ padding: 14px 20px; font-size: .85rem; vertical-align: middle; }}

    .mono {{ font-family: 'JetBrains Mono', monospace; }}
    .font-bold {{ font-weight: 700; }}
    .small {{ font-size: .75rem; }}
    .muted {{ color: #94a3b8; }}
    .url-cell {{ max-width: 280px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
    .method {{
      background: rgba(56,189,248,0.15); color: #38bdf8;
      border: 1px solid rgba(56,189,248,0.3);
      border-radius: 6px; padding: 3px 8px;
      font-family: 'JetBrains Mono', monospace;
      font-size: .75rem; font-weight: 700;
    }}
    .tag {{
      display: inline-block; border-radius: 999px;
      padding: 4px 12px; font-size: .7rem; font-weight: 800;
      letter-spacing: .06em; text-transform: uppercase;
    }}
    .tag-block {{ background: rgba(239,68,68,0.15); border: 1px solid rgba(239,68,68,0.4); color: #ef4444; box-shadow: 0 0 10px rgba(239,68,68,0.2); }}
    .tag-allow {{ background: rgba(16,185,129,0.15); border: 1px solid rgba(16,185,129,0.4); color: #10b981; box-shadow: 0 0 10px rgba(16,185,129,0.2); }}

    .empty {{ padding: 60px; text-align: center; color: var(--muted); font-size: 1rem; }}
    footer {{ text-align: center; padding: 40px; font-size: .8rem; color: var(--muted); font-weight: 500; }}
    footer a {{ color: #a78bfa; text-decoration: none; }}
    footer a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <header>
    <div class="logo">AI WAF Dashboard</div>
    <div class="live-dot"></div>
    <div class="hdr-right">
      <span>Backend: <span class="code-badge">{backend}</span></span>
      <span class="mode-badge">Mode: {mode}</span>
      <span>Auto-refresh 5s</span>
    </div>
  </header>

  <main>
    <div class="stats">
      <div class="stat total">
        <label>Total Requests Analyzed</label>
        <div class="val">{total}</div>
      </div>
      <div class="stat blocked">
        <label>Threats Blocked</label>
        <div class="val">{blocked}</div>
      </div>
      <div class="stat allowed">
        <label>Clean Allowed</label>
        <div class="val">{allowed}</div>
      </div>
    </div>

    <div class="section-title">Threat Breakdown</div>
    <div class="pills">
      {pills_html if pills_html else '<span style="color:var(--muted);font-size:.9rem;padding:10px">No threats detected yet.</span>'}
    </div>

    <div class="section-title">Recent Requests log</div>
    <div class="table-wrap">
      {"<table><thead><tr><th>Timestamp</th><th>Method</th><th>URL</th><th>Analysis Result</th><th>AI Score</th><th>Action</th></tr></thead><tbody>" + rows_html + "</tbody></table>" if log else '<div class="empty">No requests analyzed yet. Send some traffic to port 8083!</div>'}
    </div>
  </main>

  <footer>
    AI WAF Middleware · Powered by <b>Groq LLM</b> · <a href="/waf-test">Go to Test Console</a>
  </footer>
</body>
</html>"""
