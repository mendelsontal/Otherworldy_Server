from server.db.database import Database, init_db

def main():
    init_db()
    
    username = "testuser2"
    password = "password123"

    # Only create if doesn't exist
    if not Database.verify_user(username, password):
        user = Database.create_user(username, password)
        print(f"Created user: {user.username}")
    else:
        print(f"User '{username}' already exists")

if __name__ == "__main__":
    main()
