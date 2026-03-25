from neo4j import GraphDatabase
import sys

def test_connection_variations():
    uri = "bolt://127.0.0.1:7687"
    user = "neo4j"
    password = "Chien@2022"
    
    print("Attempting connection with encrypted=False...")
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        with driver.session() as session:
            result = session.run("RETURN 1 as val")
            print(f"Success (encrypted=False): {result.single()['val']}")
        driver.close()
        return
    except Exception as e:
        print(f"Failed (encrypted=False): {e}")

    print("\nAttempting connection with encrypted=True...")
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=True)
        with driver.session() as session:
            result = session.run("RETURN 1 as val")
            print(f"Success (encrypted=True): {result.single()['val']}")
        driver.close()
        return
    except Exception as e:
        print(f"Failed (encrypted=True): {e}")

if __name__ == "__main__":
    test_connection_variations()
