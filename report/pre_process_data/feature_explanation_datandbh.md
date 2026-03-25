# Giải nghĩa và Khai phá dữ liệu Người được bảo hiểm (Persons) - UPGRADED

Bảng dưới đây giải thích các trường dữ liệu và hiện trạng chất lượng trong hệ thống hiện tại.

## 1. Giải nghĩa các Feature (Data Dictionary)

| Tên cột | Mô tả | Kiểu dữ liệu | Hiện trạng | Đánh giá |
| :--- | :--- | :--- | :--- | :--- |
| `user_id` | Mã định danh duy nhất (UUID). | `Object` | Đầy đủ | **Khóa chính**: Cần thiết để liên kết bồi thường. |
| `identity_number` | Số CCCD/CMND/Hộ chiếu. | `String` | Khá đầy đủ | **Định danh**: Phát hiện trùng lặp người dùng. |
| `full_name` | Họ và tên khách hàng. | `String` | Đầy đủ | Chuẩn hóa VIẾT HOA để đồng bộ. |
| `date_of_birth` | Ngày tháng năm sinh. | `Date` | Đầy đủ | Dùng để tính tuổi (Age). |
| `phone_number` | Số điện thoại liên lạc. | `String` | Thiếu ~46% | **Truy vết**: Dùng phát hiện cụm trục lợi chung SĐT. |
| `salary` | Mức lương ghi nhận. | `Float` | **Trống 100%** | Không thể dùng để chấm điểm rủi ro tài chính. |
| `contract_id` | Mã hợp đồng bảo hiểm. | `String` | Đầy đủ | Liên kết với các quyền lợi sản phẩm. |

---

## 2. Phân tích Khai phá (Data Mining Insights)

Dưới đây là các đặc trưng nhân khẩu học được trích xuất từ mẫu 50,000 bản ghi:

### Phân bổ Độ tuổi
![Age Distribution](file:///D:/desktop_folder/04_Fraud_Detection/report/pre_process_data/charts_persons/age_dist.png)
*Hình 1: Biểu đồ mật độ tuổi. Dữ liệu tập trung mạnh ở nhóm tuổi lao động (18-45), đây là nhóm có hành vi yêu cầu bồi thường năng động nhất.*

### Thách thức về Chất lượng Dữ liệu
- **Thiếu hụt Financial Data:** Việc mất hoàn toàn dữ liệu `salary` trong các chunk dữ liệu NDBH hiện tại là một rào cản lớn cho việc phân tích rủi ro dựa trên thu nhập.
- **Dữ liệu rác:** Mặc dù `phone_number` thiếu nhiều, nhưng các số điện thoại hiện có cần được chuẩn hóa (loại bỏ dấu chấm, khoảng trắng) trước khi nạp vào Graph Database để tránh tạo ra các node trùng lặp sai lệch.

---

## 3. Quy tắc Chuẩn hóa (Normalization Rules)

Để đảm bảo dữ liệu "sạch" khi nạp vào Dashboard và Graph:
1. **Name Handling:** `Nguyễn Văn A` -> `NGUYEN VAN A`.
2. **Phone Handling:** `09.123 456-7` -> `091234567`.
3. **Age Calculation:** Tính toán động `Tuổi = Năm hiện tại - Năm sinh` để phân tích rủi ro theo nhóm đối tượng.
4. **Data Supplement:** Khuyến nghị bổ sung `Gender` và `Address` từ các nguồn dữ liệu bổ trợ để làm giàu Ego-Network của người dùng.
