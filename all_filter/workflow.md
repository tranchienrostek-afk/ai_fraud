# Master Workflow: The "Multi-Layered Sieve"

## Overview

This document describes the end-to-end flow of a single insurance claim streaming through the 5-Agent Fraud Detection System.

## Step-by-Step Execution

### 1. Ingestion (T=0s)

- **User Action:** Submits a claim via Mobile App.
- **Data:** Photo of invoice, diagnosis "Dengue Fever", amount "5,000,000 VND".
- **System State:** `Status: PENDING`.

### 2. Layer 1: Hygiene Check (T+0.5s)

- **Orchestrator -> Agent 01 (Gatekeeper)**
- **Check:** Is OCR readable? Are dates valid? Is policy active?
- **Result:** dates are valid. Policy is active.
- **Outcome:** `PASS`.

### 3. Layer 2 & 3: Deep Analysis (T+2.0s)

- **Orchestrator -> Broadcasts to Agent 02 & Agent 03**
  - **Agent 02 (Graph):**
    - _Finding:_ Phone number `090...` is linked to 3 other claims rejected last month.
    - _Output:_ `Graph_Risk = 85`.
  - **Agent 03 (Anomaly):**
    - _Finding:_ Cost of 5M VND is within 1-sigma of "Dengue Fever" average (4.5M VND).
    - _Output:_ `Anomaly_Risk = 15` (Low).

### 4. Layer 4: Scoring (T+2.5s)

- **Orchestrator -> Agent 04 (Scoring)**
- **Input:**
  - Graph = 85 (High)
  - Anomaly = 15 (Low)
  - Rule = Pass
- **Model Calculation:** XGBoost weights Graph connections higher than mild cost deviations.
- **Result:** `Final_Fraud_Score = 78`.
- **Category:** `HIGH RISK` (Threshold is 60).

### 5. Layer 5: Explanation (T+3.0s)

- **Orchestrator -> Agent 05 (Narrator)**
- **Task:** Explain Score 78.
- **Drafting Report:**
  - _Top Driver:_ Link to suspicious phone number (+50 points).
  - _Secondary Driver:_ New account (< 3 months) (+10 points).
  - _Mitigating Factor:_ Cost is reasonable (-5 points).
- **Final Output:** "Cảnh báo: Hồ sơ có liên kết rủi ro cao. Số điện thoại người yêu cầu trùng với các hồ sơ trục lợi đã bị từ chối trước đây (nhóm sự kiện tháng 10). Mức chi phí hợp lý nhưng cần xác minh danh tính người thụ hưởng."

### 6. Final Disposition (T+3.5s)

- **Orchestrator Action:**
  - Do NOT auto-pay.
  - Route claim to **"Priority Investigation Queue"**.
  - Append **Agent 05's Report** to the case file.
  - Send notification to User: "Hồ sơ của bạn đang được xem xét kỹ hơn, vui lòng chờ 24h."

---

## Failure Modes & Recovery

| Failure                                     | Response                                                                                                                  |
| :------------------------------------------ | :------------------------------------------------------------------------------------------------------------------------ |
| **Agent 01 crashes/times out**              | **Fail Open:** Log error, but tentatively accept ingestion to avoid blocking user. Flag for manual review.                |
| **Agent 02 (Graph) is slow**                | **Timeout (3s):** Orchestrator proceeds with `Graph_Score = NULL` (Neutral). Note "Graph Unavailable" in logs.            |
| **Agent 04 predicts LOW Score for a Fraud** | **False Negative:** This is a model error. Feedback loop required from Human Investigators to retrain Agent 04 next week. |
