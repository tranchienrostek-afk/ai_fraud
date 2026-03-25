from neo4j import GraphDatabase

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Chien@2022"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
with driver.session() as session:
    # 1. Check specific User ID
    user_id = "499401dd-444f-460d-a0a1-77ffc0c507c5"
    res = session.run('MATCH (p:Person {user_id: $uid}) RETURN p.full_name, p.phone_number', {"uid": user_id})
    record = res.single()
    if record:
        print(f"User {user_id} found: Name={record[0]}, Phone={record[1]}")
    else:
        print(f"User {user_id} NOT found.")
    
    # 2. Check ANY phone containing the pattern
    phone_pattern = "985048243"
    res = session.run('MATCH (p:Person) WHERE p.phone_number CONTAINS $pat RETURN p.user_id, p.full_name LIMIT 5', {"pat": phone_pattern})
    matches = list(res)
    print(f"Nodes containing '{phone_pattern}': {len(matches)}")
    for m in matches:
        print(f" - {m[0]}: {m[1]}")

driver.close()
