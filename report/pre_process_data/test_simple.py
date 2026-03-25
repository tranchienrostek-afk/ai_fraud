from neo4j import GraphDatabase

def test_return_1():
    uri = "bolt://127.0.0.1:7687"
    user = "neo4j"
    password = "Chien@2022"
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            result = session.run("RETURN 1 as val")
            print(f"Success: {result.single()['val']}")
        driver.close()
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_return_1()
