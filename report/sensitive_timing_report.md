# Báo cáo Truy vết: Chỉ số Thời điểm "Nhạy cảm"

Phân tích này tập trung vào các hồ sơ phát sinh ngay sau khi tham gia bảo hiểm hoặc ngay sau khi hết thời gian chờ (Waiting Period), vốn là dấu hiệu của việc "có bệnh mới mua bảo hiểm".

## 1. Kết quả Phân tích Tổng quát
Trên tổng số ~565.000 hồ sơ, tôi đã áp dụng các bộ lọc rủi ro về thời gian:

- **Hồ sơ lớn (>10M) phát sinh sớm (<60 ngày):** Phát hiện **32 trường hợp**.
- **Cụm hồ sơ ngay sau thời gian chờ (Ngày 31-45):** Phát hiện **1.085 hồ sơ**. Đây là nhóm có mật độ claim cao bất thường ngay khi vừa đủ điều kiện bảo hiểm.

## 2. Các trường hợp trọng điểm (High-Risk Early Claims)
Dưới đây là một số ví dụ điển hình về các hồ sơ có số tiền lớn phát sinh cực sớm:

| User ID | Ngày hiệu lực | Ngày Claim | Số ngày chờ | Số tiền duyệt | Chẩn đoán |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `0644...` | 13/05/2025 | 21/06/2025 | 39 ngày | 24,530,000 VNĐ | Chấn thương đầu |
| `a221...` | 01/02/2025 | 15/03/2025 | 42 ngày | 21,800,000 VNĐ | Phẫu thuật nội soi |
| `8e3a...` | 10/11/2024 | 22/12/2024 | 42 ngày | 20,450,000 VNĐ | Gãy xương đùi |

## 3. Phân tích Nâng cấp Hợp đồng
Trong dữ liệu hiện tại, chưa phát hiện hành vi nâng cấp gói bảo hiểm (Upgrade) ngay trước khi claim lớn một cách rõ rệt. Đa số khách hàng giữ nguyên mức quyền lợi (`contract_level`) từ đầu kỳ.

## 4. Kết luận và Kiến nghị
Mặc dù không tìm thấy hồ sơ >50 triệu trong 30 ngày đầu (có thể do quy trình thẩm định chặt chẽ của công ty bạn đã loại bỏ từ trước), nhưng nhóm **32 hồ sơ trên 10 triệu trong 60 ngày đầu** là cực kỳ đáng nghi ngại.

**Kiến nghị:**
- Đối với 32 hồ sơ này: Kiểm tra lại lịch sử bệnh án (Pre-existing conditions) tại các bệnh viện khác trước ngày tham gia bảo hiểm.
- Đối với nhóm 1.085 hồ sơ "vừa hết thời gian chờ là claim ngay": Cần thống kê xem có sự tập trung vào một số đại lý bảo hiểm hoặc phòng khám cụ thể nào không.

**Dữ liệu chi tiết:**
- [Danh sách hồ sơ sớm giá trị cao (CSV)](file:///D:/desktop_folder/04_Fraud_Detection/report/suspicious_early_claims.csv)
