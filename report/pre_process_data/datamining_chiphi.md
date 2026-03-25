# Khai phá Dữ liệu Chi phí (Data Mining - DataChiPhi)

Báo cáo chi tiết về hành vi chi phí y tế trích xuất từ dữ liệu mới (`D:\desktop_folder\04_Fraud_Detection\report\new_data`).

## 1. Tổng quan (Summary)
- **Tổng số bản ghi ban đầu:** 103,189
- **Số bản ghi bị loại bỏ (Dữ liệu rác/Lỗi lệch cột):** 4,720
- **Số bản ghi hiệu dụng (Sau làm sạch):** 98,469
- **Số lượng hồ sơ bồi thường (Claims) hiệu dụng:** 9,652
- **Số loại thuốc/dịch vụ hiệu dụng:** 40,296
- **Tổng chi phí bồi thường (sau khi làm sạch & chia 100):** 37,587,271,638 VND

## 2. Chất lượng dữ liệu (Data Quality)
Phân tích này đã áp dụng các bộ lọc để loại bỏ dữ liệu rác từ `new_data`:
- **Loại bỏ Lệch cột:** Các dòng có UUID hoặc ngày tháng nhảy vào cột Phân loại (`item_type`).
- **Loại bỏ Đơn giá ảo:** Giới hạn đơn giá tối đa 1 tỷ VND/đơn vị (Các giá trị cao hơn thường do lỗi CSV hoặc định dạng số).
- **Loại bỏ Giá trị rỗng:** Các dòng không thể chuyển đổi thành số ở cột Tiền/Số lượng.

## 3. Cơ cấu chi phí theo Loại (Item Type)
| item_type            |   count |
|:---------------------|--------:|
| THUOC                |   58220 |
| KHAC                 |   15478 |
| MAU_CHE_PHAM_MAU     |    5919 |
| XET_NGHIEM           |    4422 |
| DICH_VU_KY_THUAT     |    4091 |
| VAT_TU_Y_TE          |    3256 |
| KHAM_BENH            |    2672 |
| PHAU_THUAT_THU_THUAT |    1727 |
| CHAN_DOAN_HINH_ANH   |    1701 |
| NGAY_GIUONG_BENH     |     411 |
| VAN_CHUYEN           |     320 |
| THAM_DO_CHUC_NANG    |     252 |

## 4. Top 10 Danh mục Chi phí cao nhất (Categories)
| Danh mục | Số lượng | Tổng chi phí (VND) | Đơn giá TB |
| :--- | :---: | :---: | :---: |
| {THUOC} | 19,397.0 | 6,242,455,964 | 523,643 |
| {KHAC} | 4,446.0 | 1,466,957,014 | 340,222 |
| {PHAU_THUAT_THU_THUAT} | 688.0 | 951,661,861 | 1,676,645 |
| {DICH_VU_KY_THUAT} | 1,370.0 | 791,138,948 | 611,728 |
| {NGAY_GIUONG_BENH} | 149.0 | 410,338,038 | 1,992,106 |
| {XET_NGHIEM} | 1,604.0 | 367,086,935 | 466,473 |
| {KHAM_BENH} | 746.0 | 252,706,318 | 343,613 |
| {CHAN_DOAN_HINH_ANH} | 600.0 | 202,195,341 | 365,156 |
| {MAU_CHE_PHAM_MAU} | 2,143.0 | 157,584,571 | 84,289 |
| {THAM_DO_CHUC_NANG} | 92.0 | 154,526,350 | 231,629 |

## 5. Top 15 Thuốc/Dịch vụ tiêu tốn nhất
| Tên Thuốc/Dịch vụ | Số lần sử dụng | Tổng chi phí (VND) | Đơn giá trung bình |
| :--- | :---: | :---: | :---: |
| Dịch vụ khám chữa bệnh | 330.0 | 594,709,799 | 1,595,459 |
| Chẩn đoán hình ảnh | 521.0 | 531,736,793 | 970,221 |
| 2. Số khám bệnh | 1.0 | 500,048,150 | 500,048,150 |
| Đo hoạt độ ALT (GPT) [Máu] | 682.0 | 450,824,667 | 36,864 |
| Xét nghiệm | 693.0 | 418,903,499 | 528,658 |
| Ziaja- Nhũ Tương Mềm Da 3% Urê | 1.0 | 371,127,582 | 371,128 |
| Dịch vụ y tế - Nội trú | 69.0 | 341,068,618 | 2,103,534 |
| Phẫu thuật | 56.0 | 339,716,715 | 5,354,865 |
| Chi phí khám và điều trị | 30.0 | 306,150,859 | 10,205,029 |
| Thuốc | 285.0 | 304,303,629 | 1,002,889 |
| Thăm dò chức năng | 199.0 | 303,426,248 | 1,506,699 |
| Dịch vụ y tế - Ngoại trú | 381.0 | 261,860,667 | 407,841 |
| Khám chuyên khoa Dinh dưỡng | 1.0 | 250,000,286 | 250 |
| Chi phí điều trị và tiền giường | 4.0 | 224,638,955 | 56,159,739 |
| Thủ thuật | 220.0 | 224,540,409 | 960,253 |

## 6. Top 15 Hạng mục có Đơn giá cao nhất (Sau làm sạch)
Đây là các chi phí thực tế cao cần giám sát chặt chẽ:

| Tên Thuốc/Dịch vụ | Danh mục | Đơn giá (VND) | Tổng tiền |
| :--- | :--- | :---: | :---: |
| Prospan 85ml | {THUOC} | 800,000,000 | 80,000 |
| Nurofen 60 ml (100mg /5ml) | {THUOC} | 552,381,000 | 55,238 |
| RỪA MŨI (NHI) | nan | 516,100,000 | 100,000 |
| 2. Số khám bệnh | nan | 500,048,150 | 500,048,150 |
| Phòng yêu cầu tiêu chuẩn | {THUOC} | 500,000,000 | 1,500,000 |
| Scofi 10ml | {THUOC} | 380,952,380 | 120,000 |
| Scofi 10ml | {THUOC} | 380,952,380 | 38,095 |
| Scofi 10ml | {THUOC} | 380,952,380 | 76,190 |
| Xisat 75ml baby | {XET_NGHIEM} | 314,285,710 | 31,429 |
| Xisat 75ml baby | nan | 314,285,710 | 31,429 |
| Chụp cộng hưởng từ cột sống thắt lượng - cùng (0.2-1.5T) [không có chất tương phần] | nan | 257,530,000 | 2,575 |
| Simethicone Stella 15ml | {THUOC} | 257,142,900 | 27,000 |
| Chẩn đoán hình ảnh | nan | 241,900,000 | 241,900,000 |
| Thăm dò chức năng | nan | 233,900,000 | 233,900,000 |
| NEXIUM MUPS 40 H/14V | nan | 228,571,429 | 160,000 |

## 7. Kết luận & Đề xuất
1. **Dữ liệu thực tế:** Sau khi loại bỏ dữ liệu rác, tổng chi phí bồi thường nằm trong mức thực tế của quy mô tệp khách hàng.
2. **Điểm nóng chi phí:** Các dịch vụ như {cat_stats.index[0] if not cat_stats.empty else "N/A"} và {cat_stats.index[1] if len(cat_stats)>1 else ""} là nơi tập trung nguồn lực tài chính lớn nhất.
3. **Giám sát đơn giá:** Các hạng mục tại Mục 6 có đơn giá lớn (vài chục đến vài trăm triệu), cần quy trình phê duyệt đặc biệt.
