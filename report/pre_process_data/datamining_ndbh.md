# Báo cáo Khai phá Dữ liệu Người được Bảo hiểm (Insured Persons Data Mining) - UPGRADED

## 1. Tóm tắt Điều hành (Executive Summary)

- **Tổng số bản ghi rà soát:** 210,000+ bản ghi (Toàn bộ 21 tệp tin DataNDBH).
- **Chỉ số Sức khỏe Dữ liệu:** Đang ở mức **Nguy cấp (Critical Failure)** đối với một số trường thông tin tài chính.
- **Phạm vi độ tuổi:** 0 - 73 tuổi.

### Phân bổ Độ tuổi
![Age Distribution](file:///D:/desktop_folder/04_Fraud_Detection/report/pre_process_data/charts_persons/age_dist.png)
*Hình 1: Biểu đồ mật độ tuổi. Có thể thấy rõ các nhóm khách hàng mục tiêu tập trung mạnh ở dải 25-45 tuổi.*

---

## 2. Phân tích Chất lượng Dữ liệu (Data Integrity Audit)

Dựa trên quá trình quét sâu (Deep Scan) toàn bộ các chunk dữ liệu, chúng tôi ghi nhận các vấn đề nghiêm trọng sau:

- **Salary (Thu nhập):** **Trống 100% (NULL)**. Hoàn toàn không có dữ liệu lương trong các tệp tin xuất từ hệ thống hiện tại.
  - *Hệ quả:* Không thể thực hiện Risk Scoring dựa trên khả năng tài chính.
- **Gender (Giới tính):** Không tồn tại trong Schema của tập dữ liệu NDBH này. 
- **Phone Number (Số điện thoại):** Thiếu hụt khoảng **46%**. Đây là rào cản lớn cho việc truy vết các mạng lưới trục lợi (Syndicates) dùng chung SĐT.
- **Address (Địa chỉ):** Hoàn toàn rỗng.

---

## 3. Các đặc trưng định danh (ID Integrity)

Mặc dù thiếu hụt thông tin nhân khẩu học, các khóa liên kết vẫn đảm bảo tính toàn vẹn:

- **user_id:** 100% chuẩn UUID, không có giá trị rỗng. Sẵn sàng làm khóa gốc liên kết với bảng Claims và Expenses.
- **identity_number:** Đã được chuẩn hóa để loại bỏ khoảng trắng và ký tự đặc biệt, sẵn sàng cho việc chống trùng lặp (De-duplication).

---

## 4. Quy tắc Chuẩn hóa (Normalization Rules)

Hệ thống đã áp dụng các quy tắc sau để làm sạch dữ liệu phục vụ nạp vào Graph Database:

| Feature | Quy tắc Chuẩn hóa |
| :--- | :--- |
| `full_name` | Chuyển sang VIẾT HOA (UPPER CASE) + Trim whitespace. |
| `phone_number` | Numeric only (Loại bỏ dấu chấm, khoảng trắng, gạch nối). |
| `date_of_birth` | Quy đổi về định dạng chuẩn ISO 8601 (YYYY-MM-DD). |
| `Age` (Phái sinh) | Tính toán động: `Tuổi = 2026 - Năm sinh`. |

---

## 5. Kết luận & Hành động (Recommendations)

1. **Khôi phục dữ liệu:** Cần yêu cầu đội IT/Admin trích xuất lại trường `salary` và `gender` từ hệ thống Core gốc để làm giàu Ego-Network của người dùng.
2. **Standardization:** Việc làm sạch tên và SĐT là bắt buộc để tránh tạo ra các "Node ảo" trong Graph khi cùng một người dùng nhập liệu theo nhiều cách khác nhau.
3. **Data Enrichment:** Khuyến nghị sử dụng `identity_number` để liên kết chéo với các nguồn dữ liệu bên ngoài nhằm bù đắp cho sự thiếu hụt địa chỉ.
