# Giải nghĩa các Feature - File DataChiPhi_part1.csv

Bảng dưới đây giải thích các trường dữ liệu trong file chi tiết chi phí y tế.

| Tên cột | Mô tả | Giá trị mặc định | Kiểu biến | Đánh giá |
| :--- | :--- | :--- | :--- | :--- |
| `detail_id` | Mã định danh duy nhất của dòng chi phí. | N/A | `Object (UUID)` | **Rất quan trọng**: Dùng để phân biệt các hạng mục trong cùng một hồ sơ. |
| `claim_id` | Mã định danh của hồ sơ bồi thường. | N/A | `Object (UUID)` | **Rất quan trọng**: Khóa ngoại để liên kết với bảng Hồ sơ bồi thường (Claims). |
| `drug_or_service_name` | Tên của thuốc, vật tư y tế hoặc dịch vụ kỹ thuật. | N/A | `String` | **Rất quan trọng**: Dùng để phân tích hành vi lạm dụng thuốc hoặc dịch vụ. |
| `quantity` | Số lượng thuốc hoặc dịch vụ đã sử dụng. | 1 | `Integer` | **Quan trọng**: Dùng để tính toán tổng chi phí và kiểm tra tính hợp lý. |
| `unit` | Đơn vị tính (VD: Viên, Gói, Lần). | N/A | `String` | **Bình thường**: Giúp hiểu rõ đơn giá và số lượng. |
| `unit_price` | Đơn giá của một đơn vị thuốc/dịch vụ. | 0 | `Float` | **Rất quan trọng**: Dùng để phát hiện các trường hợp kê giá cao bất thường. |
| `total_amount` | Tổng số tiền của hạng mục này (`unit_price` * `quantity`). | 0 | `Float` | **Rất quan trọng**: Chỉ số tài chính chính để tính tổng mức bồi thường. |
| `item_type` | Phân loại hạng mục (VD: Drug, Service, Material). | N/A | `String` | **Quan trọng**: Giúp phân tích cơ cấu chi phí (thuốc vs dịch vụ). |
| `category` | Danh mục chuyên sâu (VD: Kháng sinh, Nội soi, Xét nghiệm). | N/A | `String` | **Quan trọng**: Dùng để lọc và phân tích theo nhóm bệnh lý/kỹ thuật. |
| `benefit_id` | Mã quyền lợi bảo hiểm áp dụng cho hạng mục này. | N/A | `String` | **Bình thường**: Kiểm tra tính hợp lệ của quyền lợi bảo hiểm. |
| `exclusion_amount` | Số tiền không được bảo hiểm chi trả (loại trừ). | 0 | `Float` | **Quan trọng**: Dùng để xác định số tiền thực tế bảo hiểm phải trả. |
| `created_at` | Thời điểm ghi nhận dữ liệu vào hệ thống. | N/A | `DateTime` | **Bình thường**: Theo dõi lịch sử và thời gian xử lý. |

---
**Ghi chú**: Các giá trị tiền tệ trong file gốc đang được lưu ở đơn vị phóng đại 100 lần so với thực tế (Cần chia cho 100 khi xử lý).
