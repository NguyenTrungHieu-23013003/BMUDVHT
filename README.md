# ⚠️ VulnApp & FixedApp — OWASP Top 10 Lab
Dự án Lab thực nghiệm phục vụ môn học **Bảo mật Ứng dụng và Hệ thống**. Dự án xây dựng một ứng dụng web PHP/SQLite chứa 4 lỗ hổng bảo mật phổ biến theo chuẩn OWASP Top 10, đồng thời đi kèm phiên bản đã được vá lỗi và một lớp tường lửa bảo vệ hệ thống ModSecurity WAF.

---

## 🛠️ Yêu cầu hệ thống
*   [Docker](https://www.docker.com/) & Docker Compose.

---

## 🚀 Hướng dẫn khởi chạy
Để khởi chạy toàn bộ Lab (bao gồm cả Bản Lỗi, Bản Vá và WAF), chạy lệnh duy nhất sau ở thư mục chứa project:

```powershell
docker compose up -d --build
```

---

## 🌐 Danh sách các dịch vụ & Cổng truy cập

Sau khi chạy thành công, bạn có thể truy cập các địa chỉ sau:

| Dịch vụ | Địa chỉ truy cập | Ghi chú |
|---|---|---|
| **Bản lỗi (VulnApp)** | [http://localhost:8081](http://localhost:8081) | Tấn công trực tiếp, minh họa lỗ hổng hoạt động |
| **Bản vá (FixedApp)** | [http://localhost:8081/fixed.php](http://localhost:8081/fixed.php) | Code đã vá bảo mật (Prepared statement, bcrypt, htmlspecialchars...) |
| **Qua bảo vệ WAF** | [http://localhost:8082](http://localhost:8082) | Đi qua ModSecurity WAF (Sử dụng bộ luật OWASP CRS) |

---

## 📚 Tài liệu đi kèm (Documentation)
Để phục vụ quá trình báo cáo và thuyết trình trước giảng viên, dự án đi kèm các tài liệu chi tiết trong thư mục `docs/`:

1.  **[Báo cáo bảo mật chi tiết (docs/bao_cao_bao_mat.md)](docs/bao_cao_bao_mat.md)**: Phân tích lý thuyết, code lỗi, payload tấn công, code vá và cơ chế hoạt động của WAF.
2.  **[Kịch bản kiểm thử demo (docs/kich_ban_test.md)](docs/kich_ban_test.md)**: Hướng dẫn từng bước cách thực hiện tấn công thực tế trên cả 3 môi trường để trình chiếu cho giảng viên xem.
3.  **[Câu hỏi phản biện & Phân công thuyết trình (docs/danh_gia_va_phan_bien.md)](docs/danh_gia_va_phan_bien.md)**: Tổng hợp các câu hỏi hóc búa giảng viên thường hỏi và gợi ý phân chia vai trò thuyết trình cho nhóm 4 người để đạt điểm tối đa.

---

*Dự án được thực hiện trong môi trường kiểm soát phục vụ mục đích học tập.*
