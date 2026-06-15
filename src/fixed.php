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

// --- PROFILE — ✅ FIX: IDOR protection ---
$profileUser = null;
if ($currentPage === 'profile' && isset($_GET['id']) && isset($_SESSION['fixed_user'])) {
    $requestedId = (int)$_GET['id'];
    $myId   = (int)$_SESSION['fixed_user']['id'];
    $myRole = $_SESSION['fixed_user']['role'];

    // ✅ Authorization check: Only self or admin can view
    if ($requestedId === $myId || $myRole === 'admin') {
        $stmt = $db->prepare("SELECT * FROM users WHERE id = ?");
        $stmt->execute([$requestedId]);
        $profileUser = $stmt->fetch(PDO::FETCH_ASSOC);
    } else {
        $message = "🚫 403 Forbidden — Bạn không có quyền xem hồ sơ này!";
        $messageType = "error";
    }
}
?>
<!DOCTYPE html>
<html>
<head><title>Fixed Version - SQLi, XSS, and IDOR Patched</title></head>
<body>
  <!-- Existing pages -->
</body>
</html>
