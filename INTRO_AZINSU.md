# AZINSU AI FRAUD
## Giải Pháp Phát Hiện Gian Lận Bảo Hiểm Y Tế Dựa Trên Tri Thức Đồ Thị

---

## 1. Tổng quan

**AZINSU AI FRAUD** là hệ thống phòng vệ chủ động trong quy trình bồi thường bảo hiểm y tế, sử dụng phân tích dữ liệu chuyên sâu, nhận diện hành vi bất thường và khai phá tri thức đồ thị (Knowledge Graph Mining) để phát hiện sớm các dấu hiệu gian lận trong hồ sơ yêu cầu chi trả.

Hệ thống có các năng lực cốt lõi vượt trội:
- **Nhận diện một cách hệ thống và chính xác** các trường hợp trùng lặp hồ sơ theo chuỗi thời gian và hành vi sử dụng dịch vụ.
- **Phát hiện các khoản chi phí kê khai không phù hợp** với phác đồ điều trị, mặt bằng chi phí thị trường cũng như quyền lợi hợp đồng. 
- **Theo dõi tần suất sử dụng dịch vụ** được triển khai liên tục giúp cảnh báo sớm các trường hợp phát sinh hồ sơ bất thường. 
- **Phân tích mạng lưới liên kết**, hệ thống có khả năng bóc tách các mối quan hệ tiềm ẩn giữa khách hàng, cơ sở y tế và các bên liên quan, qua đó nhận diện các dấu hiệu trục lợi có tổ chức.

Thay vì đưa ra kết luận cảm tính, hệ thống tạo ra các cảnh báo có mức độ rủi ro, kèm theo căn cứ dữ liệu và dấu vết giải thích rõ ràng để hỗ trợ thẩm định viên ra quyết định. Nhờ đó, việc phát hiện nguy cơ gian lận không còn phụ thuộc chủ yếu vào phán đoán thủ công, mà được thực hiện một cách có hệ thống, nhất quán và dựa trên dữ liệu.

---

## 🚀 Điểm nhấn Công nghệ & Giải pháp

Để đạt được hiệu quả phòng vệ tối ưu, **AZINSU AI FRAUD** được xây dựng trên 9 trụ cột cốt lõi:

1.  **Chiến lược Phòng vệ Chủ động:** Chuyển đổi từ rà soát thủ công sang phát hiện tự động dựa trên hành vi và liên kết dữ liệu.
2.  **Kiến trúc Multi-Agent 5 lớp:** Quy trình sàng lọc đa tầng từ Gatekeeper (Kiểm soát quy tắc) đến Narrator (Giải thích bằng ngôn ngữ tự nhiên).
3.  **Knowledge Graph chuyên sâu:** Mô hình hóa toàn bộ thực thể bảo hiểm với **10 loại node** và **9 loại quan hệ** phức tạp trên Neo4j.
4.  **Hệ thống 25 Quy tắc Kiểm soát:** Phân loại thông minh thành 3 nhóm (Cá nhân, Thời gian/Hợp đồng, Đồ thị nâng cao) với các mức độ cảnh báo từ High đến Critical.
5.  **Chấm điểm Rủi ro Đa chiều:** Thuật toán chấm điểm composite dựa trên **5 trục rủi ro** trọng yếu, trực quan hóa qua biểu đồ Radar.
6.  **Trung tâm Điều hành SIU Dashboard:** Hệ thống quản trị tập trung với **7 Tab phân tích** chuyên sâu (Mạng lưới, Bệnh lý, Anti-selection, v.v.).
7.  **Stack Công nghệ Hiện đại:** Sự kết hợp mạnh mẽ giữa Neo4j (Graph DB), FastAPI (Backend), và các thư viện trực quan hóa cao cấp như Cytoscape.js và ECharts.
8.  **Quy trình Human-in-the-loop:** Flow vận hành mượt mà từ dữ liệu thô đến cảnh báo AI, hỗ trợ thẩm định viên ra quyết định cuối cùng một cách chính xác.
9.  **Giá trị Đa phương:** Mang lại lợi ích thực tế cho cả thẩm định viên (giảm tải), doanh nghiệp (giảm tổn thất) và khách hàng (bồi thường nhanh chóng).

---

## 2. Kiến trúc hệ thống: Mô hình 5 lớp sàng lọc

Hệ thống được thiết kế theo kiến trúc Multi-Agent gồm 5 lớp xử lý tuần tự, đảm bảo không bỏ sót bất kỳ mẫu gian lận nào:

| Lớp | Tên gọi | Chức năng |
|-----|---------|-----------|
| 1 | **Gatekeeper** | Kiểm tra quy tắc nghiệp vụ — xác thực tính hợp lệ của hồ sơ |
| 2 | **Graph Detective** | Phân tích mạng lưới quan hệ — phát hiện tổ chức gian lận |
| 3 | **Anomaly Hunter** | Phát hiện bất thường bằng phương pháp thống kê và học máy |
| 4 | **Scoring Judge** | Tổng hợp điểm rủi ro đa chiều — xếp hạng đối tượng nghi vấn |
| 5 | **Narrator** | Sinh tường thuật giải thích — cung cấp căn cứ cho thẩm định viên |

---

## 3. Cơ sở dữ liệu Tri thức Đồ thị (Knowledge Graph)

Toàn bộ dữ liệu bồi thường được mô hình hóa thành đồ thị quan hệ trên nền tảng Neo4j, cho phép truy vấn và phân tích các mối liên kết phức tạp mà cơ sở dữ liệu truyền thống không thể thực hiện.

**10 loại thực thể (Node):**
Person, Claim, Hospital, Doctor, BankAccount, Contract, ExpenseDetail, Diagnosis, DrugOrService, Insurer

**9 loại quan hệ (Relationship):**
FILED_CLAIM, AT_HOSPITAL, EXAMINED_BY, RECEIVES_TO, HAS_CONTRACT, HAS_EXPENSE, IS_ITEM, DIAGNOSED_WITH, INSURED_BY

Mô hình đồ thị này cho phép truy vết đường đi của dòng tiền, phát hiện nhóm đối tượng chia sẻ thông tin cá nhân, và nhận diện các vòng tròn gian lận có tổ chức.

---

## 4. Bộ quy tắc kiểm soát: 25 Mẫu phát hiện gian lận

### Nhóm A: Gian lận cá nhân (Rules 1-10)

| # | Tên quy tắc | Mức độ | Mô tả |
|---|-------------|--------|-------|
| 1 | Trục lợi vặt (Petty Fraud) | HIGH | Hồ sơ < 200k lặp lại > 7 lần |
| 2 | Trung thành CSYT bất thường | HIGH | Bệnh nhẹ khám > 2 lần tại cùng cơ sở |
| 3 | Cụm SĐT dùng chung | CRITICAL | > 5 người chia sẻ 1 số điện thoại |
| 4 | Nhóm tài khoản ngân hàng | CRITICAL | Nhiều người nhận tiền vào cùng 1 STK |
| 5 | Cặp Bác sĩ - Bệnh viện nóng | HIGH | Bác sĩ ký > 20 hồ sơ đáng ngờ tại 1 BV |
| 6 | Phòng khám ma (Ghost Clinic) | HIGH | BV có > 70% hồ sơ dưới 200k |
| 7 | Tần suất claim cao bất thường | HIGH | Khách hàng nộp > 10 hồ sơ |
| 8 | Doctor Shopping | MEDIUM | Cùng bệnh, khám >= 3 BV khác nhau |
| 9 | Chẩn đoán - Số tiền bất thường | HIGH | Claim > 3x trung vị cho cùng bệnh lý |
| 10 | Đơn giá thuốc/DV vượt ngưỡng | CRITICAL | Đơn giá > 3x trung bình thị trường |

### Nhóm B: Gian lận hợp đồng & thời gian (Rules 11-15)

| # | Tên quy tắc | Mức độ | Mô tả |
|---|-------------|--------|-------|
| 11 | Tỷ lệ Bồi thường / Phí BH | CRITICAL | Bồi thường > 5x phí đóng |
| 12 | Thời gian nằm viện bất thường | HIGH | Điều trị > 3x trung vị cho cùng bệnh |
| 13 | Tỷ lệ từ chối cao | HIGH | > 50% chi phí bị loại trừ |
| 14 | Hợp đồng hết hạn vẫn claim | CRITICAL | Nộp hồ sơ sau ngày hết hạn HĐ |
| 15 | Nộp hồ sơ trễ bất thường | HIGH | > 90 ngày sau khám hoặc ngày nộp trước ngày khám |

### Nhóm C: Khai phá đồ thị nâng cao (Rules 16-25)

| # | Tên quy tắc | Mức độ | Mô tả |
|---|-------------|--------|-------|
| 16 | Nâng cấp HĐ rồi Claim lớn | CRITICAL | Claim > 5 triệu trong 90 ngày đầu hợp đồng |
| 17 | Vòng tròn Bác sĩ - Bệnh nhân | CRITICAL | >= 5 bệnh nhân luôn đi cùng 1 bác sĩ (>= 3 lần/người) |
| 18 | Nhảy bệnh viện cùng tuần | HIGH | Khám >= 2 BV khác nhau trong 7 ngày |
| 19 | Trùng lặp danh mục chi phí | HIGH | Cùng 1 claim khai > 2 chi phí trùng danh mục |
| 20 | STK không khớp tên | CRITICAL | Tiền chảy sang tài khoản người khác |
| 21 | Cặp Đại lý - Bác sĩ bất thường | HIGH | 1 đại lý xử lý > 20 hồ sơ từ 1 bác sĩ |
| 22 | Bệnh lý vs Chi phí không tương xứng | HIGH | Bệnh nhẹ nhưng chi phí > 3x trung vị nhóm |
| 23 | Dòng tiền vòng tròn | CRITICAL | >= 3 người dùng chung STK VÀ chung BV |
| 24 | Cụm claim cuối tuần | MEDIUM | > 60% hồ sơ vào cuối tuần (khi >= 5 claims) |
| 25 | Nhiều hồ sơ cùng ngày cùng BV | HIGH | >= 2 hồ sơ cùng ngày tại cùng 1 BV (bill splitting) |

**Phân bổ mức độ:** 10 CRITICAL | 13 HIGH | 2 MEDIUM

---

## 5. Hệ thống chấm điểm rủi ro đa chiều

Mỗi đối tượng được đánh giá trên 5 trục rủi ro, tổng hợp thành điểm composite (0-10):

| Trục đánh giá | Trọng số | Ý nghĩa |
|---------------|----------|---------|
| Tỷ lệ bồi thường / Phí BH | 35% | Tác động tài chính — trọng số cao nhất |
| Tần suất nộp hồ sơ | 20% | Khối lượng claim bất thường |
| Tỷ lệ hồ sơ nhỏ (Petty) | 15% | Dấu hiệu trục lợi vặt có hệ thống |
| Thời gian điều trị | 15% | Nằm viện kéo dài bất thường |
| Đa dạng chẩn đoán | 15% | Lặp lại cùng bệnh hay đa dạng |

Biểu đồ Radar 5 chiều trực quan hóa hồ sơ rủi ro cho từng **cá nhân**, **bệnh viện**, và **bác sĩ**.

---

## 6. Dashboard phân tích trực quan

Dashboard SIU (Special Investigation Unit) cung cấp 7 góc nhìn phân tích:

### Tab 1: Mạng lưới Liên kết
- Đồ thị tương tác (Cytoscape.js) hiển thị quan hệ giữa 8 loại thực thể
- Phát hiện trực quan các nhóm đối tượng chia sẻ STK, SĐT, bệnh viện
- Click-to-expand: mở rộng mạng lưới từ bất kỳ node nào
- Inspector Panel: xem chi tiết thuộc tính và quan hệ

### Tab 2: Quy tắc Kiểm soát
- Bảng tổng hợp 25 quy tắc với số lượng phát hiện và mức độ nghiêm trọng
- Drill-down vào từng quy tắc xem danh sách đối tượng cụ thể
- Click vào đối tượng để xem toàn bộ câu chuyện (Person Story)

### Tab 3: Đối tượng Nghi vấn
- Top 50 đối tượng có điểm rủi ro cao nhất
- Biểu đồ Radar cá nhân cho từng đối tượng
- Timeline chi tiết: lịch sử claim, phân bổ chẩn đoán, bác sĩ, bệnh viện

### Tab 4: Dòng thời gian
- Biểu đồ kép: số lượng + tổng tiền claim theo tháng
- Heatmap: phân bố claim theo ngày trong tháng
- Thanh ngang audit rules theo mức độ nghiêm trọng

### Tab 5: Phân tích Bệnh lý
- Scatter plot: trung vị vs max theo nhóm chẩn đoán (bubble = số lượng)
- Phát hiện outlier bệnh lý có chi phí vượt ngưỡng
- Drill-down vào từng chẩn đoán xem phân bổ mùa vụ

### Tab 6: Thời gian chờ (Anti-Selection)
- Histogram phân bổ claim theo tháng kể từ ngày mua BH
- Phát hiện hiện tượng mua BH rồi claim ngay (0-7 ngày)
- Top 10 bệnh lý claim sớm nhất sau đăng ký

### Tab 7: Báo cáo Tổng hợp
- Top 20 bệnh viện: hiệu suất, tỷ lệ petty, chi phí trung bình
- Top 20 nhóm bệnh: phân bổ theo mùa vụ
- Phân tích anti-selection theo chẩn đoán

---

## 7. Công nghệ nền tảng

| Thành phần | Công nghệ | Vai trò |
|------------|-----------|---------|
| Backend API | FastAPI + Uvicorn | 18 API endpoints, xử lý truy vấn |
| Cơ sở dữ liệu đồ thị | Neo4j 5.12 + APOC + GDS | Lưu trữ và truy vấn quan hệ phức tạp |
| Cơ sở dữ liệu quan hệ | PostgreSQL 15 | Dữ liệu giao dịch |
| Vector Database | Qdrant | Tìm kiếm tương tự, phát hiện bất thường |
| Trực quan hóa | ECharts 5.5 + Cytoscape.js 3.28 | 9+ loại biểu đồ + đồ thị mạng lưới |
| Hạ tầng | Docker Compose | 5 services, CI/CD tự động qua GitHub Actions |

---

## 8. Quy trình vận hành

```
Dữ liệu bồi thường mới
        |
        v
  [Nạp vào Knowledge Graph]
        |
        v
  [25 Quy tắc kiểm soát tự động chạy]
        |
        v
  [Chấm điểm rủi ro đa chiều]
        |
        v
  [Dashboard SIU hiển thị kết quả]
        |
        v
  [Thẩm định viên xem xét + ra quyết định]
```

- Hệ thống **không** tự động từ chối hồ sơ
- Hệ thống **cung cấp** cảnh báo + căn cứ + giải thích
- Quyết định cuối cùng thuộc về **thẩm định viên** (Human-in-the-loop)

---

## 9. Giá trị mang lại

**Cho Thẩm định viên:**
- Giảm thời gian rà soát thủ công — hệ thống đã sàng lọc và xếp hạng
- Có căn cứ dữ liệu rõ ràng khi đưa ra quyết định
- Phát hiện được các mẫu gian lận phức tạp mà mắt thường không thể nhận biết

**Cho Doanh nghiệp:**
- Giảm tổn thất do gian lận có tổ chức
- Nâng cao tính minh bạch và nhất quán trong quy trình kiểm soát
- Cơ sở dữ liệu tri thức tích lũy theo thời gian, ngày càng thông minh hơn

**Cho Khách hàng:**
- Quy trình bồi thường nhanh hơn cho hồ sơ hợp lệ
- Công bằng — mọi hồ sơ được đánh giá theo cùng tiêu chuẩn

---

*AZINSU AI FRAUD — Minh bạch hóa quy trình, tối ưu hóa niềm tin.*
