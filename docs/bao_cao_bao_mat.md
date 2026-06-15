# BÁO CÁO AN TOÀN THÔNG TIN
## Phân tích và Khai thác Lỗ hổng Bảo mật Ứng dụng Web — OWASP Top 10

---

**Môn học:** An toàn thông tin  
**Nhóm thực hiện:** Nhóm 5  
**Môi trường lab:** Docker · PHP 8.2 · SQLite · ModSecurity WAF  
**URL thực nghiệm:**
- Phiên bản lỗi: `http://localhost:8081`
- Phiên bản đã vá: `http://localhost:8081/fixed.php`
- Qua WAF (ModSecurity): `http://localhost:80`

---

## 1. Tổng quan

Báo cáo này trình bày quá trình phân tích, tái hiện và vá 4 lỗ hổng bảo mật phổ biến thuộc danh sách **OWASP Top 10 2021** trên ứng dụng web mô phỏng VulnApp. Mỗi lỗ hổng được trình bày theo cấu trúc: định nghĩa → khai thác demo → phân tích code → bản vá → kiểm chứng.

| # | Lỗ hổng | OWASP 2021 | Mức độ |
|---|---------|------------|--------|
| 1 | SQL Injection | A03 — Injection | 🔴 Critical |
| 2 | Stored XSS | A03 — Injection | 🟠 High |
| 3 | IDOR | A01 — Broken Access Control | 🟠 High |
| 4 | Broken Auth (Plaintext Password) | A07 — Identification & Auth Failures | 🔴 Critical |

---

## 2. Kiến trúc hệ thống Lab

```
┌─────────────────────────────────────────────────────┐
│                    Attacker (Browser)                │
└────────────┬──────────────────────┬─────────────────┘
             │ :8081 (trực tiếp)    │ :80 (qua WAF)
             ▼                      ▼
    ┌─────────────────┐   ┌──────────────────────┐
    │  vulnapp        │   │  ModSecurity WAF      │
    │  PHP 8.2-Apache │◄──│  (OWASP CRS Nginx)   │
    │  SQLite DB      │   │  PARANOIA Level 1     │
    └────────┬────────┘   └──────────────────────┘
             │
    ┌────────▼────────┐
    │  /var/data/     │
    │  users.db       │
    └─────────────────┘
```

**Mục đích hai luồng truy cập:**
- **`:8081`** — Tấn công trực tiếp, minh họa lỗ hổng hoạt động
- **`:80`** — WAF chặn các payload phổ biến, minh họa lớp phòng thủ

---

## 3. Lỗ hổng 1 — SQL Injection (OWASP A03)

### 3.1 Định nghĩa
SQL Injection xảy ra khi input người dùng được ghép trực tiếp vào câu truy vấn SQL mà không qua sanitization. Attacker có thể thao túng logic truy vấn, bypass xác thực, hoặc đọc toàn bộ database.

### 3.2 Phân tích code lỗi

```php
// ❌ VULNERABLE — index.php dòng 49
$user = $_POST['username'];
$pass = $_POST['password'];
$sql = "SELECT * FROM users WHERE username='$user' AND password='$pass'";
$result = $db->query($sql)->fetch(PDO::FETCH_ASSOC);
```

### 3.3 Demo tấn công

**Payload:** Nhập vào ô username: `' OR '1'='1' --`

**Câu SQL sinh ra:**
```sql
SELECT * FROM users 
WHERE username='' OR '1'='1' --' AND password=''
```

**Giải thích:**
- `'` đóng chuỗi username
- `OR '1'='1'` làm mệnh đề WHERE luôn TRUE
- `--` comment hóa phần còn lại (bao gồm kiểm tra password)
- Kết quả: trả về **user đầu tiên trong bảng (admin)** → đăng nhập thành công không cần mật khẩu

### 3.4 Hậu quả
- Bypass hoàn toàn xác thực
- Có thể dùng `UNION SELECT` để đọc bảng khác
- Dẫn đến lộ toàn bộ dữ liệu users (kết hợp với lỗi Broken Auth)

### 3.5 Bản vá

```php
// ✅ FIXED — fixed.php
$stmt = $db->prepare("SELECT * FROM users WHERE username = ?");
$stmt->execute([$user]);
$result = $stmt->fetch(PDO::FETCH_ASSOC);

if ($result && password_verify($pass, $result['password'])) {
    // Đăng nhập thành công
}
```

**Nguyên lý bảo vệ:** Prepared Statement tách biệt code SQL và data. Input người dùng được driver xử lý như *data thuần*, ký tự `'` được escape tự động → payload `' OR '1'='1' --` trở thành chuỗi tìm kiếm theo nghĩa đen, không tìm thấy user nào.

### 3.6 Kiểm chứng
Sau khi vá, nhập payload `' OR '1'='1' --` vào `fixed.php` → thông báo "Sai tên đăng nhập hoặc mật khẩu" — **tấn công thất bại**.

---

## 4. Lỗ hổng 2 — Stored XSS (OWASP A03)

### 4.1 Định nghĩa
Stored XSS (Persistent XSS) xảy ra khi ứng dụng lưu input độc hại vào database rồi render lại mà không escape, khiến JavaScript của attacker chạy trong trình duyệt của mọi người dùng xem trang đó.

### 4.2 Phân tích code lỗi

```php
// ❌ VULNERABLE — index.php dòng 82 (INSERT)
$content = $_POST['content']; // Không sanitize
$db->exec("INSERT INTO comments (author, content) VALUES ('$author', '$content')");

// ❌ VULNERABLE — index.php dòng 326 (RENDER)
echo $c['content']; // Không escape → <script> chạy thẳng
```

### 4.3 Demo tấn công

**Payload nhập vào ô bình luận:**
```html
<script>alert('XSS - Nhom5 - ' + document.cookie)</script>
```

**Hậu quả:**
1. Script được lưu vào database nguyên vẹn
2. Mỗi khi bất kỳ user nào tải trang Comments → browser thực thi script
3. Attacker có thể đánh cắp session cookie, redirect người dùng, hoặc thực hiện hành động thay họ

### 4.4 Bản vá

```php
// ✅ FIXED — fixed.php
// INSERT: dùng Prepared Statement
$stmt = $db->prepare("INSERT INTO comments_fixed (author, content) VALUES (?, ?)");
$stmt->execute([$author, $content]);

// RENDER: escape khi hiển thị
echo htmlspecialchars($c['content'], ENT_QUOTES, 'UTF-8');
// <script> → &lt;script&gt; → hiển thị text, không chạy JS
```

**Quy tắc vàng:** Luôn escape output tại điểm render, không phải tại điểm nhập. `htmlspecialchars()` chuyển `<`, `>`, `"`, `'`, `&` thành HTML entities vô hại.

### 4.5 Kiểm chứng
Nhập payload XSS vào `fixed.php` → bình luận hiển thị đúng nghĩa đen `<script>alert(...)` dưới dạng text — **script không chạy**.

---

## 5. Lỗ hổng 3 — IDOR (OWASP A01)

### 5.1 Định nghĩa
IDOR (Insecure Direct Object Reference) xảy ra khi ứng dụng sử dụng ID có thể đoán được (như ID số nguyên) để truy cập tài nguyên mà không kiểm tra quyền của người dùng hiện tại.

### 5.2 Phân tích code lỗi

```php
// ❌ VULNERABLE — index.php dòng 91-94
$id = $_GET['id']; // Lấy thẳng từ URL parameter
// Không có bất kỳ kiểm tra nào: id này có thuộc user đang đăng nhập không?
$profileUser = $db->query("SELECT * FROM users WHERE id=$id")->fetch(PDO::FETCH_ASSOC);
```

### 5.3 Demo tấn công

User **bob** (id=3) đăng nhập, sau đó thay đổi URL:
```
http://localhost:8081/?page=profile&id=1   → Xem hồ sơ admin
http://localhost:8081/?page=profile&id=2   → Xem hồ sơ alice (lương, số điện thoại)
http://localhost:8081/?page=profile&id=4   → Xem hồ sơ charlie
```

**Dữ liệu lộ:** email, tiểu sử, số lương, thông tin nhạy cảm của tất cả người dùng.

### 5.4 Bản vá

```php
// ✅ FIXED — fixed.php
$requestedId = (int)$_GET['id'];
$myId   = (int)$_SESSION['fixed_user']['id'];
$myRole = $_SESSION['fixed_user']['role'];

// Chỉ cho phép: xem chính mình HOẶC là admin
if ($requestedId !== $myId && $myRole !== 'admin') {
    // Từ chối — 403 Forbidden
    $message = "🚫 403 Forbidden — Bạn không có quyền xem hồ sơ này!";
} else {
    $stmt = $db->prepare("SELECT * FROM users WHERE id = ?");
    $stmt->execute([$requestedId]);
    $profileUser = $stmt->fetch(PDO::FETCH_ASSOC);
}
```

**Nguyên lý:** Authorization check phải diễn ra ở **server-side**, trước khi truy vấn database. Client không bao giờ được tin tưởng.

### 5.5 Kiểm chứng
Đăng nhập là bob vào `fixed.php`, thay URL `?id=1` → nhận thông báo 403 Forbidden — **không xem được hồ sơ admin**.

---

## 6. Lỗ hổng 4 — Broken Authentication: Plaintext Password (OWASP A07)

### 6.1 Định nghĩa
Lưu mật khẩu dạng plaintext là lỗi nghiêm trọng nhất trong quản lý thông tin xác thực. Khi database bị lộ (qua SQLi, backup leak, insider threat...), toàn bộ mật khẩu gốc bị lộ ngay lập tức.

### 6.2 Phân tích code lỗi

```php
// ❌ VULNERABLE — index.php dòng 30-33
$db->exec("INSERT INTO users VALUES (1,'admin','admin123',...)");
$db->exec("INSERT INTO users VALUES (2,'alice','alice456',...)");
// Mật khẩu lưu nguyên văn trong database
```

### 6.3 Hậu quả thực tế

Khi kết hợp với SQLi, attacker chạy:
```sql
' UNION SELECT id, username, password, email, role FROM users --
```
→ Lấy được toàn bộ: `admin:admin123`, `alice:alice456`...

**Chuỗi tấn công tiếp theo (Credential Stuffing):**
Người dùng thường tái sử dụng mật khẩu → attacker thử `alice456` trên Gmail, Facebook, ngân hàng của alice.

### 6.4 Bản vá

```php
// ✅ FIXED — fixed.php (seeding)
$db->exec("INSERT INTO users VALUES (1,'admin','" 
    . password_hash('admin123', PASSWORD_BCRYPT) 
    . "','admin@vulnapp.local','admin','...')");

// Khi đăng nhập, verify hash:
if ($result && password_verify($pass, $result['password'])) {
    // Đăng nhập hợp lệ
}
```

**Mật khẩu trong DB sau khi vá:**
```
$2y$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhu
```
→ Dù lộ database, không thể đọc ngược ra `admin123`.

**Tại sao bcrypt?**
- **Adaptive cost:** Có thể tăng work factor theo thời gian
- **Built-in salt:** Mỗi hash khác nhau dù cùng input → chống rainbow table
- **Slow by design:** Brute-force tốn nhiều thời gian hơn MD5/SHA hàng nghìn lần

### 6.5 Kiểm chứng
Xem trang "Xem DB" ở `fixed.php` → cột password hiển thị `$2y$10$...` — **không đọc được mật khẩu gốc**.

---

## 7. Vai trò của WAF — ModSecurity OWASP CRS

### 7.1 Cấu hình

```yaml
# docker-compose.yml
waf:
  image: owasp/modsecurity-crs:nginx
  environment:
    BACKEND: "http://vulnapp:80"
    MODSEC_RULE_ENGINE: "On"
    PARANOIA: 1
    ANOMALY_INBOUND: 5
```

### 7.2 Cách WAF hoạt động

WAF (Web Application Firewall) kiểm tra HTTP request qua bộ rule **OWASP CRS (Core Rule Set)** trước khi forward đến ứng dụng:

```
Browser → WAF (:80) → [Kiểm tra rule] → vulnapp (:80 nội bộ)
                              │
                    Phát hiện SQLi/XSS?
                         YES → 403 Forbidden
                          NO → Forward request
```

### 7.3 Demo WAF

| Hành động | Qua :8081 (không WAF) | Qua :80 (có WAF) |
|-----------|----------------------|-----------------|
| Login bình thường | ✅ Vào được | ✅ Vào được |
| Payload `' OR '1'='1' --` | ✅ Bypass thành công | 🚫 403 Blocked |
| Payload `<script>alert()</script>` | ✅ Stored & executed | 🚫 403 Blocked |

### 7.4 Hạn chế của WAF

> [!WARNING]
> WAF **không phải giải pháp thay thế** cho code an toàn. WAF có thể bị bypass bởi:
> - Encoding tricks (`%27` thay vì `'`)
> - Payload phức tạp, ít phổ biến
> - Logic flaws (như IDOR) — WAF không hiểu business logic

**Kết luận:** WAF là lớp phòng thủ bổ sung (Defense in Depth), không phải giải pháp duy nhất.

---

## 8. So sánh Trước và Sau vá

| Tấn công | VulnApp (:8081) | FixedApp (/fixed.php) |
|----------|----------------|----------------------|
| SQLi bypass login | ✅ Thành công | ❌ Thất bại |
| Stored XSS | ✅ Script chạy | ❌ Hiện text thuần |
| IDOR xem profile người khác | ✅ Xem được | ❌ 403 Forbidden |
| Dump mật khẩu gốc | ✅ Đọc được plaintext | ❌ Chỉ thấy bcrypt hash |

---

## 9. Khuyến nghị bảo mật tổng thể

### Cho Developer:
1. **Luôn dùng Prepared Statement** — không bao giờ ghép string vào SQL
2. **Escape output, không phải input** — dùng `htmlspecialchars()` khi render
3. **Authorization check ở server-side** — mọi request đều phải xác minh quyền
4. **Dùng bcrypt/Argon2** cho mật khẩu — không bao giờ MD5, SHA1, plaintext
5. **Principle of Least Privilege** — DB user chỉ có quyền SELECT/INSERT cần thiết

### Cho hệ thống:
1. **WAF** — bổ sung lớp lọc, không phụ thuộc hoàn toàn
2. **HTTPS** — mã hóa traffic, chống man-in-the-middle
3. **Rate limiting** — chống brute-force
4. **Security headers** — `Content-Security-Policy`, `X-Frame-Options`
5. **Logging & Monitoring** — phát hiện tấn công sớm

---

## 10. Tài liệu tham khảo

1. OWASP Top 10 2021 — https://owasp.org/Top10/
2. OWASP SQL Injection Prevention Cheat Sheet
3. OWASP XSS Prevention Cheat Sheet
4. OWASP Broken Access Control
5. PHP `password_hash()` — https://www.php.net/manual/en/function.password-hash.php
6. ModSecurity OWASP CRS — https://coreruleset.org/
7. PDO Prepared Statements — https://www.php.net/manual/en/pdo.prepare.php

---

*Báo cáo được thực hiện trong môi trường lab Docker kiểm soát, phục vụ mục đích học thuật.*
