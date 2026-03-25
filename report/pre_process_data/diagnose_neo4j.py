from neo4j import GraphDatabase
import sys

URI = "bolt://127.0.0.1:7687"
USER = "neo4j"
PASS = "Chien@2022"

def diagnose():
    try:
        driver = GraphDatabase.driver(URI, auth=(USER, PASS))
        with driver.session() as session:
            # Check Version
            version = session.run("CALL dbms.components() YIELD name, versions, edition RETURN name, versions, edition").single()
            print(f"Neo4j Version: {version['versions'][0]} ({version['edition']})")
            
            # Check Counts
            counts = session.run("MATCH (n) RETURN labels(n)[0] as label, count(*) as count")
            print("Node Counts:")
            for r in counts:
                print(f"  {r['label']}: {r['count']}")
                
        driver.close()
    except Exception as e:
        print(f"Diagnosis failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    diagnose()
