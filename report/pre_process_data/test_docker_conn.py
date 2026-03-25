from neo4j import GraphDatabase

def test_docker_neo4j():
    uri = "bolt://localhost:7687"
    user = "neo4j"
    pas = "password"
    
    print(f"Testing Docker Neo4j at {uri}...")
    try:
        driver = GraphDatabase.driver(uri, auth=(user, pas))
        with driver.session() as session:
            result = session.run("RETURN 1 as val")
            print(f"Success: {result.single()['val']}")
        driver.close()
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_docker_neo4j()
