from server.db.database import Database, init_db

def main():
    init_db()
    
    username = "1234567"
    password = "1234567"

    if not Database.verify_user(username, password):
        user = Database.create_user(username, password)
        print(f"Created user: {user.username}")  # ✅ no DetachedInstanceError
    else:
        print(f"User '{username}' already exists")

if __name__ == "__main__":
    main()
