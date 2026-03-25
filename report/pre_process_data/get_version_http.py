import requests
import json

def get_version():
    url = "http://127.0.0.1:7474/db/neo4j/tx/commit"
    user = "neo4j"
    pas = "Chien@2022"
    
    payload = {
        "statements": [
            {
                "statement": "CALL dbms.components() YIELD name, versions, edition RETURN name, versions, edition"
            }
        ]
    }
    
    try:
        resp = requests.post(url, auth=(user, pas), json=payload)
        print(f"Status: {resp.status_code}")
        print(f"Response: {json.dumps(resp.json(), indent=2)}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    get_version()
