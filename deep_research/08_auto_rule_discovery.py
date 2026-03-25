"""
╔══════════════════════════════════════════════════════════════════╗
║  MODULE 3: Auto-Rule Discovery from Subgraph Patterns           ║
║  NetworkX graph analysis + auto-generate Cypher rule candidates  ║
║  Chạy: python 08_auto_rule_discovery.py                         ║
╚══════════════════════════════════════════════════════════════════╝

Hướng 3 trong 05_recommendation.md:
- Xây dựng NetworkX graph từ Neo4j
- Tính centrality, community detection
- Tìm frequent subgraph patterns trong fraud cases
- Tự sinh Cypher rule candidates
"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import pandas as pd
import numpy as np
import networkx as nx
from neo4j import GraphDatabase
from collections import Counter, defaultdict
from datetime import datetime
from itertools import combinations

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
    print("  MODULE 3: AUTO-RULE DISCOVERY")
    print("  NetworkX Analysis + Cypher Rule Generation")
    print("=" * 70)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    driver.verify_connectivity()
    print("[OK] Neo4j connected\n")

    # ═══════════════════════════════════════════════════════════
    # STEP 1: BUILD NETWORKX GRAPH
    # ═══════════════════════════════════════════════════════════
    print("[1/5] Building NetworkX graph from Neo4j...")

    # Load all relationships into NetworkX
    G = nx.Graph()

    # Person -> Claim (SUBMITTED)
    df_sub = neo4j_query(driver, """
        MATCH (p:Person)-[:SUBMITTED]->(c:Claim)
        RETURN p.user_id AS person_id, p.full_name AS person_name,
               c.claim_id AS claim_id, c.amount AS claim_amount,
               c.diagnosis AS diagnosis, c.claim_date AS claim_date
    """)
    print(f"  SUBMITTED edges: {len(df_sub)}")

    for _, r in df_sub.iterrows():
        pid = f"P:{r['person_id']}"
        cid = f"C:{r['claim_id']}"
        G.add_node(pid, type="Person", name=r["person_name"])
        G.add_node(cid, type="Claim", amount=r["claim_amount"],
                   diagnosis=r["diagnosis"], date=r["claim_date"])
        G.add_edge(pid, cid, rel="SUBMITTED")

    # Claim -> Hospital, Doctor, Bank
    for rel, label, id_field, extra in [
        ("TREATED_AT", "Hospital", "hospital_code", []),
        ("EXAMINED_BY", "Doctor", "doctor_name", []),
        ("PAID_TO", "Bank", "bank_account", ["beneficiary_name"]),
    ]:
        cypher_map = {
            "TREATED_AT": """
                MATCH (c:Claim)-[:TREATED_AT]->(h:Hospital)
                RETURN c.claim_id AS claim_id, h.hospital_code AS target_id
            """,
            "EXAMINED_BY": """
                MATCH (c:Claim)-[:EXAMINED_BY]->(d:Doctor)
                RETURN c.claim_id AS claim_id, d.name AS target_id
            """,
            "PAID_TO": """
                MATCH (c:Claim)-[:PAID_TO]->(b:Bank)
                RETURN c.claim_id AS claim_id,
                       b.account_number AS target_id,
                       b.beneficiary_name AS extra_name
            """,
        }
        df_rel = neo4j_query(driver, cypher_map[rel])
        print(f"  {rel} edges: {len(df_rel)}")

        for _, r in df_rel.iterrows():
            cid = f"C:{r['claim_id']}"
            tid = f"{label[0]}:{r['target_id']}"
            G.add_node(tid, type=label)
            if cid in G:
                G.add_edge(cid, tid, rel=rel)

    # Person-to-Person via shared phone
    df_phone = neo4j_query(driver, """
        MATCH (p1:Person)-[:SUBMITTED]->(:Claim),
              (p2:Person)-[:SUBMITTED]->(:Claim)
        WHERE p1.phone_number = p2.phone_number
          AND p1.phone_number > 100000000
          AND p1.user_id < p2.user_id
        RETURN DISTINCT p1.user_id AS p1_id, p2.user_id AS p2_id,
               toString(toInteger(p1.phone_number)) AS shared_phone
    """)
    print(f"  SHARED_PHONE edges: {len(df_phone)}")

    for _, r in df_phone.iterrows():
        pid1 = f"P:{r['p1_id']}"
        pid2 = f"P:{r['p2_id']}"
        if pid1 in G and pid2 in G:
            G.add_edge(pid1, pid2, rel="SHARED_PHONE", phone=r["shared_phone"])

    # Person-to-Person via shared bank
    df_bank_share = neo4j_query(driver, """
        MATCH (p1:Person)-[:SUBMITTED]->(:Claim)-[:PAID_TO]->(b:Bank)<-[:PAID_TO]-(:Claim)<-[:SUBMITTED]-(p2:Person)
        WHERE p1.user_id < p2.user_id
        RETURN DISTINCT p1.user_id AS p1_id, p2.user_id AS p2_id,
               b.account_number AS shared_bank
    """)
    print(f"  SHARED_BANK edges: {len(df_bank_share)}")

    for _, r in df_bank_share.iterrows():
        pid1 = f"P:{r['p1_id']}"
        pid2 = f"P:{r['p2_id']}"
        if pid1 in G and pid2 in G:
            G.add_edge(pid1, pid2, rel="SHARED_BANK", bank=r["shared_bank"])

    print(f"\n  Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    # ═══════════════════════════════════════════════════════════
    # STEP 2: CENTRALITY ANALYSIS
    # ═══════════════════════════════════════════════════════════
    print("\n[2/5] Computing centrality metrics...")

    # Focus on Person nodes
    person_nodes = [n for n, d in G.nodes(data=True) if d.get("type") == "Person"]

    # Degree centrality
    degree = dict(G.degree(person_nodes))
    # Betweenness on person subgraph (too expensive on full graph)
    person_subgraph = G.subgraph(
        [n for n in G.nodes() if G.nodes[n].get("type") in ("Person", "Bank", "Hospital")]
    )

    betweenness = {}
    if person_subgraph.number_of_nodes() < 5000:
        betweenness = nx.betweenness_centrality(person_subgraph)
    else:
        # Approximate for large graphs
        betweenness = nx.betweenness_centrality(person_subgraph, k=min(500, person_subgraph.number_of_nodes()))

    centrality_data = []
    for pn in person_nodes:
        name = G.nodes[pn].get("name", "")
        centrality_data.append({
            "node_id": pn,
            "full_name": name,
            "degree": degree.get(pn, 0),
            "betweenness": round(betweenness.get(pn, 0), 6),
            # Count different relationship types
            "claim_edges": sum(1 for _, _, d in G.edges(pn, data=True) if d.get("rel") == "SUBMITTED"),
            "shared_phone_edges": sum(1 for _, _, d in G.edges(pn, data=True) if d.get("rel") == "SHARED_PHONE"),
            "shared_bank_edges": sum(1 for _, _, d in G.edges(pn, data=True) if d.get("rel") == "SHARED_BANK"),
        })

    df_centrality = pd.DataFrame(centrality_data).sort_values("degree", ascending=False)
    df_centrality["connectivity_score"] = (
        df_centrality["shared_phone_edges"] * 3 +
        df_centrality["shared_bank_edges"] * 5 +
        df_centrality["degree"] * 0.5
    ).round(2)

    print(f"\n  TOP 15 MOST CONNECTED PERSONS (potential Masterminds):")
    print(df_centrality.head(15).to_string(index=False))

    # ═══════════════════════════════════════════════════════════
    # STEP 3: COMMUNITY DETECTION (Connected Components)
    # ═══════════════════════════════════════════════════════════
    print("\n[3/5] Finding communities / syndicates...")

    # Build person-only graph with shared edges
    person_link_graph = nx.Graph()
    for u, v, d in G.edges(data=True):
        if d.get("rel") in ("SHARED_PHONE", "SHARED_BANK"):
            person_link_graph.add_edge(u, v, **d)

    components = list(nx.connected_components(person_link_graph))
    # Filter components with >= 3 persons
    syndicates = [c for c in components if len(c) >= 3]
    syndicates.sort(key=len, reverse=True)

    print(f"  -> {len(syndicates)} potential syndicates (>= 3 connected persons)")

    syndicate_details = []
    for idx, comp in enumerate(syndicates[:20]):
        members = []
        total_claims = 0
        total_amount = 0
        shared_phones = set()
        shared_banks = set()

        for node in comp:
            name = G.nodes[node].get("name", node)
            members.append(name)
            # Count claims
            for _, neighbor, d in G.edges(node, data=True):
                if d.get("rel") == "SUBMITTED":
                    total_claims += 1
                    amt = G.nodes[neighbor].get("amount", 0)
                    if amt and amt == amt:  # not NaN
                        total_amount += amt

            for u, v, d in person_link_graph.edges(node, data=True):
                if d.get("rel") == "SHARED_PHONE":
                    shared_phones.add(d.get("phone", ""))
                if d.get("rel") == "SHARED_BANK":
                    shared_banks.add(d.get("bank", ""))

        syndicate_details.append({
            "syndicate_id": idx + 1,
            "num_members": len(comp),
            "members": " | ".join(members[:8]),
            "total_claims": total_claims,
            "total_amount": round(total_amount),
            "shared_phones": " | ".join(shared_phones),
            "shared_banks": " | ".join(shared_banks),
            "link_types": f"Phone:{len(shared_phones)}, Bank:{len(shared_banks)}",
        })

    df_syndicates = pd.DataFrame(syndicate_details)
    if not df_syndicates.empty:
        print(df_syndicates.to_string(index=False))

    # ═══════════════════════════════════════════════════════════
    # STEP 4: FREQUENT PATTERN MINING
    # ═══════════════════════════════════════════════════════════
    print("\n[4/5] Mining frequent fraud patterns...")

    # Pattern: What structural features are common among high-activity persons?
    patterns = defaultdict(int)
    pattern_examples = defaultdict(list)

    top_persons = df_centrality.nlargest(50, "connectivity_score")

    for _, row in top_persons.iterrows():
        node = row["node_id"]
        features = set()

        if row["shared_phone_edges"] > 0:
            features.add("SHARED_PHONE")
        if row["shared_bank_edges"] > 0:
            features.add("SHARED_BANK")
        if row["claim_edges"] > 10:
            features.add("HIGH_FREQ_CLAIMS")
        elif row["claim_edges"] > 5:
            features.add("MED_FREQ_CLAIMS")

        # Check claim characteristics
        claim_neighbors = [n for _, n, d in G.edges(node, data=True) if d.get("rel") == "SUBMITTED"]
        petty_count = sum(1 for cn in claim_neighbors
                         if G.nodes[cn].get("amount", 0) is not None
                         and G.nodes[cn].get("amount", 0) == G.nodes[cn].get("amount", 0)
                         and 0 < G.nodes[cn].get("amount", 0) < 200000)
        if petty_count > 3:
            features.add("PETTY_CLAIMS")

        # Check diagnosis diversity
        diags = set(G.nodes[cn].get("diagnosis", "") for cn in claim_neighbors
                    if G.nodes[cn].get("diagnosis"))
        if len(diags) <= 2 and len(claim_neighbors) > 5:
            features.add("LOW_DIAG_DIVERSITY")

        pattern_key = frozenset(features)
        if len(pattern_key) >= 2:
            patterns[pattern_key] += 1
            pattern_examples[pattern_key].append(row["full_name"])

    print(f"\n  Frequent feature combinations among suspicious persons:")
    sorted_patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)
    for pattern, count in sorted_patterns[:15]:
        examples = pattern_examples[pattern][:3]
        print(f"  [{count:>3}x] {' + '.join(sorted(pattern))}")
        print(f"         Examples: {', '.join(examples)}")

    # ═══════════════════════════════════════════════════════════
    # STEP 5: AUTO-GENERATE CYPHER RULES
    # ═══════════════════════════════════════════════════════════
    print("\n[5/5] Generating Cypher rule candidates...")

    rules = []

    # Rule templates based on discovered patterns
    for pattern, count in sorted_patterns:
        if count < 2:
            continue

        rule_parts = []
        match_clauses = ["MATCH (p:Person)-[:SUBMITTED]->(c:Claim)"]
        where_clauses = []
        with_clauses = []
        return_fields = ["p.user_id AS user_id", "p.full_name AS full_name"]

        if "SHARED_BANK" in pattern:
            match_clauses.append("MATCH (p)-[:SUBMITTED]->(:Claim)-[:PAID_TO]->(b:Bank)<-[:PAID_TO]-(:Claim)<-[:SUBMITTED]-(p2:Person)")
            where_clauses.append("p <> p2")
            return_fields.append("b.account_number AS shared_bank")
            rule_parts.append("shared_bank_account")

        if "SHARED_PHONE" in pattern:
            match_clauses.append("MATCH (p2:Person)-[:SUBMITTED]->(:Claim)")
            where_clauses.append("p.phone_number = p2.phone_number AND p <> p2 AND p.phone_number > 100000000")
            return_fields.append("toString(toInteger(p.phone_number)) AS shared_phone")
            rule_parts.append("shared_phone")

        if "HIGH_FREQ_CLAIMS" in pattern or "MED_FREQ_CLAIMS" in pattern:
            threshold = 10 if "HIGH_FREQ_CLAIMS" in pattern else 5
            with_clauses.append(f"WITH p, count(c) AS num_claims WHERE num_claims > {threshold}")
            return_fields.append("num_claims")
            rule_parts.append(f"freq_gt_{threshold}")

        if "PETTY_CLAIMS" in pattern:
            with_clauses.append(
                "WITH p, count(c) AS total, "
                "sum(CASE WHEN c.amount < 200000 AND c.amount > 0 THEN 1 ELSE 0 END) AS petty "
                "WHERE petty > 3"
            )
            return_fields.extend(["total AS total_claims", "petty AS petty_claims"])
            rule_parts.append("petty_fraud")

        if "LOW_DIAG_DIVERSITY" in pattern:
            with_clauses.append(
                "WITH p, count(c) AS total, collect(DISTINCT c.diagnosis) AS diags "
                "WHERE total > 5 AND size(diags) <= 2"
            )
            return_fields.extend(["total AS total_claims", "diags AS diagnoses"])
            rule_parts.append("low_diversity")

        if not rule_parts:
            continue

        rule_name = "AUTO_RULE_" + "_AND_".join(rule_parts)

        # Build the query (simplified - may need manual refinement)
        cypher = "\n".join(match_clauses)
        if where_clauses:
            cypher += "\nWHERE " + " AND ".join(where_clauses)
        if with_clauses:
            cypher += "\n" + "\n".join(with_clauses)
        cypher += "\nRETURN " + ", ".join(return_fields)
        cypher += "\nORDER BY num_claims DESC LIMIT 50" if "num_claims" in cypher else "\nLIMIT 50"

        rules.append({
            "rule_name": rule_name,
            "pattern": " + ".join(sorted(pattern)),
            "frequency": count,
            "cypher": cypher,
            "description": f"Auto-discovered: {count} suspects match pattern [{' + '.join(sorted(pattern))}]",
        })

    print(f"\n  {len(rules)} Cypher rule candidates generated:\n")
    for i, rule in enumerate(rules):
        print(f"  ┌─ RULE {i+1}: {rule['rule_name']}")
        print(f"  │  Pattern: {rule['pattern']}")
        print(f"  │  Frequency: {rule['frequency']} suspects")
        print(f"  │  Description: {rule['description']}")
        print(f"  │  Cypher:")
        for line in rule["cypher"].split("\n"):
            print(f"  │    {line}")
        print(f"  └{'─' * 65}")

    # ═══════════════════════════════════════════════════════════
    # EXPORT
    # ═══════════════════════════════════════════════════════════
    output = f"08_Auto_Rules_{TODAY}.xlsx"
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_centrality.to_excel(writer, sheet_name="Centrality", index=False)
        if not df_syndicates.empty:
            df_syndicates.to_excel(writer, sheet_name="Syndicates", index=False)

        # Pattern frequency
        pat_df = pd.DataFrame([
            {"pattern": " + ".join(sorted(p)), "count": c,
             "examples": ", ".join(pattern_examples[p][:5])}
            for p, c in sorted_patterns
        ])
        if not pat_df.empty:
            pat_df.to_excel(writer, sheet_name="Patterns", index=False)

        # Rules
        if rules:
            pd.DataFrame(rules).to_excel(writer, sheet_name="Cypher_Rules", index=False)

    print(f"\n[OK] Exported: {output}")
    driver.close()
    print("DONE.")


if __name__ == "__main__":
    main()
