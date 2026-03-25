from neo4j import GraphDatabase
import sys

def clear_neo4j():
    uri = "neo4j://127.0.0.1:7687"
    user = "neo4j"
    password = "Chien@2022"

    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            print("Clearing database...")
            # detachment delete everything
            session.run("MATCH (n) DETACH DELETE n")
            print("Database cleared.")
        driver.close()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    clear_neo4j()
