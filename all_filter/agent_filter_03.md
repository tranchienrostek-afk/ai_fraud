# Agent Design Document: The Anomaly Hunter (Agent 03)

## 1. Role & Identity

- **Name:** The Profiler (Chuyên Gia Hành Vi)
- **Layer:** Layer 3 - Unsupervised Anomaly Detection (Bộ lọc Bất thường)
- **Type:** Unsupervised Learning / Statistical Modeling
- **Persona:** A profiler who doesn't look for things that are "wrong", but things that are "weird" or "rare".

## 2. Goals

- **Primary Goal:** Detect "Unknown Unknowns" (new fraud schemes never seen before).
- **Secondary Goal:** Flag activities that statistically deviate from the norm (Outliers).
- **Success Metric:** Discovery of high-value fraud cases that bypassed Rules (Layer 1) and Graph (Layer 2).

## 3. Input Data

- **Historical Data:**
  - User's past claims history (frequency, amount, locations).
  - Peer Group data (similar age, location, policy type).
- **Current Claim Data:**
  - Detailed diagnosis codes (ICD-10), Prescription drugs, Treatment costs.

## 4. Key Functions & Logic

### 4.1. Semantic Anomaly Detection (NLP)

Compare textual/categorical data for consistency:

- **Technique:** Embedding clinical notes and diagnosis codes into vector space (e.g., Word2Vec, BERT).
- **Logic:** _Cosine Similarity_ check.
  - _Example:_ Diagnosis = "Flu" (mild) vs. Treatment = "Chemotherapy drugs" (severe).
  - _Result:_ Low similarity score -> **ANOMALY**.

### 4.2. Statistical Outlier Detection

Compare numerical values against distribution:

- **Technique:** Z-score, Interquartile Range (IQR).
- **Logic:**
  - _Input:_ Cost of "Appendectomy".
  - _Stats:_ Mean = $500, StdDev = $50.
  - _Current Claim:_ $2500 (Z-score = 40).
  - _Result:_ > 3 Sigma -> **ANOMALY**.

### 4.3. Behavioral Profiling (Time-Series)

Analyze patterns over time:

- **Technique:** Isolation Forest or LSTM Autoencoders.
- **Logic:**
  - _Normal Behavior:_ 1 claim/year.
  - _Sudden Burst:_ 5 claims in 1 week for different minor ailments.
  - _Result:_ Reconstruction Error High -> **ANOMALY**.

## 5. Tools & Technology

- **Unsupervised Learning:** Scikit-learn (Isolation Forest, One-Class SVM).
- **Deep Learning:** PyTorch/TensorFlow (Autoencoders for reconstruction error).
- **NLP:** HuggingFace Transformers (BioBERT for medical text).

## 6. Actions & Interface

- **Action A: High Probability Outlier**
  - _Trigger:_ Anomaly Score > Threshold (e.g., Top 1% of outliers).
  - _Output:_ `Anomaly_Risk_Score: HIGH`. Reason: "Cost mismatch with Diagnosis (99th percentile)."
- **Action B: Normal Variation**
  - _Trigger:_ Inside acceptable statistical bounds.
  - _Output:_ `Anomaly_Risk_Score: LOW` forwarded to **Agent 04 (Scoring Judge)**.

## 7. Example Scenarios

- **Scenario 1 (The Upcoding Doctor):**
  - Diagnosis: "Common Cold". Procedure codes billed: "Complex Respiratory Therapy".
  - **Agent 03:** "Semantically inconsistent. Cost is 500% higher than peer average." -> **FLAG**.
- **Scenario 2 (The Sunday Fraudster):**
  - User submits claim at 3:00 AM on a Sunday (statistically rare time for non-emergency admin tasks).
  - **Agent 03:** "Temporal anomaly detected." -> **FLAG (Weak signal)**.
