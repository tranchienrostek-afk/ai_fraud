import requests
import json

def extract_endpoints():
    url = "http://127.0.0.1:7474/"
    user = "neo4j"
    pas = "Chien@2022"
    
    try:
        resp = requests.get(url, auth=(user, pas))
        data = resp.json()
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    extract_endpoints()
