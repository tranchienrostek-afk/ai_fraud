import requests
import json

def test_neo4j_http_query():
    url = "http://127.0.0.1:7474/db/neo4j/tx/commit"
    user = "neo4j"
    pas = "Chien@2022"
    
    payload = {
        "statements": [
            {
                "statement": "RETURN 1 as val"
            }
        ]
    }
    
    print(f"Testing HTTP Query at {url}...")
    try:
        resp = requests.post(
            url, 
            auth=(user, pas), 
            json=payload,
            headers={"Accept": "application/json", "Content-Type": "application/json"}
        )
        print(f"Status: {resp.status_code}")
        print(f"Response: {json.dumps(resp.json(), indent=2)}")
    except Exception as e:
        print(f"Failed HTTP Query: {e}")

if __name__ == "__main__":
    test_neo4j_http_query()
