# Báo cáo Khai phá Dữ liệu Quyền lợi (Benefit Data Mining)

Tài liệu này tổng hợp các bước chuẩn hóa và khai phá dữ liệu cho bộ dữ liệu Quyền lợi bảo hiểm (`DataQuyenLoi`), phục vụ mục đích phát hiện các bất thường trong chi trả.

## 1. Kết quả Làm sạch & Chuẩn hóa

Bảng dữ liệu đã được xử lý qua pipeline tự động (`datamining_benefits.py`) với các quy tắc sau:

- **Quy đổi Tiền tệ (100x):** Tương tự các bộ dữ liệu khác, cột `requested_amount` và `approved_amount` đã được chia cho 100 để đưa về đơn vị VND chuẩn.
- **Mapping Cột:** 
  - `Số hợp đồng bảo hiểm` -> `policy_number`
  - `Số hồ sơ` -> `claim_id`
  - `Quyền lợi bảo hiểm` -> `benefit_name`
- **Chuẩn hóa Văn bản:** Toàn bộ tên quyền lợi được chuyển về chữ IN HOA và loại bỏ khoảng trắng thừa.

## 2. Thống kê & Phân bổ Quyền lợi

### Tần suất sử dụng
Phần lớn các hồ sơ tập trung vào các quyền lợi nội trú và ngoại trú cơ bản. Các quyền lợi đặc thù như "Nha khoa" hoặc "Thai sản" có tần suất thấp hơn nhưng chi phí đơn lẻ thường cao hơn.

![Sử dụng Quyền lợi](file:///D:/desktop_folder/04_Fraud_Detection/report/pre_process_data/charts_benefits/benefit_usage.png)

### Phân bổ Giá trị Chi trả (VND)
Dữ liệu chi trả sau khi làm sạch cho thấy một dải giá rộng, từ vài nghìn đồng đến hàng chục triệu đồng. Đồ thị log-scale cho thấy mật độ tập trung cao ở các mức chi trả trung bình.

![Phân bổ Tiền](file:///D:/desktop_folder/04_Fraud_Detection/report/pre_process_data/charts_benefits/benefit_dist.png)

## 3. Chỉ số Rủi ro & Cảnh báo (Fraud Indicators)

- **Trùng lặp Quyền lợi:** Cần rà soát các trường hợp một `claim_id` áp dụng cho nhiều quyền lợi chồng chéo hoặc vượt quá phạm vi hạn mức của gói bảo hiểm.
- **Tình trạng Phê duyệt:** Tỷ lệ hồ sơ "Đã thanh toán" chiếm ưu thế tuyệt đối. Các hồ sơ bị "Từ chối" hoặc "Hủy" cần được phân tích lý do (`Lý do từ chối`) để tìm ra các mẫu trục lợi bất thành.

---
**File kết quả:** [DataQuyenLoi_Cleaned_Final.csv](file:///D:/desktop_folder/04_Fraud_Detection/report/cleaned_data_final/DataQuyenLoi_Cleaned_Final.csv)
