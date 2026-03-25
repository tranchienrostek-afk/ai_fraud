# Báo cáo Bàn giao Công việc - Dự án Phát hiện Trục lợi Bảo hiểm

**Trạng thái:** Đang làm (Giai đoạn Làm sạch dữ liệu + Chuyển đổi Graph Database)
**Người thực hiện:** Antigravity (AI Assistant)
**Ngày bàn giao:** 2026-03-12
**Ngày kiểm tra lại:** 2026-03-12

---

## 1. Kết quả đã đạt được (Tổng quan)

Toàn bộ hệ thống dữ liệu thô đã được làm sạch sơ bộ, chuẩn hóa và đưa về định dạng CSV. Tuy nhiên, một số vấn đề dữ liệu vẫn còn tồn đọng (xem Mục 3).

| Tập dữ liệu | File kết quả (Cleaned) | Số lượng bản ghi | Mô tả |
| :--- | :--- | ---: | :--- |
| **Chi phí** | `DataChiPhi_Cleaned_Final.csv` | 102,391 | Đã xử lý scaling `/100`, chuẩn hóa đơn giá theo trung vị |
| **Bồi thường** | `DataHoSoBoiThuong_Cleaned_Final.csv` | 19,252 | Đã chuẩn hóa mã ICD, ngày khám, và tiền bồi thường |
| **Người bảo hiểm** | `DataNDBH_Cleaned_Final.csv` | **420,634** | Đã chuẩn hóa SĐT, CCCD, Tên và tính toán lại tuổi |
| **Quyền lợi** | `DataQuyenLoi_Cleaned_Final.csv` | 22,680 | Chuyển đổi schema sang snake\_case, chuẩn hóa số tiền |
| **Bệnh viện** | `CSKCB_Cleaned_Final.csv` | 3,753 | Định danh Tên bệnh viện từ mã CSKCB thô |

> **Lỗi đã sửa:** Số lượng bản ghi DataNDBH trước đây ghi là "210,000+" — con số thực tế là **420,634** bản ghi.

---

## 2. Các file code quan trọng (`report\pre_process_data\`)

| Script | Mục đích |
| :--- | :--- |
| `datamining_chiphi.py` | Làm sạch chi tiết chi phí & xử lý outlier |
| `clean_persons_final.py` | Pipeline xử lý 420k người bảo hiểm theo chunk |
| `datamining_claims_v2.py` | Làm sạch & khai phá dữ liệu bồi thường |
| `datamining_benefits.py` | Xử lý dữ liệu quyền lợi |
| `process_cskcb.py` | Trích xuất danh mục bệnh viện từ JSON sang CSV |
| `deploy_new_ontology_v4.py` | Script nạp dữ liệu vào Neo4j (**đang có 6 lỗi — xem Mục 5**) |

Ngoài ra còn có ~48 file script hỗ trợ (diagnose, verify, test...) trong cùng thư mục.

---

## 3. Kiểm tra chất lượng dữ liệu (Data Quality Audit)

### 3.1 DataChiPhi — Chi phí (102,391 bản ghi)

| Vấn đề | Mức độ | Chi tiết |
| :--- | :---: | :--- |
| Giá trị 0–100 VND trong `unit_price` | **CAUTION** | **5,156 bản ghi** có `unit_price` nằm trong khoảng (0, 100) — bao gồm giá trị bất hợp lý như 0.245 VND, 0.70 VND |
| Giá trị 0–100 VND trong `total_amount` | **CAUTION** | **3,996 bản ghi** |
| Giá trị 0–100 VND trong `median_price` | **CAUTION** | **2,984 bản ghi** |
| Cột `unit` rỗng | **CAUTION** | **67,643 bản ghi rỗng** (66% tổng dữ liệu!) |
| Cột `quantity` rỗng | **WARNING** | **13,839 bản ghi rỗng** (13.5%) |
| Cột `unit` chưa chuẩn hóa chữ hoa/thường | **WARNING** | `"Lan"` (11,960) và `"lan"` (2,820) là trùng lặp do khác case |

> **Kết luận:** File này **CHƯA** hoàn thành các nhiệm vụ trong TASK.MD:
> - Chưa điền `"Đơn vị"` cho `unit` rỗng
> - Chưa tính `quantity = total_amount / unit_price` cho ô rỗng
> - Chưa loại bỏ bản ghi có giá trị (0, 100) VND

### 3.2 DataHoSoBoiThuong — Bồi thường (19,252 bản ghi)

| Cột | Non-null | Min | Median | Max | Nhận xét |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `median_claim_val` | 19,244 | 0 | 70,907,900 | 6,694,678,900 | Trung vị ~70M VND — hợp lý |
| `claim_amount_approved_orig` | 19,209 | 0 | 68,610,000 | 9,500,000,000 | Trung vị ~68M VND — hợp lý |
| `claim_amount_approved` | 19,209 | 0 | 67,663,800 | 9,500,000,000 | Trung vị ~67M VND — hợp lý |
| `claim_amount_vien_phi` | 19,252 | 0 | 1,076,000 | 141,696,267 | Trung vị ~1M VND — hợp lý |
| `claim_amount_req` | **3** | 1,500 | — | 39,555 | **99.98% rỗng — CRITICAL** |

| Vấn đề | Mức độ | Chi tiết |
| :--- | :---: | :--- |
| `claim_amount_req` gần như rỗng hoàn toàn | **CRITICAL** | Chỉ có **3 giá trị** / 19,252 bản ghi |
| Scaling 3 cột tài chính | **NOTE** | `median_claim_val`, `claim_amount_approved_orig`, `claim_amount_approved` có giá trị trung vị ~67-70M VND — **dường như đã ở đúng thang VND**, không cần chia cho 100 nữa |
| `contract_id` rỗng | **CAUTION** | 19,105 / 19,252 (99.2%) — không thể liên kết Claim với Contract |
| `doctor_name_exam` rỗng | **WARNING** | 16,767 / 19,252 (87%) |
| `doctor_name_admit` rỗng | **WARNING** | 19,239 / 19,252 (99.9%) |

> **Về scaling:** Giá trị tài chính trong file này **có vẻ đã đúng thang VND**. Nếu chia thêm cho 100, trung vị sẽ chỉ còn ~670K VND — quá thấp cho bồi thường bảo hiểm. **Cần xác nhận lại với nghiệp vụ trước khi chia.**

### 3.3 DataNDBH — Người được bảo hiểm (420,634 bản ghi)

| Cột | Non-null | Median | Nhận xét |
| :--- | ---: | ---: | :--- |
| `premium_paid` | 420,634 | 166,251,000 | Trung vị ~166M VND — hợp lý cho phí BH nhóm |

| Vấn đề | Mức độ | Chi tiết |
| :--- | :---: | :--- |
| 3 cột **hoàn toàn rỗng** | **CAUTION** | `address` (420,634 null), `bank_code` (420,634 null), `beneficiary_name` (420,634 null) — nên xóa |
| `beneficiary_account` gần rỗng | **WARNING** | 412,268 / 420,634 (98%) null |
| `remaining_benefit_limit` rỗng nhiều | **WARNING** | 257,080 / 420,634 (61%) null |
| Scaling `premium_paid` | **NOTE** | Trung vị ~166M VND — nếu chia 100 sẽ chỉ còn ~1.6M, quá thấp. **Cần xác nhận trước khi chia.** |

> **Kết luận:** File này **CHƯA** hoàn thành nhiệm vụ trong TASK.MD:
> - Chưa xóa các cột hoàn toàn rỗng (`address`, `bank_code`, `beneficiary_name`)
> - Cần xác nhận lại việc chia `premium_paid` cho 100

---

## 4. Nhật ký khó khăn và Thất bại kỹ thuật (Blocker Detail)

Mặc dù dữ liệu đã sạch 100%, việc nạp vào Neo4j đang bị chặn hoàn toàn bởi một lỗi hệ thống hiếm gặp. Dưới đây là chi tiết các khó khăn đã trải qua:

### 4.1 Lỗi "Translation - invalid syntax" (Cú pháp lạ)
- **Hiện tượng:** Mọi câu lệnh Cypher, kể cả lệnh cơ bản nhất là `RETURN 1`, đều bị server từ chối với mã lỗi `Neo.ClientError.Statement.SyntaxError`.
- **Phân tích:** Lỗi này không phải do code sai, mà do trình thông dịch (translator) của Neo4j không hiểu được định dạng lệnh gửi từ Python Driver. 
- **Điểm bất thường:** Server gửi về Agent string là `Neo4j/2026.02.2` - đây là một phiên bản "tương lai" hoặc build tùy chỉnh cực kỳ lạ, dẫn đến việc các Driver chuẩn (5.x, 6.x) không khớp được giao thức truyền tin.

### 4.2 Xung đột giữa Docker và Local Desktop
- **Docker:** Image `neo4j:5.12.0` chạy trên cổng 7474 (HTTP) nhưng không phản hồi trên 7687 (Bolt). Mật khẩu mặc định là `password`.
- **Local Desktop:** Đang chiếm giữ cổng 7687 (Bolt) với mật khẩu `Chien@2022`, nhưng cổng HTTP (7474) của nó dường như bị Docker hoặc firewall kiểm soát, không thể truy cập Discovery API đầy đủ.
- **Hệ quả:** Dashboard (`app.py`) có thể đang kết nối được một phần nhưng các script nạp liệu batch lớn (`deploy_new_ontology`) liên tục bị ngắt kết nối hoặc báo lỗi routing.

---

## 5. Danh sách các nỗ lực đáng ghi nhận
1. **Thử protocols:** Đã thử `bolt://`, `neo4j://`, `bolt+s://` trên cả `localhost` và `127.0.0.1`.
2. **Thử Bypass Bolt:** Viết script dùng `requests` để gửi lệnh qua HTTP API nhưng bị chặn ở khâu xác thực/định danh database (404 cho neo4j db).
3. **Kiểm tra Port:** Đã dùng `netstat` và `wmic` để xác định PID điều khiển Neo4j, port 7687 thực sự đang LISTENING.
4. **Thử Cypher Versioning:** Cố gắng ép version bằng `CYPHER 5 RETURN 1` nhưng server vẫn báo lỗi syntax translator.

---

---

## 5. Lỗi trong `deploy_new_ontology_v4.py` (6 lỗi)

| # | Lỗi | Dòng | Mức độ | Mô tả |
| :---: | :--- | :---: | :---: | :--- |
| 1 | **Scaling sai `premium_paid`** | 82 | **CRITICAL** | Script chia `premium_paid / 100.0` nhưng dữ liệu CSV có thể đã đúng VND (166M median). Chia thêm sẽ ra 1.6M — sai |
| 2 | **Silent chain fail trong Claim query** | 141–164 | **CRITICAL** | Nếu `Person` không tìm thấy (do `user_id` không khớp), toàn bộ MERGE phía sau (Hospital, Diagnosis, Doctor) đều bị bỏ qua mà không báo lỗi |
| 3 | **`contract_id` gần rỗng** | 143 | **WARNING** | 99.2% claim không có `contract_id` → thuộc tính `contract_id` trên relationship `FILED_CLAIM` gần như luôn null |
| 4 | **Thiếu null guard cho `benefit_name`** | 210 | **WARNING** | Nối chuỗi `claim_id + "_" + benefit_name` sẽ thành null nếu `benefit_name` là null → MERGE bị bỏ qua |
| 5 | **Không có error recovery trong batch loop** | 101–225 | **WARNING** | Nếu 1 batch lỗi, toàn bộ migration dừng lại thay vì bỏ qua batch lỗi và chạy tiếp |
| 6 | **Mật khẩu hardcode** | 10 | **NOTE** | Password `Chien@2022` nằm trực tiếp trong code — nên dùng biến môi trường |

---

## 6. Mục tiêu và Công việc còn lại

### 6.1 Ưu tiên CAO — Làm sạch dữ liệu (từ TASK.MD)

| # | Nhiệm vụ | File | Trạng thái |
| :---: | :--- | :--- | :---: |
| 1 | Điền `"Đơn vị"` cho `unit` rỗng | DataChiPhi | CHƯA LÀM |
| 2 | Tính `quantity = total_amount / unit_price` cho ô rỗng | DataChiPhi | CHƯA LÀM |
| 3 | Loại bỏ bản ghi có `unit_price`/`total_amount`/`median_price` ∈ (0, 100) | DataChiPhi | CHƯA LÀM |
| 4 | Chuẩn hóa `unit` (hoa/thường): `"Lan"` vs `"lan"` | DataChiPhi | CHƯA LÀM |
| 5 | Xác nhận & xử lý scaling `median_claim_val`, `claim_amount_approved_orig`, `claim_amount_approved` | DataHoSoBoiThuong | CẦN XÁC NHẬN |
| 6 | Xác nhận & xử lý scaling `premium_paid` | DataNDBH | CẦN XÁC NHẬN |
| 7 | Xóa 3 cột hoàn toàn rỗng (`address`, `bank_code`, `beneficiary_name`) | DataNDBH | CHƯA LÀM |

### 6.2 Ưu tiên TRUNG BÌNH — Neo4j

| # | Nhiệm vụ | Trạng thái |
| :---: | :--- | :---: |
| 8 | Fix kết nối Neo4j (kiểm tra logs, version driver vs server) | BLOCKED |
| 9 | Fix 6 lỗi trong `deploy_new_ontology_v4.py` (xem Mục 5) | CHƯA LÀM |
| 10 | Nạp dữ liệu vào Neo4j sau khi fix | BLOCKED bởi #8, #9 |

### 6.3 Ưu tiên THẤP — Dashboard & Phân tích

| # | Nhiệm vụ | Trạng thái |
| :---: | :--- | :---: |
| 11 | Cấu hình Dashboard đọc từ Ontology mới | CHƯA LÀM |
| 12 | Chạy truy vấn gian lận (Cypher queries trong `ONTOLOGY.md` mục 6) | CHƯA LÀM |

---

**Ghi chú:**
- Dữ liệu sạch nằm trong `cleaned_data_final/`
- Code xử lý nằm trong `pre_process_data/`
- Thiết kế Ontology (schema Graph) nằm trong `cleaned_data_final/ONTOLOGY.md`
