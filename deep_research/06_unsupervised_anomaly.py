"""
╔══════════════════════════════════════════════════════════════════╗
║  MODULE 1: Unsupervised Anomaly Detection on Graph Features     ║
║  Isolation Forest + DBSCAN trên feature vector từ Neo4j         ║
║  Chạy: python 06_unsupervised_anomaly.py                        ║
╚══════════════════════════════════════════════════════════════════╝

Hướng 1 trong 05_recommendation.md:
- Trích feature từ graph (frequency, amount, connectivity, temporal)
- Chạy Isolation Forest → anomaly score per Person
- Chạy DBSCAN → tìm cluster bất thường
- Không cần label, không cần rule cứng
"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import pandas as pd
import numpy as np
from neo4j import GraphDatabase
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from datetime import datetime

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "Chien@2022"
NEO4J_DB = "neo4j"
TODAY = datetime.now().strftime("%Y%m%d")


def neo4j_query(driver, cypher):
    records, _, _ = driver.execute_query(cypher, database_=NEO4J_DB)
    if not records:
        return pd.DataFrame()
    rows = []
    for r in records:
        row = {}
        for k in r.keys():
            v = r[k]
            if isinstance(v, list):
                v = str(v)
            row[k] = v
        rows.append(row)
    return pd.DataFrame(rows)


def main():
    print("=" * 70)
    print("  MODULE 1: UNSUPERVISED ANOMALY DETECTION")
    print("  Isolation Forest + DBSCAN on Graph Features")
    print("=" * 70)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    driver.verify_connectivity()
    print("[OK] Neo4j connected\n")

    # ═══════════════════════════════════════════════════════════
    # STEP 1: EXTRACT FEATURES PER PERSON (Graph → Tabular)
    # ═══════════════════════════════════════════════════════════
    print("[1/5] Extracting graph features per Person...")

    df = neo4j_query(driver, """
        MATCH (p:Person)-[:SUBMITTED]->(c:Claim)
        WITH p, collect(c) AS claims
        WHERE size(claims) >= 2

        // --- Frequency features ---
        WITH p, claims,
             size(claims) AS num_claims,
             min(claims[0].claim_date) AS first_dt,
             max(claims[size(claims)-1].claim_date) AS last_dt

        // --- Amount features ---
        UNWIND claims AS c
        WITH p, num_claims, first_dt, last_dt, c
        WITH p, num_claims, first_dt, last_dt,
             avg(c.amount) AS avg_amount,
             max(c.amount) AS max_amount,
             min(c.amount) AS min_amount,
             stDev(c.amount) AS std_amount,
             sum(CASE WHEN c.amount < 200000 AND c.amount > 0 THEN 1 ELSE 0 END) AS petty_count,
             sum(CASE WHEN c.amount = 0 THEN 1 ELSE 0 END) AS zero_count,
             sum(c.amount) AS total_amount,
             collect(DISTINCT c.diagnosis) AS unique_diag,
             count(c) AS claim_count

        RETURN p.user_id AS user_id,
               p.full_name AS full_name,
               toString(toInteger(p.phone_number)) AS phone,
               p.contract_level AS contract_level,

               // Frequency
               claim_count AS f_num_claims,
               first_dt AS first_claim_date,
               last_dt AS last_claim_date,

               // Amount
               CASE WHEN avg_amount = avg_amount THEN round(avg_amount) ELSE 0 END AS f_avg_amount,
               CASE WHEN max_amount = max_amount THEN round(max_amount) ELSE 0 END AS f_max_amount,
               CASE WHEN std_amount = std_amount THEN round(std_amount) ELSE 0 END AS f_std_amount,
               round(total_amount) AS f_total_amount,

               // Petty/Zero ratios
               petty_count AS f_petty_count,
               zero_count AS f_zero_count,
               round(toFloat(petty_count) / claim_count, 3) AS f_petty_ratio,
               round(toFloat(zero_count) / claim_count, 3) AS f_zero_ratio,

               // Diagnosis diversity
               size(unique_diag) AS f_unique_diagnoses,
               round(1.0 - toFloat(size(unique_diag)) / claim_count, 3) AS f_diag_repetition
    """)

    print(f"  -> {len(df)} persons with >= 2 claims")

    # Enrich: bank sharing degree
    print("[2/5] Enriching with network connectivity features...")

    df_bank = neo4j_query(driver, """
        MATCH (p:Person)-[:SUBMITTED]->(c:Claim)-[:PAID_TO]->(b:Bank)
        WITH p.user_id AS user_id, b,
             collect(DISTINCT b.account_number) AS banks
        OPTIONAL MATCH (p2:Person)-[:SUBMITTED]->(:Claim)-[:PAID_TO]->(b)
        WHERE p2.user_id <> user_id
        WITH user_id, banks, count(DISTINCT p2) AS shared_bank_users
        RETURN user_id,
               size(banks) AS f_num_banks,
               shared_bank_users AS f_shared_bank_users
    """)

    if not df_bank.empty:
        df = df.merge(df_bank, on="user_id", how="left")
    for col in ["f_num_banks", "f_shared_bank_users"]:
        if col not in df.columns:
            df[col] = 0
        df[col] = df[col].fillna(0)

    # Phone sharing
    df_phone = neo4j_query(driver, """
        MATCH (p:Person)-[:SUBMITTED]->(:Claim)
        WHERE p.phone_number > 100000000
        WITH p.phone_number AS phone, collect(DISTINCT p.user_id) AS uids
        WHERE size(uids) > 1
        UNWIND uids AS uid
        RETURN uid AS user_id, size(uids) AS f_phone_shared_count
    """)

    if not df_phone.empty:
        df = df.merge(df_phone, on="user_id", how="left")
    if "f_phone_shared_count" not in df.columns:
        df["f_phone_shared_count"] = 1
    df["f_phone_shared_count"] = df["f_phone_shared_count"].fillna(1)

    # Hospital concentration
    df_hosp = neo4j_query(driver, """
        MATCH (p:Person)-[:SUBMITTED]->(c:Claim)-[:TREATED_AT]->(h:Hospital)
        WITH p.user_id AS user_id,
             count(DISTINCT h) AS num_hospitals,
             count(c) AS hospital_linked_claims
        RETURN user_id,
               num_hospitals AS f_num_hospitals,
               hospital_linked_claims AS f_hospital_claims
    """)

    if not df_hosp.empty:
        df = df.merge(df_hosp, on="user_id", how="left")
    for col in ["f_num_hospitals", "f_hospital_claims"]:
        if col not in df.columns:
            df[col] = 0
        df[col] = df[col].fillna(0)

    # ═══════════════════════════════════════════════════════════
    # STEP 2: ISOLATION FOREST
    # ═══════════════════════════════════════════════════════════
    print("[3/5] Running Isolation Forest...")

    feature_cols = [
        "f_num_claims", "f_avg_amount", "f_max_amount", "f_std_amount",
        "f_total_amount", "f_petty_count", "f_zero_count",
        "f_petty_ratio", "f_zero_ratio",
        "f_unique_diagnoses", "f_diag_repetition",
        "f_num_banks", "f_shared_bank_users", "f_phone_shared_count",
        "f_num_hospitals", "f_hospital_claims",
    ]

    # Ensure numeric
    for col in feature_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    X = df[feature_cols].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Isolation Forest: contamination = "auto" lets it decide
    iso = IsolationForest(
        n_estimators=200,
        contamination=0.05,  # expect ~5% anomalies
        random_state=42,
        n_jobs=-1,
    )
    df["iso_label"] = iso.fit_predict(X_scaled)       # -1 = anomaly
    df["iso_score"] = iso.decision_function(X_scaled)  # lower = more anomalous
    # Normalize to 0-10 scale (0=normal, 10=most anomalous)
    scores = df["iso_score"]
    df["anomaly_score"] = ((scores.max() - scores) / (scores.max() - scores.min()) * 10).round(2)

    anomalies = df[df["iso_label"] == -1].sort_values("anomaly_score", ascending=False)
    print(f"  -> {len(anomalies)} anomalies detected ({len(anomalies)*100/len(df):.1f}%)")

    # ═══════════════════════════════════════════════════════════
    # STEP 3: DBSCAN CLUSTERING
    # ═══════════════════════════════════════════════════════════
    print("[4/5] Running DBSCAN clustering...")

    dbscan = DBSCAN(eps=1.5, min_samples=3)
    df["cluster"] = dbscan.fit_predict(X_scaled)

    cluster_stats = df.groupby("cluster").agg(
        size=("user_id", "count"),
        avg_anomaly=("anomaly_score", "mean"),
        avg_claims=("f_num_claims", "mean"),
        avg_petty_ratio=("f_petty_ratio", "mean"),
        avg_total_amount=("f_total_amount", "mean"),
    ).round(2)
    cluster_stats = cluster_stats.sort_values("avg_anomaly", ascending=False)

    print(f"  -> {df['cluster'].nunique()} clusters found")
    print(f"  -> Noise points (cluster=-1): {(df['cluster'] == -1).sum()}")

    # ═══════════════════════════════════════════════════════════
    # STEP 4: FEATURE IMPORTANCE (which features drive anomaly)
    # ═══════════════════════════════════════════════════════════
    print("[5/5] Computing feature importance...")

    normal_means = df[df["iso_label"] == 1][feature_cols].mean()
    anomaly_means = df[df["iso_label"] == -1][feature_cols].mean()
    importance = ((anomaly_means - normal_means) / (normal_means + 1e-10)).abs().sort_values(ascending=False)

    # ═══════════════════════════════════════════════════════════
    # RESULTS
    # ═══════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("  RESULTS")
    print("=" * 70)

    print("\n[A] TOP 25 ANOMALOUS PERSONS (Isolation Forest):")
    print("-" * 70)
    show_cols = ["full_name", "f_num_claims", "f_total_amount", "f_petty_ratio",
                 "f_zero_count", "f_diag_repetition", "f_shared_bank_users",
                 "f_phone_shared_count", "anomaly_score"]
    print(anomalies.head(25)[show_cols].to_string(index=False))

    print(f"\n[B] FEATURE IMPORTANCE (what makes anomalies different):")
    print("-" * 70)
    for feat, imp in importance.head(10).items():
        normal_v = normal_means[feat]
        anomaly_v = anomaly_means[feat]
        direction = "HIGHER" if anomaly_v > normal_v else "LOWER"
        print(f"  {feat:30s}: anomaly={anomaly_v:>12,.1f} vs normal={normal_v:>12,.1f}  ({direction}, {imp:.1f}x)")

    print(f"\n[C] CLUSTER ANALYSIS (DBSCAN):")
    print("-" * 70)
    print(cluster_stats.to_string())

    # Suspicious clusters: high anomaly score
    sus_clusters = cluster_stats[
        (cluster_stats["avg_anomaly"] > 4) & (cluster_stats.index >= 0)
    ]
    if not sus_clusters.empty:
        print(f"\n  SUSPICIOUS CLUSTERS (avg anomaly > 4):")
        for cid, row in sus_clusters.iterrows():
            members = df[df["cluster"] == cid]["full_name"].tolist()
            print(f"    Cluster {cid}: {int(row['size'])} members, "
                  f"anomaly={row['avg_anomaly']:.1f}, "
                  f"avg_claims={row['avg_claims']:.0f}")
            for m in members[:5]:
                print(f"      - {m}")
            if len(members) > 5:
                print(f"      ... va {len(members)-5} nguoi nua")

    # Anomaly score distribution
    print(f"\n[D] ANOMALY SCORE DISTRIBUTION:")
    print("-" * 70)
    for threshold in [8, 6, 4, 2]:
        count = (df["anomaly_score"] >= threshold).sum()
        print(f"  Score >= {threshold}: {count} persons ({count*100/len(df):.1f}%)")

    # ═══════════════════════════════════════════════════════════
    # EXPORT
    # ═══════════════════════════════════════════════════════════
    output = f"06_Anomaly_Detection_{TODAY}.xlsx"
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # All persons with scores
        export_cols = (
            ["user_id", "full_name", "phone", "contract_level"] +
            feature_cols +
            ["anomaly_score", "iso_label", "cluster"]
        )
        df.sort_values("anomaly_score", ascending=False)[export_cols].to_excel(
            writer, sheet_name="All_Scores", index=False
        )

        # Anomalies only
        anomalies[export_cols].to_excel(
            writer, sheet_name="Anomalies", index=False
        )

        # Cluster summary
        cluster_stats.to_excel(writer, sheet_name="Clusters")

        # Feature importance
        imp_df = pd.DataFrame({
            "feature": importance.index,
            "importance": importance.values,
            "anomaly_mean": [anomaly_means[f] for f in importance.index],
            "normal_mean": [normal_means[f] for f in importance.index],
        })
        imp_df.to_excel(writer, sheet_name="Feature_Importance", index=False)

    print(f"\n[OK] Exported: {output}")

    driver.close()
    print("DONE.")


if __name__ == "__main__":
    main()
