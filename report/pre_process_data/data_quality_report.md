# Báo cáo Phản hồi Chất lượng Dữ liệu (Data Quality Feedback Report)

**Dự án:** Fraud Detection - Phân tích Dữ liệu Chi phí (DataChiPhi)
**Người lập:** Antigravity AI
**Đối tượng nhận:** Đội ngũ Kỹ thuật / Data Engineering

---

## 1. Tổng quan Tình trạng Dữ liệu (Overview)
Trong quá trình xử lý và khai phá dữ liệu chi phí y tế (DataChiPhi), chúng tôi phát hiện tệp dữ liệu gốc có độ nhiễu và sai số **RẤT CAO**, gây ảnh hưởng trực tiếp đến tính chính xác của các thuật toán phát hiện gian lận.

Báo cáo này liệt kê các lỗi hệ thống được tìm thấy và các "thuật toán chữa cháy" đã được áp dụng để làm sạch dữ liệu.

---

## 2. Các lỗi dữ liệu nghiêm trọng (Identified Data Issues)

### 2.1. Lỗi Đơn vị Tiền tệ (Scaling & Magnitude Errors)
Đây là lỗi phổ biến nhất, gây ra biến động giá trị lên tới hàng ngàn lần.
- **Biểu hiện:** Các thuốc thông thường (Zinmax, Gichion) có đơn giá ghi nhận 50.000.000 - 100.000.000 VND.
- **Nguyên nhân:** Sự không đồng nhất về đơn vị tính giữa các cơ sở y tế (có nơi dùng đồng, có nơi dùng hào/xu, có nơi nhân hệ số ảo 100x hoặc 10.000x).
- **Ví dụ điển hình:** `Urê máu` lẽ ra chỉ vài chục ngàn VND nhưng được ghi nhận là 4.480.448.000 trong file gốc (DataChiPhi_part3.csv).

### 2.2. Lỗi Lệch Cột (Row Misalignment)
- **Biểu hiện:** Tên thuốc chứa các mã định danh (UUID), ngày tháng, hoặc các đoạn mã kỹ thuật.
- **Nguyên nhân:** Định dạng CSV không được escape đúng cách (chủ yếu do dấu phẩy hoặc dấu ngoặc nhọn `{}` nằm trong nội dung trường dữ liệu).
- **Hậu quả:** Dữ liệu tài chính nhảy sang cột Item Type hoặc Category, làm sai lệch phân bổ chi phí theo nhóm.

### 2.3. Lỗi Cột Đơn Giá (Unit Price Corruption)
- **Biểu hiện:** Cột `unit_price` hoàn toàn không khớp với `total_amount` và `quantity`.
- **Ví dụ:** Một bản ghi Zinmax có `total_amount` 10.000.000 nhưng `unit_price` lại ghi 10.000.000.000.0.
- **Kết luận:** Cột `unit_price` trong hệ thống gốc không thể tin cậy.

### 2.4. Lỗi Encode (BOM/Encoding)
- **Biểu hiện:** Header đầu tiên (`detail_id`) bị dính ký tự lạ khiến script parse lỗi nếu không dùng `utf-8-sig`.

---

## 3. Giải pháp làm sạch đã áp dụng (Implemented Solutions)

Chúng tôi đã thiết lập một "Đường ống làm sạch" (Cleaning Pipeline) 4 tầng trong script `datamining_script.py`:

1. **Tầng 1 (Scaling Baseline):** Chia toàn bộ tiền tệ cho 100 (đưa về VND chuẩn).
2. **Tầng 2 (Derived Logic):** Bỏ qua cột `unit_price` gốc. Tính toán lại đơn giá: `Unit Price = Total Amount / Quantity`.
3. **Tầng 3 (Statistical Normalization - VITAL):** 
   - Hệ thống tự động tính mức giá trung vị (Median) cho từng tên thuốc/dịch vụ trên toàn bộ 100.000 dòng.
   - Nếu bản ghi nào có giá cao vọt (> 10x Median), hệ thống tự động áp dụng hệ số hạ áp 100x hoặc 10.000x để đưa về vùng thực tế.
4. **Tầng 4 (Business Safeguards):** Áp dụng trần chi phí theo loại hình dịch vụ:
   - Xét nghiệm: < 5tr VND/lần.
   - Khám bệnh: < 2tr VND/lần.

### Biểu đồ trực quan hóa kết quả (Visualization)
![So sánh dải giá theo Phân loại](file:///D:/desktop_folder/04_Fraud_Detection/report/pre_process_data/charts/category_boxplot.png)
*Hình 3: Boxplot so sánh dải đơn giá giữa các phân loại chính sau khi làm sạch. Dữ liệu hiện tại đã phản ánh đúng bản chất nghiệp vụ (vd: Phẫu thuật có dải giá cao hơn Xét nghiệm).*

---

## 4. Kết quả sau làm sạch
- **Sản phẩm:** File [solution_chiphi.md](file:///D:/desktop_folder/04_Fraud_Detection/report/pre_process_data/solution_chiphi.md).
- **Độ tin cậy:** Các giá trị ảo (Urea 44tr, Gichion 42tr) đã biến mất. Các thuốc đắt tiền thực sự (Perjeta, Herceptin) được giữ lại chính xác.
- **Tổng tiền phê duyệt:** Giảm từ mức ảo > 100 tỷ VND về mức thực tế ~34 tỷ VND.

## 5. Kiến nghị cho Đội Kỹ thuật
1. Kiểm tra lại Logic Export CSV: Đảm bảo Escape các ký tự đặc biệt trong tên thuốc.
2. Chuẩn hóa Đơn vị tính: Ép toàn bộ dữ liệu từ các đối tác về một đơn vị VND duy nhất trước khi lưu kho (Data Warehouse).
3. Verify cột Unit Price: Rà soát lại công thức tính đơn vị tại source code của hệ thống core.
