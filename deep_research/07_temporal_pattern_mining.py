"""
╔══════════════════════════════════════════════════════════════════╗
║  MODULE 2: Temporal Pattern Mining                              ║
║  Phát hiện chuỗi hành vi bất thường theo thời gian              ║
║  Chạy: python 07_temporal_pattern_mining.py                     ║
╚══════════════════════════════════════════════════════════════════╝

Hướng 2 trong 05_recommendation.md:
- JIT Cluster Detection (claim ngay sau hạn chờ)
- Burst Detection (dồn nhiều claim trong thời gian ngắn)
- Same-day multi-person patterns
- Periodic/recurring pattern mining
- So sánh với "normal journey" distribution
"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import pandas as pd
import numpy as np
from neo4j import GraphDatabase
from collections import Counter, defaultdict
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
    print("  MODULE 2: TEMPORAL PATTERN MINING")
    print("=" * 70)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    driver.verify_connectivity()
    print("[OK] Neo4j connected\n")

    # ═══════════════════════════════════════════════════════════
    # STEP 1: LOAD ALL CLAIMS WITH TIMESTAMPS
    # ═══════════════════════════════════════════════════════════
    print("[1/6] Loading claim timeline data...")

    df = neo4j_query(driver, """
        MATCH (p:Person)-[:SUBMITTED]->(c:Claim)
        OPTIONAL MATCH (c)-[:TREATED_AT]->(h:Hospital)
        RETURN p.user_id AS user_id,
               p.full_name AS full_name,
               toString(toInteger(p.phone_number)) AS phone,
               c.claim_id AS claim_id,
               c.claim_date AS claim_date,
               c.amount AS amount,
               c.diagnosis AS diagnosis,
               h.hospital_code AS hospital_code
        ORDER BY p.user_id, c.claim_date
    """)

    df["claim_dt"] = pd.to_datetime(df["claim_date"], errors="coerce")
    df["claim_day"] = df["claim_dt"].dt.date
    df["day_of_month"] = df["claim_dt"].dt.day
    df["month"] = df["claim_dt"].dt.to_period("M").astype(str)
    df["weekday"] = df["claim_dt"].dt.dayofweek  # 0=Mon, 6=Sun
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

    print(f"  -> {len(df)} claims loaded for {df['user_id'].nunique()} persons")

    results = {}

    # ═══════════════════════════════════════════════════════════
    # PATTERN 1: BURST DETECTION
    # Nhiều claim trong thời gian ngắn bất thường
    # ═══════════════════════════════════════════════════════════
    print("\n[2/6] PATTERN 1: Burst Detection...")

    bursts = []
    for uid, group in df.groupby("user_id"):
        if len(group) < 3:
            continue
        g = group.sort_values("claim_dt")
        dates = g["claim_dt"].dropna().values

        # Sliding window: count claims in 7-day, 15-day, 30-day windows
        for window_days, label in [(7, "7d"), (15, "15d"), (30, "30d")]:
            for i in range(len(dates)):
                window_end = dates[i] + np.timedelta64(window_days, "D")
                claims_in_window = ((dates >= dates[i]) & (dates <= window_end)).sum()

                threshold = {7: 4, 15: 6, 30: 10}[window_days]
                if claims_in_window >= threshold:
                    bursts.append({
                        "user_id": uid,
                        "full_name": g["full_name"].iloc[0],
                        "phone": g["phone"].iloc[0],
                        "window": label,
                        "start_date": str(dates[i])[:10],
                        "claims_in_window": claims_in_window,
                        "total_amount": g[
                            (g["claim_dt"] >= dates[i]) &
                            (g["claim_dt"] <= window_end)
                        ]["amount"].sum(),
                    })
                    break  # one burst per window per person

    df_burst = pd.DataFrame(bursts)
    if not df_burst.empty:
        df_burst = df_burst.drop_duplicates(subset=["user_id", "window"])
        df_burst = df_burst.sort_values(["claims_in_window"], ascending=False)
    results["bursts"] = df_burst
    print(f"  -> {len(df_burst)} burst patterns found")

    if not df_burst.empty:
        print("\n  TOP 15 BURST PATTERNS:")
        print(df_burst.head(15).to_string(index=False))

    # ═══════════════════════════════════════════════════════════
    # PATTERN 2: JIT CLUSTER (Just-In-Time after waiting period)
    # Claims dồn vào ngày 1-5 của tháng (vừa qua hạn chờ)
    # ═══════════════════════════════════════════════════════════
    print("\n[3/6] PATTERN 2: JIT Cluster (Day-of-Month Analysis)...")

    dom_dist = df["day_of_month"].value_counts().sort_index()
    avg_per_day = len(df) / 31

    # Find days with abnormally high claim volume
    jit_days = dom_dist[dom_dist > avg_per_day * 1.5]

    print(f"\n  Day-of-month distribution (avg = {avg_per_day:.0f}/day):")
    print(f"  {'Day':>4} | {'Count':>6} | {'Bar'}")
    print(f"  {'-'*4} | {'-'*6} | {'-'*40}")
    for day in range(1, 32):
        count = dom_dist.get(day, 0)
        bar = "#" * int(count / avg_per_day * 15)
        flag = " *** SPIKE" if count > avg_per_day * 1.5 else ""
        print(f"  {day:>4} | {count:>6} | {bar}{flag}")

    # Persons who consistently claim on day 1-3
    early_month = df[df["day_of_month"] <= 3]
    early_claimers = early_month.groupby("user_id").agg(
        full_name=("full_name", "first"),
        early_claims=("claim_id", "count"),
        total_claims=("claim_id", lambda x: df[df["user_id"] == x.iloc[0]].shape[0] if len(x) > 0 else 0),
    ).reset_index()
    # re-calculate total_claims properly
    total_per_user = df.groupby("user_id")["claim_id"].count().rename("total_claims_all")
    early_claimers = early_claimers.merge(total_per_user, on="user_id", how="left")
    early_claimers["early_ratio"] = (early_claimers["early_claims"] / early_claimers["total_claims_all"]).round(2)
    early_claimers = early_claimers[early_claimers["early_claims"] >= 3].sort_values("early_claims", ascending=False)

    results["jit_claimers"] = early_claimers
    print(f"\n  Persons with >= 3 claims on day 1-3 of month: {len(early_claimers)}")
    if not early_claimers.empty:
        print(early_claimers.head(10).to_string(index=False))

    # ═══════════════════════════════════════════════════════════
    # PATTERN 3: SAME-DAY MULTI-PERSON AT SAME HOSPITAL
    # Nhiều người khám cùng ngày tại cùng BV
    # ═══════════════════════════════════════════════════════════
    print("\n[4/6] PATTERN 3: Same-Day Multi-Person Clusters...")

    df_with_hosp = df[df["hospital_code"].notna() & (df["hospital_code"] != "")].copy()
    if not df_with_hosp.empty:
        day_hosp = df_with_hosp.groupby(["claim_day", "hospital_code"]).agg(
            num_persons=("user_id", "nunique"),
            num_claims=("claim_id", "count"),
            persons=("full_name", lambda x: " | ".join(x.unique()[:5])),
            diagnoses=("diagnosis", lambda x: " | ".join(x.dropna().unique()[:3])),
            total_amount=("amount", "sum"),
        ).reset_index()
        day_hosp = day_hosp[day_hosp["num_persons"] >= 3].sort_values("num_persons", ascending=False)
        results["same_day_clusters"] = day_hosp

        print(f"  -> {len(day_hosp)} same-day clusters (>= 3 persons at same hospital)")
        if not day_hosp.empty:
            print(day_hosp.head(10).to_string(index=False))
    else:
        results["same_day_clusters"] = pd.DataFrame()
        print("  -> Khong du du lieu hospital linkage")

    # ═══════════════════════════════════════════════════════════
    # PATTERN 4: DIAGNOSIS SEQUENCE REPETITION
    # Cùng person, cùng diagnosis, lặp liên tục
    # ═══════════════════════════════════════════════════════════
    print("\n[5/6] PATTERN 4: Diagnosis Sequence Repetition...")

    repeats = []
    for uid, group in df.groupby("user_id"):
        if len(group) < 3:
            continue
        g = group.sort_values("claim_dt")
        diag_seq = g["diagnosis"].dropna().tolist()

        # Find longest consecutive run of same diagnosis
        if not diag_seq:
            continue
        max_run = 1
        max_diag = diag_seq[0]
        current_run = 1
        for i in range(1, len(diag_seq)):
            if diag_seq[i] == diag_seq[i-1]:
                current_run += 1
                if current_run > max_run:
                    max_run = current_run
                    max_diag = diag_seq[i]
            else:
                current_run = 1

        # Also count most frequent diagnosis
        diag_counts = Counter(diag_seq)
        top_diag, top_count = diag_counts.most_common(1)[0]
        total = len(diag_seq)

        if max_run >= 3 or (top_count >= 4 and top_count / total >= 0.6):
            repeats.append({
                "user_id": uid,
                "full_name": g["full_name"].iloc[0],
                "total_claims": total,
                "longest_consecutive_run": max_run,
                "run_diagnosis": max_diag[:60] if max_diag else "",
                "most_freq_diagnosis": top_diag[:60] if top_diag else "",
                "most_freq_count": top_count,
                "repetition_ratio": round(top_count / total, 2),
                "total_amount": round(g["amount"].sum()),
            })

    df_repeats = pd.DataFrame(repeats).sort_values("longest_consecutive_run", ascending=False) if repeats else pd.DataFrame()
    results["diag_repeats"] = df_repeats

    print(f"  -> {len(df_repeats)} persons with repetitive diagnosis patterns")
    if not df_repeats.empty:
        print(df_repeats.head(15).to_string(index=False))

    # ═══════════════════════════════════════════════════════════
    # PATTERN 5: INTER-CLAIM INTERVAL ANOMALY
    # So sánh với "normal journey"
    # ═══════════════════════════════════════════════════════════
    print("\n[6/6] PATTERN 5: Inter-Claim Interval Analysis...")

    intervals_all = []
    person_intervals = []

    for uid, group in df.groupby("user_id"):
        g = group.sort_values("claim_dt")
        dates = g["claim_dt"].dropna()
        if len(dates) < 2:
            continue

        diffs = dates.diff().dt.days.dropna().values
        if len(diffs) == 0:
            continue

        intervals_all.extend(diffs.tolist())
        person_intervals.append({
            "user_id": uid,
            "full_name": g["full_name"].iloc[0],
            "num_claims": len(g),
            "avg_interval_days": round(np.mean(diffs), 1),
            "min_interval_days": int(np.min(diffs)),
            "max_interval_days": int(np.max(diffs)),
            "std_interval_days": round(np.std(diffs), 1),
            "zero_gap_claims": int((diffs == 0).sum()),  # same day
            "total_amount": round(g["amount"].sum()),
        })

    df_intervals = pd.DataFrame(person_intervals)

    if not df_intervals.empty:
        # Global stats
        global_mean = np.mean(intervals_all)
        global_std = np.std(intervals_all)
        global_median = np.median(intervals_all)

        print(f"\n  Global inter-claim interval:")
        print(f"    Mean: {global_mean:.1f} days | Median: {global_median:.0f} days | Std: {global_std:.1f}")

        # Flag persons with unusually short intervals
        df_intervals["z_score"] = (
            (df_intervals["avg_interval_days"] - global_mean) / (global_std + 0.01)
        ).round(2)

        # Anomalous: very short intervals or many same-day claims
        short_interval = df_intervals[
            (df_intervals["avg_interval_days"] < global_mean * 0.3) &
            (df_intervals["num_claims"] >= 5)
        ].sort_values("avg_interval_days")

        results["short_intervals"] = short_interval

        print(f"\n  Persons with abnormally short intervals ({len(short_interval)}):")
        if not short_interval.empty:
            print(short_interval.head(15)[
                ["full_name", "num_claims", "avg_interval_days", "min_interval_days",
                 "zero_gap_claims", "total_amount"]
            ].to_string(index=False))

        # Same-day claims (multiple claims on same day)
        same_day = df_intervals[df_intervals["zero_gap_claims"] >= 3].sort_values(
            "zero_gap_claims", ascending=False
        )
        results["same_day_self"] = same_day
        print(f"\n  Persons with >= 3 same-day claims: {len(same_day)}")
        if not same_day.empty:
            print(same_day.head(10)[
                ["full_name", "num_claims", "zero_gap_claims", "avg_interval_days", "total_amount"]
            ].to_string(index=False))

    # ═══════════════════════════════════════════════════════════
    # EXPORT
    # ═══════════════════════════════════════════════════════════
    output = f"07_Temporal_Patterns_{TODAY}.xlsx"
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for name, result_df in results.items():
            if isinstance(result_df, pd.DataFrame) and not result_df.empty:
                result_df.to_excel(writer, sheet_name=name[:31], index=False)

        if not df_intervals.empty:
            df_intervals.sort_values("avg_interval_days").to_excel(
                writer, sheet_name="All_Intervals", index=False
            )

    print(f"\n[OK] Exported: {output}")
    driver.close()
    print("DONE.")


if __name__ == "__main__":
    main()
