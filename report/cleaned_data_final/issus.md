# BÁO CÁO SỰ CỐ KỸ THUẬT (CYPHER SYNTAX BLOCKER)

**Trạng thái:** Đang xử lý (In Progress)
**Thời gian xử lý:** 12/03/2026

## 1. Sự cố ban đầu
Mọi truy vấn Cypher qua Python Driver đều thất bại với lỗi:
`neo4j.exceptions.CypherSyntaxError: {code: Neo.ClientError.Statement.SyntaxError} {message: Translation - invalid syntax}`

**Nguyên nhân gốc:** Neo4j Desktop chạy phiên bản bất thường `Neo4j/2026.02.2` (không phải bản chính thức), engine translator bị lỗi. Port 7474 (HTTP) và 7687 (Bolt) đều do process này chiếm.

## 2. Đã xử lý được

### 2.1. Kill Neo4j Desktop, chuyển sang Docker
- Kill toàn bộ process Neo4j Desktop (PID 13852 + các PID con).
- Start Docker container `neo4j:5.12.0` từ `docker-compose.yml`.
- **Kết quả:** Neo4j Docker hoạt động bình thường, `RETURN 1` thành công.

### 2.2. Fix script `deploy_new_ontology_v4.py`
- Password: `Chien@2022` → `password` (Docker credentials).
- Fix lỗi `SemanticError: Cannot merge relationship with null property`:
  - `FILED_CLAIM {contract_id: row.contract_id}` → MERGE không property, SET riêng.
  - `AT_HOSPITAL {visit_type, admission_date, discharge_date}` → MERGE không property, SET riêng.
- **Lý do:** 99% claims (19,105/19,252 rows) có `contract_id = NULL`.

### 2.3. Nạp dữ liệu lần 1
- **Persons/Contracts/BankAccounts:** Nạp thành công (~421 batch x 1000 rows, ~143 giây).
- **Claims:** Fail do lỗi null property (đã fix ở 2.2).

### 2.4. Nạp dữ liệu lần 2 (sau fix)
- Script chạy lại nhưng **bị treo/rất chậm** ở bước re-MERGE Persons (vì data đã tồn tại, MERGE phải check từng node).
- **Đã kill script** để tránh lãng phí thời gian.

## 3. Việc cần làm tiếp (TODO)

### Cách 1: Clear DB rồi chạy lại 1 lần sạch
```cypher
-- Chạy trong cypher-shell hoặc Neo4j Browser (localhost:7474)
MATCH (n) DETACH DELETE n;
```
Sau đó chạy lại: `python report/pre_process_data/deploy_new_ontology_v4.py`

### Cách 2: Tối ưu script (nếu vẫn chậm)
- Tăng batch_size từ 1000 → 5000.
- Dùng `session.execute_write()` thay vì `session.run()` để có explicit transaction.
- Thêm `CALL { ... } IN TRANSACTIONS OF 5000 ROWS` (Neo4j 5.x feature).
- Cân nhắc dùng `neo4j-admin database import` cho lần nạp đầu tiên (nhanh nhất).

## 4. Trạng thái hiện tại của Neo4j Docker
- Container: `fraud_neo4j` (neo4j:5.12.0) — **đang chạy**.
- Credentials: `neo4j / password`.
- Ports: `7474` (HTTP Browser), `7687` (Bolt).
- Data: Chỉ có Persons/Contracts/BankAccounts. Claims/Expenses/Benefits **chưa nạp**.
