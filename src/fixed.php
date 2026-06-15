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

// Temporary plain seed for SQLi demonstration
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

    // ✅ Prepared statement — SQL Injection is patched
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
?>
<!DOCTYPE html>
<html>
<head><title>Fixed Version - SQLi Patched</title></head>
<body>
  <h2>🔑 Đăng nhập (SQL Injection đã vá)</h2>
  <form method="POST">
    <input type="text" name="username" placeholder="Username">
    <input type="password" name="password" placeholder="Password">
    <button type="submit" name="login">Đăng nhập</button>
  </form>
</body>
</html>
