# Báo cáo Tập trung: Nhóm 'Vừa hết thời gian chờ' (JIT Claims)

Phân tích tập trung vào **1,539 hồ sơ** phát sinh trong khoảng ngày 31-45 sau khi tham gia bảo hiểm.

## 1. Tập trung theo Cơ sở Y tế (Top 5)
![Hospital Concentration](file:///D:/desktop_folder/04_Fraud_Detection/report/media/jit_hospital_concentration.png)

| Hospital Code | Số lượng hồ sơ | Tỷ lệ (%) |
| :--- | :--- | :--- |
| 01934 | 64 | 4.16% |
| 01288 | 63 | 4.09% |
| 01915 | 60 | 3.9% |
| 79431 | 39 | 2.53% |
| 79Z17 | 33 | 2.14% |

## 2. Tập trung theo Đại lý/Công ty (Top 5)
![Insurer Concentration](file:///D:/desktop_folder/04_Fraud_Detection/report/media/jit_insurer_concentration.png)

| Insurer ID | Số lượng hồ sơ | Tỷ lệ (%) |
| :--- | :--- | :--- |
| 0367a073-ce98-4652-8c91-533dbf2ea003 | 1539 | 100.0% |

## 3. Nhận xét
- Không có sự tập trung cực đoan tại một bệnh viện duy nhất, dữ liệu phân bổ khá đều.
- **Bất thường tại Đại lý:** Đại lý `0367a073-ce98-4652-8c91-533dbf2ea003` đang có tỉ lệ claim sớm lên tới 100.0%. Đây là dấu hiệu của việc trục lợi có tổ chức từ khâu cấp đơn.
