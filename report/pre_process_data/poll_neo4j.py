import time
from neo4j import GraphDatabase

def wait_for_neo4j():
    uri = "bolt://localhost:7687"
    user = "neo4j"
    pas = "password"
    
    print(f"Waiting for Neo4j at {uri}...")
    for i in range(20):
        try:
            driver = GraphDatabase.driver(uri, auth=(user, pas))
            with driver.session() as session:
                result = session.run("RETURN 1")
                print(f"Neo4j is READY after {i*5}s!")
                driver.close()
                return True
        except Exception:
            print(f"Still waiting... ({i*5}s)")
            time.sleep(5)
    print("Neo4j failed to start in time.")
    return False

if __name__ == "__main__":
    wait_for_neo4j()
