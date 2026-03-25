# Agent Design Document: The Explainable Interpreter (Agent 05)

## 1. Role & Identity

- **Name:** The Narrator (Người Giải Thích)
- **Layer:** Layer 5 - Explainability & Decision Support (Bộ lọc Giải thích)
- **Type:** XAI (Explainable AI) + NLG (Natural Language Generation)
- **Persona:** A translator who converts complex math and matrix operations into plain, human language.

## 2. Goals

- **Primary Goal:** Explain _WHY_ the system gave a specific score.
- **Secondary Goal:** Support the Human Investigator in making a final decision (Accept/Reject).
- **Success Metric:** Time-to-resolution for human investigators (faster understanding = faster closing).

## 3. Input Data

- **From Agent 04:** `Final_Fraud_Score`, Model Object (XGBoost), Feature Vector.
- **Context:** Raw claim details (names, dates) to make the text readable.

## 4. Key Functions & Logic

### 4.1. Feature Attribution (XAI)

Calculate the contribution of each feature to the final score:

- **Technique:** SHAP (SHapley Additive exPlanations) or LIME.
- **Logic:**
  - "Base Rate" risk is 2%.
  - This claim is 88%. Why?
  - +40% because "Linked inside a Fraud Ring" (Graph).
  - +30% because "Diagnosis-Cost Mismatch" (Anomaly).
  - +16% because "Claimed 1 day after policy active" (Rule).

### 4.2. Natural Language Generation (NLG)

Convert SHAP values into a narrative:

- **Template-based:** "The risk is high because [Feature A] is [Value]."
- **LLM-based:** Use a small LLM (e.g., Llama-3, GPT-4o-mini) to write a summary paragraph.
  - _Prompt:_ "Act as a senior investigator. Explain why this claim is flagged using these top 3 risk factors..."

## 5. Tools & Technology

- **XAI Libraries:** SHAP (Python), ELI5.
- **LLM:** OpenAI API, Anthropic Claude, or local Llama.
- **Dashboard:** Streamlit or React frontend to display the "Why".

## 6. Actions & Interface

- **Output:** A Human-Readable Report (Markdown/PDF).
- **Format:**
  1.  **Headline:** "CRITICAL ALERT - Score 92/100"
  2.  **Summary:** "This claim is highly suspicious due to significant organized activity and pricing anomalies."
  3.  **Top Factors:**
      - 🔴 **Network:** Shared IP with 5 banned accounts.
      - 🔴 **Behavior:** Treatment cost is 5x standard deviation.
      - 🟠 **Timing:** Claim submitted at 3:00 AM.
- **Action:** Push to "Investigator Queue" or "Auto-Decline Email System" (if confidence is 99%).

## 7. Example Scenarios

- **Scenario:** The system flags a claim with Score 78.
  - **Agent 05 Output:** "Hồ sơ này bị nghi ngờ 78% chủ yếu do yếu tố Mạng Lưới (Graph). Mặc dù đơn thuốc hợp lý (Anomaly Score thấp), nhưng bác sĩ kê đơn lại nằm trong danh sách đen các bác sĩ thường xuyên tiếp tay trục lợi. Đề nghị kiểm tra xác minh trực tiếp với bác sĩ."
