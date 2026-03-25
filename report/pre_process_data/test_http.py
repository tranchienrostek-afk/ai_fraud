import requests
from requests.auth import HTTPBasicAuth

def test_http():
    url = "http://127.0.0.1:7474/"
    user = "neo4j"
    pas = "Chien@2022"
    
    print(f"Testing HTTP at {url} with {pas}...")
    try:
        resp = requests.get(url, auth=HTTPBasicAuth(user, pas), timeout=5)
        print(f"Status: {resp.status_code}")
        print(f"Body: {resp.text[:500]}")
    except Exception as e:
        print(f"Failed HTTP: {e}")

if __name__ == "__main__":
    test_http()
