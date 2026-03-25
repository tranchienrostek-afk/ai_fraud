# CLAUDE.md - Hướng dẫn Trợ lý AI cho Dự án Fraud Detection

Dự án này tập trung vào việc phát hiện trục lợi bảo hiểm bằng cách sử cấu trúc dữ liệu Graph (Neo4j) và các phân tích thống kê trên Python.

## 1. Ngữ cảnh & Mục tiêu (Context & Objectives)
- **Mục tiêu:** Làm sạch, quy đổi và phân tích dữ liệu bảo hiểm (Chi phí, Bồi thường, Người được bảo hiểm) để tìm ra các mô hình trục lợi.
- **Dữ liệu chính:**
  - `DataChiPhi`: Chi tiết từng hạng mục chi phí y tế.
  - `DataHoSoBoiThuong`: Thông tin tổng quan hồ sơ bồi thường.
  - `DataNDBH`: Thông tin nhân khẩu học người được bảo hiểm.
- **Lưu ý đặc biệt:** Đơn vị tiền tệ thường bị phóng đại hoặc thu nhỏ 100 lần (Scaling factor 100x).

## 2. Công nghệ (Tech Stack)
- **Ngôn ngữ:** Python (3.x).
- **Thư viện:** `pandas`, `numpy`, `matplotlib`, `seaborn`, `glob`, `os`.
- **Database:** Neo4j (Graph Database).
- **IDE:** Claude Code / Antigravity Agent.

## 3. Quy tắc Code & Naming (Coding Standards)
- **Naming Convention:**
  - Files: `snake_case` (ví dụ: `datamining_script.py`).
  - Variables/Columns: `snake_case`.
  - Encoding: Luôn sử dụng `utf-8-sig` khi đọc/ghi file CSV có chứa tiếng Việt.
- **Quy tắc Scaling (Quan trọng):**
  - Dữ liệu tài chính cần được đưa về đơn vị VND chuẩn.
  - Quy tắc hiện tại:
    - `Expenses`: `/ 100.0`.
    - `Claim Req`: `/ 100.0`.
    - `Claim Approved`: Giữ nguyên or `* 100.0` (Tùy thuộc vào việc khớp với Expenses).
    - `Vien phi`: `/ 100.0`.

## 4. Cấu trúc thư mục (Directory Structure)
- `D:\desktop_folder\04_Fraud_Detection\`
  - `report/`: Chứa các báo cáo phân tích (.md) và biểu đồ (.png).
    - `pre_process_data/`: Script xử lý và báo cáo kỹ thuật.
    - `cleaned_data_final/`: Dữ liệu đã làm sạch cuối cùng.
    - `new_data/`: Dữ liệu thô đầu vào.
  - `neo4j/`: Scripts liên quan đến database.

## 5. Workflow đề xuất
1. **Phân tích (Analyze):** Kiểm tra schema và mẫu dữ liệu (100-1000 dòng).
2. **Chẩn đoán (Diagnose):** Viết script `diag_*.py` để kiểm tra độ rỗng, scaling và phân bổ.
3. **Làm sạch (Clean):** Viết script `clean_*.py` hoặc `datamining_*.py` để chuẩn hóa.
4. **Báo cáo (Report):** Xuất file `.md` với các Alert (Note, Warning, Caution) và nhúng biểu đồ.

## 6. Lệnh thường dùng (Common Scripts)
- Chạy làm sạch bồi thường: `python report/pre_process_data/datamining_claims_v2.py`
- Chạy làm sạch NDBH: `python report/pre_process_data/clean_persons_final.py`
- Kiểm tra dung lượng/số dòng: `python -c "import pandas as pd; ..."`
