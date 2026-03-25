# 🏥 HƯỚNG DẪN VẬN HÀNH HỆ THỐNG FRAUD DETECTION (SIU)

## 1. Khởi động Cơ sở dữ liệu Neo4j (Docker)
Neo4j chạy trong Docker container tên là `fraud_neo4j`. Phải bật Neo4j trước khi chạy server.

```bash
# Kiểm tra trạng thái container
docker ps -a --filter name=fraud_neo4j

# Khởi động Neo4j
docker start fraud_neo4j

# Xem log để biết khi nào Neo4j sẵn sàng
docker logs -f fraud_neo4j
```
*Đợi đến khi thấy log báo: `Bolt enabled on 0.0.0.0:7687`.*

## 2. Khởi động Dashboard Server (FastAPI)
Server nằm trong thư mục `deep_research/dashboard`.

```bash
cd deep_research/dashboard
python app.py
```
*Mặc định server chạy tại: [http://127.0.0.1:5000](http://127.0.0.1:5000)*

## 3. Kiểm tra Hệ thống (Validation)

### Kiểm tra API bằng Curl:
```bash
# Kiểm tra danh sách quy tắc kiểm soát
curl -s http://127.0.0.1:5000/api/audit-rules | python -m json.tool

# Kiểm tra Radar rủi ro (Thay {user_id} bằng ID thật)
curl -s http://127.0.0.1:5000/api/person-risk-radar/{user_id}
```

## 4. Các lưu ý quan trọng khi Code
- **Neo4j Port**: 7687 (Bolt).
- **App Port**: 5000 (FastAPI).
- **Lỗi 500**: Thường do Cypher Query sai cú pháp hoặc lỗi ngoặc nhọn `{}` khi dùng f-string trong Python. Luôn bọc ngoặc nhọn đúp `{{ }}` cho Cypher maps.
- **Index**: Nếu query chậm, hãy kiểm tra xem các Index đã được tạo chưa (Rule 11-15 cần index `claim_id`, `claim_date`, `visit_date`).

## 5. Cấu trúc Thư mục SIU
- `app.py`: Backend chính & 15 luật Fraud SIU.
- `static/js/charts.js`: Logic vẽ Radar Chart & ECharts.
- `static/js/app.js`: Logic drill-down & gọi API.
