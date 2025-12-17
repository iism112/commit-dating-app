import urllib.request
import urllib.error
import json

BASE_URL = "http://127.0.0.1:8000/api"

def make_request(url, method="GET", data=None, headers=None):
    if headers is None: headers = {}
    
    req = urllib.request.Request(url, method=method, headers=headers)
    if data:
        req.data = json.dumps(data).encode('utf-8')
        req.add_header('Content-Type', 'application/json')
        
    try:
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_api():
    print("Logging in/Registering...")
    
    # Try Login
    reg_data = {
        "name": "Debug Bot",
        "email": "debug@bot.com",
        "password": "pass",
        "role": "Debugger"
    }
    
    user_data = make_request(f"{BASE_URL}/login", "POST", {"email": "debug@bot.com", "password": "pass"})
    
    if not user_data:
        print("Login failed, trying register...")
        user_data = make_request(f"{BASE_URL}/register", "POST", reg_data)
        
    if not user_data:
        print("Auth failed completely.")
        return

    user_id = user_data['id']
    print(f"Authenticated as ID: {user_id}")
    
    headers = {"X-User-Id": str(user_id)}
    
    # Get Profile Me
    print("Fetching /profile/me...")
    me = make_request(f"{BASE_URL}/profile/me", "GET", headers=headers)
    print("Me:", json.dumps(me, indent=2))
    
    # Get Specific Profile
    print(f"Fetching /profiles/{user_id} (Self fetch)...")
    target = make_request(f"{BASE_URL}/profiles/{user_id}", "GET", headers=headers)
    
    if target:
        print("SUCCESS: Retrieved specific profile:")
        print(json.dumps(target, indent=2))
    else:
        print("FAILURE: Could not retrieve profile by ID.")

if __name__ == "__main__":
    test_api()
