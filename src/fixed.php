<?php
session_start();

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

if ($db->query("SELECT COUNT(*) FROM users")->fetchColumn() == 0) {
    $db->exec("INSERT INTO users VALUES (1,'admin','admin123','admin@vulnapp.local','admin','Quản trị viên hệ thống')");
    $db->exec("INSERT INTO users VALUES (2,'alice','alice456','alice@gmail.com','user','Nhân viên kế toán')");
}

$message = ""; $messageType = "";
$currentPage = $_GET['page'] ?? 'home';

// --- LOGIN — ✅ FIX: Prepared Statement ---
if (isset($_POST['login'])) {
    $user = $_POST['username'];
    $pass = $_POST['password'];

    $stmt = $db->prepare("SELECT * FROM users WHERE username = ? AND password = ?");
    $stmt->execute([$user, $pass]);
    $result = $stmt->fetch(PDO::FETCH_ASSOC);

    if ($result) {
        $_SESSION['fixed_user'] = $result;
        $message = "✅ Đăng nhập thành công! Xin chào <b>{$result['username']}</b>";
        $messageType = "success";
        $currentPage = 'home';
    } else {
        $message = "❌ Sai tên đăng nhập hoặc mật khẩu.";
        $messageType = "error";
    }
}

// --- COMMENT — ✅ FIX: Stored XSS patched ---
if (isset($_POST['comment']) && isset($_SESSION['fixed_user'])) {
    $author  = $_SESSION['fixed_user']['username'];
    $content = $_POST['content'];

    // Prepared statement for insert
    $stmt = $db->prepare("INSERT INTO comments_fixed (author, content) VALUES (?, ?)");
    $stmt->execute([$author, $content]);
    $message = "💬 Đã đăng bình luận.";
    $messageType = "success";
    $currentPage = 'comments';
}

$comments = $db->query("SELECT * FROM comments_fixed ORDER BY id DESC LIMIT 20")->fetchAll(PDO::FETCH_ASSOC);
?>
<!DOCTYPE html>
<html>
<head><title>Fixed Version - SQLi and XSS Patched</title></head>
<body>
  <h2>🔑 Đăng nhập (SQL Injection đã vá)</h2>
  <!-- Form login here -->

  <h2>💬 Bình luận (Stored XSS đã vá)</h2>
  <?php foreach ($comments as $c): ?>
    <div>
      <b><?= htmlspecialchars($c['author']) ?>:</b> 
      <!-- ✅ HTMLSpecialChars output encoding to prevent XSS -->
      <?= htmlspecialchars($c['content'], ENT_QUOTES, 'UTF-8') ?>
    </div>
  <?php endforeach; ?>
</body>
</html>
