# System Architecture Diagram

This diagram visualizes the "Multi-Layered Sieve" architecture, data flows, and component interactions.

```mermaid
graph TD
    %% Nodes
    User(["👤 User / Mobile App"])
    FE["💻 Streamlit Frontend"]
    API["🚀 FastAPI Backend"]

    subgraph "Orchestration Layer"
        Orch["👮 Orchestrator"]
    end

    subgraph "Agent Layer"
        A1["🛡️ Agent 01: Gatekeeper"]
        A2["🕸️ Agent 02: Graph Detective"]
        A3["🔮 Agent 03: Anomaly Hunter"]
        A4["⚖️ Agent 04: Scoring Judge"]
        A5["🗣️ Agent 05: Narrator"]
    end

    subgraph "Data & Infrastructure"
        DB_SQL[("🗄️ PostgreSQL\nAdmin Data")]
        DB_Graph[("🕸️ Neo4j\nRelationships")]
        DB_Vector[("🧬 Qdrant\nEmbeddings")]
    end

    subgraph "Azure AI Services"
        Azure_Embed["🧠 Azure OpenAI\nEmbeddings"]
        Azure_Chat["💬 Azure OpenAI\nGPT-4o"]
    end

    %% Flows
    User -->|Submit Claim| FE
    FE -->|JSON Payload| API
    API -->|Process Request| Orch

    %% Layer 1
    Orch -->|"1. Validate"| A1
    A1 <-->|"Read/Write"| DB_SQL
    A1 -- Reject --> User
    A1 -- Pass --> Orch

    %% Layer 2 & 3 (Parallel)
    Orch -->|"2. Analyze"| A2
    Orch -->|"2. Analyze"| A3

    A2 <-->|"Query Patterns"| DB_Graph
    A3 <-->|"Semantic Search"| DB_Vector
    A3 <-->|"Get Vector"| Azure_Embed

    %% Layer 4
    A2 -- "Graph Score" --> Orch
    A3 -- "Anomaly Score" --> Orch
    Orch -->|"3. Aggregate"| A4
    A4 -->|"Calculate Risk"| Orch

    %% Layer 5
    Orch -->|"4. Explain (if High Risk)"| A5
    A5 <-->|"Generate Text"| Azure_Chat
    A5 -->|"Explanation"| Orch

    %% Final
    Orch -->|"Final Result"| API
    API -->|"Display Dashboard"| FE

    %% Styling
    classDef user fill:#f9f,stroke:#333,stroke-width:2px;
    classDef agent fill:#bbf,stroke:#333,stroke-width:2px;
    classDef db fill:#bfb,stroke:#333,stroke-width:2px;
    classDef ai fill:#fbb,stroke:#333,stroke-width:2px;

    class User,FE user;
    class A1,A2,A3,A4,A5,Orch agent;
    class DB_SQL,DB_Graph,DB_Vector db;
    class Azure_Embed,Azure_Chat ai;
```

## Giải thích luồng dữ liệu

1.  **Dữ liệu Hành chính (Tím)**: `Agent 01` đọc/ghi vào PostgreSQL để kiểm tra sự tồn tại của hợp đồng và lịch sử cơ bản.
2.  **Dữ liệu Quan hệ (Xanh lá)**: `Agent 02` truy vấn Neo4j để tìm các kết nối ẩn (bạn bè, người thân, thiết bị chung).
3.  **Dữ liệu Vector (Xanh lá)**: `Agent 03` gửi văn bản bệnh án lên Azure OpenAI để lấy vector, sau đó tìm kiếm trong Qdrant.
4.  **Dữ liệu Suy luận (Đỏ)**: `Agent 05` gửi toàn bộ ngữ cảnh (context) lên Azure GPT-4o để yêu cầu viết báo cáo giải thích.
