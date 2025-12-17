import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"
HEADERS = {"X-User-Id": "3"}

def test_endpoint(endpoint):
    print(f"\nFetching {endpoint}...")
    try:
        res = requests.get(f"{BASE_URL}{endpoint}", headers=HEADERS)
        if res.status_code == 200:
            data = res.json()
            print(f"Status: 200 OK")
            print(f"Count: {len(data)}")
            
            # Print first item as sample
            if len(data) > 0:
                print("Sample Item:")
                print(json.dumps(data[0], indent=2))
            
            for item in data:
                if 'id' not in item or item['id'] is None:
                    print(f"ERROR: Item missing 'id' or is None in {endpoint}: {item}")
        else:
            print(f"Error: {res.status_code} {res.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_endpoint("/matches")
    test_endpoint("/profiles")
