"""test_console.py — OWASP comparison test console: Attack vs ModSec vs AI WAF."""


def test_console_page(model: str, mode: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>AI WAF — OWASP Lab</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:#07080f;
  --surface:rgba(18,18,32,0.8);
  --card:rgba(22,22,40,0.6);
  --border:rgba(255,255,255,0.07);
  --muted:#64748b;
  --text:#e2e8f0;
  --red:#ef4444;--orange:#f97316;--purple:#a855f7;--green:#10b981;--yellow:#eab308;
}}
body{{background:var(--bg);background-image:radial-gradient(ellipse 80% 50% at 50% -20%,rgba(120,60,220,0.15),transparent);color:var(--text);font-family:'Inter',sans-serif;min-height:100vh}}
::-webkit-scrollbar{{width:5px}}::-webkit-scrollbar-thumb{{background:rgba(255,255,255,0.1);border-radius:9px}}

/* ── HEADER ── */
.hdr{{position:sticky;top:0;z-index:99;padding:0 24px}}
.hdr-inner{{max-width:960px;margin:0 auto;display:flex;align-items:center;gap:12px;padding:14px 20px;background:rgba(8,8,18,0.75);backdrop-filter:blur(20px);border:1px solid var(--border);border-top:none;border-radius:0 0 16px 16px;box-shadow:0 8px 32px rgba(0,0,0,0.4)}}
.logo{{font-weight:700;font-size:1rem;background:linear-gradient(135deg,#c084fc,#38bdf8);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.dot{{width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 10px var(--green);animation:pulse 2s infinite;flex-shrink:0}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
.hdr-right{{margin-left:auto;display:flex;gap:8px;align-items:center}}
.chip{{padding:3px 10px;border-radius:999px;font-size:.7rem;font-weight:600;letter-spacing:.05em;text-transform:uppercase}}
.chip-model{{background:rgba(192,132,252,.1);border:1px solid rgba(192,132,252,.3);color:#e879f9}}
.chip-mode{{background:rgba(16,185,129,.1);border:1px solid rgba(16,185,129,.3);color:#34d399}}
.dash-btn{{color:#38bdf8;font-size:.78rem;text-decoration:none;padding:5px 12px;border:1px solid rgba(56,189,248,.25);border-radius:8px;background:rgba(56,189,248,.05);transition:.2s}}
.dash-btn:hover{{background:rgba(56,189,248,.12)}}

/* ── PAGE WRAPPER ── */
.page{{max-width:960px;margin:0 auto;padding:28px 24px 60px}}

/* ── SECTION TITLE ── */
.section-title{{font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:var(--muted);margin-bottom:20px;display:flex;align-items:center;gap:10px}}
.section-title::after{{content:'';flex:1;height:1px;background:var(--border)}}

/* ── VULN CARD ── */
.vuln-card{{background:var(--card);border:1px solid var(--border);border-radius:16px;overflow:hidden;margin-bottom:20px;backdrop-filter:blur(12px);box-shadow:0 8px 24px rgba(0,0,0,0.3);animation:fadeUp .5s ease both;transition:box-shadow .3s}}
.vuln-card:nth-child(1){{animation-delay:.05s}}
.vuln-card:nth-child(2){{animation-delay:.1s}}
.vuln-card:nth-child(3){{animation-delay:.15s}}
.vuln-card:nth-child(4){{animation-delay:.2s}}
.vuln-card:hover{{box-shadow:0 12px 36px rgba(0,0,0,0.45)}}
@keyframes fadeUp{{from{{opacity:0;transform:translateY(16px)}}to{{opacity:1;transform:none}}}}

/* ── CARD HEADER ── */
.card-hdr{{display:flex;align-items:center;gap:14px;padding:18px 20px 14px;border-bottom:1px solid var(--border)}}
.card-icon{{font-size:1.5rem;line-height:1}}
.card-meta{{flex:1}}
.card-name{{font-size:1rem;font-weight:700;letter-spacing:-.01em}}
.card-tag{{font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.07em;margin-top:2px}}
.card-desc{{font-size:.82rem;color:#94a3b8;line-height:1.5;max-width:480px}}
.payload-wrap{{margin-left:auto;min-width:220px;max-width:280px}}
.payload-label{{font-size:.65rem;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);margin-bottom:5px;font-weight:600}}
.payload-box{{width:100%;background:rgba(0,0,0,0.35);border:1px solid rgba(255,255,255,.07);border-radius:8px;padding:8px 10px;font-family:'JetBrains Mono',monospace;font-size:.72rem;color:#a5b4fc;resize:vertical;min-height:46px;outline:none;transition:.2s;line-height:1.4}}
.payload-box:focus{{border-color:rgba(165,180,252,.4);background:rgba(0,0,0,.5)}}

/* ── TEST GRID ── */
.test-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:0}}

/* ── TEST PANEL ── */
.test-panel{{padding:16px 18px;border-right:1px solid var(--border);display:flex;flex-direction:column;gap:10px}}
.test-panel:last-child{{border-right:none}}
.panel-label{{font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.07em;opacity:.75;display:flex;align-items:center;gap:6px}}
.panel-label::before{{content:'';width:6px;height:6px;border-radius:50%;flex-shrink:0}}
.pl-attack{{color:var(--red)}}.pl-attack::before{{background:var(--red);box-shadow:0 0 6px var(--red)}}
.pl-modsec{{color:var(--orange)}}.pl-modsec::before{{background:var(--orange);box-shadow:0 0 6px var(--orange)}}
.pl-ai{{color:var(--purple)}}.pl-ai::before{{background:var(--purple);box-shadow:0 0 6px var(--purple)}}

/* ── BUTTON ── */
.btn{{padding:9px 14px;border-radius:10px;border:none;cursor:pointer;font-weight:600;font-size:.8rem;display:flex;align-items:center;justify-content:center;gap:7px;width:100%;transition:all .2s cubic-bezier(.4,0,.2,1);position:relative;overflow:hidden;color:#fff}}
.btn::after{{content:'';position:absolute;inset:0;background:linear-gradient(rgba(255,255,255,.12),transparent);opacity:0;transition:.2s}}
.btn:hover::after{{opacity:1}}
.btn:hover{{transform:translateY(-1px);box-shadow:0 6px 16px rgba(0,0,0,.35)}}
.btn:active{{transform:none}}
.btn:disabled{{opacity:.5;cursor:not-allowed;transform:none}}
.btn-a{{background:linear-gradient(135deg,#ef4444,#b91c1c);box-shadow:0 3px 12px rgba(239,68,68,.25)}}
.btn-m{{background:linear-gradient(135deg,#f97316,#c2410c);box-shadow:0 3px 12px rgba(249,115,22,.25)}}
.btn-ai{{background:linear-gradient(135deg,#9333ea,#4f46e5);box-shadow:0 3px 12px rgba(147,51,234,.3)}}
.sp{{display:none;width:14px;height:14px;border:2px solid rgba(255,255,255,.25);border-top-color:#fff;border-radius:50%;animation:spin .6s linear infinite}}
@keyframes spin{{to{{rotate:360deg}}}}
.btn.ld .t{{display:none}}.btn.ld .sp{{display:block}}

/* ── RESULT BOX ── */
.res{{border-radius:10px;padding:11px 13px;min-height:64px;font-size:.78rem;display:flex;flex-direction:column;gap:6px;border:1px solid transparent;transition:all .3s ease}}
.res-idle{{background:rgba(0,0,0,.2);border-color:rgba(255,255,255,.05);color:var(--muted);align-items:center;justify-content:center;text-align:center}}
.res-spin{{background:rgba(0,0,0,.2);border-color:rgba(255,255,255,.05);align-items:center;justify-content:center}}
.res-spin .sp2{{width:20px;height:20px;border:2px solid rgba(255,255,255,.1);border-top-color:var(--purple);border-radius:50%;animation:spin .7s linear infinite}}
.res-danger{{background:rgba(239,68,68,.08);border-color:rgba(239,68,68,.3)}}
.res-ok{{background:rgba(16,185,129,.08);border-color:rgba(16,185,129,.35)}}
.res-warn{{background:rgba(239,68,68,.08);border-color:rgba(239,68,68,.25)}}
.rt{{font-weight:700;font-size:.85rem}}
.rs{{color:#94a3b8;font-size:.72rem;line-height:1.4;margin-top:1px}}
.score-bar{{height:5px;background:rgba(255,255,255,.07);border-radius:999px;overflow:hidden;margin-top:4px}}
.score-fill{{height:100%;border-radius:999px;transition:width .8s cubic-bezier(.4,0,.2,1)}}
</style>
</head>
<body>

<div class="hdr">
  <div class="hdr-inner">
    <span class="logo">OWASP Lab</span>
    <div class="dot"></div>
    <span style="color:var(--muted);font-size:.8rem">Tấn công &amp; Phòng thủ</span>
    <div class="hdr-right">
      <span class="chip chip-model">🤖 {model}</span>
      <span class="chip chip-mode">WAF: {mode}</span>
      <a class="dash-btn" href="/waf-dashboard">📊 Dashboard</a>
    </div>
  </div>
</div>

<div class="page">
  <div class="section-title">4 lỗ hổng OWASP Top 10</div>

  <!-- ── SQL Injection ── -->
  <div class="vuln-card" id="row-sqli">
    <div class="card-hdr">
      <span class="card-icon">🧬</span>
      <div class="card-meta">
        <div class="card-name">SQL Injection</div>
        <div class="card-tag" style="color:var(--red)">OWASP A03 · Critical</div>
        <div class="card-desc" style="margin-top:6px">Tiêm mã SQL vào form đăng nhập — bypass xác thực, đăng nhập tài khoản admin mà không cần mật khẩu.</div>
      </div>
      <div class="payload-wrap">
        <div class="payload-label">Payload (username field)</div>
        <textarea class="payload-box" id="sqli-payload">' OR '1'='1' --</textarea>
      </div>
    </div>
    <div class="test-grid">
      <div class="test-panel">
        <div class="panel-label pl-attack">Tấn công thật · :8081</div>
        <button class="btn btn-a" id="sqli-btn-a" onclick="testAttack('sqli')"><span class="t">⚔️ Tấn công</span><div class="sp"></div></button>
        <div class="res res-idle" id="sqli-res-a">Chưa test</div>
      </div>
      <div class="test-panel">
        <div class="panel-label pl-modsec">ModSecurity · :8082</div>
        <button class="btn btn-m" id="sqli-btn-m" onclick="testModsec('sqli')"><span class="t">🛡️ ModSecurity</span><div class="sp"></div></button>
        <div class="res res-idle" id="sqli-res-m">Chưa test</div>
      </div>
      <div class="test-panel">
        <div class="panel-label pl-ai">AI WAF (Groq) · :8083</div>
        <button class="btn btn-ai" id="sqli-btn-ai" onclick="testAI('sqli')"><span class="t">🤖 AI WAF</span><div class="sp"></div></button>
        <div class="res res-idle" id="sqli-res-ai">Chưa test</div>
      </div>
    </div>
  </div>

  <!-- ── Stored XSS ── -->
  <div class="vuln-card" id="row-xss">
    <div class="card-hdr">
      <span class="card-icon">💉</span>
      <div class="card-meta">
        <div class="card-name">Stored XSS</div>
        <div class="card-tag" style="color:var(--orange)">OWASP A03 · High</div>
        <div class="card-desc" style="margin-top:6px">Lưu JavaScript độc vào DB qua form bình luận — mọi người dùng xem trang đó đều bị thực thi mã.</div>
      </div>
      <div class="payload-wrap">
        <div class="payload-label">Payload (comment content)</div>
        <textarea class="payload-box" id="xss-payload">&lt;script&gt;alert('XSS-'+document.cookie)&lt;/script&gt;</textarea>
      </div>
    </div>
    <div class="test-grid">
      <div class="test-panel">
        <div class="panel-label pl-attack">Tấn công thật · :8081</div>
        <button class="btn btn-a" id="xss-btn-a" onclick="testAttack('xss')"><span class="t">⚔️ Tấn công</span><div class="sp"></div></button>
        <div class="res res-idle" id="xss-res-a">Chưa test</div>
      </div>
      <div class="test-panel">
        <div class="panel-label pl-modsec">ModSecurity · :8082</div>
        <button class="btn btn-m" id="xss-btn-m" onclick="testModsec('xss')"><span class="t">🛡️ ModSecurity</span><div class="sp"></div></button>
        <div class="res res-idle" id="xss-res-m">Chưa test</div>
      </div>
      <div class="test-panel">
        <div class="panel-label pl-ai">AI WAF (Groq) · :8083</div>
        <button class="btn btn-ai" id="xss-btn-ai" onclick="testAI('xss')"><span class="t">🤖 AI WAF</span><div class="sp"></div></button>
        <div class="res res-idle" id="xss-res-ai">Chưa test</div>
      </div>
    </div>
  </div>

  <!-- ── IDOR ── -->
  <div class="vuln-card" id="row-idor">
    <div class="card-hdr">
      <span class="card-icon">🔓</span>
      <div class="card-meta">
        <div class="card-name">IDOR</div>
        <div class="card-tag" style="color:var(--yellow)">OWASP A01 · High</div>
        <div class="card-desc" style="margin-top:6px">Thay đổi tham số ID trên URL để xem dữ liệu cá nhân của người dùng khác không thuộc quyền truy cập.</div>
      </div>
      <div class="payload-wrap">
        <div class="payload-label">URL target (id=3 → xem id=1)</div>
        <textarea class="payload-box" id="idor-payload">/index.php?page=profile&amp;id=1</textarea>
      </div>
    </div>
    <div class="test-grid">
      <div class="test-panel">
        <div class="panel-label pl-attack">Tấn công thật · :8081</div>
        <button class="btn btn-a" id="idor-btn-a" onclick="testAttack('idor')"><span class="t">⚔️ Tấn công</span><div class="sp"></div></button>
        <div class="res res-idle" id="idor-res-a">Chưa test</div>
      </div>
      <div class="test-panel">
        <div class="panel-label pl-modsec">ModSecurity · :8082</div>
        <button class="btn btn-m" id="idor-btn-m" onclick="testModsec('idor')"><span class="t">🛡️ ModSecurity</span><div class="sp"></div></button>
        <div class="res res-idle" id="idor-res-m">Chưa test</div>
      </div>
      <div class="test-panel">
        <div class="panel-label pl-ai">AI WAF (Groq) · :8083</div>
        <button class="btn btn-ai" id="idor-btn-ai" onclick="testAI('idor')"><span class="t">🤖 AI WAF</span><div class="sp"></div></button>
        <div class="res res-idle" id="idor-res-ai">Chưa test</div>
      </div>
    </div>
  </div>

  <!-- ── Broken Auth ── -->
  <div class="vuln-card" id="row-auth">
    <div class="card-hdr">
      <span class="card-icon">🔑</span>
      <div class="card-meta">
        <div class="card-name">Broken Auth</div>
        <div class="card-tag" style="color:var(--purple)">OWASP A07 · Critical</div>
        <div class="card-desc" style="margin-top:6px">Ứng dụng lưu mật khẩu plaintext trong DB — khi DB bị lộ, toàn bộ tài khoản bị chiếm ngay lập tức.</div>
      </div>
      <div class="payload-wrap">
        <div class="payload-label">Payload (login form body)</div>
        <textarea class="payload-box" id="auth-payload">username=admin&password=admin123</textarea>
      </div>
    </div>
    <div class="test-grid">
      <div class="test-panel">
        <div class="panel-label pl-attack">Tấn công thật · :8081</div>
        <button class="btn btn-a" id="auth-btn-a" onclick="testAttack('auth')"><span class="t">⚔️ Tấn công</span><div class="sp"></div></button>
        <div class="res res-idle" id="auth-res-a">Chưa test</div>
      </div>
      <div class="test-panel">
        <div class="panel-label pl-modsec">ModSecurity · :8082</div>
        <button class="btn btn-m" id="auth-btn-m" onclick="testModsec('auth')"><span class="t">🛡️ ModSecurity</span><div class="sp"></div></button>
        <div class="res res-idle" id="auth-res-m">Chưa test</div>
      </div>
      <div class="test-panel">
        <div class="panel-label pl-ai">AI WAF (Groq) · :8083</div>
        <button class="btn btn-ai" id="auth-btn-ai" onclick="testAI('auth')"><span class="t">🤖 AI WAF</span><div class="sp"></div></button>
        <div class="res res-idle" id="auth-res-ai">Chưa test</div>
      </div>
    </div>
  </div>

</div><!-- /page -->

<script>
function getCfg(key) {{
  const p = document.getElementById(key + '-payload').value;
  switch(key) {{
    case 'sqli':
      return {{
        attack: {{ method:'POST', path:'/index.php', params:{{}}, body:{{username:p, password:''}} }},
        probe:  {{ method:'POST', url:'http://localhost:8083/index.php', params:{{}}, body:{{username:p, password:''}}, user_id:'unknown' }},
        vuln:   'sqli'
      }};
    case 'xss': {{
      const d = p.replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&amp;/g,'&');
      return {{
        attack: {{ method:'POST', path:'/index.php', params:{{page:'comments'}}, body:{{content:d}} }},
        probe:  {{ method:'POST', url:'http://localhost:8083/index.php?page=comments', params:{{page:'comments'}}, body:{{content:d}}, user_id:'unknown' }},
        vuln:   'xss_stored'
      }};
    }}
    case 'idor': {{
      const u = p.replace(/&amp;/g,'&');
      const qi = u.indexOf('?');
      const params = qi>-1 ? Object.fromEntries(new URLSearchParams(u.substring(qi+1))) : {{}};
      return {{
        attack: {{ method:'GET', path:u, params:{{}}, body:{{}} }},
        probe:  {{ method:'GET', url:'http://localhost:8083'+u, params, body:{{}}, user_id:'3' }},
        vuln:   'idor'
      }};
    }}
    case 'auth': {{
      const body = Object.fromEntries(new URLSearchParams(p));
      return {{
        attack: {{ method:'POST', path:'/index.php', params:{{}}, body }},
        probe:  {{ method:'POST', url:'http://localhost:8083/index.php', params:{{}}, body, user_id:'unknown' }},
        vuln:   'auth_plaintext'
      }};
    }}
  }}
}}

function setLd(id, on) {{
  const b = document.getElementById(id);
  b.disabled = on;
  b.classList.toggle('ld', on);
}}

function showRes(id, html, cls) {{
  const el = document.getElementById(id);
  el.className = 'res ' + cls;
  el.innerHTML = html;
}}

function ldBox(id) {{
  const el = document.getElementById(id);
  el.className = 'res res-spin';
  el.innerHTML = '<div class="sp2"></div>';
}}

async function testAttack(key) {{
  const cfg = getCfg(key);
  setLd(key+'-btn-a', true); ldBox(key+'-res-a');
  try {{
    const r = await fetch('/waf-attack', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify(cfg.attack)}});
    const d = await r.json();
    if (d.success) {{
      showRes(key+'-res-a', `<div class="rt" style="color:#ef4444">💥 Tấn công thành công</div><div class="rs">HTTP ${{d.status}} — Ứng dụng bị xâm phạm!</div>`, 'res-danger');
    }} else {{
      showRes(key+'-res-a', `<div class="rt" style="color:#94a3b8">⚠️ Gửi được (HTTP ${{d.status}})</div><div class="rs">Request thực thi — không có WAF chặn</div>`, 'res-idle');
    }}
  }} catch(e) {{ showRes(key+'-res-a', `<div class="rs">Lỗi: ${{e.message}}</div>`, 'res-idle'); }}
  setLd(key+'-btn-a', false);
}}

async function testModsec(key) {{
  const cfg = getCfg(key);
  setLd(key+'-btn-m', true); ldBox(key+'-res-m');
  try {{
    const r = await fetch('/waf-modsec', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify(cfg.attack)}});
    const d = await r.json();
    if (d.blocked) {{
      showRes(key+'-res-m', `<div class="rt" style="color:#10b981">🛡️ Đã chặn — 403</div><div class="rs">ModSecurity CRS nhận diện và block payload</div>`, 'res-ok');
    }} else {{
      showRes(key+'-res-m', `<div class="rt" style="color:#ef4444">❌ Không chặn — HTTP ${{d.status}}</div><div class="rs">ModSecurity bỏ qua payload này</div>`, 'res-warn');
    }}
  }} catch(e) {{ showRes(key+'-res-m', `<div class="rs">Lỗi: ${{e.message}}</div>`, 'res-idle'); }}
  setLd(key+'-btn-m', false);
}}

const TC = {{sqli:'#ef4444',xss_stored:'#f97316',idor:'#eab308',auth_plaintext:'#a855f7',none:'#10b981'}};
const TL = {{sqli:'SQL Injection',xss_stored:'Stored XSS',idor:'IDOR',auth_plaintext:'Auth Plaintext',none:'Sạch ✅'}};

async function testAI(key) {{
  const cfg = getCfg(key);
  setLd(key+'-btn-ai', true); ldBox(key+'-res-ai');
  try {{
    const r = await fetch('/waf-probe', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify(cfg.probe)}});
    const v = await r.json();
    const color = TC[v.type] || '#818cf8';
    const label = TL[v.type] || v.type;
    if (v.action === 'block') {{
      showRes(key+'-res-ai',
        `<div class="rt" style="color:#10b981">🤖 Đã chặn — ${{label}}</div>
         <div class="rs">Score: <b style="color:${{color}}">${{v.score}}/100</b></div>
         <div class="score-bar"><div class="score-fill" style="width:${{v.score}}%;background:${{color}}"></div></div>`,
        'res-ok');
    }} else {{
      showRes(key+'-res-ai',
        `<div class="rt" style="color:#f97316">⚠️ Cho qua — ${{label}}</div>
         <div class="rs">Score: <b style="color:${{color}}">${{v.score}}/100</b> (dưới ngưỡng)</div>
         <div class="score-bar"><div class="score-fill" style="width:${{v.score}}%;background:${{color}}"></div></div>`,
        'res-warn');
    }}
  }} catch(e) {{ showRes(key+'-res-ai', `<div class="rs">Lỗi: ${{e.message}}</div>`, 'res-idle'); }}
  setLd(key+'-btn-ai', false);
}}
</script>
</body>
</html>"""
