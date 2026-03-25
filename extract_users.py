from neo4j import GraphDatabase
import os

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Chien@2022"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
with driver.session() as session:
    res = session.run('MATCH (p:Person) WHERE p.phone_number CONTAINS "985048243" RETURN p.user_id, p.full_name')
    users = [f"{r[0]}|{r[1]}" for r in res]

with open(r'D:\desktop_folder\04_Fraud_Detection\suspicious_user_ids.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(users))

driver.close()
print(f"Extracted {len(users)} users.")
