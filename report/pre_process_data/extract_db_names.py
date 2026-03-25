import requests
import json

def extract_db_names():
    url = "http://127.0.0.1:7474/db/system/tx/commit"
    user = "neo4j"
    pas = "Chien@2022"
    
    payload = {
        "statements": [
            {
                "statement": "SHOW DATABASES YIELD name, currentStatus"
            }
        ]
    }
    
    try:
        resp = requests.post(url, auth=(user, pas), json=payload)
        data = resp.json()
        if "results" in data and len(data["results"]) > 0:
            for row in data["results"][0]["data"]:
                print(f"Database: {row['row'][0]} | Status: {row['row'][1]}")
        else:
            print(f"No results or Error: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    extract_db_names()
