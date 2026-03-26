# Hệ thống AI Phát hiện Trục lợi Bảo hiểm Đa tầng (Multi-layered Fraud Detection System)

## 1. Giới thiệu: Luôn đi trước gian lận một bước

**AZINSU AI FRAUD** được định vị như một lớp phòng vệ chủ động trong quy trình bồi thường, sử dụng phân tích dữ liệu, nhận diện hành vi và phân tích liên kết để phát hiện sớm các dấu hiệu bất thường trong hồ sơ yêu cầu chi trả.

### Năng lực cốt lõi:
- **Phát hiện đa tầng:** Nhận diện một cách hệ thống và chính xác các trường hợp trùng lặp hồ sơ theo chuỗi thời gian và hành vi sử dụng dịch vụ.
- **Kiểm soát chi phí:** Phát hiện các khoản chi phí kê khai không phù hợp với phác đồ điều trị, mặt bằng chi phí thị trường cũng như quyền lợi hợp đồng. 
- **Cảnh báo sớm:** Theo dõi tần suất sử dụng dịch vụ được triển khai liên tục giúp cảnh báo sớm các trường hợp phát sinh hồ sơ bất thường. 
- **Phân tích liên kết (Graph Analysis):** Bóc tách các mối quan hệ tiềm ẩn giữa khách hàng, cơ sở y tế và các bên liên quan, qua đó nhận diện các dấu hiệu trục lợi có tổ chức.

Nhờ đó, việc phát hiện nguy cơ gian lận không còn phụ thuộc chủ yếu vào phán đoán thủ công, mà được thực hiện một cách có hệ thống, nhất quán và dựa trên dữ liệu.

---

## 2. Kiến trúc 5 Lớp Lọc (The 5-Layer Sieve)

Hệ thống xử lý hồ sơ yêu cầu bồi thường (Claim) qua 5 lớp lọc tuần tự và song song:

### 🛡️ Lớp 1: Bộ lọc Quy tắc & Vệ sinh (Rule-based Gatekeeper)

- **Nhiệm vụ:** Loại bỏ các hồ sơ không hợp lệ về mặt hành chính hoặc lỗi sơ đẳng ("Honest Mistakes").
- **Hành động:** Trả lại hồ sơ kèm hướng dẫn sửa lỗi ngay lập tức thay vì từ chối.
- **Đại diện:** [Agent 01 - The Gatekeeper](all_filter/agent_filter_01.md)

### 🕸️ Lớp 2: Bộ lọc Mạng lưới (Graph Detective)

- **Nhiệm vụ:** Phát hiện các đường dây trục lợi có tổ chức (Organized Fraud) bằng cách tìm kiếm các mối quan hệ ẩn.
- **Công nghệ:** Graph Database (Neo4j), Community Detection.
- **Đại diện:** [Agent 02 - The Connector](all_filter/agent_filter_02.md)

### 📊 Lớp 3: Bộ lọc Bất thường (Anomaly Hunter)

- **Nhiệm vụ:** Tìm kiếm các hành vi "lạ", hiếm gặp hoặc chưa từng có tiền lệ (Unknown Unknowns).
- **Công nghệ:** Unsupervised Learning (Isolation Forest), NLP.
- **Đại diện:** [Agent 03 - The Profiler](all_filter/agent_filter_03.md)

### ⚖️ Lớp 4: Bộ lọc Chấm điểm (Scoring Judge)

- **Nhiệm vụ:** Tổng hợp tất cả tín hiệu từ các lớp trước để tính toán một con số rủi ro duy nhất (Fraud Score).
- **Công nghệ:** Gradient Boosting (XGBoost/LightGBM).
- **Đại diện:** [Agent 04 - The Actuary](all_filter/agent_filter_04.md)

### 🗣️ Lớp 5: Bộ lọc Giải thích (Explainable Interpreter)

- **Nhiệm vụ:** Giải thích lý do tại sao AI đưa ra quyết định đó bằng ngôn ngữ tự nhiên, giúp con người ra quyết định cuối cùng.
- **Công nghệ:** XAI (SHAP), LLM (GenAI).
- **Đại diện:** [Agent 05 - The Narrator](all_filter/agent_filter_05.md)

---

## 3. Điều phối Quy trình (Orchestration)

Toàn bộ quy trình được điều phối bởi một **Agent Orchestrator** (Trưởng nhóm điều tra), đảm bảo dữ liệu chạy đúng luồng, xử lý lỗi và đồng bộ hóa kết quả từ các Agent con.

- 👉 Xem chi tiết thiết kế: [Agent Orchestrator](all_filter/agent_orchestrator.md)
- 👉 Xem kịch bản chạy mẫu: [Workflow Simulation](all_filter/workflow.md)

## 4. Công nghệ Sử dụng (Tech Stack)

- **Core Logic:** Python
- **Database:** PostgreSQL (Transactional), Neo4j (Graph), Feast (Feature Store).
- **AI/ML:** Scikit-learn, XGBoost, PyTorch, LangGraph (hoặc Airflow).
- **LLM:** OpenAI API / Llama 3 (cho phần giải thích).

## 5. Hướng dẫn Sử dụng Tài liệu

Thư mục `all_filter/` chứa các tài liệu "Agent Design Document" chi tiết cho từng thành phần. Đây là bản thiết kế kỹ thuật (Blueprints) để đội ngũ kỹ sư có thể bắt tay vào code hoặc cấu hình Agent.

1.  Đọc file [workflow.md](all_filter/workflow.md) để hiểu bức tranh toàn cảnh.
2.  Xem sơ đồ hệ thống: [Sơ đồ Kiến trúc Nội bộ](system_diagram.md).
3.  Đi sâu vào từng `agent_filter_xx.md` để xem logic chi tiết (Input/Output/Algorithms).

## 6. Hướng dẫn Kích hoạt Hệ thống

### Yêu cầu

- Docker & Docker Compose đã được cài đặt.
- Tài khoản Azure OpenAI (đã cấu hình trong `.env`).

### Các bước triển khai

1.  **Khởi tạo cơ sở dữ liệu & Backend:**

    ```bash
    docker-compose up -d --build
    ```

    Lệnh này sẽ khởi chạy 4 container: `postgres` (SQL), `neo4j` (Graph), `qdrant` (Vector), và `app` (Python Backend).

2.  **Truy cập hệ thống:**
    - **Backend API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
    - **Frontend Dashboard:** [http://localhost:8501](http://localhost:8501)
    - **Neo4j Manager:** [http://localhost:7474](http://localhost:7474) (User: neo4j / Pass: password)

3.  **Kịch bản Demo:**
    - Truy cập Dashboard tại port 8501.
    - Nhập thông tin hồ sơ bảo hiểm giả định.
    - Nhấn "Analyze Claim" để xem 5 Agent hoạt động và trả về điểm số rủi ro cùng lời giải thích.
# ai_fraud
