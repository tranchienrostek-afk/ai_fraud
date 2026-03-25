# Agent Design Document: The Case Manager (Orchestrator)

## 1. Role & Identity

- **Name:** The Case Manager (Trưởng Nhóm Điều Tra)
- **Layer:** Orchestration Layer (Lớp Điều Phối)
- **Type:** Controller / Workflow Engine
- **Persona:** A pragmatic team leader who assigns work, gathers reports, and makes the final call.

## 2. Goals

- **Primary Goal:** Coordinate the 5 specialized agents to process claims efficiently.
- **Secondary Goal:** Handle errors, retries, and data routing between agents.
- **Success Metric:** Throughput (Claims processed per minute) and System Stability (Zero dropped claims).

## 3. Workflow Logic (The "Sieve" Strategy)

### 3.1. Phase 1: The Gatekeeper (Sequential)

- **Action:** Send Claim -> **Agent 01**.
- **Decision:**
  - _IF_ `REJECT` -> **STOP**. Notify User immediately.
  - _IF_ `PASS` -> **CONTINUE** to Phase 2.

### 3.2. Phase 2: The Deep Dive (Parallel)

- **Action:** Send Claim details **simultaneously** to:
  - **Agent 02 (Graph)** -> Get `Graph_Score`.
  - **Agent 03 (Anomaly)** -> Get `Anomaly_Score`.
- **Synchronization:** Wait for BOTH to finish. (Timeout: 5 seconds).

### 3.3. Phase 3: The Verdict (Sequential)

- **Action:** Aggregate outputs from Phase 2 + Original Data -> Send to **Agent 04 (Scoring)**.
- **Decision:**
  - **Low Risk (0-20):** Auto-Approve. -> **STOP**.
  - **High Risk (>20):** Forward to Phase 4.

### 3.4. Phase 4: The Explanation (Sequential)

- **Action:** Send full context (Scores + Features) -> **Agent 05 (Narrator)**.
- **Output:** Generate "Investigation Report".
- **Final Action:** Push Report + Claim to Human Review Queue.

## 4. Tools & Technology (Implementation)

- **Workflow Engine:**
  - **Prefect / Airflow:** Heavyweight, good for batch processing.
  - **LangGraph:** Lightweight, code-first, good for agentic workflows.
- **Message Queue:** RabbitMQ / Kafka / Redis (for buffering high-volume claims).

## 5. Conflict Resolution

- _Scenario:_ Agent 02 says "High Risk" (Graph Link) but Agent 03 says "Low Risk" (Normal Behavior).
- _Strategy:_ **Preserve the Risk**. The Orchestrator forwards _all_ conflicting signals to Agent 04. Agent 04's trained model decides which signal is more important. The Orchestrator does _not_ override expert agents.

## 6. System Architecture Diagram (Text-based)

```mermaid
graph TD
    User[User / Mobile App] -->|Submit Claim| Orch[**Orchestrator**]

    Orch -->|1. Validate| A1[Agent 01: Gatekeeper]
    A1 -->|Reject| User
    A1 -->|Pass| Orch

    Orch -->|2. Analyze (Parallel)| A2[Agent 02: Graph]
    Orch -->|2. Analyze (Parallel)| A3[Agent 03: Anomaly]

    A2 -->|Graph Score| Orch
    A3 -->|Anomaly Score| Orch

    Orch -->|3. Calculate Risk| A4[Agent 04: Scoring]
    A4 -->|Final Score| Orch

    Orch -->|Decision?| Check{Score > Threshold?}
    Check -->|No| Approve[Auto-Approve / Payment]
    Check -->|Yes| A5[Agent 05: Narrator]

    A5 -->|Explanation| Human[Human Investigator]
```
