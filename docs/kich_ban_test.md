# KỊCH BẢN KIỂM THỬ (TEST Walkthrough)
## Demo 4 Lỗ Hổng OWASP: Bản Lỗi vs Bản Vá vs Lớp WAF

Để demo thuyết phục nhất trước giảng viên, bạn nên thực hiện việc kiểm thử (test) theo trình tự 5 bước dưới đây.

---

### BƯỚC 0: Khởi động lại môi trường sạch (Clear Database & Reset)
Trước khi test, hãy reset toàn bộ Database và Container về trạng thái ban đầu:

```powershell
docker compose down -v
docker compose up -d --build
```
*Lệnh này sẽ xóa database cũ (`-v` volume), khởi tạo lại database sạch và bật tất cả các cổng:*
*   **`http://localhost:8081`**: Truy cập trực tiếp (Dùng để test Bản Lỗi vs Bản Vá).
*   **`http://localhost:8082`**: Truy cập qua lớp ModSecurity WAF.
*   **`http://localhost:8083`**: Truy cập qua AI WAF (Groq LLM — cần `GROQ_API_KEY` trong `.env`).
*   **`http://localhost:8083/waf-test`**: 🆕 **Test Console** — Giao diện trực quan so sánh 3 lớp phòng thủ.

---

### BƯỚC 1: Demo Lỗ hổng SQL Injection (Bypass Đăng nhập)

#### 1. Tấn công trên Bản Lỗi (VulnApp)
1. Mở trình duyệt, truy cập: **`http://localhost:8081/index.php`**
2. Nhập vào ô Tên đăng nhập:
   ```sql
   ' OR '1'='1' --
   ```
3. Mật khẩu: *Để trống*
4. Ấn **Đăng nhập**
   *   **Kết quả:** Bypass thành công! Bạn được đăng nhập trực tiếp vào tài khoản của **Quản trị viên (admin)**. Màn hình hiển thị câu SQL bị inject.

#### 2. Thử lại trên Bản Vá (FixedApp)
1. Truy cập trang đã vá: **`http://localhost:8081/fixed.php`**
2. Nhập payload tương tự: `' OR '1'='1' --`
3. Ấn **Đăng nhập**
   *   **Kết quả:** Báo lỗi `"Sai tên đăng nhập hoặc mật khẩu"`. Tấn công bị vô hiệu hóa hoàn toàn nhờ Prepared Statement.

#### 3. Thử tấn công qua lớp bảo vệ WAF
1. Truy cập qua cổng WAF: **`http://localhost:8082/index.php`**
2. Nhập payload: `' OR '1'='1' --`
3. Ấn **Đăng nhập**
   *   **Kết quả:** Trình duyệt nhận về trang **403 Forbidden** từ ModSecurity WAF. Payload tấn công đã bị WAF phát hiện và chặn đứng từ vòng gửi xe.

---

### BƯỚC 2: Demo Lỗ hổng Stored XSS (Bình luận độc hại)

#### 1. Đăng nhập tài khoản hợp lệ
*Đăng nhập vào cả hai trang bằng tài khoản thật để test bình luận:*
*   **Tài khoản:** `admin` / **Mật khẩu:** `admin123`

#### 2. Tấn công trên Bản Lỗi (VulnApp)
1. Truy cập: **`http://localhost:8081/index.php?page=comments`**
2. Nhập nội dung bình luận:
   ```html
   <script>alert('XSS - Nhom5 - ' + document.cookie)</script>
   ```
3. Ấn **Gửi bình luận**
   *   **Kết quả:** Xuất hiện ngay lập tức hộp thoại **Popup Alert** hiển thị Cookie của bạn. 
   *   **Hậu quả:** Kể từ bây giờ, bất kỳ ai (kể cả Alice, Bob) truy cập vào trang bình luận này cũng đều bị hiện popup Alert đó (Do JS đã được lưu vĩnh viễn vào Database).

#### 3. Thử lại trên Bản Vá (FixedApp)
1. Truy cập: **`http://localhost:8081/fixed.php?page=comments`**
2. Nhập payload tương tự: `<script>alert('XSS')</script>`
3. Ấn **Gửi bình luận**
   *   **Kết quả:** Bình luận hiển thị nguyên văn chuỗi `<script>alert('XSS')</script>` dưới dạng văn bản bình thường. **Không có popup nào hiện lên** nhờ hàm `htmlspecialchars()`.

#### 4. Thử tấn công qua lớp bảo vệ WAF
1. Truy cập qua cổng WAF: **`http://localhost:8082/index.php?page=comments`**
2. Nhập payload tương tự và ấn gửi
   *   **Kết quả:** Lập tức bị WAF chặn về trang **403 Forbidden**.

---

### BƯỚC 3: Demo Lỗ hổng IDOR (Xem hồ sơ người khác)

#### 1. Đăng nhập tài khoản thường
Đăng nhập bằng tài khoản của **Bob** trên cả hai trang:
*   **Tên đăng nhập:** `bob` / **Mật khẩu:** `bob789`

#### 2. Tấn công trên Bản Lỗi (VulnApp)
1. Truy cập trang Hồ sơ: **`http://localhost:8081/index.php?page=profile&id=3`** (ID của Bob).
2. Sửa tham số trên thanh địa chỉ URL thành:
   `http://localhost:8081/index.php?page=profile&id=2` (ID của Alice)
   *   **Kết quả:** Bạn đọc được thông tin cá nhân của Alice kèm thông tin nhạy cảm: **"Nhân viên kế toán - Lương: 15,000,000 VND"**.
3. Tiếp tục sửa thành `&id=1` (Admin)
   *   **Kết quả:** Xem được toàn bộ bio, email của Admin mà không cần bất kỳ quyền quản trị nào.

#### 3. Thử lại trên Bản Vá (FixedApp)
1. Đăng nhập Bob trên: **`http://localhost:8081/fixed.php`**
2. Truy cập hồ sơ Bob: `fixed.php?page=profile&id=3` (Xem bình thường).
3. Đổi URL thành `fixed.php?page=profile&id=2` (Alice) hoặc `&id=1` (Admin)
   *   **Kết quả:** Xuất hiện thông báo lỗi: **`🚫 403 Forbidden — Bạn không có quyền xem hồ sơ này!`**. Hệ thống đã xác thực Session ID trùng khớp với User ID yêu cầu trước khi hiển thị dữ liệu.

---

### BƯỚC 4: Demo Lỗ hổng Broken Authentication (Lưu mật khẩu thô)

#### 1. Xem DB trên Bản Lỗi (VulnApp)
1. Đăng nhập và truy cập: **`http://localhost:8081/index.php?page=dump`** (hoặc click nút **💀 Dump DB** trên thanh Menu).
2. **Kết quả:** Bảng cơ sở dữ liệu hiện ra, cột **Password** hiển thị rõ mồn một các mật khẩu dạng thô (plaintext) như: `admin123`, `alice456`, `bob789`.
   *   *Hậu quả:* Attacker chỉ cần chiếm được DB là có toàn quyền truy cập toàn bộ tài khoản người dùng.

#### 2. Xem DB trên Bản Vá (FixedApp)
1. Đăng nhập và truy cập: **`http://localhost:8081/fixed.php?page=dump`** (hoặc click nút **🔒 Xem DB**).
2. **Kết quả:** Cột **Password** giờ đây chỉ chứa các chuỗi hash bảo mật của thuật toán Bcrypt dạng:
   `$2y$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhu`
   *   *Giải thích:* Thuật toán Bcrypt là mã hóa một chiều (hashing). Dù hacker có lấy được chuỗi này cũng không thể giải mã ngược lại thành mật khẩu gốc để đi đăng nhập ở các dịch vụ khác của nạn nhân.

---

### BƯỚC 5: So sánh trực quan trên Test Console (AI WAF vs ModSecurity)

1. Mở trình duyệt, truy cập bảng điều khiển tổng hợp: **`http://localhost:8083/waf-test`**
2. Tại đây, hệ thống hiển thị giao diện Glassmorphism hiện đại với 4 thẻ ứng với 4 loại lỗ hổng.
3. Nhấp vào các nút **⚔️ Tấn công**, **🛡️ ModSecurity** và **🤖 AI WAF** để xem phản hồi thời gian thực của từng lớp phòng thủ.
4. **Kết quả điểm nhấn:** Giảng viên sẽ thấy **AI WAF (Groq)** có khả năng phân tích ngữ cảnh, chấm điểm rủi ro (Risk Score) chính xác và có thể nhận diện các cuộc tấn công phức tạp mà WAF truyền thống ModSecurity có thể bỏ sót.
