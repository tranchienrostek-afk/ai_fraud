# Giải nghĩa các Feature - File DataQuyenLoi (Raw)

Bảng dưới đây giải thích các trường dữ liệu thực tế tìm thấy trong bộ dữ liệu Quyền lợi bảo hiểm (Benefits) sau khi đã chuẩn hóa.

| Tên cột Gốc | Tên cột chuẩn hóa | Mô tả | Đánh giá |
| :--- | :--- | :--- | :--- |
| `Số hồ sơ` | `claim_id` | Mã định danh hồ sơ bồi thường. | **Khóa ngoại quan trọng** |
| `Số hợp đồng bảo hiểm` | `policy_number` | Mã số hợp đồng bảo hiểm liên kết. | **Quan trọng** |
| `Quyền lợi bảo hiểm` | `benefit_name` | Tên loại quyền lợi áp dụng (Nội trú, Ngoại trú...). | **Rất quan trọng** |
| `Số tiền yêu cầu bồi thường` | `requested_amount` | Số tiền khách hàng yêu cầu chi trả. | **Phóng đại 100x** |
| `Số tiền bồi thường` | `approved_amount` | Số tiền thực tế hệ thống đã phê duyệt chi trả. | **Phóng đại 100x** |
| `ICD` | `icd_code` | Mã chẩn đoán quốc tế liên quan đến quyền lợi này. | **Quan trọng** |
| `Trạng thái hồ sơ` | `status` | Tình trạng hiện tại của hồ sơ (Đã thanh toán, Từ chối...). | **Rất quan trọng** |
| `Ngày vào viện` | `admission_date` | Ngày bắt đầu đợt điều trị. | **Cơ sở tính thời gian** |
| `Tên người được bảo hiểm` | `full_name` | Tên của người sở hữu quyền lợi. | **Định danh** |

---
**Ghi chú**: Toàn bộ các trường số tiền (`requested_amount`, `approved_amount`) trong file gốc đang bị phóng đại 100 lần và đã được pipeline làm sạch quy đổi về VND.
