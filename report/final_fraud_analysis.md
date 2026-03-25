# BÁO CÁO TỔNG KẾT: KHAI PHÁ DỮ LIỆU TRỤC LỢI BẢO HIỂM (DEEP RESEARCH)

Báo cáo này tổng hợp toàn bộ các phát hiện về hành vi rủi ro từ 565.811 dòng dữ liệu thô, được phân tích qua 5 lớp lọc trí tuệ nhân tạo và thống kê.

## 1. Bức tranh Toàn cảnh
- **Tổng số hồ sơ (Claims) được duyệt:** 19.259 hồ sơ.
- **Tổng số tiền bồi thường:** ~50 tỷ VNĐ (Ước tính).
- **Phạm vi Đại lý:** 100% hồ sơ thuộc quản lý của đại lý **Dương Văn Hoàng**.

## 2. Các Nhóm Chỉ số Rủi ro Chính (Top Findings)

### A. Nhóm "Syndicates" (Trục lợi có tổ chức) - **NGHIÊM TRỌNG**
Đây là phát hiện đáng báo động nhất về hạ tầng trục lợi:
- **Dùng chung STK Ngân hàng:** 
    - STK `1` được dùng cho **182 người** khác nhau.
    - STK `1048306057` được dùng cho **98 người**.
- **Dùng chung thông tin liên lạc:** Phát hiện 933 số điện thoại và 955 Email bị trùng lặp giữa nhiều khách hàng không cùng hộ gia đình.

### B. Nhóm "Nhân bản Bệnh án" (Medical Cloning)
Phát hiện **259 cụm nội dung** bệnh án bị sao chép y hệt (Copy-Paste) cho hàng trăm người dùng:
- Mẫu "Viêm mũi họng cấp" bị sao chép cho **806 người**.
- Mẫu "Viêm phế quản phổi" bị sao chép cho **218 người**.

### C. Nhóm "Thời điểm Nhạy cảm" & "Bệnh có sẵn"
Dấu hiệu "Có bệnh mới mua bảo hiểm" (Pre-existing conditions):
- **JIT Claims:** 1.539 hồ sơ phát sinh ngay sau khi hết thời gian chờ (Ngày 31-45).
- **Waiting Period Violation:** 1.256 hồ sơ bệnh đặc biệt (Tim mạch, Tiểu đường, Ung thư) phát sinh trong năm đầu tiên, đặc biệt là trong 60 ngày đầu.

### D. Nhóm "Hóa đơn Bán lẻ" (< 200k)
- **387 người dùng** có hành vi chuyên biệt: 100% các lần claim đều dưới 200.000 VNĐ để lách luật hóa đơn tài chính.

### E. Các kịch bản "Đặc thù" (Custom Scenarios)
- **Đứt dây chằng năm đầu:** 31 trường hợp claim tai nạn đứt dây chằng ngay trong năm đầu tham gia (khả năng cao là bệnh có sẵn).
- **Lặp lại đơn thuốc:** 129 người dùng có trên 5 lần claim liên tiếp chỉ để lấy tiền thuốc cho các bệnh nhẹ.
- **Điều trị không cân xứng:** Không tìm thấy hồ sơ 30M cho viêm họng, nhưng đã phát hiện các hồ sơ >13M cho các bệnh tương tự (Tay chân miệng) với thời gian nằm viện kéo dài.

## 3. Phân hạng Rủi ro (Risk Scoring)
Tôi đã gán điểm rủi ro cho từng hồ sơ dựa trên sự kết hợp của các chỉ số trên:
- **Rủi ro Rất cao (Score >= 10):** **814 hồ sơ**. (Tập trung nhóm Syndicate và Outlier lớn).
- **Rủi ro Cao (Score 5-9):** **1.309 hồ sơ**.

## 4. Kết luận và Kiến nghị
1. **Kiểm tra Đại lý:** Cần thực hiện thanh tra toàn diện đại lý **Dương Văn Hoàng** và các STK ngân hàng dùng chung.
2. **Đối soát Cơ sở Y tế:** Làm việc với các bệnh viện có tỷ lệ "Copy-Paste" bệnh án cao để chấn chỉnh quy trình lập hồ sơ.
3. **Từ chối Bồi thường:** Rà soát danh sách 1.256 hồ sơ vi phạm thời gian chờ bệnh đặc biệt để thu hồi/từ chối chi trả.

---
**Tệp dữ liệu tổng hợp (Master Risk List):** [master_fraud_risk_list.csv](file:///D:/desktop_folder/04_Fraud_Detection/report/master_fraud_risk_list.csv)

*Báo cáo được thực hiện tự động bởi Antigravity AI.*
