import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_profile_fetch(user_id):
    # Valid header assuming User 5 ("Alice") exists and is logged in or another user (6) looks at her.
    # User 6 is Bob, matches with Alice (5).
    headers = {"X-User-Id": "6"} 
    
    print(f"Fetching profile {user_id} as User 6...")
    try:
        res = requests.get(f"{BASE_URL}/profiles/{user_id}", headers=headers)
        if res.status_code == 200:
            print(f"SUCCESS: {res.json()}")
        else:
            print(f"FAILURE: {res.status_code} {res.text}")
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    test_profile_fetch(5)
