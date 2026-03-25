from neo4j import GraphDatabase
import sys

URI = "bolt://127.0.0.1:7687"
USER = "neo4j"
PASS = "Chien@2022"

def test_constraints():
    driver = GraphDatabase.driver(URI, auth=(USER, PASS))
    with driver.session() as session:
        print("Testing Neo4j 5.x syntax...")
        try:
            session.run("CREATE CONSTRAINT test_5 IF NOT EXISTS FOR (p:Person) REQUIRE p.test_id IS UNIQUE")
            print("  5.x syntax works!")
            session.run("DROP CONSTRAINT test_5")
            return "5.x"
        except Exception as e:
            print(f"  5.x syntax failed: {e}")
            
        print("Testing Neo4j 4.x syntax...")
        try:
            session.run("CREATE CONSTRAINT ON (p:Person) ASSERT p.test_id IS UNIQUE")
            print("  4.x syntax works!")
            session.run("DROP CONSTRAINT ON (p:Person) ASSERT p.test_id IS UNIQUE")
            return "4.x"
        except Exception as e:
            print(f"  4.x syntax failed: {e}")
            
    driver.close()
    return "unknown"

if __name__ == "__main__":
    version_syntax = test_constraints()
    print(f"Detected syntax version: {version_syntax}")
