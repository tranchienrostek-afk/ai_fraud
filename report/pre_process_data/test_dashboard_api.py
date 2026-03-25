import requests
import json

def test_dashboard():
    url = "http://127.0.0.1:8000/api/overview"
    print(f"Testing Dashboard API at {url}...")
    try:
        resp = requests.get(url, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Response: {json.dumps(resp.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"Failed to connect to Dashboard: {e}")

if __name__ == "__main__":
    test_dashboard()
