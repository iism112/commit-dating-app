import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

def run_test():
    print("1. Creating User A...")
    user_a = requests.post(f"{BASE_URL}/register", json={
        "name": "User A", 
        "email": "a@test.com", 
        "password": "pass", 
        "role": "Tester"
    }).json()
    id_a = user_a.get('id')
    print(f"   User A ID: {id_a}")

    print("2. Creating User B...")
    user_b = requests.post(f"{BASE_URL}/register", json={
        "name": "User B", 
        "email": "b@test.com", 
        "password": "pass", 
        "role": "Tester"
    }).json()
    id_b = user_b.get('id')
    print(f"   User B ID: {id_b}")
    
    # Create Match (Like each other)
    print("3. Creating Match...")
    requests.post(f"{BASE_URL}/action", json={"target_id": id_b, "action_type": "like"}, headers={"X-User-Id": str(id_a)})
    requests.post(f"{BASE_URL}/action", json={"target_id": id_a, "action_type": "like"}, headers={"X-User-Id": str(id_b)})

    # Send Message A -> B
    print("4. Sending Message A -> B...")
    res = requests.post(f"{BASE_URL}/messages", json={"match_id": id_b, "text": "Hello B!"}, headers={"X-User-Id": str(id_a)})
    print(f"   Send Status: {res.status_code}")

    # Check Notifications for B
    print("5. Checking Notifications for B...")
    notif = requests.get(f"{BASE_URL}/notifications", headers={"X-User-Id": str(id_b)}).json()
    count = notif.get('unread_count')
    print(f"   Unread Count for B: {count}")
    
    if count == 1:
        print("SUCCESS: Unread count correct!")
    else:
        print("FAILURE: Unread count incorrect.")

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        print(f"Error: {e}")
