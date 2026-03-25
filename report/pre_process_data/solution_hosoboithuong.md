# Báo cáo Khai phá Dữ liệu Hồ sơ Bồi thường (Claims Data Mining)

## 1. Tóm tắt Điều hành (Executive Summary)

- **Tổng số hồ sơ xử lý:** 19,259 bản ghi.
- **Số hồ sơ hợp lệ sau làm sạch:** 19,252 bản ghi.
- **Tổng giá trị bồi thường phê duyệt:** **2,514,869,330,358 VND**.

### Phân bổ Giá trị Bồi thường
![Phân bổ Claim](file:///D:/desktop_folder/04_Fraud_Detection/report/pre_process_data/charts_claims/claim_dist.png)
*Hình 1: Đồ thị mật độ số tiền bồi thường (Log scale) sau khi đã chuẩn hóa tỷ lệ 100x.*

## 2. Phân tích Chất lượng Dữ liệu (Data Integrity)

- **Lỗi Magnitude (100x):** Toàn bộ dữ liệu gốc được xác nhận bị phóng đại 100 lần (tế bào gốc của hệ thống cũ). Đã được quy đổi về VND chuẩn.
- **Chuẩn hóa ICD:** Các mã chẩn đoán đã được làm sạch khoảng trắng và xử lý giá trị khuyết.
- **Xử lý Outlier:** Áp dụng phương pháp Median-check theo nhóm bệnh để phát hiện các hồ sơ có giá trị đột biến do lỗi nhập liệu (glitched zeros).

## 3. Top 10 Bệnh lý có chi phí bồi thường cao nhất

| Chẩn đoán (ICD Primary) | Tổng tiền Phê duyệt (VND) |
| :--- | :---: |
| Viêm mũi họng cấp [cảm thường] | 108,623,393,800 |
| Viêm phế quản cấp | 98,578,491,300 |
| Viêm phế quản phổi, không đặc hiệu | 97,675,564,788 |
| Viêm họng cấp | 55,151,400,800 |
| Sâu răng | 39,435,443,600 |
| Cúm do vi rút đã được định danh | 32,228,131,500 |
| Viêm mũi xoang cấp tính | 29,638,318,200 |
| Viêm phổi, tác nhân không xác định | 29,281,018,900 |
| Viêm ruột thừa cấp | 29,060,621,700 |
| Mổ lấy thai cho một thai | 27,732,748,700 |

## 4. Phân bổ theo Loại hình Điều trị

| Loại hình | Tổng tiền (VND) | Tỷ trọng |
| :--- | :---: | :---: |
| Nội trú | 1,137,136,012,300 | 45.2% |
| Ngoại trú | 1,112,683,895,553 | 44.2% |
| Tai nạn | 195,129,537,505 | 7.8% |
| Khác | 53,101,901,700 | 2.1% |
| Sản khoa | 12,363,520,400 | 0.5% |
| Mã 6 | 4,454,462,900 | 0.2% |
| Chưa phân loại | 0 | 0.0% |

## 5. Kết luận & Đề xuất

- **Tính nhất quán:** Dữ liệu bồi thường hoàn toàn khớp với dữ liệu chi phí (Expenses) sau khi áp dụng cùng một hệ số scaling 100x.
- **Phát hiện trục lợi:** Các nhóm bệnh như 'Viêm mũi họng' hay 'Viêm phế quản' chiếm số lượng lớn nhưng chi phí đơn lẻ thấp. Cần tập trung vào các hồ sơ có thời gian điều trị ngắn nhưng chi phí chạm trần.
