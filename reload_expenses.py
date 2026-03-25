"""
Reload Expense nodes với đúng column mapping.
Chỉ xóa Expense + HAS_EXPENSE, KHÔNG ảnh hưởng data khác.

Chạy: python reload_expenses.py
"""
from neo4j import GraphDatabase
import pandas as pd
import glob
import os

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Chien@2022"
NEO4J_DB = "neo4j"
BASE_DIR = r"D:\desktop_folder\04_Fraud_Detection\report\data_splits"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def run(query, params=None):
    with driver.session(database=NEO4J_DB) as s:
        result = s.run(query, params)
        return result.consume()


# Bước 1: Xóa toàn bộ Expense cũ
print("Xóa Expense cũ (batch)...")
while True:
    info = run("""
        MATCH (e:Expense)
        WITH e LIMIT 5000
        DETACH DELETE e
        RETURN count(*) AS deleted
    """)
    deleted = info.counters.nodes_deleted
    print(f"  Đã xóa {deleted} nodes")
    if deleted == 0:
        break

print("Đã xóa hết Expense cũ.\n")

# Bước 2: Load lại với đúng column mapping
files = sorted(glob.glob(os.path.join(BASE_DIR, "DataChiPhi_chunks", "*.csv")))
total_created = 0

for f in files:
    fname = os.path.basename(f)
    print(f"Loading {fname}...")
    df = pd.read_csv(f)
    df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce')
    df['total_amount'] = pd.to_numeric(df['total_amount'], errors='coerce')
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')

    rows = df.where(pd.notnull(df), None).to_dict('records')

    # Batch 2000 rows mỗi lần
    batch_size = 2000
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        run("""
            UNWIND $rows AS row
            MATCH (c:Claim {claim_id: row.claim_id})
            CREATE (e:Expense {
                item_name: row.drug_or_service_name,
                category: row.category,
                item_type: row.item_type,
                unit_price: row.unit_price,
                amount: row.total_amount,
                quantity: row.quantity,
                unit: row.unit
            })
            CREATE (c)-[:HAS_EXPENSE]->(e)
        """, {"rows": batch})
        total_created += len(batch)
        print(f"  Batch {i // batch_size + 1}: {len(batch)} rows")

print(f"\nHoàn tất! Tổng {total_created} Expense nodes đã được tạo.")

# Bước 3: Kiểm tra nhanh
with driver.session(database=NEO4J_DB) as s:
    r = s.run("MATCH (e:Expense) RETURN count(e) AS cnt, count(e.amount) AS has_amt, count(e.item_name) AS has_name").single()
    print(f"Kiểm tra: {r['cnt']} Expense, {r['has_amt']} có amount, {r['has_name']} có item_name")

    r2 = s.run("MATCH (e:Expense) WHERE e.amount > 0 RETURN avg(e.amount) AS avg_price, min(e.amount) AS min_p, max(e.amount) AS max_p").single()
    print(f"Amount: avg={r2['avg_price']:.0f}, min={r2['min_p']}, max={r2['max_p']}")

    r3 = s.run("MATCH (e:Expense) RETURN DISTINCT e.category AS cat, count(*) AS cnt ORDER BY cnt DESC LIMIT 15").data()
    print("Categories:")
    for row in r3:
        print(f"  {row['cat']}: {row['cnt']}")

driver.close()
