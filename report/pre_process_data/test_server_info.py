from neo4j import GraphDatabase

def get_server_info():
    uri = "bolt://127.0.0.1:7687"
    user = "neo4j"
    password = "Chien@2022"
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        # This should work without running a cypher query
        info = driver.get_server_info()
        print(f"Address: {info.address}")
        print(f"Agent: {info.agent}")
        print(f"Protocol Version: {info.protocol_version}")
        driver.close()
    except Exception as e:
        print(f"Failed to get info: {e}")

if __name__ == "__main__":
    get_server_info()
