# Agent Design Document: The Scoring Judge (Agent 04)

## 1. Role & Identity

- **Name:** The Actuary (Nhà Định Phí / Thẩm Phán)
- **Layer:** Layer 4 - Risk Scoring & Aggregation (Bộ lọc Chấm điểm)
- **Type:** Supervised Learning / Ensemble Model
- **Persona:** A cold, calculating judge who weighs all evidence to deliver a final verdict (score).

## 2. Goals

- **Primary Goal:** Quantify the risk into a single actionable number: **Fraud Score**.
- **Secondary Goal:** Rank claims by priority for human investigators (triage).
- **Success Metric:** Precision/Recall (AUC-ROC) of the final score against confirmed fraud labels.

## 3. Input Data (The "Evidence")

- **From Agent 02:** `Graph_Risk_Score`, `Community_Size`, `PageRank_Centrality`.
- **From Agent 03:** `Anomaly_Score`, `Cost_Deviation_Z_Score`, `Semantic_Mismatch_Score`.
- **Raw Features:** `Claim_Amount`, `Time_Since_Policy_Start`, `Claim_Frequency`.

## 4. Key Functions & Logic

### 4.1. Feature Engineering

Create "Golden Features" that predict fraud highly:

- **"Golden Period":** Time diff between Policy Start Date and First Claim Date. (Fraudsters often claim immediately after the waiting period).
- **"Velocity":** Number of claims in the last 30 days.
- **Ratio Features:** (Claimed Amount / Policy Limit).

### 4.2. Scoring Model (The Brain)

Train a Supervised Learning model on historical labelled data (Fraud vs. Non-Fraud):

- **Algorithm:** Gradient Boosting (XGBoost / LightGBM / CatBoost).
- **Why?** Handling non-linear relationships and tabular data best.
- **Logic:**
  $$ FinalScore = w_1 \cdot GraphFeatures + w_2 \cdot AnomalyFeatures + w_3 \cdot BehavioralFeatures $$

### 4.3. Risk Classification

Map the continuous score (0.0 - 1.0) to decision buckets:

- **0 - 20:** Safe (Auto-Approve).
- **21 - 60:** Low Risk (Random Audit).
- **61 - 85:** High Risk (Manual Review).
- **86 - 100:** Critical (Immediate Investigation).

## 5. Tools & Technology

- **ML Framework:** XGBoost, LightGBM, Scikit-learn.
- **Feature Store:** Feast (to serve real-time features like "user_claims_last_24h").
- **Model Registry:** MLflow.

## 6. Actions & Interface

- **Output:** A JSON object containing:
  ```json
  {
    "claim_id": "C-12345",
    "final_fraud_score": 88,
    "risk_level": "CRITICAL",
    "contributing_factors": ["Graph_Cluster_High", "Cost_Anomaly_Extreme"]
  }
  ```
- **Forwarding:** Sends this package to **Agent 05 (The Narrator)**.

## 7. Example Scenarios

- **Scenario 1:**
  - Graph Score: Med.
  - Anomaly Score: Low.
  - Policy Check: OK.
  - **Result:** Score = 35 (Low Risk) -> **Pass**.
- **Scenario 2:**
  - Graph Score: High (Linked to blacklist).
  - Anomaly Score: High (Strange diagnosis).
  - **Result:** Score = 95 (Critical) -> **BLOCK & REPORT**.
