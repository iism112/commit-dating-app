import asyncio
import websockets
import json
import requests
import threading
import time

# Install websockets: pip install websockets

BASE_HTTP = "http://127.0.0.1:8000/api"
BASE_WS = "ws://127.0.0.1:8000/ws"

async def listen_for_messages(user_id, expected_msg_text):
    uri = f"{BASE_WS}/{user_id}"
    print(f"   [User {user_id}] Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print(f"   [User {user_id}] Connected!")
            
            # Wait for message with timeout
            try:
                msg = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(msg)
                print(f"   [User {user_id}] Received: {data}")
                
                if data.get('text') == expected_msg_text:
                    print(f"   [User {user_id}] SUCCESS: Verified message content.")
                else:
                    print(f"   [User {user_id}] FAILURE: Content mismatch.")
            except asyncio.TimeoutError:
                print(f"   [User {user_id}] TIMEOUT: Did not receive message in 5s.")

    except Exception as e:
        print(f"   [User {user_id}] Error: {e}")

def trigger_message(sender_id, receiver_id, text):
    time.sleep(2) # Give WS time to connect
    print(f"   [Sender {sender_id}] Sending HTTP POST msg to {receiver_id}...")
    requests.post(f"{BASE_HTTP}/messages", 
                  json={"match_id": receiver_id, "text": text}, 
                  headers={"X-User-Id": str(sender_id)})

def run_test():
    # 1. Setup Users (Reuse IDs from previous tests if possible, simplified here)
    # We will assume User 3 and User 4 from previous test exist and matched
    alice_id = 3
    bob_id = 4
    
    msg_text = f"WS Test {int(time.time())}"

    # 2. Start Listener (Bob)
    print("--- Starting WS Listener (Bob) ---")
    
    # Run async listener
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Start Sender in parallel thread
    t = threading.Thread(target=trigger_message, args=(alice_id, bob_id, msg_text))
    t.start()
    
    # Block until message received or timeout
    loop.run_until_complete(listen_for_messages(bob_id, msg_text))
    t.join()

if __name__ == "__main__":
    run_test()
