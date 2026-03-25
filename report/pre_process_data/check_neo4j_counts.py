from neo4j import GraphDatabase

def check_counts():
    uri = "bolt://localhost:7687"
    user = "neo4j"
    pas = "password"
    
    try:
        driver = GraphDatabase.driver(uri, auth=(user, pas))
        with driver.session() as session:
            res_nodes = session.run("MATCH (n) RETURN count(n) as cnt")
            res_rels = session.run("MATCH ()-[r]->() RETURN count(r) as cnt")
            print(f"Nodes: {res_nodes.single()['cnt']}")
            print(f"Relationships: {res_rels.single()['cnt']}")
            
            # Specific counts
            res_persons = session.run("MATCH (n:Person) RETURN count(n) as cnt")
            print(f"Persons: {res_persons.single()['cnt']}")
            
            res_claims = session.run("MATCH (n:Claim) RETURN count(n) as cnt")
            print(f"Claims: {res_claims.single()['cnt']}")
        driver.close()
    except Exception as e:
        print(f"Feiled: {e}")

if __name__ == "__main__":
    check_counts()
