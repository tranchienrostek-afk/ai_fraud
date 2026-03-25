from neo4j import GraphDatabase

def test_pass(p):
    uri = "bolt://localhost:7687"
    user = "neo4j"
    print(f"Testing password: {p}")
    try:
        driver = GraphDatabase.driver(uri, auth=(user, p))
        with driver.session() as session:
            result = session.run("RETURN 1")
            print(f"  SUCCESS with {p}!")
        driver.close()
        return True
    except Exception as e:
        print(f"  FAILED with {p}: {e}")
        return False

if __name__ == "__main__":
    test_pass("Chien@2022")
    test_pass("password")
    test_pass("neo4j")
