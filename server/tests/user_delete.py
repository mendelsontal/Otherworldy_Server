from server.db.database import Database, init_db

def main():
    init_db()

    username = "1234567"  # 🔹 change this to whichever user you want to delete

    if Database.delete_user(username):
        print(f"User '{username}' deleted successfully.")
    else:
        print(f"User '{username}' not found.")

if __name__ == "__main__":
    main()
