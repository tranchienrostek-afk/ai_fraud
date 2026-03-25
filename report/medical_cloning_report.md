# Báo cáo Truy vết: Nhân bản Bệnh án (Medical Record Cloning)

Phân tích dựa trên 100% dữ liệu phát hiện **259 cụm nội dung** được sao chép y hệt cho nhiều bệnh nhân.

## 1. Các mẫu nội dung "Copy-Paste" phổ biến nhất
| Nội dung Diễn biến bệnh/Dịch vụ | Tổng số hồ sơ | Số người dùng khác nhau |
| :--- | :--- | :--- |
| "viêm mũi họng cấp [cảm thường]" | 1,265 | 806 |
| "viêm phế quản phổi, không đặc hiệu" | 325 | 218 |
| "tăng huyết áp vô căn (nguyên phát)" | 268 | 154 |
| "viêm lợi [nướu] và bệnh quanh răng" | 192 | 188 |
| "bệnh trào ngược dạ dày- thực quản" | 182 | 145 |
| "khám tổng quát và kiểm tra sức khoẻ cho những người không có bệnh được chẩn đoán trước đó hoặc không có than phiền về sứ..." | 181 | 168 |
| "các viêm khác của âm đạo và âm hộ" | 168 | 110 |
| "cúm do vi rút đã được định danh" | 160 | 144 |
| "ct tnhh bv dktn an sinh-phuc truong minh" | 154 | 100 |
| "viêm họng có phỏng nước do vi rút entero có phát ban [bệnh tay chân miệng]" | 141 | 101 |
| "nhiễm trùng đường hô hấp trên cấp, không xác định" | 140 | 105 |
| "bệnh quanh răng, không đặc hiệu" | 136 | 131 |
| "viêm gan vi rút b mạn tính, không đồng nhiễm viêm gan vi rút d" | 127 | 86 |
| "viêm phổi, tác nhân không xác định" | 87 | 70 |
| "nhiễm khuẩn đường ruột do vi khuẩn khác" | 70 | 59 |

## 2. Kết luận
- **Tỷ lệ nhân bản:** Việc một đoạn văn bản dài trên 30 ký tự xuất hiện y hệt nhau cho hàng chục người dùng khác nhau là bằng chứng xác thực của việc làm giả hồ sơ bệnh án hoặc quy trình lập hồ sơ hời hợt, không ghi nhận đúng thực tế bệnh nhân.
- **Khuyến nghị:** Cần đối soát danh sách hồ sơ trong tệp `medical_cloning_clusters.csv` với các Cơ sở Y tế để làm rõ tại sao có sự trùng lặp này.
