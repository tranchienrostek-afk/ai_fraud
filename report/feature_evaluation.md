# Bảng Đánh giá Thuộc tính (Feature Evaluation) - Neo4j Migration

Bảng này liệt kê các thuộc tính từ dữ liệu thô và đề xuất cách xử lý khi đưa vào Neo4j để tối ưu hóa khả năng truy vết rủi ro.

| Nhóm dữ liệu | Thuộc tính (Column) | Trạng thái đề xuất | Lý do / Giá trị kinh doanh |
| :--- | :--- | :--- | :--- |
| **Định danh (PII)** | `phone_number`, `email` | **GIỮ (Node/Link)** | Cực kỳ quan trọng để tìm các nhóm dùng chung thông tin (Syndicates). |
| **Định danh (PII)** | `address` | **BỎ (Attribute)** | Dữ liệu địa chỉ không chuẩn hóa, dễ làm rối đồ thị nếu tạo Node. Chỉ giữ làm thuộc tính của Person. |
| **Định danh (PII)** | `date_of_birth` | **BỎ** | Ít giá trị trong liên kết đồ thị, có thể dùng để tính tuổi nhưng không tạo liên kết. |
| **Tài chính** | `beneficiary_account` | **GIỮ (Node)** | Trọng tâm phát hiện trục lợi có tổ chức. Cần tạo Node Bank. |
| **Tài chính** | `salary`, `premium_paid` | **CÂN NHẮC THÊM** | Giúp đánh giá tính cân xứng giữa thu nhập và yêu cầu bồi thường (Scoring). |
| **Hợp đồng** | `contract_level` | **CÂN NHẮC THÊM** | Cần thiết để kiểm tra hành vi nâng cấp gói bảo hiểm ngay trước khi claim. |
| **Điều trị** | `doctor_name_exam` | **CÂN NHẮC THÊM** | Phát hiện sự thông đồng giữa bác sĩ và khách hàng/đại lý. |
| **Điều trị** | `clinical_notes`, `discharge_diagnosis` | **GIỮ (Scoring)** | Dùng để đối soát với các "Cụm nhân bản" (Medical Cloning) đã phát hiện. |
| **Thời gian** | `admission/discharge_date` | **BỎ (Attribute)** | Chuyển thành thuộc tính của Claim để tính `treatment_duration_days`. Không tạo Node thời gian. |
| **Tổ chức** | `hospital_code`, `insurer_id` | **GIỮ (Node)** | Phát hiện sự tập trung bất thường tại các cơ sở y tế hoặc đại lý cụ thể. |
| **Vận hành** | `created_at`, `remaining_benefit_limit` | **BỎ** | Thông tin quản trị hệ thống, không đóng góp vào việc phát hiện dấu hiệu trục lợi. |

## Các "Feature" đề xuất bổ sung (Derived Features)
Ngoài dữ liệu thô, tôi đề xuất đưa thêm các thuộc tính đã qua xử lý vào đồ thị:
1. **Risk Score:** Điểm rủi ro tổng hợp đã tính toán từ bước trước.
2. **Cluster ID:** ID của các cụm nhãn bản bệnh án hoặc cụm JIT (Just-In-Time) claims.

---
**Hành động tiếp theo:** Vui lòng phản hồi "Đồng ý" hoặc chỉ định các thuộc tính bạn muốn thay đổi trạng thái (ví dụ: "Muốn giữ Address làm Node").
