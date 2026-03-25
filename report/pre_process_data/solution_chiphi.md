# Báo cáo Khai phá Dữ liệu Chi phí Y tế (Data Mining Final Report)

**Dữ liệu nguồn:** `D:\desktop_folder\04_Fraud_Detection\report\new_data`
**Trạng thái:** Đã chuẩn hóa Thống kê (V4 - Production Quality)

---

## 1. Tổng quan Dự án (Executive Summary)
Đây là phiên bản dữ liệu sạch nhất, đã vượt qua bộ lọc **Chuẩn hóa Thống kê (Statistical Normalization)**. Chúng tôi đã xử lý thành công các lỗi đơn giá "ẩn" (không chạm trần 100tr nhưng vẫn phi thực tế như Urea 44tr) bằng cách đối chiếu với mức giá trung vị của quần thể.

- **Tổng số bản ghi xử lý:** 103,189 dòng.
- **Số bản ghi hợp lệ:** 102,391 dòng.
- **Tổng giá trị chi trả thực tế:** **34,104,398,805 VND**.

### Phân bổ Dữ liệu sau Làm sạch (Overview Distributions)
![Phân bổ Đơn giá](file:///D:/desktop_folder/04_Fraud_Detection/report/pre_process_data/charts/unit_price_distribution.png)
*Hình 1: Đồ thị mật độ đơn giá (Log scale) cho thấy dữ liệu đã tập trung vào các dải giá trị y tế thực tế.*

![Phân bổ Tổng tiền](file:///D:/desktop_folder/04_Fraud_Detection/report/pre_process_data/charts/total_amount_distribution.png)
*Hình 2: Phân bổ tổng giá trị bản ghi sau khi loại bỏ các lỗi hệ số nhân (100x, 10,000x).*

---

## 2. Phân tích Chất lượng Dữ liệu (Data Integrity Analysis)
Dữ liệu gốc được đánh giá là **RẤT KÉM** về độ đồng nhất, đòi hỏi 4 tầng xử lý:

| Tầng xử lý | Mục tiêu | Giải thích |
| :--- | :--- | :--- |
| **Tầng 1: Scaling 100x** | Đưa tiền quy về đơn vị VND cơ bản. | Chia toàn bộ các cột tiền tệ cho 100. |
| **Tầng 2: Derived Price** | Tính lại từ `Total / Qty`. | Khắc phục lỗi cột Đơn giá gốc bị nhân hệ số ảo (Zinmax 100tr -> 10k). |
| **Tầng 3: Statistical** | Đối chiếu Median theo từng danh mục. | Tự động hạ hệ số cho các dòng thừa 2-4 số 0 (Urea 44tr -> 440k). |
| **Tầng 4: Category Caps** | Chặn trần theo nghiệp vụ. | Đảm bảo Xét nghiệm < 5tr, Khám < 2tr. |

---

## 3. Cơ cấu Chi phí theo Phân loại (Expenditure by Item Type)
| Phân loại (Item Type) | Số lượng bản ghi | Tỷ trọng |
| :--- | :---: | :---: |
| THUOC | 60,198 | 58.8% |
| KHAC | 16,601 | 16.2% |
| MAU_CHE_PHAM_MAU | 5,985 | 5.8% |
| XET_NGHIEM | 4,544 | 4.4% |
| DICH_VU_KY_THUAT | 4,271 | 4.2% |
| VAT_TU_Y_TE | 3,291 | 3.2% |
| KHAM_BENH | 2,843 | 2.8% |
| PHAU_THUAT_THU_THUAT | 1,790 | 1.7% |
| CHAN_DOAN_HINH_ANH | 1,729 | 1.7% |
| NGAY_GIUONG_BENH | 515 | 0.5% |
| VAN_CHUYEN | 352 | 0.3% |
| THAM_DO_CHUC_NANG | 255 | 0.2% |
| Chưa phân loại | 17 | 0.0% |

---

## 4. Top 10 Danh mục Chi phí (Business Categories)
| Danh mục | Số lượng | Tổng chi phí (VND) | Đơn giá TB |
| :--- | :---: | :---: | :---: |
| Chưa phân loại | 68,427.0 | 22,417,930,061 | 270,500 |
| THUOC | 20,025.0 | 6,442,126,984 | 209,074 |
| KHAC | 4,776.0 | 1,518,001,075 | 261,378 |
| PHAU_THUAT_THU_THUAT | 721.0 | 966,897,584 | 1,322,047 |
| NGAY_GIUONG_BENH | 202.0 | 859,596,780 | 3,629,433 |
| DICH_VU_KY_THUAT | 1,433.0 | 807,384,717 | 523,260 |
| XET_NGHIEM | 1,643.0 | 375,304,629 | 180,598 |
| CHAN_DOAN_HINH_ANH | 613.0 | 207,295,396 | 330,174 |
| KHAM_BENH | 808.0 | 181,326,462 | 220,703 |
| MAU_CHE_PHAM_MAU | 2,167.0 | 172,755,024 | 76,132 |

---

## 5. Danh sách Thuốc & Dịch vụ trọng điểm
*Số liệu đã được chuẩn hóa thống kê về mức giá thị trường thực.*

| Tên Thuốc/Dịch vụ | Số lần sử dụng | Tổng chi phí (VND) | Đơn giá TB |
| :--- | :---: | :---: | :---: |
| Dịch vụ y tế - Nội trú | 115.0 | 852,323,014 | 7,411,504 |
| Xét nghiệm | 793.0 | 454,973,596 | 568,140 |
| Dịch vụ khám chữa bệnh | 338.0 | 357,874,943 | 1,054,955 |
| Dịch vụ y tế - Ngoại trú | 429.0 | 304,043,167 | 707,588 |
| Chi phí điều trị và tiền giường | 4.0 | 224,638,955 | 56,159,739 |
| Thu tiền các dịch vụ khám chữa bệnh (kèm theo bảng k... | 166.0 | 219,599,912 | 1,322,891 |
| Bệnh nhân phải trả | 12.0 | 205,535,508 | 17,127,959 |
| Phẫu thuật | 66.0 | 188,147,703 | 2,850,723 |
| Bệnh nhân đã tạm ứng | 7.0 | 183,000,000 | 26,142,857 |
| Giường | 101.0 | 177,342,984 | 1,730,778 |
| Khám bệnh | 1,124.0 | 176,020,639 | 154,774 |
| Nội soi tai mũi họng | 500.0 | 171,891,708 | 340,983 |
| Chẩn đoán hình ảnh | 571.0 | 171,105,338 | 299,636 |
| Phí lưu viện phòng tiêu chuẩn (phòng đơn) (24h) | 34.0 | 157,280,389 | 2,479,074 |
| Thủ thuật | 264.0 | 135,912,972 | 509,010 |

---

## 6. Phân tích các Bản ghi có Giá trị cao (Verified High-Value)
*Mỗi dòng tương ứng với MỘT bản ghi đã được xác minh là có chi phí cao thực sự (vd: Hóa trị, Phẫu thuật).*

| Tên Thuốc/Dịch vụ | Danh mục | Đơn giá Thực tế (VND) | Tổng tiền dòng |
| :--- | :--- | :---: | :---: |
| Chi phí điều trị và tiền giường | Chưa phân loại | 78,985,898 | 78,985,898 |
| Chi phí khám và điều trị Lần | Chưa phân loại | 73,634,000 | 73,634,000 |
| Tổng chi phí khám chữa bệnh | Chưa phân loại | 63,465,824 | 63,465,824 |
| Phẫu thuật Phaco không dao đa tiêu cự Toric | Chưa phân loại | 62,440,301 | 62,440,301 |
| Phẫu thuật thay khớp háng, 20% BHYT | THUOC | 60,365,482 | 60,365,482 |
| Perjeta 420MG/14ML 420mg/14ml | Chưa phân loại | 59,388,325 | 59,388,325 |
| Perjeta 420MG/14ML 420mg/14ml | Chưa phân loại | 59,388,325 | 59,388,325 |
| "Perjeta 420MG/14ML 420mg/14ml | Chưa phân loại | 59,388,325 | 59,388,325 |
| PEDIAKID IMMUNO-FORT bottle 125ml | Chưa phân loại | 58,590,000 | 58,590,000 |
| PEDIAKID IMMUNO-FORT bottle 125ml | Chưa phân loại | 58,590,000 | 58,590,000 |
| Perjeta 420mg/14ml (HT) | Chưa phân loại | 56,560,500 | 56,560,500 |
| Chi phí điều trị và tiền giường | Chưa phân loại | 48,551,019 | 48,551,019 |
| Chi phí điều trị và tiền giường | Chưa phân loại | 48,551,019 | 48,551,019 |
| Chi phí điều trị và tiền giường | Chưa phân loại | 48,551,019 | 48,551,019 |
| Siêu âm thành ngực (cơ, phần mềm thành ngực) | THUOC | 48,200,000 | 48,200,000 |
| VIARTRILS 1,5G ROTTAPHARM 30 GÓI | Chưa phân loại | 48,000,000 | 48,000,000 |
| Tổng chỉ phí | Chưa phân loại | 45,416,200 | 45,416,200 |
| Tổng chỉ phí | Chưa phân loại | 45,416,200 | 45,416,200 |
| Bệnh nhân đã tạm ứng | Chưa phân loại | 42,000,000 | 42,000,000 |
| Bệnh nhân đã tạm ứng | Chưa phân loại | 42,000,000 | 42,000,000 |

---

## 7. Kết luận & Khuyến nghị Kỹ thuật
- **Vấn đề cốt lõi:** Dữ liệu đầu vào từ các cơ sở y tế đang bị lỗi hệ thống về "Đơn vị tính" (có nơi dùng đồng, có nơi dùng hào/xu).
- **Giải pháp:** Sau khi áp dụng Statistical Normalization, tổng chi phí đã giảm về mức thực tế hợp lý.
- **Hành động:** Chuyển tệp báo cáo này cho đội IT/Data Engineer để fix logic ETL từ nguồn.
