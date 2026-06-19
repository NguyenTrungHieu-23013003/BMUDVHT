# Báo cáo Tổng quan Dự án: OWASP Security Lab & AI WAF Middleware

## 1. Giới thiệu chung
Dự án **BMUDVHT** là một hệ thống phòng thí nghiệm bảo mật web (Security Lab) được thiết kế để minh họa và so sánh hiệu quả giữa các phương pháp tấn công web phổ biến (theo chuẩn OWASP) và các cơ chế phòng thủ khác nhau. Điểm nhấn đặc biệt của dự án là việc tích hợp một **AI WAF (Web Application Firewall)** sử dụng sức mạnh của Mô hình Ngôn ngữ Lớn (LLM) để nhận diện và ngăn chặn các cuộc tấn công một cách thông minh, thay thế cho các luật (rules) cứng nhắc truyền thống.

## 2. Kiến trúc Hệ thống
Hệ thống được thiết kế theo mô hình Microservices và được đóng gói hoàn toàn bằng Docker, bao gồm các thành phần (services) chính:

1. **VulnApp / FixedApp (Cổng 8081):**
   - **Bản lỗi (`index.php`):** Được thiết kế cố tình chứa các lỗ hổng bảo mật để làm mục tiêu tấn công.
   - **Bản vá (`fixed.php`):** Ứng dụng đã được lập trình an toàn, sử dụng Prepared Statements (chống SQLi), `htmlspecialchars` (chống XSS), và hash mật khẩu (Bcrypt).
2. **ModSecurity WAF (Cổng 8082):**
   - Đóng vai trò là Reverse Proxy.
   - Sử dụng bộ luật tiêu chuẩn OWASP CRS (Core Rule Set). Đây là đại diện cho hệ thống tường lửa WAF truyền thống dựa trên Regex.
3. **AI WAF Middleware (Cổng 8083):**
   - Hệ thống tường lửa thế hệ mới được viết bằng Python (FastAPI).
   - Tích hợp API của **Groq** (sử dụng model `llama-3.3-70b-versatile`).
   - Có một bảng điều khiển (Test Console) Giao diện Kính mờ (Glassmorphism) để trực quan hóa quá trình kiểm thử.

## 3. Các Lỗ hổng Bảo mật được Triển khai
Hệ thống tập trung vào 4 nhóm lỗ hổng nguy hiểm và phổ biến nhất:
*   **SQL Injection (OWASP A03 - Critical):** Lỗi tiêm nhiễm mã SQL vào form đăng nhập, cho phép kẻ tấn công bypass cơ chế xác thực mà không cần mật khẩu (ví dụ: payload `' OR '1'='1' --`).
*   **Stored XSS (OWASP A03 - High):** Lỗ hổng Cross-Site Scripting lưu trữ. Kẻ tấn công có thể chèn mã JavaScript độc hại vào mục bình luận, mã này sẽ được thực thi trên trình duyệt của bất kỳ nạn nhân nào xem bình luận đó.
*   **IDOR (OWASP A01 - High):** Insecure Direct Object Reference. Cho phép người dùng thao túng tham số `id` trên URL để truy cập trái phép vào dữ liệu cá nhân của người dùng khác.
*   **Broken Authentication (OWASP A07 - Critical):** Lỗ hổng xác thực do lưu trữ mật khẩu dưới dạng văn bản gốc (plaintext) trong cơ sở dữ liệu.

## 4. Cơ chế hoạt động của AI WAF
Thay vì kiểm tra dữ liệu theo danh sách từ khóa bị cấm, AI WAF hoạt động bằng cách:
1. **Đánh chặn (Intercept):** Bắt toàn bộ các request (Method, URL, Params, Body). Bỏ qua các file tĩnh tĩnh (`.css`, `.js`, `.png`) để tối ưu hiệu năng.
2. **Phân tích (Classification):** Gom các dữ liệu của request tạo thành một "Prompt" và gửi tới Groq LLM. AI sẽ đóng vai trò là một "Chuyên gia Bảo mật", phân tích ngữ cảnh và quyết định xem đoạn dữ liệu đó là an toàn hay chứa mã độc thuộc loại nào (SQLi, XSS...).
3. **Chấm điểm & Quyết định:** Trả về một chuỗi JSON chứa điểm rủi ro (0-100). Nếu điểm số vượt qua ngưỡng thiết lập (`BLOCK_THRESHOLD = 70`), hệ thống sẽ trả về mã lỗi 403 (Forbidden) để chặn đứng cuộc tấn công.

## 5. Công nghệ sử dụng
- **Backend Vulnerable App:** PHP thuần, MariaDB (Cơ sở dữ liệu).
- **AI Middleware:** Python, FastAPI, Thư viện `groq`.
- **Frontend (Test Console):** HTML, CSS thuần với phong cách thiết kế Glassmorphism hiện đại.
- **Triển khai:** Docker & Docker Compose.

## 6. Tổng kết
Dự án không chỉ là một môi trường để thực hành tấn công mạng (Offensive Security) mà còn cung cấp một giải pháp tiếp cận mới trong việc phòng thủ (Defensive Security) bằng cách ứng dụng AI. Bảng điều khiển (Test Console) tích hợp cho phép thao tác "One-Click", giúp người dùng dễ dàng so sánh hiệu quả giữa việc không có bảo vệ, dùng WAF truyền thống (ModSecurity) và dùng AI WAF.
