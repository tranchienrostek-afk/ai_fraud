"""
AZINSU - EDA Deep Analysis Script
Khai pha sau du lieu Neo4j: data quality, anomaly detection, network scoring.
Chay: python eda_deep_analysis.py
"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import pandas as pd
from neo4j import GraphDatabase
from datetime import datetime

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "Chien@2022"
NEO4J_DB = "neo4j"
TODAY = datetime.now().strftime("%Y%m%d")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

def q(cypher):
    records, _, _ = driver.execute_query(cypher, database_=NEO4J_DB)
    if not records:
        return pd.DataFrame()
    rows = []
    for r in records:
        row = {}
        for k in r.keys():
            v = r[k]
            if isinstance(v, list):
                v = " | ".join(str(x) for x in v)
            row[k] = v
        rows.append(row)
    return pd.DataFrame(rows)


# ═══════════════════════════════════════════════════════════════
# PHAN 1: DATA QUALITY REPORT
# ═══════════════════════════════════════════════════════════════

print("=" * 70)
print("  PHAN 1: DATA QUALITY AUDIT")
print("=" * 70)

# 1.1 Orphan analysis
df_orphan = q("""
    MATCH (c:Claim)
    OPTIONAL MATCH (p:Person)-[:SUBMITTED]->(c)
    OPTIONAL MATCH (c)-[:TREATED_AT]->(h:Hospital)
    OPTIONAL MATCH (c)-[:EXAMINED_BY]->(doc:Doctor)
    OPTIONAL MATCH (c)-[:PAID_TO]->(b:Bank)
    RETURN c.claim_id AS claim_id,
           c.amount AS amount,
           c.diagnosis AS diagnosis,
           CASE WHEN p IS NULL THEN 'MISSING' ELSE 'OK' END AS person_link,
           CASE WHEN h IS NULL THEN 'MISSING' ELSE 'OK' END AS hospital_link,
           CASE WHEN doc IS NULL THEN 'MISSING' ELSE 'OK' END AS doctor_link,
           CASE WHEN b IS NULL THEN 'MISSING' ELSE 'OK' END AS bank_link
""")

print("\n[1.1] Relationship Coverage:")
for col in ['person_link', 'hospital_link', 'doctor_link', 'bank_link']:
    counts = df_orphan[col].value_counts()
    ok = counts.get('OK', 0)
    miss = counts.get('MISSING', 0)
    total = ok + miss
    print(f"  {col:20s}: {ok:>6} OK ({ok*100/total:.1f}%) | {miss:>6} MISSING ({miss*100/total:.1f}%)")

# 1.2 Amount anomalies
print("\n[1.2] Amount Anomalies:")
amt = df_orphan['amount']
print(f"  Total claims: {len(amt)}")
print(f"  Amount = 0:   {(amt == 0).sum()} ({(amt == 0).mean()*100:.1f}%)")
print(f"  Amount = NaN: {amt.isna().sum()} ({amt.isna().mean()*100:.1f}%)")
valid = amt[(amt > 0) & amt.notna()]
print(f"  Valid amount: {len(valid)} ({len(valid)*100/len(amt):.1f}%)")
if len(valid) > 0:
    print(f"  Stats (valid): min={valid.min():,.0f} | median={valid.median():,.0f} | "
          f"mean={valid.mean():,.0f} | max={valid.max():,.0f}")

# 1.3 Orphan claims with high amount
orphan_high = df_orphan[(df_orphan['person_link'] == 'MISSING') & (df_orphan['amount'] > 10_000_000)]
print(f"\n[1.3] Orphan Claims > 10M (no Person linked): {len(orphan_high)}")
if not orphan_high.empty:
    print(orphan_high.nlargest(10, 'amount')[['claim_id', 'amount', 'diagnosis']].to_string(index=False))


# ═══════════════════════════════════════════════════════════════
# PHAN 2: FRAUD PATTERN SCORING
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("  PHAN 2: FRAUD PATTERN SCORING")
print("=" * 70)

# 2.1 Composite risk score per claimant
df_risk = q("""
    MATCH (p:Person)-[:SUBMITTED]->(c:Claim)
    WITH p,
         count(c) AS num_claims,
         sum(c.amount) AS total_amount,
         sum(CASE WHEN c.amount < 200000 AND c.amount > 0 THEN 1 ELSE 0 END) AS petty_claims,
         sum(CASE WHEN c.amount = 0 THEN 1 ELSE 0 END) AS zero_claims,
         collect(c.diagnosis) AS all_diag,
         collect(DISTINCT c.diagnosis) AS unique_diag,
         min(c.claim_date) AS first_claim,
         max(c.claim_date) AS last_claim
    RETURN p.user_id AS user_id,
           p.full_name AS full_name,
           toString(toInteger(p.phone_number)) AS phone,
           p.contract_level AS contract_level,
           num_claims,
           round(total_amount) AS total_amount,
           petty_claims,
           zero_claims,
           size(unique_diag) AS unique_diagnoses,
           first_claim, last_claim
    ORDER BY num_claims DESC
""")

if not df_risk.empty:
    # Calculate composite risk score
    df_risk['freq_score'] = df_risk['num_claims'].apply(
        lambda x: min(x / 5, 10)  # 5 claims = score 10
    ).round(2)
    df_risk['petty_ratio'] = (df_risk['petty_claims'] / df_risk['num_claims']).round(2)
    df_risk['petty_score'] = (df_risk['petty_ratio'] * 10).round(2)
    df_risk['zero_score'] = df_risk['zero_claims'].apply(lambda x: min(x * 3, 10)).round(2)
    df_risk['diversity_score'] = (
        1 - df_risk['unique_diagnoses'] / df_risk['num_claims']
    ).clip(0, 1).apply(lambda x: x * 10).round(2)  # low diversity = high risk

    df_risk['composite_risk'] = (
        df_risk['freq_score'] * 0.35 +
        df_risk['petty_score'] * 0.25 +
        df_risk['zero_score'] * 0.15 +
        df_risk['diversity_score'] * 0.25
    ).round(2)

    print("\n[2.1] TOP 20 Riskiest Claimants (Composite Score):")
    top = df_risk.nlargest(20, 'composite_risk')
    cols = ['full_name', 'num_claims', 'total_amount', 'petty_claims',
            'zero_claims', 'unique_diagnoses', 'composite_risk']
    print(top[cols].to_string(index=False))

    print(f"\n  Risk Distribution:")
    for threshold, label in [(8, 'CUC CAO (>=8)'), (6, 'CAO (6-8)'),
                              (4, 'TB (4-6)'), (0, 'THAP (<4)')]:
        if threshold == 0:
            count = (df_risk['composite_risk'] < 4).sum()
        elif threshold == 4:
            count = ((df_risk['composite_risk'] >= 4) & (df_risk['composite_risk'] < 6)).sum()
        elif threshold == 6:
            count = ((df_risk['composite_risk'] >= 6) & (df_risk['composite_risk'] < 8)).sum()
        else:
            count = (df_risk['composite_risk'] >= 8).sum()
        print(f"    {label}: {count} persons")


# ═══════════════════════════════════════════════════════════════
# PHAN 3: DIAGNOSIS-AMOUNT ANOMALY
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("  PHAN 3: DIAGNOSIS vs AMOUNT ANOMALY")
print("=" * 70)

df_diag = q("""
    MATCH (c:Claim)
    WHERE c.diagnosis IS NOT NULL AND c.diagnosis <> '' AND c.amount > 0
    WITH c.diagnosis AS diagnosis, c.amount AS amount
    RETURN diagnosis,
           count(*) AS cnt,
           round(avg(amount)) AS avg_amt,
           round(percentileCont(amount, 0.5)) AS median_amt,
           round(min(amount)) AS min_amt,
           round(max(amount)) AS max_amt
    ORDER BY cnt DESC
    LIMIT 30
""")

if not df_diag.empty:
    df_diag['max_vs_median'] = (df_diag['max_amt'] / df_diag['median_amt']).round(1)
    outliers = df_diag[df_diag['max_vs_median'] > 10].sort_values('max_vs_median', ascending=False)

    print("\n[3.1] Diagnoses with EXTREME price variance (max > 10x median):")
    if not outliers.empty:
        print(outliers[['diagnosis', 'cnt', 'median_amt', 'max_amt', 'max_vs_median']].to_string(index=False))
    else:
        print("  Khong tim thay")

    # Minor disease with high cost
    minor_keywords = ['viêm họng', 'viêm mũi', 'cảm', 'viêm dạ dày']
    print("\n[3.2] Minor diseases with suspiciously high max amounts:")
    for _, row in df_diag.iterrows():
        diag_lower = str(row['diagnosis']).lower()
        if any(kw in diag_lower for kw in minor_keywords) and row['max_amt'] > 5_000_000:
            print(f"  {row['diagnosis']}")
            print(f"    Count: {row['cnt']} | Median: {row['median_amt']:,.0f} | "
                  f"Max: {row['max_amt']:,.0f} | Ratio: {row['max_vs_median']}x")


# ═══════════════════════════════════════════════════════════════
# PHAN 4: NETWORK CENTRALITY (Bank hubs)
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("  PHAN 4: NETWORK HUB ANALYSIS")
print("=" * 70)

df_bank = q("""
    MATCH (p:Person)-[:SUBMITTED]->(c:Claim)-[:PAID_TO]->(b:Bank)
    WITH b, collect(DISTINCT p.full_name) AS users,
         count(c) AS claims, sum(c.amount) AS total,
         collect(DISTINCT c.diagnosis) AS diags
    WHERE size(users) > 1
    RETURN b.account_number AS stk,
           b.beneficiary_name AS owner,
           size(users) AS num_users,
           claims, round(total) AS total_amount,
           size(diags) AS unique_diags,
           users AS all_users
    ORDER BY num_users DESC
""")

if not df_bank.empty:
    print(f"\n[4.1] Bank accounts shared by multiple users: {len(df_bank)}")
    print(df_bank[['stk', 'owner', 'num_users', 'claims', 'total_amount']].to_string(index=False))

    # Check if users sharing bank have different last names (non-family)
    print("\n[4.2] Suspicious: Shared bank with DIFFERENT last names:")
    for _, row in df_bank.iterrows():
        names = str(row['all_users']).split(' | ')
        last_names = set()
        for n in names:
            parts = n.strip().split()
            if parts:
                last_names.add(parts[0])
        if len(last_names) > 2:
            print(f"  STK {row['stk']} ({row['owner']}): {len(last_names)} ho khac nhau -> {row['all_users'][:80]}")


# ═══════════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════════

output = f"EDA_Deep_Analysis_{TODAY}.xlsx"
with pd.ExcelWriter(output, engine="openpyxl") as writer:
    if not df_risk.empty:
        df_risk.sort_values('composite_risk', ascending=False).to_excel(
            writer, sheet_name="Risk_Scoring", index=False)
    if not df_diag.empty:
        df_diag.sort_values('max_vs_median', ascending=False).to_excel(
            writer, sheet_name="Diagnosis_Anomaly", index=False)
    if not df_bank.empty:
        df_bank.to_excel(writer, sheet_name="Bank_Network", index=False)
    df_orphan.to_excel(writer, sheet_name="Orphan_Audit", index=False)

print(f"\n[OK] Xuat file: {output}")

driver.close()
print("\nHOAN TAT.")
