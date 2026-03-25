# FINAL SIU-Standard Implementation Plan (v4)

## 1. Production Cypher Engine (app.py)

### 11_Premium_Claim_Ratio (CRITICAL)

```cypher
MATCH (p:Person)-[:HAS_CONTRACT]->(cont:Contract)
WITH p, sum(coalesce(cont.premium_paid, 0)) AS total_premium
OPTIONAL MATCH (p)-[:FILED_CLAIM]->(c:Claim)
WITH p, total_premium, sum(coalesce(c.claim_amount_approved, 0)) AS total_payout
WHERE total_premium > 0 AND total_payout > 5 * total_premium
RETURN p.user_id AS user_id, p.full_name AS ho_ten,
       round(total_premium) AS tong_phi,
       round(total_payout) AS tong_boi_thuong,
       round(total_payout * 1.0 / total_premium, 1) AS ti_le_boi_thuong
ORDER BY ti_le_boi_thuong DESC LIMIT 100
```

### 12_Treatment_Duration_Outlier (HIGH)

_Scoping fix: median_duration carried via WITH._

```cypher
MATCH (c:Claim)-[:DIAGNOSED_WITH]->(d:Diagnosis)
WHERE c.treatment_duration_days IS NOT NULL
WITH d.icd_name AS pathology, collect(c.treatment_duration_days) AS durations
WITH pathology, percentileCont(durations, 0.5) AS median_duration
MATCH (c:Claim)-[:DIAGNOSED_WITH]->(d:Diagnosis)
WHERE d.icd_name = pathology
  AND c.treatment_duration_days > 3 * median_duration
  AND c.treatment_duration_days > 2
RETURN c.claim_id AS claim_id, pathology,
       c.treatment_duration_days AS duration,
       round(median_duration, 1) AS median_per_diag
ORDER BY duration DESC LIMIT 100
```

### 13_High_Exclusion_Ratio (HIGH) - [REINSTATED]

```cypher
MATCH (c:Claim)-[:HAS_EXPENSE]->(e:ExpenseDetail)
WITH c, sum(coalesce(e.total_amount, 0)) AS total,
     sum(coalesce(e.exclusion_amount, 0)) AS excluded
WHERE total > 0 AND (excluded * 1.0 / total) > 0.5
RETURN c.claim_id AS claim_id, round(total) AS tong_tien,
       round(excluded) AS mien_thuong,
       round((excluded * 100.0 / total), 1) AS ti_le_tu_choi_pct
ORDER BY ti_le_tu_choi_pct DESC LIMIT 100
```

### 14_Expired_Contract_Claim (CRITICAL)

```cypher
MATCH (p:Person)-[:HAS_CONTRACT]->(cont:Contract), (p)-[:FILED_CLAIM]->(c:Claim)
WHERE date(c.claim_date) > date(cont.contract_end_date)
RETURN p.user_id AS user_id, p.full_name AS ho_ten,
       c.claim_id AS claim_id, toString(date(cont.contract_end_date)) AS ngay_het_han,
       toString(date(c.claim_date)) AS ngay_kham
LIMIT 100
```

### 15_Claim_Filing_Delay (HIGH)

```cypher
MATCH (c:Claim)
WHERE c.visit_date IS NOT NULL AND c.claim_date IS NOT NULL
WITH c, date(c.visit_date) AS d_visit, date(c.claim_date) AS d_claim
WITH c, d_visit, d_claim, duration.inDays(d_visit, d_claim).days AS delay
WHERE delay > 90 OR delay < 0
RETURN c.claim_id AS claim_id, toString(d_visit) AS ngay_kham,
       toString(d_claim) AS ngay_nop, delay AS so_ngay_tre
ORDER BY delay DESC LIMIT 100
```

## 2. Risk Radar & Composite Logic (Python)

### Zero-Safety Normalization

- **Petty**: `0 if total == 0 else max(0, min(100, (petty/total)*100))`
- **Loss**: `max(0, min(100, (payout / (premium + 1)) * 20))`
- **Duration**: `max(0, min(100, (avg_duration / 5) * 33))`
- **Delay**: `max(0, min(100, (avg_delay / 90) * 100))`

### api_top_suspects Update

- Integrate `premium_paid` ratio and `treatment_duration` outliers into the final risk score calculation.

## 3. SIU Performance Index Strategy

```cypher
CREATE INDEX FOR (c:Claim) ON (c.claim_id);
CREATE INDEX FOR (c:Claim) ON (c.claim_date);
CREATE INDEX FOR (c:Claim) ON (c.visit_date);
CREATE INDEX FOR (c:Claim) ON (c.treatment_duration_days);
CREATE INDEX FOR (c:Claim) ON (c.claim_amount_approved);
CREATE INDEX FOR (cont:Contract) ON (cont.contract_end_date);
CREATE INDEX FOR (p:Person) ON (p.user_id);
CREATE INDEX FOR (d:Diagnosis) ON (d.icd_name);
CREATE INDEX FOR (e:ExpenseDetail) ON (e.claim_id);
```

## 4. Implementation Sequence

1. **Phase 1: DB**: Create all 9 Indices.
2. **Phase 2: Backend**: Implement 15 Rules (re-adding rule 13) + Update Suspect score logic.
3. **Phase 3: Radar API**: Create `/api/person-risk-radar` with normalization safety.
4. **Phase 4: Frontend**: Update [index.html](file:///D:/desktop_folder/04_Fraud_Detection/deep_research/dashboard/static/index.html) (Modal/Radar), [js/charts.js](file:///D:/desktop_folder/04_Fraud_Detection/deep_research/dashboard/static/js/charts.js) (Radar render), and [js/app.js](file:///D:/desktop_folder/04_Fraud_Detection/deep_research/dashboard/static/js/app.js) (Drill-down integration).
