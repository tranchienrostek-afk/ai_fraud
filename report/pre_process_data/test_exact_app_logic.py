from neo4j import GraphDatabase
import traceback

def test_exact_app():
    # Credentials from app.py
    NEO4J_URI = "neo4j://127.0.0.1:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASS = "Chien@2022"
    NEO4J_DB = "neo4j"

    print(f"Connecting to {NEO4J_URI} as {NEO4J_USER}...")
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
        driver.verify_connectivity()
        print("Driver connectivity verified!")
        
        # Using the same method as app.py
        records, summary, keys = driver.execute_query(
            "RETURN 1 as val",
            database_=NEO4J_DB
        )
        print(f"Query Success: {records[0]['val']}")
        driver.close()
    except Exception as e:
        print("--- Error Details ---")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_exact_app()
