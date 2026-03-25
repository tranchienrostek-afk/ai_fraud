# Agent Design Document: The Gatekeeper (Agent 01)

## 1. Role & Identity

- **Name:** The Gatekeeper (Người Gác Cổng)
- **Layer:** Layer 1 - Rule-based & Hygiene Filter (Bộ lọc Quy tắc & Vệ sinh)
- **Type:** Deterministic / Rule-based System
- **Persona:** A strict but helpful administrative clerk who catches silly mistakes before they become problems.

## 2. Goals

- **Primary Goal:** Filter out "noise" and "honest mistakes" (errors due to clumsiness, not malice).
- **Secondary Goal:** Educate users to fix their own errors immediately, reducing the load for downstream complex agents.
- **Success Metric:** % of invalid applications rejected _before_ reaching the database.

## 3. Input Data

- **Documents:** Identification cards, Medical invoices, Prescriptions, Claim forms.
- **Format:** Images (JPG/PNG), PDFs, or structured JSON (if submitted via app).
- **Context:** Application timestamp, User ID.

## 4. Key Functions & Logic

### 4.1. OCR & Data Extraction

Extract text from images/PDFs into structured fields:

- `patient_name`, `dob`, `policy_number`
- `hospital_name`, `admission_date`, `discharge_date`
- `diagnosis`, `total_amount`

### 4.2. Validation Rules (The "Sieve")

Apply rigid "IF-THEN" rules:

1.  **Completeness Check:**
    - _IF_ `missing_mandatory_field` (e.g., no signature, no date) -> _THEN_ `REJECT`.
2.  **Temporal Logic Check:**
    - _IF_ `discharge_date` < `admission_date` -> _THEN_ `REJECT`.
    - _IF_ `admission_date` < `policy_start_date` (Pre-existing condition exclusion period) -> _THEN_ `FLAG`.
3.  **Financial Logic Check:**
    - _IF_ `claim_amount` > `policy_max_limit` -> _THEN_ `REJECT`.
4.  **Fuzzy Matching (Typos):**
    - usage of `TheFuzz` library to match `hospital_name` against a master list of accredited hospitals.
    - _IF_ match score < 80% but > 50% -> _THEN_ `SUGGEST_CORRECTION`.

## 5. Tools & Technology

- **OCR:** Tesseract, Google Cloud Vision, or Azure Form Recognizer.
- **Rule Engine:** EasyRules (Java), Drools, or Python `rule-engine` library.
- **Fuzzy Logic:** `TheFuzz` (Python) or Levenshtein distance algorithms.

## 6. Actions & Interface

- **Action A: Immediate Rejection with Education**
  - _Trigger:_ Logic error found (e.g., Start Date > End Date).
  - _Output:_ Friendly error message: "Oops! It looks like your discharge date is _before_ your admission date. Please check the calendar and try again."
- **Action B: Pass Forward**
  - _Trigger:_ All rules passed.
  - _Output:_ Structured JSON object forwarded to **Agent 02 (The Connector)**.

## 7. Example Scenarios

- **Scenario 1 (Honest Mistake):** User uploads a bill where the date is "02/30/2023" (invalid date).
  - _Result:_ Gatekeeper catches it -> Asks user to re-upload.
- **Scenario 2 (Valid):** User uploads a complete file.
  - _Result:_ Gatekeeper validates -> Forwards to Layer 2.
