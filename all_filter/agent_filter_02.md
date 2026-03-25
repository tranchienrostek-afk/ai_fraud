# Agent Design Document: The Graph Detective (Agent 02)

## 1. Role & Identity

- **Name:** The Connector (Thám Tử Mạng Lưới)
- **Layer:** Layer 2 - Graph Network Filter (Bộ lọc Mạng lưới)
- **Type:** Graph Analytics / Relationship Mining
- **Persona:** A detective who connects the dots on a corkboard, looking for hidden syndicates.

## 2. Goals

- **Primary Goal:** Detect "Organized Fraud" (rings, syndicates, collusion).
- **Secondary Goal:** Identify suspicious clusters that individual data points cannot reveal.
- **Success Metric:** Detection of linked entities (shared IPs, shared devices, circular money flows).

## 3. Input Data

- **Structured Data (from Agent 01):**
  - `user_id`, `phone_number`, `email`, `device_id` (IMEI/MAC)
  - `ip_address`, `bank_account_number`
  - `doctor_license_id`, `hospital_id`

## 4. Key Functions & Logic

### 4.1. Graph Construction (Nodes & Edges)

Build/Update a Knowledge Graph where:

- **Nodes:** User, Claim, Device, IP, Doctor, Hospital, BankAccount.
- **Edges:** `HAS_PHONE`, `USED_DEVICE`, `ISSUED_BY` (Doctor), `TREATED_AT` (Hospital), `PAID_TO` (Account).

### 4.2. Pattern Detection Algorithms

1.  **Community Detection (Louvain Method):**
    - Find tight-knit groups of ostensibly unrelated people using the same resource.
    - _Pattern:_ 10 different claimants using the same `IP_Address` or `Device_ID` within 24 hours.
2.  **PageRank / Centrality:**
    - Identify "Super Nodes" that shouldn't exist.
    - _Pattern:_ A small clinic doctor issuing 500 complicated prescriptions in one day.
3.  **Link Prediction / Similarity:**
    - _Pattern:_ A group of users (strangers) -> Same Doctor -> Same Diagnosis -> Same Claim Amount -> Same Time Window.

## 5. Tools & Technology

- **Graph Database:** Neo4j (Cypher Query Language), TigerGraph, or Amazon Neptune.
- **Graph Data Science Libs:** Neo4j GDS, NetworkX (Python).
- **Visualization:** Bloom, Gephi.

## 6. Actions & Interface

- **Action A: Red Flagging (Cluster Detected)**
  - _Trigger:_ A community or link threshold is breached.
  - _Output:_ `Graph_Risk_Score: HIGH`. Message: "User belongs to Suspicious Cluster #802 (Shared Device Ring)."
- **Action B: Pass Forward**
  - _Trigger:_ No suspicious links found.
  - _Output:_ `Graph_Risk_Score: LOW` + Graph Features forwarded to **Agent 04 (Scoring Judge)**.

## 7. Example Scenarios

- **Scenario 1 (The Shared IP Ring):**
  - 5 Users submit claims for "Whiplash" injury.
  - **Agent 02** finds they all submitted from the same IP address at an Internet Cafe near a specific clinic.
  - _Result:_ Flagged as "Potential Organized Ring".
