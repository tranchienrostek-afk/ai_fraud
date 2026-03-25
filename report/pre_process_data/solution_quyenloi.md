# Báo cáo Khai phá Dữ liệu Quyền lợi Bảo hiểm (Benefits Data Mining)

## 1. Tóm tắt Điều hành (Executive Summary)

- **Tổng số bản ghi xử lý:** 22,680 dòng.
- **Tổng giá trị chi trả thực tế:** **27,736,666,320 VND**.
- **Tình trạng Scaling:** Đã phát hiện và xử lý lỗi phóng đại 100x trên toàn bộ cột số tiền.

### Sử dụng Quyền lợi
![Sử dụng Quyền lợi](file:///D:/desktop_folder/04_Fraud_Detection/report/pre_process_data/charts_benefits/benefit_usage.png)
*Hình 1: Biểu đồ tần suất sử dụng các loại quyền lợi bảo hiểm.*

## 2. Phân tích Chất lượng Dữ liệu (Data Integrity)

> [!IMPORTANT]
> Toàn bộ dữ liệu tiền tệ trong `DataQuyenLoi` thô bị nhân 100 lần. Đơn giá thực tế đã được quy đổi VND chuẩn.

- **Mã hóa ICD:** Đồng bộ với danh mục chẩn đoán quốc tế.
- **Trạng thái Thanh toán:** 10 loại trạng thái khác nhau, chủ yếu là 'Đã thanh toán'.

## 3. Top 10 Quyền lợi có chi phí cao nhất

| Tên Quyền lợi | Tổng tiền Chi trả (VND) |
| :--- | :---: |
| VIỆN PHÍ | 8,640,102,480 |
| CHI PHÍ KHÁM, XÉT NGHIỆM, CHẨN ĐOÁN, THUỐC KÊ TOA | 7,741,614,662 |
| CHI PHÍ PHẪU THUẬT | 3,073,869,950 |
| CHĂM SÓC RĂNG CƠ BẢN | 944,506,552 |
| CHI PHÍ Y TẾ BAO GỒM CẢ DỊCH VỤ XE CỨU THƯƠNG | 899,447,769 |
| CHI PHÍ Y TẾ DO TAI NẠN | 601,640,912 |
| CHI PHÍ Y TẾ | 583,395,010 |
| CHI PHÍ KHÁM NẾU MUA THUỐC TẠI HỆ THỐNG CHUỖI NHÀ THUỐC LONG CHÂU | 504,310,593 |
| CHI PHÍ/LẦN KHÁM NẾU HỒ SƠ BỒI THƯỜNG CÓ MUA THUỐC TẠI HỆ THỐNG CHUỖI NHÀ THUỐC FPT LONG CHÂU | 395,194,951 |
| CHI PHÍ TRƯỚC NHẬP VIỆN | 390,464,610 |

## 4. Phân bổ Số tiền Chi trả

![Phân bổ Tiền](file:///D:/desktop_folder/04_Fraud_Detection/report/pre_process_data/charts_benefits/benefit_dist.png)
*Hình 2: Phân bổ log-scale của giá trị bồi thường theo quyền lợi.*

