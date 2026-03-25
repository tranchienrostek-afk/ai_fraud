# Báo cáo Khai phá Dữ liệu Người được Bảo hiểm (Insured Persons Data Mining)

## 1. Tóm tắt Điều hành (Executive Summary)

- **Tổng số bản ghi rà soát:** 50,000 (Mẫu đại diện từ 21 tệp tin).
- **Chỉ số Sức khỏe Dữ liệu:** Đang ở mức **Cảnh báo (Critical)** do thiếu hụt nhiều trường thông tin cốt lõi.
- **Phạm vi độ tuổi:** 0 - 73 tuổi.

## 2. Phân tích Nhân khẩu học (Demographics)

### Phân bổ Độ tuổi
![Age Distribution](file:///D:/desktop_folder/04_Fraud_Detection/report/pre_process_data/charts_persons/age_dist.png)
*Hình 1: Biểu đồ mật độ tuổi. Có thể thấy rõ các nhóm khách hàng mục tiêu và dải tuổi tiềm ẩn rủi ro trục lợi cao.*

## 3. Cảnh báo Chất lượng Dữ liệu (Critical Data Quality Issues)

> [!CAUTION]
> **Tính Toàn vẹn Thông tin Thấp:** Hệ thống ghi nhận sự thiếu hụt nghiêm trọng các đặc trưng phục vụ khai phá rủi ro.

- **Salary (Thu nhập):** **100% NULL**. Không thể thực hiện Risk Scoring dựa trên thu nhập như kế hoạch ban đầu.
- **Gender (Giới tính):** Không tồn tại trong Schema của tập dữ liệu NDBH hiện tại.
- **Phone Number:** Thiếu hụt khoảng **46%**, làm giảm hiệu quả của các thuật toán liên kết cụm (Network Clustering).
- **Address (Địa chỉ):** Hoàn toàn rỗng, làm mất khả năng phân tích trục lợi theo khu vực địa lý.

## 4. Chuẩn hóa Dữ liệu phục vụ Graph Database

Dù dữ liệu thiếu hụt, chúng tôi đã áp dụng bộ quy tắc chuẩn hóa để sẵn sàng cho việc nạp vào Neo4j:

| Feature | Quy tắc Chuẩn hóa |
| :--- | :--- |
| `full_name` | UPPER CASE + Trim whitespace. |
| `phone_number`| Numeric only (Loại bỏ dấu chấm, khoảng trắng, gạch nối). |
| `date_of_birth`| Quy đổi về ISO Standard (YYYY-MM-DD). |
| `user_id` | Đảm bảo định dạng UUID chuẩn. |

## 5. Đề xuất & Hành động tiếp theo

- **Data Enrichment:** Bắt buộc phải thực hiện Join chéo với cơ sở dữ liệu gốc (Excel/SQL) để lấy lại thông tin `salary` và `gender`.
- **Phone Tracking:** Sử dụng các Số điện thoại hiện có để xây dựng Ego-Network, truy vết các `user_id` khác nhau dùng chung một liên lạc.
