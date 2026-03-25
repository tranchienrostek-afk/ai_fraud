import pandas as pd
from neo4j import GraphDatabase

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Chien@2022"

df = pd.read_csv(r'D:\desktop_folder\04_Fraud_Detection\report\data_splits\DataNDBH_chunks\DataNDBH_part1.csv', nrows=100)
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

found = 0
missing = []

with driver.session() as session:
    for _, row in df.iterrows():
        uid = row['user_id']
        res = session.run('MATCH (p:Person {user_id: $uid}) RETURN p.user_id', {"uid": uid})
        if res.single():
            found += 1
        else:
            missing.append(uid)

driver.close()
print(f"Total Rows Checked: {len(df)}")
print(f"Found in Neo4j: {found}")
print(f"Missing from Neo4j: {len(missing)}")
if missing:
    print(f"Sample Missing: {missing[:5]}")
