import sqlite3

def inspect_db():
    conn = sqlite3.connect('commit_dating.db')
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("TABLES:", tables)

    print("--- USERS ---")
    cursor.execute("SELECT id, name, email, password FROM users")
    users = cursor.fetchall()
    for u in users:
        print(u)
        if u[0] is None:
            print("ALERT: User with NULL ID found!")

    print("\n--- MATCHES ---")
    cursor.execute("SELECT id, user1_id, user2_id FROM matches")
    matches = cursor.fetchall()
    for m in matches:
        print(m)
        if m[0] is None or m[1] is None or m[2] is None:
            print("ALERT: Match with NULL ID found!")

    conn.close()

if __name__ == "__main__":
    inspect_db()
