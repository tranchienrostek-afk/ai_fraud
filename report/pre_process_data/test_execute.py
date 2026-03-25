from neo4j import GraphDatabase

def test_execute_query():
    uri = "bolt://127.0.0.1:7687"
    user = "neo4j"
    password = "Chien@2022"
    database = "neo4j"
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        records, summary, keys = driver.execute_query(
            "RETURN 1 as val",
            database_=database
        )
        print(f"Success: {records[0]['val']}")
        driver.close()
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_execute_query()
