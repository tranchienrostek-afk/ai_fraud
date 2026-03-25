# Giải nghĩa các Feature - File DataHoSoBoiThuong_part1.csv

Bảng dưới đây giải thích các trường dữ liệu trong file hồ sơ bồi thường (Claims).

| Tên cột | Mô tả | Giá trị mặc định | Kiểu biến | Đánh giá |
| :--- | :--- | :--- | :--- | :--- |
| `claim_id` | Mã định danh duy nhất của hồ sơ bồi thường. | N/A | `Object (UUID)` | **Cực kỳ quan trọng**: Khóa chính của bảng Claims. |
| `user_id` | Mã định danh của người được bảo hiểm. | N/A | `Object (UUID)` | **Cực kỳ quan trọng**: Khóa ngoại liên kết với bảng Người được bảo hiểm (Persons). |
| `claim_number` | Số hồ sơ bồi thường (mã số nghiệp vụ). | N/A | `String` | **Quan trọng**: Dùng để tra cứu hồ sơ trên hệ thống nghiệp vụ. |
| `full_name` | Tên đầy đủ của người bệnh/người yêu cầu. | N/A | `String` | **Bình thường**: Dùng để hiển thị và xác nhận nhanh. |
| `claim_type` | Loại hình bồi thường (Nội trú, Ngoại trú, Tai nạn,...). | N/A | `String` | **Quan trọng**: Phân loại hồ sơ để áp dụng quy tắc kiểm soát khác nhau. |
| `insurer_id` | Mã công ty bảo hiểm/đơn vị xử lý. | N/A | `String` | **Bình thường**: Xác định nguồn gốc hồ sơ. |
| `actual_receipt_date` | Ngày thực tế nhận hồ sơ. | N/A | `Date` | **Quan trọng**: Tính toán thời gian xử lý (SLA). |
| `claim_amount_requested` | Số tiền yêu cầu bồi thường. | 0 | `Float` | **Rất quan trọng**: Con số khách hàng mong muốn được chi trả. |
| `claim_amount_approved` | Số tiền được phê duyệt chi trả thực tế. | 0 | `Float` | **Rất quan trọng**: Con số cuối cùng bảo hiểm chi trả. |
| `ICD` | Mã bệnh quốc tế (VD: J00, K29,...). | N/A | `String` | **Cực kỳ quan trọng**: Dùng để phát hiện trục lợi dựa trên chẩn đoán bệnh. |
| `Trạng thái hồ sơ` | Trạng thái hiện tại (Đã thanh toán, Đang xử lý, Từ chối). | N/A | `String` | **Quan trọng**: Theo dõi tiến độ bồi thường. |

---
**Ghi chú**: Các giá trị tiền tệ trong file gốc đang được lưu ở đơn vị phóng đại 100 lần so với thực tế (Cần chia cho 100 khi xử lý).
