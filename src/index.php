<?php
session_start();

// ================================================================
// KHỞI TẠO DATABASE
// ================================================================
$db = new PDO('sqlite:/var/data/users.db');
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

// Bảng users — mật khẩu lưu PLAINTEXT (lỗi Broken Auth)
$db->exec("CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    password TEXT,
    email TEXT,
    role TEXT,
    bio TEXT
)");

// Bảng comments — lưu không sanitize (lỗi XSS)
$db->exec("CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author TEXT,
    content TEXT
)");

// Dữ liệu mẫu
if ($db->query("SELECT COUNT(*) FROM users")->fetchColumn() == 0) {
    // ❌ LỖI BROKEN AUTH: mật khẩu lưu plaintext, không hash
    $db->exec("INSERT INTO users VALUES (1,'admin','admin123','admin@vulnapp.local','admin','Quản trị viên hệ thống')");
    $db->exec("INSERT INTO users VALUES (2,'alice','alice456','alice@gmail.com','user','Nhân viên kế toán - Lương: 15,000,000 VND')");
    $db->exec("INSERT INTO users VALUES (3,'bob','bob789','bob@gmail.com','user','Nhân viên kỹ thuật - Dự án: Bí mật Quốc phòng')");
    $db->exec("INSERT INTO users VALUES (4,'charlie','charlie000','charlie@gmail.com','user','Giám đốc kinh doanh - SĐT: 0901234567')");
}

// ================================================================
// XỬ LÝ CÁC ACTION
// ================================================================
$message = "";
$messageType = "";
$currentPage = $_GET['page'] ?? 'home';

// --- LOGIN (có lỗi SQL Injection) ---
if (isset($_POST['login'])) {
    $user = $_POST['username'];
    $pass = $_POST['password'];

    // ❌ LỖI SQL INJECTION: ghép thẳng input, không dùng prepared statement
    $sql = "SELECT * FROM users WHERE username='$user' AND password='$pass'";
    try {
        $result = $db->query($sql)->fetch(PDO::FETCH_ASSOC);
        if ($result) {
            $_SESSION['user'] = $result;
            $_SESSION['sql_executed'] = $sql;
            $message = "✅ Đăng nhập thành công! Xin chào <b>{$result['username']}</b>";
            $messageType = "success";
            $currentPage = 'home';
        } else {
            $message = "❌ Sai tên đăng nhập hoặc mật khẩu.";
            $messageType = "error";
            $_SESSION['sql_executed'] = $sql;
        }
    } catch (Exception $e) {
        $message = "⚠️ Lỗi SQL: " . $e->getMessage();
        $messageType = "error";
    }
}

// --- LOGOUT ---
if (isset($_GET['logout'])) {
    session_destroy();
    header("Location: index.php");
    exit;
}

// --- GỬI COMMENT (có lỗi Stored XSS) ---
if (isset($_POST['comment']) && isset($_SESSION['user'])) {
    $author  = $_SESSION['user']['username'];
    $content = $_POST['content']; // ❌ LỖI XSS: không sanitize

    // ❌ LỖI SQL INJECTION lần 2: ghép thẳng vào INSERT
    $db->exec("INSERT INTO comments (author, content) VALUES ('$author', '$content')");
    $message = "💬 Đã đăng bình luận.";
    $messageType = "success";
    $currentPage = 'comments';
}

// --- XEM HỒ SƠ (có lỗi IDOR) ---
$profileUser = null;
if ($currentPage === 'profile' && isset($_GET['id'])) {
    $id = $_GET['id'];
    // ❌ LỖI IDOR: không kiểm tra xem id này có thuộc về user đang đăng nhập không
    // Ai cũng có thể đổi ?id=1, ?id=2, ?id=3... để xem hồ sơ người khác
    $profileUser = $db->query("SELECT * FROM users WHERE id=$id")->fetch(PDO::FETCH_ASSOC);
}

// --- DUMP DATABASE (hậu quả của SQLi + Broken Auth) ---
$dumpData = null;
if (isset($_GET['dump']) && isset($_SESSION['user'])) {
    $dumpData = $db->query("SELECT id, username, password, email, role FROM users")->fetchAll(PDO::FETCH_ASSOC);
}

$comments = $db->query("SELECT * FROM comments ORDER BY id DESC LIMIT 20")->fetchAll(PDO::FETCH_ASSOC);
$loggedIn = isset($_SESSION['user']);
$me = $_SESSION['user'] ?? null;
?>
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>VulnApp — Lab OWASP Top 10</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f0f2f5; color: #1a1a18; }

/* NAV */
nav { background: #1a1a18; padding: 0 24px; display: flex; align-items: center; gap: 0; }
nav .logo { color: #ef4444; font-weight: 700; font-size: 16px; padding: 14px 0; margin-right: 24px; }
nav a { color: #aaa; text-decoration: none; font-size: 13px; padding: 14px 14px; display: inline-block; transition: color .15s; }
nav a:hover { color: #fff; }
nav a.active { color: #fff; border-bottom: 2px solid #ef4444; }
nav .spacer { flex: 1; }
nav .user-badge { color: #4ade80; font-size: 12px; padding: 14px 0; }

.wrap { max-width: 900px; margin: 0 auto; padding: 24px 16px; }

/* VULN BADGE */
.vuln-tag { display: inline-flex; align-items: center; gap: 6px; font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 99px; margin-bottom: 12px; }
.vuln-sqli  { background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca; }
.vuln-xss   { background: #fff7ed; color: #c2410c; border: 1px solid #fed7aa; }
.vuln-idor  { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }
.vuln-auth  { background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0; }

/* CARDS */
.card { background: #fff; border-radius: 12px; border: 1px solid #e5e7eb; padding: 20px 24px; margin-bottom: 20px; }
.card h2 { font-size: 16px; margin-bottom: 14px; }

/* HINT BOX */
.hint { background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px; padding: 10px 14px; font-size: 12px; color: #92400e; margin-bottom: 14px; line-height: 1.6; }
.hint code { background: #fef3c7; padding: 1px 5px; border-radius: 4px; font-family: monospace; }

/* FORM */
label { font-size: 13px; color: #555; display: block; margin-bottom: 4px; margin-top: 10px; }
input[type=text], input[type=password], textarea {
    width: 100%; padding: 9px 12px; border: 1px solid #d1d5db; border-radius: 8px;
    font-size: 13px; font-family: inherit; transition: border-color .15s;
}
input:focus, textarea:focus { outline: none; border-color: #6366f1; }
.btn { display: inline-block; padding: 9px 20px; border-radius: 8px; border: none; font-size: 13px; font-weight: 500; cursor: pointer; transition: background .15s; }
.btn-red   { background: #ef4444; color: #fff; }
.btn-red:hover { background: #dc2626; }
.btn-blue  { background: #3b82f6; color: #fff; }
.btn-blue:hover { background: #2563eb; }
.btn-green { background: #22c55e; color: #fff; }
.btn-green:hover { background: #16a34a; }
.btn-gray  { background: #f3f4f6; color: #374151; border: 1px solid #d1d5db; }
.btn-gray:hover { background: #e5e7eb; }

/* MESSAGE */
.msg { padding: 10px 14px; border-radius: 8px; font-size: 13px; margin-bottom: 14px; }
.msg.success { background: #f0fdf4; border: 1px solid #86efac; color: #166534; }
.msg.error   { background: #fef2f2; border: 1px solid #fca5a5; color: #991b1b; }

/* SQL DISPLAY */
.sql-box { background: #0f172a; border-radius: 8px; padding: 12px 16px; font-family: monospace; font-size: 13px; color: #e2e8f0; margin: 10px 0; word-break: break-all; line-height: 1.6; }
.sql-box .highlight { color: #f87171; font-weight: 700; }

/* PROFILE GRID */
.profile-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 12px; }
.profile-nav-card { border: 1px solid #e5e7eb; border-radius: 8px; padding: 10px; text-align: center; cursor: pointer; text-decoration: none; transition: border-color .15s; }
.profile-nav-card:hover { border-color: #3b82f6; background: #eff6ff; }
.profile-nav-card .uid { font-size: 20px; font-weight: 700; color: #3b82f6; }
.profile-nav-card .uname { font-size: 12px; color: #666; }

/* PROFILE CARD */
.profile-detail { border: 1px solid #bfdbfe; border-radius: 10px; background: #eff6ff; padding: 16px 20px; }
.profile-detail .field { display: flex; gap: 12px; padding: 6px 0; border-bottom: 1px solid #dbeafe; font-size: 13px; }
.profile-detail .field:last-child { border-bottom: none; }
.profile-detail .field-key { color: #1d4ed8; font-weight: 600; min-width: 100px; }

/* COMMENT */
.comment-item { padding: 10px 0; border-bottom: 1px solid #f3f4f6; }
.comment-item:last-child { border-bottom: none; }
.comment-author { font-size: 12px; font-weight: 600; color: #6366f1; margin-bottom: 3px; }

/* DUMP TABLE */
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th { background: #1a1a18; color: #fff; padding: 8px 12px; text-align: left; }
td { padding: 8px 12px; border-bottom: 1px solid #f3f4f6; }
td.password-cell { color: #ef4444; font-weight: 600; font-family: monospace; }
tr:hover td { background: #fef2f2; }

/* OVERVIEW BADGES */
.owasp-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.owasp-card { border-radius: 10px; padding: 14px 16px; border: 1px solid; }
.owasp-card h3 { font-size: 13px; font-weight: 600; margin-bottom: 4px; }
.owasp-card p { font-size: 12px; line-height: 1.5; }

.tag-row { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 16px; }
</style>
</head>
<body>

<nav>
  <div class="logo">⚠️ VulnApp</div>
  <a href="?page=home" class="<?= $currentPage==='home'?'active':'' ?>">Trang chủ</a>
  <?php if ($loggedIn): ?>
  <a href="?page=comments" class="<?= $currentPage==='comments'?'active':'' ?>">Bình luận</a>
  <a href="?page=profile&id=<?= $me['id'] ?>" class="<?= $currentPage==='profile'?'active':'' ?>">Hồ sơ</a>
  <a href="?page=dump" class="<?= $currentPage==='dump'?'active':'' ?>" style="color:#f87171">💀 Dump DB</a>
  <?php endif; ?>
  <div class="spacer"></div>
  <?php if ($loggedIn): ?>
    <span class="user-badge">👤 <?= htmlspecialchars($me['username']) ?> (<?= $me['role'] ?>)</span>
    <a href="?logout=1" style="color:#f87171;margin-left:12px">Đăng xuất</a>
  <?php endif; ?>
</nav>

<div class="wrap">

<?php if ($message): ?>
  <div class="msg <?= $messageType ?>"><?= $message ?></div>
<?php endif; ?>

<!-- ================================================================ -->
<!-- TRANG CHỦ / LOGIN                                                  -->
<!-- ================================================================ -->
<?php if ($currentPage === 'home'): ?>

<?php if (!$loggedIn): ?>
<div class="card">
  <div class="vuln-tag vuln-sqli">⚡ OWASP A03 — SQL Injection</div>
  <h2>🔑 Đăng nhập</h2>
  <div class="hint">
    💡 <b>Tấn công SQLi:</b> Nhập <code>' OR '1'='1' --</code> vào ô username, để trống password<br>
    → Bypass hoàn toàn, đăng nhập được dù không biết mật khẩu
  </div>
  <form method="POST">
    <label>Tên đăng nhập</label>
    <input type="text" name="username" placeholder="Thử: ' OR '1'='1' --">
    <label>Mật khẩu</label>
    <input type="password" name="password" placeholder="Để trống cũng được khi dùng SQLi">
    <div style="margin-top:14px">
      <button type="submit" name="login" class="btn btn-red">Đăng nhập</button>
      <span style="font-size:12px;color:#999;margin-left:12px">Tài khoản thật: admin / admin123</span>
    </div>
  </form>

  <?php if (isset($_SESSION['sql_executed'])): ?>
  <div style="margin-top:16px">
    <div style="font-size:13px;font-weight:600;margin-bottom:6px;color:#555">🔍 Câu SQL đã thực thi:</div>
    <div class="sql-box"><?php
      $rawSql = $_SESSION['sql_executed'];
      // Highlight phần nguy hiểm
      $highlighted = htmlspecialchars($rawSql);
      $highlighted = preg_replace("/(OR '1'='1'[^']*)/i", '<span class="highlight">$1</span>', $highlighted);
      echo $highlighted;
    ?></div>
    <div style="font-size:12px;color:#888;margin-top:6px">
      ↑ Khi nhập <code>' OR '1'='1' --</code>, mệnh đề WHERE luôn đúng → trả về user đầu tiên trong bảng (admin)
    </div>
  </div>
  <?php endif; ?>
</div>

<?php else: ?>

<!-- Dashboard sau khi đăng nhập -->
<div class="card">
  <h2>🏠 Chào mừng, <span style="color:#6366f1"><?= htmlspecialchars($me['username']) ?></span>!</h2>
  <p style="font-size:13px;color:#666;margin-bottom:16px">Bạn đã đăng nhập thành công. Khám phá các lỗ hổng bảo mật bên dưới.</p>

  <div class="owasp-grid">
    <div class="owasp-card" style="background:#fef2f2;border-color:#fecaca">
      <h3 style="color:#b91c1c">⚡ A03 — SQL Injection</h3>
      <p style="color:#7f1d1d">Đã khai thác thành công ở màn đăng nhập. Câu SQL bị thao túng để bypass xác thực.</p>
    </div>
    <div class="owasp-card" style="background:#fff7ed;border-color:#fed7aa">
      <h3 style="color:#c2410c">🔥 A03 — Stored XSS</h3>
      <p style="color:#7c2d12">Thử vào trang Bình luận, nhập script độc hại → script được lưu và chạy khi tải trang.</p>
    </div>
    <div class="owasp-card" style="background:#eff6ff;border-color:#bfdbfe">
      <h3 style="color:#1d4ed8">🔓 A01 — IDOR</h3>
      <p style="color:#1e3a8a">Thử vào Hồ sơ, đổi ?id=1, 2, 3, 4 để xem thông tin cá nhân của người khác.</p>
    </div>
    <div class="owasp-card" style="background:#f0fdf4;border-color:#bbf7d0">
      <h3 style="color:#166534">💀 A07 — Broken Auth</h3>
      <p style="color:#14532d">Bấm "Dump DB" để thấy toàn bộ mật khẩu được lưu dạng plaintext, không mã hóa.</p>
    </div>
  </div>
</div>

<?php endif; ?>

<!-- ================================================================ -->
<!-- TRANG BÌNH LUẬN — STORED XSS                                       -->
<!-- ================================================================ -->
<?php elseif ($currentPage === 'comments'): ?>
<div class="card">
  <div class="vuln-tag vuln-xss">🔥 OWASP A03 — Stored XSS</div>
  <h2>💬 Bình luận</h2>
  <div class="hint">
    💡 <b>Tấn công Stored XSS:</b> Nhập vào ô nội dung:<br>
    <code>&lt;script&gt;alert('XSS - Nhom5 - ' + document.cookie)&lt;/script&gt;</code><br>
    → Script được lưu vào database, <b>tự động chạy</b> mỗi khi ai tải trang này
  </div>
  <?php if ($loggedIn): ?>
  <form method="POST">
    <label>Nội dung bình luận</label>
    <textarea name="content" rows="3" placeholder="Nhập bình luận hoặc payload XSS..."></textarea>
    <div style="margin-top:10px">
      <button type="submit" name="comment" class="btn btn-red">Gửi bình luận</button>
    </div>
  </form>
  <?php endif; ?>

  <div style="margin-top:20px;border-top:1px solid #f3f4f6;padding-top:16px">
    <div style="font-size:13px;font-weight:600;margin-bottom:10px">Các bình luận đã đăng:</div>
    <?php if (empty($comments)): ?>
      <div style="font-size:13px;color:#aaa">Chưa có bình luận nào. Hãy thử nhập payload XSS!</div>
    <?php else: ?>
      <?php foreach ($comments as $c): ?>
        <div class="comment-item">
          <div class="comment-author"><?= htmlspecialchars($c['author']) ?></div>
          <!-- ❌ LỖI XSS: echo thẳng không qua htmlspecialchars -->
          <div><?= $c['content'] ?></div>
        </div>
      <?php endforeach; ?>
    <?php endif; ?>
  </div>

  <div style="margin-top:16px;padding-top:16px;border-top:1px solid #f3f4f6">
    <div style="font-size:12px;font-weight:600;color:#c2410c;margin-bottom:6px">❌ Code lỗi (dòng echo không sanitize):</div>
    <div class="sql-box"><span class="highlight">echo $c['content'];</span>  <span style="color:#64748b">// ❌ Chạy thẳng bất kỳ HTML/JS nào từ DB</span></div>
    <div style="font-size:12px;font-weight:600;color:#166534;margin-bottom:6px;margin-top:10px">✅ Code đúng:</div>
    <div class="sql-box" style="color:#86efac">echo htmlspecialchars($c['content'], ENT_QUOTES, 'UTF-8');  <span style="color:#64748b">// Vô hiệu hóa &lt;script&gt;</span></div>
  </div>
</div>

<!-- ================================================================ -->
<!-- TRANG HỒ SƠ — IDOR                                                 -->
<!-- ================================================================ -->
<?php elseif ($currentPage === 'profile'): ?>
<div class="card">
  <div class="vuln-tag vuln-idor">🔓 OWASP A01 — IDOR (Insecure Direct Object Reference)</div>
  <h2>👤 Hồ sơ người dùng</h2>
  <div class="hint">
    💡 <b>Tấn công IDOR:</b> Bạn đang đăng nhập với tài khoản <b><?= htmlspecialchars($me['username'] ?? '') ?></b> (id=<?= $me['id'] ?? '?' ?>)<br>
    Hãy thử đổi <code>?id=1</code>, <code>?id=2</code>, <code>?id=3</code>, <code>?id=4</code> trên URL<br>
    → Xem được thông tin cá nhân, email, tiểu sử của người khác <b>mà không cần quyền gì</b>
  </div>

  <!-- Nút điều hướng nhanh -->
  <div class="profile-grid">
    <?php for ($i = 1; $i <= 4; $i++): ?>
    <a href="?page=profile&id=<?= $i ?>" class="profile-nav-card" style="<?= (isset($_GET['id']) && $_GET['id'] == $i) ? 'border-color:#3b82f6;background:#eff6ff' : '' ?>">
      <div class="uid">#<?= $i ?></div>
      <div class="uname">?id=<?= $i ?></div>
    </a>
    <?php endfor; ?>
  </div>

  <?php if ($profileUser): ?>
  <div class="profile-detail">
    <div style="font-size:13px;font-weight:700;color:#1d4ed8;margin-bottom:10px">
      📋 Đang xem hồ sơ ID=<?= htmlspecialchars($_GET['id']) ?>
      <?php if ($profileUser['id'] != $me['id']): ?>
        <span style="color:#ef4444;font-size:11px;margin-left:8px">⚠️ KHÔNG PHẢI TÀI KHOẢN CỦA BẠN!</span>
      <?php else: ?>
        <span style="color:#22c55e;font-size:11px;margin-left:8px">✓ Hồ sơ của bạn</span>
      <?php endif; ?>
    </div>
    <div class="field"><span class="field-key">ID:</span> <?= $profileUser['id'] ?></div>
    <div class="field"><span class="field-key">Username:</span> <?= htmlspecialchars($profileUser['username']) ?></div>
    <div class="field"><span class="field-key">Email:</span> <span style="color:#ef4444"><?= htmlspecialchars($profileUser['email']) ?></span></div>
    <div class="field"><span class="field-key">Role:</span> <?= htmlspecialchars($profileUser['role']) ?></div>
    <div class="field"><span class="field-key">Tiểu sử:</span> <span style="color:#dc2626;font-weight:500"><?= htmlspecialchars($profileUser['bio']) ?></span></div>
  </div>
  <?php endif; ?>

  <div style="margin-top:16px;padding-top:16px;border-top:1px solid #f3f4f6">
    <div style="font-size:12px;font-weight:600;color:#c2410c;margin-bottom:6px">❌ Code lỗi — không kiểm tra quyền:</div>
    <div class="sql-box">$id = $_GET['id'];  <span style="color:#64748b">// ❌ Lấy thẳng từ URL, ai cũng đổi được</span>
<span class="highlight">$user = $db->query("SELECT * FROM users WHERE id=$id")->fetch();</span>
<span style="color:#64748b">// Không kiểm tra: $id có phải của user đang đăng nhập không?</span></div>
    <div style="font-size:12px;font-weight:600;color:#166534;margin-bottom:6px;margin-top:10px">✅ Code đúng — kiểm tra quyền trước:</div>
    <div class="sql-box" style="color:#86efac">$id = $_GET['id'];
if ($id != $_SESSION['user']['id'] && $_SESSION['user']['role'] !== 'admin') {
    die('403 Forbidden — Bạn không có quyền xem hồ sơ này');
}
$stmt = $db->prepare("SELECT * FROM users WHERE id=?");
$stmt->execute([$id]);</div>
  </div>
</div>

<!-- ================================================================ -->
<!-- DUMP DATABASE — BROKEN AUTH                                         -->
<!-- ================================================================ -->
<?php elseif ($currentPage === 'dump'): ?>
<div class="card">
  <div class="vuln-tag vuln-auth">💀 OWASP A07 — Broken Authentication (Mật khẩu Plaintext)</div>
  <h2>🗄️ Dump toàn bộ bảng Users</h2>
  <div class="hint">
    💡 <b>Kịch bản thực tế:</b> Sau khi khai thác SQLi ở màn đăng nhập, attacker có thể<br>
    chạy lệnh <code>UNION SELECT</code> để dump toàn bộ database. Kết quả bên dưới cho thấy<br>
    mật khẩu được lưu <b>dạng plaintext</b> — lỗi Broken Authentication nghiêm trọng nhất
  </div>

  <table>
    <tr>
      <th>ID</th>
      <th>Username</th>
      <th style="color:#f87171">⚠️ Password (PLAINTEXT!)</th>
      <th>Email</th>
      <th>Role</th>
    </tr>
    <?php
    $allUsers = $db->query("SELECT id, username, password, email, role FROM users")->fetchAll(PDO::FETCH_ASSOC);
    foreach ($allUsers as $u): ?>
    <tr>
      <td><?= $u['id'] ?></td>
      <td><?= htmlspecialchars($u['username']) ?></td>
      <td class="password-cell">🔓 <?= htmlspecialchars($u['password']) ?></td>
      <td><?= htmlspecialchars($u['email']) ?></td>
      <td><?= htmlspecialchars($u['role']) ?></td>
    </tr>
    <?php endforeach; ?>
  </table>

  <div style="margin-top:16px;padding:12px 16px;background:#fef2f2;border-radius:8px;border:1px solid #fecaca;font-size:13px;color:#991b1b">
    ⚠️ <b>Hậu quả:</b> Attacker có toàn bộ mật khẩu gốc → thử đăng nhập Gmail, Facebook, ngân hàng của từng người (vì người dùng thường dùng lại mật khẩu)
  </div>

  <div style="margin-top:16px;padding-top:16px;border-top:1px solid #f3f4f6">
    <div style="font-size:12px;font-weight:600;color:#c2410c;margin-bottom:6px">❌ Code lỗi — lưu plaintext:</div>
    <div class="sql-box"><span class="highlight">INSERT INTO users (password) VALUES ('$password')</span>
<span style="color:#64748b">// ❌ Lưu thẳng mật khẩu gốc vào database</span></div>
    <div style="font-size:12px;font-weight:600;color:#166534;margin-bottom:6px;margin-top:10px">✅ Code đúng — dùng bcrypt:</div>
    <div class="sql-box" style="color:#86efac">$hashed = password_hash($password, PASSWORD_BCRYPT);
INSERT INTO users (password) VALUES ('$hashed')
<span style="color:#64748b">// ✅ Lưu dạng: $2y$10$abcdef... — không thể đọc ngược lại được</span>

// Khi verify:
password_verify($inputPassword, $hashedFromDB); // true/false</div>
  </div>
</div>

<?php endif; ?>

</div><!-- end .wrap -->
</body>
</html>
