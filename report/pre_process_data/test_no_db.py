from neo4j import GraphDatabase

def test_no_db():
    uri = "bolt://localhost:7687"
    user = "neo4j"
    pas = "Chien@2022"
    try:
        driver = GraphDatabase.driver(uri, auth=(user, pas))
        # No database specified
        with driver.session() as session:
            result = session.run("RETURN 1")
            print(f"Success with NO DB: {result.single()[0]}")
        driver.close()
    except Exception as e:
        print(f"Failed with NO DB: {e}")

if __name__ == "__main__":
    test_no_db()
