import requests
import time

BASE_URL = "http://127.0.0.1:8000/api"

def register(name, email, password, role):
    try:
        res = requests.post(f"{BASE_URL}/register", json={
            "name": name, "email": email, "password": password, "role": role
        })
        if res.status_code == 200:
            return res.json()['id']
        elif res.status_code == 400 and "already registered" in res.text:
            # Login instead
            res = requests.post(f"{BASE_URL}/login", json={"email": email, "password": password})
            return res.json()['id']
        else:
            print(f"Failed to register {name}: {res.text}")
            return None
    except Exception as e:
        print(f"Error registering {name}: {e}")
        return None

def force_match(id1, id2):
    headers1 = {"X-User-Id": str(id1)}
    headers2 = {"X-User-Id": str(id2)}
    
    print(f"User {id1} liking User {id2}...")
    requests.post(f"{BASE_URL}/action",headers=headers1, json={"target_id": id2, "action_type": "like"})
    
    print(f"User {id2} liking User {id1}...")
    requests.post(f"{BASE_URL}/action",headers=headers2, json={"target_id": id1, "action_type": "like"})
    print("Match created (hopefully)!")

if __name__ == "__main__":
    ts = int(time.time())
    email_a = f"alice_{ts}@test.com"
    email_b = f"bob_{ts}@test.com"
    
    id_a = register(f"Alice_{ts}", email_a, "password", "Frontend")
    id_b = register(f"Bob_{ts}", email_b, "password", "Backend")
    
    if id_a and id_b:
        force_match(id_a, id_b)
        print(f"\n--- CREDENTIALS ---")
        print(f"Use these to login:")
        print(f"Email: {email_a}")
        print(f"Password: password")
        print(f"-------------------")
    else:
        print("Failed to Setup users")
