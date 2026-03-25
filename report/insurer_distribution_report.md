# Báo cáo Thống kê Đại lý Bảo hiểm (Insurer Distribution Report)

Báo cáo này liệt kê danh sách các đại lý/công ty môi giới bảo hiểm và số lượng hồ sơ bồi thường tương ứng trong toàn bộ tập dữ liệu (565.811 bản ghi gốc, tương ứng 19.259 hồ sơ đã duyệt).

## 1. Thống kê Chi tiết

| Thứ tự | Tên Đại lý (Beneficiary Name) | Insurer ID | Số lượng hồ sơ | Tỷ lệ (%) |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Dương Văn Hoàng** | `0367a073-ce98-4652-8c91-533dbf2ea003` | **19,259** | **100.0%** |

## 2. Nhận xét Trọng điểm

- **Sự tập trung tuyệt đối:** Trong tập dữ liệu này, toàn bộ 100% hồ sơ bồi thường đều được quản lý/cấp đơn bởi một đại lý duy nhất có tên là **Dương Văn Hoàng**.
- **Dấu hiệu rủi ro:** Việc toàn bộ 19.259 hồ sơ (bao gồm cả các hồ sơ trục lợi JIT, hồ sơ hóa đơn bán lẻ, và hồ sơ outlier) đều tập trung tại một cá nhân/đại lý là một biến số cực kỳ quan trọng. 
- **Khuyến nghị:** Đây không còn là vấn đề của từng khách hàng đơn lẻ, mà là vấn đề rủi ro hệ thống tại đại lý này. Cần kiểm tra toàn diện quy trình hoạt động của đại lý **Dương Văn Hoàng**.

---
*Ghi chú: Tên đại lý được trích xuất từ trường `beneficiary_name` liên kết với `insurer_id` trong dữ liệu.*

**Tệp dữ liệu gốc:** [full_insurer_stats.csv](file:///D:/desktop_folder/04_Fraud_Detection/report/full_insurer_stats.csv)
