import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

def run_test():
    print("1. Creating User A...")
    user_a = requests.post(f"{BASE_URL}/register", json={
        "name": "User A", 
        "email": "a_bi@test.com", 
        "password": "pass", 
        "role": "Tester"
    }).json()
    id_a = user_a.get('id')
    print(f"   User A ID: {id_a}")

    print("2. Creating User B...")
    user_b = requests.post(f"{BASE_URL}/register", json={
        "name": "User B", 
        "email": "b_bi@test.com", 
        "password": "pass", 
        "role": "Tester"
    }).json()
    id_b = user_b.get('id')
    print(f"   User B ID: {id_b}")
    
    # Create Match
    print("3. Creating Match...")
    # A likes B
    requests.post(f"{BASE_URL}/action", json={"target_id": id_b, "action_type": "like"}, headers={"X-User-Id": str(id_a)})
    # B likes A (Match triggered here by B)
    requests.post(f"{BASE_URL}/action", json={"target_id": id_a, "action_type": "like"}, headers={"X-User-Id": str(id_b)})

    # Test Direction 1: A -> B
    print("\n--- Test 1: A sends to B ---")
    requests.post(f"{BASE_URL}/messages", json={"match_id": id_b, "text": "Msg from A"}, headers={"X-User-Id": str(id_a)})
    
    notif_b = requests.get(f"{BASE_URL}/notifications", headers={"X-User-Id": str(id_b)}).json()
    count_b = notif_b.get('unread_count')
    print(f"   Unread Count for B (Should be 1): {count_b}")
    
    if count_b == 1:
        print("   PASS: B received notification.")
    else:
        print("   FAIL: B did not receive notification.")

    # Mark as read for B
    print("   B reads messages...")
    requests.get(f"{BASE_URL}/messages/{id_a}", headers={"X-User-Id": str(id_b)})


    # Test Direction 2: B -> A
    print("\n--- Test 2: B sends to A ---")
    requests.post(f"{BASE_URL}/messages", json={"match_id": id_a, "text": "Msg from B"}, headers={"X-User-Id": str(id_b)})
    
    notif_a = requests.get(f"{BASE_URL}/notifications", headers={"X-User-Id": str(id_a)}).json()
    count_a = notif_a.get('unread_count')
    print(f"   Unread Count for A (Should be 1): {count_a}")

    if count_a == 1:
        print("   PASS: A received notification.")
    else:
        print("   FAIL: A did not receive notification.")

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        print(f"Error: {e}")
