from neo4j import GraphDatabase

# Config
NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Chien@2022"
NEO4J_DB = "neo4j"

def cleanup_scaling():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session(database=NEO4J_DB) as session:
        print("Scaling Expense nodes...")
        session.run("MATCH (e:Expense) SET e.unit_price = toFloat(e.unit_price) / 100.0, e.amount = toFloat(e.amount) / 100.0")
        
        print("Scaling Claim nodes...")
        session.run("MATCH (c:Claim) SET c.amount = toFloat(c.amount) / 100.0")
        
        print("Scaling Person nodes...")
        session.run("MATCH (p:Person) SET p.salary = toFloat(p.salary) / 100.0")
        
    driver.close()
    print("Neo4j data normalization completed.")

if __name__ == "__main__":
    cleanup_scaling()
