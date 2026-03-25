# Báo cáo Khai phá Dữ liệu Hồ sơ Bồi thường (Claims Data Mining) - UPGRADED

## 1. Tóm tắt Điều hành (Executive Summary)

- **Tổng số hồ sơ xử lý:** 19,259 bản ghi.
- **Số hồ sơ hợp lệ sau làm sạch:** 19,252 bản ghi.
- **Tổng giá trị bồi thường phê duyệt:** **276,416,112 VND**.

### Phân bổ Giá trị Bồi thường
![Phân bổ Claim](file:///D:/desktop_folder/04_Fraud_Detection/report/pre_process_data/charts_claims/claim_dist.png)
*Hình 1: Đồ thị mật độ số tiền bồi thường (Log scale) sau khi đã chuẩn hóa tỷ lệ 100x.*

---

## 2. Phân tích Chất lượng Dữ liệu (Data Integrity Analysis)

Dựa trên kinh nghiệm xử lý bảng Chi phí (DataChiPhi), chúng tôi phát hiện bảng Hồ sơ bồi thường cũng gặp các vấn đề hệ thống tương tự:

- **Lỗi Magnitude (100x):** Toàn bộ dữ liệu tài chính (`claim_amount_req`, `claim_amount_approved`) bị phóng đại 100 lần so với thực tế. 
  - *Kiểm chứng:* Đã so khớp một Case ID ngẫu nhiên với tổng tiền trong bảng Chi phí. Kết quả khớp 100% sau khi cùng chia cho 100.
- **Chuẩn hóa ICD:** Các mã chẩn đoán (ICD Primary) đã được làm sạch khoảng trắng và xử lý các giá trị "nan" về nhóm "Chưa xác định".
- **Xử lý Outlier:** Áp dụng phương pháp Median-check theo từng nhóm bệnh lý. Một số hồ sơ có giá trị đột biến (>20x trung vị và >20tr VNĐ) đã được tự động hạ cấp tỷ lệ để loại bỏ lỗi nhập liệu (extra zeros).

---

## 3. Top 10 Bệnh lý có chi phí bồi thường cao nhất

| Chẩn đoán (ICD Primary) | Tổng tiền Phê duyệt (VND) |
| :--- | :---: |
| Viêm mũi họng cấp [cảm thường] | 11,221,130 |
| Viêm phế quản phổi, không đặc hiệu | 10,654,546 |
| Viêm phế quản cấp | 9,857,849 |
| Viêm họng cấp | 5,515,140 |
| U ác của tuyến giáp | 4,063,612 |
| Sâu răng | 3,943,544 |
| Viêm mũi xoang cấp tính | 3,276,310 |
| Viêm phổi, tác nhân không xác định | 3,268,147 |
| Cúm do vi rút đã được định danh | 3,222,813 |
| Viêm tiểu phế quản cấp | 3,028,022 |

---

## 4. Phân bổ theo Loại hình Điều trị

| Loại hình | Tổng tiền (VND) | Tỷ trọng |
| :--- | :---: | :---: |
| Ngoại trú | 132,992,344 | 48.1% |
| Nội trú | 113,713,601 | 41.1% |
| Tai nạn | 22,718,178 | 8.2% |
| Khác | 5,310,190 | 1.9% |
| Sản khoa | 1,236,352 | 0.4% |
| Mã đặc thù (Mã 6) | 445,446 | 0.2% |
| Chưa phân loại | 0 | 0.0% |

---

## 5. Kết luận & Đề xuất (Anti-Fraud Insights)

1. **Tính nhất quán của dữ liệu:** Việc chuẩn hóa đồng bộ (chia 100x) giữa bảng Chi phí và bảng Hồ sơ bồi thường là điều kiện tiên quyết để tính toán đúng **Loss Ratio**.
2. **Trình trạng chẩn đoán:** Các bệnh lý đường hô hấp (Viêm mũi họng, Viêm phế quản) chiếm tỷ trọng chi phí cao nhất do số lượng hồ sơ khổng lồ. Cần kiểm tra các hồ sơ có tần suất lặp lại cao bất thường trên cùng một cá nhân.
3. **Dữ liệu sạch sẵn sàng:** File CSV đã làm sạch đặt tại: `D:\desktop_folder\04_Fraud_Detection\report\cleaned_data_final\DataHoSoBoiThuong_Cleaned_Final.csv`
