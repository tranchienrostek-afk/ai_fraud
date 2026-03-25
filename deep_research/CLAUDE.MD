# CLAUDE.md — Hướng dẫn Dự án Fraud Detection

Dự án này là hệ thống phân tích và phát hiện trục lợi bảo hiểm (Fraud Detection) sử dụng Python (FastAPI) và cơ sở dữ liệu đồ thị Neo4j. Giao diện người dùng được xây dựng bằng HTML/CSS/JS thuần với ECharts và Cytoscape.js.

## Công nghệ sử dụng (Tech Stack)
- **Backend**: FastAPI (Python 3.9+)
- **Database**: Neo4j (Graph Database)
- **Frontend**: Vanilla HTML/CSS/JS
- **Visualization**: ECharts (Biểu đồ), Cytoscape.js (Đồ thị mạng lưới)
- **Server**: Uvicorn

## Cấu trúc thư mục Chính
- `/dashboard`: Chứa mã nguồn của Dashboard
    - `/static`: HTML, CSS, JS
    - `app.py`: FastAPI server & Neo4j queries
- `/deep_research`: Chứa các script nghiên cứu, data splits và kết quả phân tích

## Quy tắc Code (Coding Standards)
- **Ngôn ngữ**: Toàn bộ UI và nhãn dữ liệu phải sử dụng **Tiếng Việt có dấu**.
- **Naming**: Sử dụng `snake_case` cho Python và `camelCase` cho JavaScript.
- **Diacritics**: Đảm bảo sử dụng đúng bảng mã UTF-8 để hiển thị tiếng Việt không bị lỗi.
- **FastAPI**: Sử dụng `cached_query` cho các truy vấn Neo4j nặng để tối ưu hiệu năng.

## Lệnh thông dụng
- **Bật Server**: `cd dashboard && uvicorn app:app --host 0.0.0.0 --port 8000 --reload`
- **Kiểm tra trạng thái**: `claude -c` (Lệnh của người dùng)
