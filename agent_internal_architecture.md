# Kiến trúc Nội bộ Agent (Agent Internal Architecture)

Tài liệu này giải thích chi tiết cơ chế "Tự chủ - Chiến lược - Giao tiếp" (Autonomy - Strategy - Communication) của từng Agent trong hệ thống, trả lời câu hỏi: **Làm sao mỗi Agent biết việc của mình và lấy đúng dữ liệu?**

## 1. Nguyên tắc "Chủ quyền Dữ liệu" (Data Sovereignty)

Mỗi Agent được thiết kế như một **Microservice độc lập**. Chúng không truy cập trực tiếp vào database chung, mà sở hữu "Giác quan" (Sensors/Connectors) riêng biệt để tương tác với vùng dữ liệu đặc thù của mình.

| Agent                   | Vùng dữ liệu (Domain)         | Công cụ truy cập (Sensor)                  | Tại sao?                                                                      |
| :---------------------- | :---------------------------- | :----------------------------------------- | :---------------------------------------------------------------------------- |
| **01. Gatekeeper**      | **Administrative Data** (SQL) | `SQLAlchemy` (Postgres)                    | Cần sự chính xác tuyệt đối (ACID) cho thông tin hợp đồng, chính sách.         |
| **02. Graph Detective** | **Relational Data** (Graph)   | `Neo4j Driver` (Cypher)                    | Cần truy vấn mối quan hệ phức tạp (bạn của bạn) mà SQL không làm được.        |
| **03. Anomaly Hunter**  | **Semantic/Vector Data**      | `Qdrant Client` + `Azure OpenAI Embedding` | Cần so sánh độ tương đồng ngữ nghĩa (vector space) thay vì từ khóa chính xác. |
| **04. Scoring Judge**   | **Aggregated Features**       | `Internal Memory` (Input from Agents 2,3)  | Cần cái nhìn tổng quan từ các báo cáo con.                                    |
| **05. Narrator**        | **Context & Language**        | `Azure OpenAI Chat` (LLM)                  | Cần khả năng suy luận ngôn ngữ và tổng hợp thông tin.                         |

## 2. Chiến lược ReAct (Reasoning + Acting)

Hệ thống áp dụng triết lý **ReAct** để đảm bảo các Agent không trả lời rập khuôn mà có sự "suy ngẫm" và "tự điều chỉnh".

### Vòng lặp Tư duy (The Thinking Loop)

Thay vì quy trình tuyến tính (Input -> Output), các Agent thông minh (như Agent 05) sẽ duy trì vòng lặp:

1.  **Observation (Quan sát):** Nhìn dữ liệu từ các Agent con.
2.  **Thought (Suy luận):** "Số liệu này có gì mâu thuẫn không? Graph báo Cao nhưng Anomaly báo Thấp?"
3.  **Action (Hành động):** "Tôi cần kiểm tra lại ngưỡng rủi ro hoặc yêu cầu con người xác minh kỹ Graph."
4.  **Final Answer (Kết luận):** Đưa ra phán quyết sau khi đã cân nhắc các mâu thuẫn.

### Triển khai cụ thể trên từng Agent:

#### 🕵️ Agent 02: Graph Detective (Loop tìm kiếm sâu)

- **Thought:** Tìm thấy 1 kết nối trùng SĐT.
- **Refinement:** "Liệu đây là người thân hay đường dây trục lợi?" -> Tiếp tục quét các node liên quan đến SĐT đó (địa chỉ, email).
- **Result:** Nếu tìm thấy > 3 người khác họ cùng dùng SĐT -> Khẳng định là gian lận.

#### 🔮 Agent 03: Anomaly Hunter (Loop so sánh)

- **Thought:** Chi phí cao bất thường.
- **Refinement:** "Liệu có phải do bệnh viện Quốc tế không?" -> So sánh với peer group của bệnh viện đó.
- **Result:** Nếu vẫn cao hơn trung bình bệnh viện -> Khẳng định là bất thường.

#### 🗣️ Agent 05: The Narrator (Loop phản biện)

- **Thought:** Nhận được Score = 65 (Vùng xám).
- **Refinement:** "Tại sao lại lửng lơ? Graph rất cao nhưng Rule lại sạch."
- **Action:** Đặt trọng số cao hơn vào Graph vì tính chất tinh vi của nó.
- **Final Answer:** Đề xuất "High Risk" kèm giải thích: "Dù hồ sơ sạch về mặt hành chính, nhưng dấu hiệu mạng lưới quá rõ ràng để bỏ qua."

## 3. Giao tiếp với Người quản lý (Orchestration Protocol)

Để đảm bảo Orchestrator hiểu được "ngôn ngữ" của từng Agent chuyên biệt, hệ thống sử dụng một **Giao thức chuẩn (Standardized Protocol)**.

Mọi Agent bất kể logic bên trong phức tạp thế nào (`Graph`, `Vector`, `ML`), đều phải trả về kết quả dưới dạng JSON chuẩn:

```json
{
  "score": <float 0-100>,       // Mức độ rủi ro định lượng
  "reason": <string>,           // Lý do vắn tắt (cho máy đọc)
  "features": <dictionary>,     // Các đặc trưng chi tiết (bad_link_count, cluster_size...)
  "thought_process": <string>   // (Mới) Chuỗi suy luận ReAct để truy vết
}
```

---

## Tổng kết

Bằng cách tích hợp **ReAct**, hệ thống chuyển từ trạng thái "Máy tính toán vô tri" sang "Thám tử tư duy". Các Agent không chỉ trả về con số, mà còn trả về cả **quá trình suy luận**, giúp quyết định cuối cùng đạt độ chính xác "đỉnh cao" nhất.
