import sys, io, os

# Write output to D: drive to avoid C: drive space issues
output_path = r"D:\desktop_folder\schema_output.txt"
f = open(output_path, "w", encoding="utf-8")

from neo4j import GraphDatabase
driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "password"))

def p(s):
    f.write(str(s) + "\n")

# 1. Labels
p("\n=== node_labels ===")
records, _, _ = driver.execute_query("CALL db.labels() YIELD label RETURN label", database_="neo4j")
for r in records:
    p(r["label"])

# 2. Relationship types
p("\n=== rel_types ===")
records, _, _ = driver.execute_query("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType", database_="neo4j")
for r in records:
    p(r["relationshipType"])

# 3. Property keys
p("\n=== property_keys ===")
records, _, _ = driver.execute_query("CALL db.propertyKeys() YIELD propertyKey RETURN propertyKey", database_="neo4j")
for r in records:
    p(r["propertyKey"])

# 4. Node details
labels_result, _, _ = driver.execute_query("CALL db.labels() YIELD label RETURN label", database_="neo4j")
for lr in labels_result:
    label = lr["label"]
    count_result, _, _ = driver.execute_query(f"MATCH (n:{label}) RETURN count(n) AS cnt", database_="neo4j")
    cnt = count_result[0]["cnt"]
    sample_result, _, _ = driver.execute_query(f"MATCH (n:{label}) RETURN n LIMIT 1", database_="neo4j")
    if sample_result:
        props = dict(sample_result[0]["n"])
        p(f"\n=== {label} ({cnt} nodes) ===")
        for k, v in props.items():
            p(f"  {k}: {type(v).__name__} = {repr(v)[:120]}")

# 5. Relationship details
rels_result, _, _ = driver.execute_query("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType", database_="neo4j")
for rr in rels_result:
    rtype = rr["relationshipType"]
    count_result, _, _ = driver.execute_query(f"MATCH ()-[r:{rtype}]->() RETURN count(r) AS cnt", database_="neo4j")
    cnt = count_result[0]["cnt"]
    endpoints, _, _ = driver.execute_query(f"MATCH (a)-[r:{rtype}]->(b) RETURN labels(a)[0] AS src, labels(b)[0] AS tgt LIMIT 1", database_="neo4j")
    if endpoints:
        src = endpoints[0]["src"]
        tgt = endpoints[0]["tgt"]
        p(f"\n=== [:{rtype}] ({cnt} rels) === {src} -> {tgt}")
    # Sample rel properties
    rel_props, _, _ = driver.execute_query(f"MATCH ()-[r:{rtype}]->() RETURN properties(r) AS props LIMIT 1", database_="neo4j")
    if rel_props and rel_props[0]["props"]:
        for k2, v2 in rel_props[0]["props"].items():
            p(f"  {k2}: {type(v2).__name__} = {repr(v2)[:120]}")

# 6. Data quality
p("\n\n=== DATA QUALITY CHECK ===")
quality_queries = {
    "Claim.claim_amount_approved NOT NULL": "MATCH (c:Claim) WHERE c.claim_amount_approved IS NOT NULL RETURN count(c) AS cnt",
    "Claim.claim_amount_vien_phi NOT NULL": "MATCH (c:Claim) WHERE c.claim_amount_vien_phi IS NOT NULL RETURN count(c) AS cnt",
    "Claim.treatment_duration_days NOT NULL": "MATCH (c:Claim) WHERE c.treatment_duration_days IS NOT NULL RETURN count(c) AS cnt",
    "Claim.visit_date NOT NULL": "MATCH (c:Claim) WHERE c.visit_date IS NOT NULL RETURN count(c) AS cnt",
    "Claim.claim_date NOT NULL": "MATCH (c:Claim) WHERE c.claim_date IS NOT NULL RETURN count(c) AS cnt",
    "Claim.discharge_diagnosis NOT NULL": "MATCH (c:Claim) WHERE c.discharge_diagnosis IS NOT NULL RETURN count(c) AS cnt",
    "Contract.premium_paid NOT NULL": "MATCH (c:Contract) WHERE c.premium_paid IS NOT NULL RETURN count(c) AS cnt",
    "Contract.contract_start_date NOT NULL": "MATCH (c:Contract) WHERE c.contract_start_date IS NOT NULL RETURN count(c) AS cnt",
    "Contract.contract_end_date NOT NULL": "MATCH (c:Contract) WHERE c.contract_end_date IS NOT NULL RETURN count(c) AS cnt",
    "Contract.contract_level NOT NULL": "MATCH (c:Contract) WHERE c.contract_level IS NOT NULL RETURN count(c) AS cnt",
    "ExpenseDetail.exclusion_amount NOT NULL": "MATCH (e:ExpenseDetail) WHERE e.exclusion_amount IS NOT NULL RETURN count(e) AS cnt",
    "ExpenseDetail.total_amount NOT NULL": "MATCH (e:ExpenseDetail) WHERE e.total_amount IS NOT NULL RETURN count(e) AS cnt",
    "ExpenseDetail.category NOT NULL": "MATCH (e:ExpenseDetail) WHERE e.category IS NOT NULL RETURN count(e) AS cnt",
    "Person.phone_number NOT NULL and <> Unknown": "MATCH (p:Person) WHERE p.phone_number IS NOT NULL AND p.phone_number <> 'Unknown' RETURN count(p) AS cnt",
    "Person.date_of_birth NOT NULL": "MATCH (p:Person) WHERE p.date_of_birth IS NOT NULL RETURN count(p) AS cnt",
    "Person.gender NOT NULL": "MATCH (p:Person) WHERE p.gender IS NOT NULL RETURN count(p) AS cnt",
    "Person.full_name NOT NULL": "MATCH (p:Person) WHERE p.full_name IS NOT NULL RETURN count(p) AS cnt",
    "BankAccount total": "MATCH (b:BankAccount) RETURN count(b) AS cnt",
    "Doctor total": "MATCH (d:Doctor) RETURN count(d) AS cnt",
    "Hospital total": "MATCH (h:Hospital) RETURN count(h) AS cnt",
    "Diagnosis total": "MATCH (d:Diagnosis) RETURN count(d) AS cnt",
    "DrugOrService total": "MATCH (d:DrugOrService) RETURN count(d) AS cnt",
    "Insurer total": "MATCH (i:Insurer) RETURN count(i) AS cnt",
}
for desc, q in quality_queries.items():
    try:
        result, _, _ = driver.execute_query(q, database_="neo4j")
        p(f"  {desc}: {result[0]['cnt']}")
    except Exception as e:
        p(f"  {desc}: ERROR - {e}")

# 7. Statistics
p("\n\n=== STATISTICAL PATTERNS ===")
stat_queries = {
    "Avg claims per person": "MATCH (p:Person)-[:FILED_CLAIM]->(c:Claim) WITH p, count(c) AS n RETURN avg(n) AS avg_claims, max(n) AS max_claims, percentileCont(n, 0.5) AS median_claims",
    "Avg amount per claim": "MATCH (c:Claim) WHERE c.claim_amount_approved > 0 RETURN avg(c.claim_amount_approved) AS avg_amt, percentileCont(c.claim_amount_approved, 0.5) AS median_amt, max(c.claim_amount_approved) AS max_amt",
    "Claims per hospital distribution": "MATCH (h:Hospital)<-[:AT_HOSPITAL]-(c:Claim) WITH h, count(c) AS n RETURN avg(n) AS avg_per_hosp, max(n) AS max_per_hosp, percentileCont(n, 0.5) AS median_per_hosp",
    "Claims per doctor distribution": "MATCH (d:Doctor)<-[:EXAMINED_BY]-(c:Claim) WITH d, count(c) AS n RETURN avg(n) AS avg_per_doc, max(n) AS max_per_doc, percentileCont(n, 0.5) AS median_per_doc",
    "Persons sharing bank accounts": "MATCH (p:Person)-[:RECEIVES_TO]->(b:BankAccount) WITH b, count(DISTINCT p) AS n WHERE n > 1 RETURN count(b) AS shared_accounts, max(n) AS max_sharing",
    "Persons sharing phones": "MATCH (p:Person) WHERE p.phone_number IS NOT NULL AND p.phone_number <> 'Unknown' WITH p.phone_number AS ph, count(p) AS n WHERE n > 1 RETURN count(ph) AS shared_phones, max(n) AS max_sharing",
    "Diagnosis diversity per person": "MATCH (p:Person)-[:FILED_CLAIM]->(c:Claim) WHERE c.discharge_diagnosis IS NOT NULL WITH p, collect(DISTINCT c.discharge_diagnosis) AS diags RETURN avg(size(diags)) AS avg_diags, max(size(diags)) AS max_diags",
    "Hospital diversity per person": "MATCH (p:Person)-[:FILED_CLAIM]->(c:Claim)-[:AT_HOSPITAL]->(h:Hospital) WITH p, count(DISTINCT h) AS n_hosp RETURN avg(n_hosp) AS avg_hosp, max(n_hosp) AS max_hosp",
    "Weekend claims ratio": "MATCH (c:Claim) WHERE c.visit_date IS NOT NULL WITH c, date(c.visit_date) AS d WITH c, d.dayOfWeek AS dow RETURN dow, count(c) AS cnt ORDER BY dow",
    "Doctors at multiple hospitals": "MATCH (d:Doctor)<-[:EXAMINED_BY]-(c:Claim)-[:AT_HOSPITAL]->(h:Hospital) WITH d, count(DISTINCT h) AS n_hosp WHERE n_hosp > 1 RETURN count(d) AS multi_hosp_docs, max(n_hosp) AS max_hosp",
    "Same-day multiple claims": "MATCH (p:Person)-[:FILED_CLAIM]->(c:Claim) WHERE c.claim_date IS NOT NULL WITH p, c.claim_date AS d, count(c) AS n WHERE n > 1 RETURN count(DISTINCT p) AS persons_with_same_day, max(n) AS max_same_day",
    "Claim amount distribution buckets": "MATCH (c:Claim) WHERE c.claim_amount_approved > 0 RETURN CASE WHEN c.claim_amount_approved < 200000 THEN 'A:<200K' WHEN c.claim_amount_approved < 1000000 THEN 'B:200K-1M' WHEN c.claim_amount_approved < 5000000 THEN 'C:1M-5M' WHEN c.claim_amount_approved < 10000000 THEN 'D:5M-10M' ELSE 'E:>10M' END AS bucket, count(c) AS cnt ORDER BY bucket",
    "Insurer distribution": "MATCH (c:Claim)-[:INSURED_BY]->(i:Insurer) RETURN i.name AS insurer, count(c) AS cnt ORDER BY cnt DESC LIMIT 10",
    "Contract levels": "MATCH (c:Contract) WHERE c.contract_level IS NOT NULL RETURN c.contract_level AS level, count(c) AS cnt ORDER BY level",
    "DrugOrService price stats": "MATCH (e:ExpenseDetail)-[:IS_ITEM]->(d:DrugOrService) WHERE e.total_amount > 0 RETURN count(e) AS total_items, avg(e.total_amount) AS avg_price, max(e.total_amount) AS max_price",
}
for desc, q in stat_queries.items():
    try:
        result, _, _ = driver.execute_query(q, database_="neo4j")
        for r in result:
            p(f"  {desc}: {dict(r)}")
    except Exception as e:
        p(f"  {desc}: ERROR - {str(e)[:150]}")

driver.close()
f.close()
print("DONE")
