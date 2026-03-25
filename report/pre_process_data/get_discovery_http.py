import requests
import json

def get_discovery():
    url = "http://127.0.0.1:7474/"
    user = "neo4j"
    pas = "Chien@2022"
    
    try:
        resp = requests.get(url, auth=(user, pas))
        print(f"Status: {resp.status_code}")
        print(f"Response: {json.dumps(resp.json(), indent=2)}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    get_discovery()
