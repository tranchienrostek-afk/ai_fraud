from neo4j import GraphDatabase

def test_cypher_5():
    uri = "bolt://127.0.0.1:7687"
    user = "neo4j"
    password = "Chien@2022"
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session(database="neo4j") as session:
            result = session.run("CYPHER 5 RETURN 1 as val")
            print(f"Success (CYPHER 5): {result.single()['val']}")
        driver.close()
    except Exception as e:
        print(f"Failed (CYPHER 5): {e}")

if __name__ == "__main__":
    test_cypher_5()
