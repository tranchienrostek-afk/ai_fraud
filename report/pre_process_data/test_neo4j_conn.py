from neo4j import GraphDatabase
import sys

URI = "bolt://127.0.0.1:7687"
USER = "neo4j"
PASS = "Chien@2022"

def check():
    try:
        driver = GraphDatabase.driver(URI, auth=(USER, PASS))
        driver.verify_connectivity()
        print("Connection successful!")
        with driver.session() as session:
            result = session.run("RETURN 1 as val")
            print(f"Query test: {result.single()['val']}")
        driver.close()
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check()
