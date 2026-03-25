import requests
import json

def list_dbs():
    # Attempt to list databases via the system database
    url = "http://127.0.0.1:7474/db/system/tx/commit"
    user = "neo4j"
    pas = "Chien@2022"
    
    payload = {
        "statements": [
            {
                "statement": "SHOW DATABASES"
            }
        ]
    }
    
    print(f"Listing databases at {url}...")
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
        print(f"Failed to list DBs: {e}")

if __name__ == "__main__":
    list_dbs()
