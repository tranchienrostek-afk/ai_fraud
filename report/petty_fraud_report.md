# Báo cáo Truy vết: Chỉ số Trục lợi qua "Hóa đơn bán lẻ"

Dựa trên yêu cầu truy vết chỉ số: **"Chỉ phát sinh hóa đơn bán lẻ dưới 200.000 VNĐ"**, tôi đã tiến hành phân tích trên toàn bộ 565.811 bản ghi dữ liệu.

## 1. Phương pháp xác định
Vì hệ thống không có nhãn "Hóa đơn bán lẻ" trực tiếp bằng văn bản, tôi đã sử dụng **phương pháp định lượng (Statistical Proxy)** dựa trên quy định tài chính:
- **Ngưỡng số tiền:** Dưới 200.000 VNĐ (ngưỡng thường không yêu cầu hóa đơn đỏ/tài chính).
- **Tính chất "Chỉ phát sinh":** Lọc những người dùng **100%** số lần claim đều dưới ngưỡng này.
- **Tần suất lặp lại:** Có ít nhất **3 lần** trở lên để loại bỏ các trường hợp ngẫu nhiên.

## 2. Kết quả thống kê
- **Số lượng người dùng khớp hoàn toàn chỉ số:** **387 người**.
- **Tổng số hồ sơ (claims) từ nhóm này:** ~1.200 hồ sơ.
- **Tỷ lệ lặp lại cao nhất:** Một cá nhân có **7 lần** đi khám liên tiếp đều dưới 200.000 VNĐ.

## 3. Phân tích hành vi (Clusters)
Nhóm 387 người này được chia thành các mức độ rủi ro:
- **Rủi ro Rất cao (Tần suất >= 5 lần):** 18 người.
- **Rủi ro Cao (Tần suất 3-4 lần):** 369 người.

## 4. Kết luận và Khuyến nghị
Chỉ số này **hoàn toàn có thể thống kê được** và là một dấu hiệu cảnh báo mạnh mẽ. 
- **Danh sách chi tiết:** Đã được lưu tại `report/suspicious_petty_claims.csv`.
- **Khối lượng bồi thường:** Tuy mỗi đơn hàng nhỏ (<200k), nhưng tổng số tiền chi trả cho nhóm 387 người này là không nhỏ và có tính chất hệ thống.

**Đề xuất:** Cần yêu cầu các hồ sơ thuộc nhóm này cung cấp thêm bằng chứng y tế (Sổ khám bệnh, đơn thuốc kèm theo) dù số tiền nhỏ để xác minh tính xác thực.
