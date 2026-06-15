<?php
session_start();

// ================================================================
// DATABASE — dùng chung file, nhưng seed mật khẩu BCRYPT riêng
// ================================================================
$db = new PDO('sqlite:/var/data/users_fixed.db');
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

$db->exec("CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    password TEXT,
    email TEXT,
    role TEXT,
    bio TEXT
)");

$db->exec("CREATE TABLE IF NOT EXISTS comments_fixed (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author TEXT,
    content TEXT
)");

// Seed với mật khẩu BCRYPT (✅ FIX Broken Auth)
if ($db->query("SELECT COUNT(*) FROM users")->fetchColumn() == 0) {
    $db->exec("INSERT INTO users VALUES (1,'admin','" . password_hash('admin123', PASSWORD_BCRYPT) . "','admin@vulnapp.local','admin','Quản trị viên hệ thống')");
    $db->exec("INSERT INTO users VALUES (2,'alice','" . password_hash('alice456', PASSWORD_BCRYPT) . "','alice@gmail.com','user','Nhân viên kế toán')");
    $db->exec("INSERT INTO users VALUES (3,'bob','"   . password_hash('bob789',   PASSWORD_BCRYPT) . "','bob@gmail.com','user','Nhân viên kỹ thuật')");
    $db->exec("INSERT INTO users VALUES (4,'charlie','" . password_hash('charlie000', PASSWORD_BCRYPT) . "','charlie@gmail.com','user','Giám đốc kinh doanh')");
}

$message = ""; $messageType = "";
$currentPage = $_GET['page'] ?? 'home';

// --- LOGIN — ✅ FIX: Prepared Statement + password_verify ---
if (isset($_POST['login'])) {
    $user = $_POST['username'];
    $pass = $_POST['password'];

    // ✅ Prepared statement — không thể inject
    $stmt = $db->prepare("SELECT * FROM users WHERE username = ?");
    $stmt->execute([$user]);
    $result = $stmt->fetch(PDO::FETCH_ASSOC);

    // ✅ password_verify kiểm tra bcrypt hash
    if ($result && password_verify($pass, $result['password'])) {
        $_SESSION['fixed_user'] = $result;
        $message = "✅ Đăng nhập thành công! Xin chào <b>{$result['username']}</b>";
        $messageType = "success";
        $currentPage = 'home';
    } else {
        $message = "❌ Sai tên đăng nhập hoặc mật khẩu.";
        $messageType = "error";
    }
}

if (isset($_GET['logout'])) {
    unset($_SESSION['fixed_user']);
    header("Location: fixed.php");
    exit;
}

// --- COMMENT — ✅ FIX: Prepared Statement + htmlspecialchars khi hiển thị ---
if (isset($_POST['comment']) && isset($_SESSION['fixed_user'])) {
    $author  = $_SESSION['fixed_user']['username'];
    $content = $_POST['content'];

    // ✅ Prepared statement cho INSERT
    $stmt = $db->prepare("INSERT INTO comments_fixed (author, content) VALUES (?, ?)");
    $stmt->execute([$author, $content]);
    $message = "💬 Đã đăng bình luận.";
    $messageType = "success";
    $currentPage = 'comments';
}

// --- PROFILE — ✅ FIX: Kiểm tra quyền (IDOR fix) ---
$profileUser = null;
if ($currentPage === 'profile' && isset($_GET['id']) && isset($_SESSION['fixed_user'])) {
    $requestedId = (int)$_GET['id'];
    $myId   = (int)$_SESSION['fixed_user']['id'];
    $myRole = $_SESSION['fixed_user']['role'];

    // ✅ Chỉ cho xem nếu là chính mình hoặc admin
    if ($requestedId === $myId || $myRole === 'admin') {
        $stmt = $db->prepare("SELECT * FROM users WHERE id = ?");
        $stmt->execute([$requestedId]);
        $profileUser = $stmt->fetch(PDO::FETCH_ASSOC);
    } else {
        $message = "🚫 403 Forbidden — Bạn không có quyền xem hồ sơ này!";
        $messageType = "error";
    }
}

$comments = $db->query("SELECT * FROM comments_fixed ORDER BY id DESC LIMIT 20")->fetchAll(PDO::FETCH_ASSOC);
$loggedIn = isset($_SESSION['fixed_user']);
$me = $_SESSION['fixed_user'] ?? null;
?>
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>FixedApp — Phiên bản đã vá lỗi</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f0fdf4; color: #1a1a18; }
nav { background: #14532d; padding: 0 24px; display: flex; align-items: center; gap: 0; }
nav .logo { color: #4ade80; font-weight: 700; font-size: 16px; padding: 14px 0; margin-right: 24px; }
nav a { color: #aaa; text-decoration: none; font-size: 13px; padding: 14px 14px; display: inline-block; transition: color .15s; }
nav a:hover { color: #fff; }
nav a.active { color: #4ade80; border-bottom: 2px solid #4ade80; }
nav .spacer { flex: 1; }
nav .user-badge { color: #4ade80; font-size: 12px; padding: 14px 0; }
.wrap { max-width: 900px; margin: 0 auto; padding: 24px 16px; }
.fix-tag { display: inline-flex; align-items: center; gap: 6px; font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 99px; margin-bottom: 12px; background: #dcfce7; color: #14532d; border: 1px solid #86efac; }
.card { background: #fff; border-radius: 12px; border: 1px solid #bbf7d0; padding: 20px 24px; margin-bottom: 20px; }
.card h2 { font-size: 16px; margin-bottom: 14px; }
.hint-ok { background: #f0fdf4; border: 1px solid #86efac; border-radius: 8px; padding: 10px 14px; font-size: 12px; color: #14532d; margin-bottom: 14px; line-height: 1.6; }
.hint-ok code { background: #dcfce7; padding: 1px 5px; border-radius: 4px; font-family: monospace; }
.hint-block { background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 10px 14px; font-size: 12px; color: #991b1b; margin-bottom: 14px; line-height: 1.6; }
label { font-size: 13px; color: #555; display: block; margin-bottom: 4px; margin-top: 10px; }
input[type=text], input[type=password], textarea { width: 100%; padding: 9px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 13px; font-family: inherit; }
input:focus, textarea:focus { outline: none; border-color: #22c55e; }
.btn { display: inline-block; padding: 9px 20px; border-radius: 8px; border: none; font-size: 13px; font-weight: 500; cursor: pointer; }
.btn-green { background: #22c55e; color: #fff; }
.btn-green:hover { background: #16a34a; }
.btn-gray { background: #f3f4f6; color: #374151; border: 1px solid #d1d5db; }
.msg { padding: 10px 14px; border-radius: 8px; font-size: 13px; margin-bottom: 14px; }
.msg.success { background: #f0fdf4; border: 1px solid #86efac; color: #166534; }
.msg.error   { background: #fef2f2; border: 1px solid #fca5a5; color: #991b1b; }
.code-box { background: #0f172a; border-radius: 8px; padding: 12px 16px; font-family: monospace; font-size: 12px; color: #86efac; margin: 8px 0; line-height: 1.7; }
.code-box .bad { color: #f87171; }
.code-box .comment { color: #64748b; }
.compare { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 14px; }
.compare-box { border-radius: 8px; padding: 12px; }
.compare-box.vuln { background: #fef2f2; border: 1px solid #fecaca; }
.compare-box.fixed-box { background: #f0fdf4; border: 1px solid #86efac; }
.compare-box .label { font-size: 11px; font-weight: 700; margin-bottom: 6px; }
.compare-box.vuln .label { color: #b91c1c; }
.compare-box.fixed-box .label { color: #15803d; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th { background: #14532d; color: #fff; padding: 8px 12px; text-align: left; }
td { padding: 8px 12px; border-bottom: 1px solid #f3f4f6; }
.comment-item { padding: 10px 0; border-bottom: 1px solid #f3f4f6; }
.comment-author { font-size: 12px; font-weight: 600; color: #16a34a; margin-bottom: 3px; }
.profile-detail { border: 1px solid #86efac; border-radius: 10px; background: #f0fdf4; padding: 16px 20px; }
.profile-detail .field { display: flex; gap: 12px; padding: 6px 0; border-bottom: 1px solid #dcfce7; font-size: 13px; }
.profile-detail .field:last-child { border-bottom: none; }
.profile-detail .field-key { color: #15803d; font-weight: 600; min-width: 100px; }
.banner { background: linear-gradient(135deg, #14532d, #166534); border-radius: 12px; padding: 20px 24px; margin-bottom: 20px; color: #fff; }
.banner h1 { font-size: 20px; margin-bottom: 6px; }
.banner p { font-size: 13px; opacity: .8; }
.switch-link { display: inline-block; margin-top: 10px; font-size: 12px; color: #86efac; text-decoration: none; }
.switch-link:hover { text-decoration: underline; }
.owasp-grid { display: grid; grid-template-columns: repeat(2,1fr); gap: 12px; }
.owasp-card { border-radius: 10px; padding: 14px 16px; background: #f0fdf4; border: 1px solid #86efac; }
.owasp-card h3 { font-size: 13px; font-weight: 600; margin-bottom: 4px; color: #15803d; }
.owasp-card p { font-size: 12px; color: #166534; line-height: 1.5; }
</style>
</head>
<body>
<nav>
  <div class="logo">✅ FixedApp</div>
  <a href="fixed.php?page=home" class="<?= $currentPage==='home'?'active':'' ?>">Trang chủ</a>
  <?php if ($loggedIn): ?>
  <a href="fixed.php?page=comments" class="<?= $currentPage==='comments'?'active':'' ?>">Bình luận</a>
  <a href="fixed.php?page=profile&id=<?= $me['id'] ?>" class="<?= $currentPage==='profile'?'active':'' ?>">Hồ sơ</a>
  <a href="fixed.php?page=dump" class="<?= $currentPage==='dump'?'active':'' ?>">🔒 Xem DB</a>
  <?php endif; ?>
  <div class="spacer"></div>
  <?php if ($loggedIn): ?>
    <span class="user-badge">👤 <?= htmlspecialchars($me['username']) ?> (<?= $me['role'] ?>)</span>
    <a href="fixed.php?logout=1" style="color:#f87171;margin-left:12px">Đăng xuất</a>
  <?php endif; ?>
</nav>

<div class="wrap">

<div class="banner">
  <h1>✅ Phiên bản đã vá lỗi (Fixed Version)</h1>
  <p>Tất cả 4 lỗ hổng OWASP đã được sửa. Hãy thử tấn công lại — sẽ không còn hoạt động!</p>
  <a href="index.php" class="switch-link">← Quay về VulnApp (phiên bản lỗi)</a>
</div>

<?php if ($message): ?>
  <div class="msg <?= $messageType ?>"><?= $message ?></div>
<?php endif; ?>

<!-- ================================================================ -->
<!-- TRANG CHỦ / LOGIN                                                  -->
<!-- ================================================================ -->
<?php if ($currentPage === 'home'): ?>

<?php if (!$loggedIn): ?>
<div class="card">
  <div class="fix-tag">✅ OWASP A03 — SQL Injection ĐÃ VÁ</div>
  <h2>🔑 Đăng nhập (Đã bảo mật)</h2>

  <div class="hint-ok">
    ✅ <b>Đã dùng Prepared Statement.</b> Thử nhập <code>' OR '1'='1' --</code> vào username → hệ thống sẽ tìm đúng nghĩa đen chuỗi đó, không tìm được user nào → đăng nhập thất bại.<br>
    🔐 Tài khoản hợp lệ: <code>admin</code> / <code>admin123</code>
  </div>

  <form method="POST">
    <label>Tên đăng nhập</label>
    <input type="text" name="username" placeholder="Thử: ' OR '1'='1' -- (sẽ bị từ chối)">
    <label>Mật khẩu</label>
    <input type="password" name="password" placeholder="Nhập đúng mật khẩu mới vào được">
    <div style="margin-top:14px">
      <button type="submit" name="login" class="btn btn-green">Đăng nhập</button>
    </div>
  </form>

  <div class="compare">
    <div class="compare-box vuln">
      <div class="label">❌ Code cũ (có lỗi SQLi)</div>
      <div class="code-box" style="margin:0">
        <span class="bad">$sql = "SELECT * FROM users</span><br>
        <span class="bad">&nbsp;&nbsp;WHERE username='$user'</span><br>
        <span class="bad">&nbsp;&nbsp;AND password='$pass'";</span><br>
        <span class="comment">// Inject: ' OR '1'='1' --</span>
      </div>
    </div>
    <div class="compare-box fixed-box">
      <div class="label">✅ Code mới (Prepared Statement)</div>
      <div class="code-box" style="margin:0">
        $stmt = $db->prepare(<br>
        &nbsp;&nbsp;"SELECT * FROM users<br>
        &nbsp;&nbsp;WHERE username = ?"<br>
        );<br>
        $stmt->execute([$user]);<br>
        <span class="comment">// Inject vô tác dụng</span>
      </div>
    </div>
  </div>
</div>

<?php else: ?>
<div class="card">
  <h2>🏠 Chào mừng, <span style="color:#16a34a"><?= htmlspecialchars($me['username']) ?></span>!</h2>
  <p style="font-size:13px;color:#666;margin-bottom:16px">Đăng nhập bằng credentials hợp lệ. Các lỗ hổng đã được vá:</p>
  <div class="owasp-grid">
    <div class="owasp-card"><h3>✅ A03 — SQL Injection → ĐÃ VÁ</h3><p>Prepared Statement: input được treat là data, không là SQL code.</p></div>
    <div class="owasp-card"><h3>✅ A03 — Stored XSS → ĐÃ VÁ</h3><p>htmlspecialchars() khi render: &lt;script&gt; bị escape thành text thuần.</p></div>
    <div class="owasp-card"><h3>✅ A01 — IDOR → ĐÃ VÁ</h3><p>Kiểm tra session trước: chỉ xem hồ sơ chính mình hoặc admin.</p></div>
    <div class="owasp-card"><h3>✅ A07 — Broken Auth → ĐÃ VÁ</h3><p>Bcrypt hash: mật khẩu lưu dạng $2y$10$... không đọc ngược được.</p></div>
  </div>
</div>
<?php endif; ?>

<!-- ================================================================ -->
<!-- BÌNH LUẬN — XSS ĐÃ VÁ                                            -->
<!-- ================================================================ -->
<?php elseif ($currentPage === 'comments'): ?>
<div class="card">
  <div class="fix-tag">✅ OWASP A03 — Stored XSS ĐÃ VÁ</div>
  <h2>💬 Bình luận (Đã bảo mật)</h2>

  <div class="hint-ok">
    ✅ <b>Thử nhập payload XSS:</b> <code>&lt;script&gt;alert('XSS')&lt;/script&gt;</code><br>
    → Script được lưu vào DB nhưng khi hiển thị bị escape → chỉ hiện text, không chạy JS.
  </div>

  <?php if ($loggedIn): ?>
  <form method="POST">
    <label>Nội dung bình luận</label>
    <textarea name="content" rows="3" placeholder="Thử nhập <script>alert('XSS')</script> — sẽ không chạy được"></textarea>
    <div style="margin-top:10px">
      <button type="submit" name="comment" class="btn btn-green">Gửi bình luận</button>
    </div>
  </form>
  <?php endif; ?>

  <div style="margin-top:20px;border-top:1px solid #dcfce7;padding-top:16px">
    <div style="font-size:13px;font-weight:600;margin-bottom:10px">Các bình luận đã đăng:</div>
    <?php if (empty($comments)): ?>
      <div style="font-size:13px;color:#aaa">Chưa có bình luận nào.</div>
    <?php else: ?>
      <?php foreach ($comments as $c): ?>
        <div class="comment-item">
          <div class="comment-author"><?= htmlspecialchars($c['author']) ?></div>
          <!-- ✅ FIX XSS: htmlspecialchars escape toàn bộ HTML/JS -->
          <div><?= htmlspecialchars($c['content'], ENT_QUOTES, 'UTF-8') ?></div>
        </div>
      <?php endforeach; ?>
    <?php endif; ?>
  </div>

  <div class="compare">
    <div class="compare-box vuln">
      <div class="label">❌ Code cũ (XSS)</div>
      <div class="code-box" style="margin:0"><span class="bad">echo $c['content'];</span><br><span class="comment">// Chạy thẳng &lt;script&gt;</span></div>
    </div>
    <div class="compare-box fixed-box">
      <div class="label">✅ Code mới (escaped)</div>
      <div class="code-box" style="margin:0">echo htmlspecialchars(<br>&nbsp;&nbsp;$c['content'],<br>&nbsp;&nbsp;ENT_QUOTES, 'UTF-8'<br>);<br><span class="comment">// &lt;script&gt; → &amp;lt;script&amp;gt;</span></div>
    </div>
  </div>
</div>

<!-- ================================================================ -->
<!-- HỒ SƠ — IDOR ĐÃ VÁ                                               -->
<!-- ================================================================ -->
<?php elseif ($currentPage === 'profile'): ?>
<div class="card">
  <div class="fix-tag">✅ OWASP A01 — IDOR ĐÃ VÁ</div>
  <h2>👤 Hồ sơ người dùng (Đã bảo mật)</h2>

  <div class="hint-ok">
    ✅ <b>Kiểm tra quyền trước khi truy cập:</b> Bạn chỉ có thể xem hồ sơ của chính mình.<br>
    Thử đổi URL thành <code>?page=profile&id=1</code>, <code>?id=2</code>... → 403 Forbidden nếu không phải bạn.
  </div>

  <?php if ($profileUser): ?>
  <div class="profile-detail">
    <div style="font-size:13px;font-weight:700;color:#15803d;margin-bottom:10px">
      📋 Hồ sơ của bạn (ID=<?= htmlspecialchars((string)$_GET['id']) ?>)
      <span style="color:#22c55e;font-size:11px;margin-left:8px">✓ Được phép xem</span>
    </div>
    <div class="field"><span class="field-key">ID:</span> <?= $profileUser['id'] ?></div>
    <div class="field"><span class="field-key">Username:</span> <?= htmlspecialchars($profileUser['username']) ?></div>
    <div class="field"><span class="field-key">Email:</span> <?= htmlspecialchars($profileUser['email']) ?></div>
    <div class="field"><span class="field-key">Role:</span> <?= htmlspecialchars($profileUser['role']) ?></div>
    <div class="field"><span class="field-key">Tiểu sử:</span> <?= htmlspecialchars($profileUser['bio']) ?></div>
  </div>
  <?php else: ?>
  <div class="hint-block">
    🚫 <b>Truy cập bị từ chối!</b> Bạn chỉ được xem hồ sơ của chính mình (id=<?= $me['id'] ?>).<br>
    Đây chính là cách IDOR được vá — server kiểm tra quyền trước khi trả dữ liệu.
  </div>
  <?php endif; ?>

  <div class="compare">
    <div class="compare-box vuln">
      <div class="label">❌ Code cũ (IDOR)</div>
      <div class="code-box" style="margin:0"><span class="bad">$id = $_GET['id'];</span><br><span class="bad">$user = $db->query(</span><br><span class="bad">&nbsp;"SELECT * FROM users</span><br><span class="bad">&nbsp;WHERE id=$id")->fetch();</span><br><span class="comment">// Không kiểm tra quyền!</span></div>
    </div>
    <div class="compare-box fixed-box">
      <div class="label">✅ Code mới (có kiểm tra)</div>
      <div class="code-box" style="margin:0">$id = (int)$_GET['id'];<br>if ($id !== $myId<br>&nbsp;&amp;&amp; $role !== 'admin') {<br>&nbsp;&nbsp;die('403 Forbidden');<br>}<br>$stmt = $db->prepare(<br>&nbsp;"SELECT * FROM users<br>&nbsp;WHERE id=?"<br>);</div>
    </div>
  </div>
</div>

<!-- ================================================================ -->
<!-- XEM DB — BROKEN AUTH ĐÃ VÁ                                        -->
<!-- ================================================================ -->
<?php elseif ($currentPage === 'dump'): ?>
<div class="card">
  <div class="fix-tag">✅ OWASP A07 — Broken Auth ĐÃ VÁ</div>
  <h2>🔒 Xem Database (Mật khẩu đã băm)</h2>

  <div class="hint-ok">
    ✅ <b>Mật khẩu lưu dạng bcrypt hash.</b> Dù attacker dump được DB, họ chỉ thấy chuỗi <code>$2y$10$...</code> — không thể đọc ngược lại mật khẩu gốc.
  </div>

  <table>
    <tr>
      <th>ID</th><th>Username</th><th style="color:#4ade80">🔒 Password (BCRYPT HASH)</th><th>Email</th><th>Role</th>
    </tr>
    <?php
    $allUsers = $db->query("SELECT id, username, password, email, role FROM users")->fetchAll(PDO::FETCH_ASSOC);
    foreach ($allUsers as $u): ?>
    <tr>
      <td><?= $u['id'] ?></td>
      <td><?= htmlspecialchars($u['username']) ?></td>
      <td style="color:#16a34a;font-family:monospace;font-size:11px">🔒 <?= htmlspecialchars($u['password']) ?></td>
      <td><?= htmlspecialchars($u['email']) ?></td>
      <td><?= htmlspecialchars($u['role']) ?></td>
    </tr>
    <?php endforeach; ?>
  </table>

  <div style="margin-top:14px;padding:12px 16px;background:#f0fdf4;border-radius:8px;border:1px solid #86efac;font-size:13px;color:#166534">
    ✅ <b>Kết quả:</b> Dù dump được bảng users, attacker chỉ thấy hash <code>$2y$10$...</code>. Không thể đăng nhập vào Gmail/Facebook của nạn nhân vì không biết mật khẩu gốc.
  </div>

  <div class="compare" style="margin-top:14px">
    <div class="compare-box vuln">
      <div class="label">❌ Code cũ (plaintext)</div>
      <div class="code-box" style="margin:0"><span class="bad">INSERT INTO users</span><br><span class="bad">(password)</span><br><span class="bad">VALUES ('admin123')</span><br><span class="comment">// Lưu thẳng → lộ hết!</span></div>
    </div>
    <div class="compare-box fixed-box">
      <div class="label">✅ Code mới (bcrypt)</div>
      <div class="code-box" style="margin:0">$hash = password_hash(<br>&nbsp;&nbsp;$pass, PASSWORD_BCRYPT<br>);<br>INSERT INTO users<br>(password) VALUES ($hash)<br><span class="comment">// $2y$10$abc... an toàn</span></div>
    </div>
  </div>
</div>

<?php endif; ?>

</div><!-- end .wrap -->
</body>
</html>
