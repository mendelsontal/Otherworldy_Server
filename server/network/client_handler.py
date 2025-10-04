# server/network/client_handler.py
import threading
import socket
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from server.network.protocol import Protocol, ProtocolError
from server.db.database import SessionLocal, pwd_context
from server.db.models import User
from server.db.characters import create_character, delete_character, check_name
import re
import json

class ClientHandler(threading.Thread):
    def __init__(self, client_socket: socket.socket, address, server):
        super().__init__(daemon=True)
        self.client_socket = client_socket
        self.address = address
        self.server = server
        self.running = True
        self.username = None
        self.user_id = None
        self.recv_buffer = ""

    def run(self):
        print(f"[+] Client connected: {self.address}")
        try:
            while self.running:
                data = self.client_socket.recv(4096)
                if not data:
                    break
                self.recv_buffer += data.decode("utf-8")
                while "\n" in self.recv_buffer:
                    line, self.recv_buffer = self.recv_buffer.split("\n", 1)
                    if line.strip():
                        self.handle_message(line.strip())
        except ConnectionResetError:
            print(f"[-] Connection reset by {self.address}")
        finally:
            self.disconnect()

    def handle_message(self, message_str: str):
        try:
            message = Protocol.decode(message_str.encode("utf-8"))
        except ProtocolError:
            try:
                message = json.loads(message_str)
            except json.JSONDecodeError:
                self.send_error("Invalid message format")
                return

        if not isinstance(message, dict):
            self.send_error("Invalid message type")
            return

        action = message.get("action")
        data = message.get("data", {})

        if action == "signup":
            self.handle_signup(data)
        elif action == "login":
            self.handle_login(data)
        elif action == "create_character":
            self.handle_create_character(data)
        elif action == "delete_character":
            self.handle_delete_character(data)
        elif action == "check_name":
            self.handle_check_name(data)
        else:
            self.send_error(f"Unknown action: {action}")
    
    def handle_signup(self, data):
        """Handle new user registration."""
        first_name = data.get("first_name", "").strip()
        last_name = data.get("last_name", "").strip()
        username = data.get("username", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()
        confirm_password = data.get("confirm_password", "").strip()

        username = username.lower()
        email = email.lower()

        # Basic validation
        if not all([first_name, last_name, username, email, password, confirm_password]):
            self.send_json({"action": "signup_failed", "reason": "All fields are required"})
            return
        if password != confirm_password:
            self.send_json({"action": "signup_failed", "reason": "Passwords do not match"})
            return
        if len(username) < 6 or len(password) < 6:
            self.send_json({"action": "signup_failed", "reason": "Username and password must be at least 6 characters"})
            return
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self.send_json({"action": "signup_failed", "reason": "Invalid email"})
            return

        session = SessionLocal()
        try:
            # Check for existing username or email
            existing = session.query(User).filter((User.username == username) | (User.email == email)).first()
            if existing:
                self.send_json({"action": "signup_failed", "reason": "Username or email already exists"})
                return

            # Create user
            hashed_pw = pwd_context.hash(password)
            user = User(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password_hash=hashed_pw
            )
            session.add(user)
            session.commit()

            self.send_json({"action": "signup_ok", "user_id": user.id, "username": user.username})
            print(f"[+] New user registered: {username}")
        except Exception as e:
            session.rollback()
            self.send_json({"action": "signup_failed", "reason": str(e)})
        finally:
            session.close()

    def handle_login(self, data):
        username = data.get("username")
        password = data.get("password")

        session = SessionLocal()
        try:
            stmt = select(User).options(selectinload(User.characters)).where(User.username == username)
            user = session.execute(stmt).scalar_one_or_none()

            if not user:
                self.send_json({"action": "login_failed", "reason": "User not found"})
                return

            if not pwd_context.verify(password, user.password_hash):
                self.send_json({"action": "login_failed", "reason": "Invalid password"})
                return

            self.username = user.username
            self.user_id = user.id
            self.send_character_list()
        finally:
            session.close()

    def handle_create_character(self, data):
        if not self.user_id:
            self.send_error("Not logged in")
            return

        name = data.get("name")
        if not name:
            self.send_error("Character name missing")
            return
        gender = data.get("gender", "Male")
        hair = data.get("hair")

        try:
            char = create_character(self.user_id, name, gender, hair)
        except ValueError as e:
            self.send_error(str(e))
            return

        self.send_json({
            "action": "character_created",
            "user_id": self.user_id,
            "character": char.as_dict()
        })
        self.send_character_list()

    def handle_delete_character(self, data):
        if not self.user_id:
            self.send_error("Not logged in")
            return

        char_id = data.get("char_id")
        if not char_id:
            self.send_error("Missing character ID")
            return

        success = delete_character(self.user_id, char_id)
        if success:
            self.send_json({
                "action": "delete_character_ok",
                "char_id": char_id,
                "user_id": self.user_id
            })
            self.send_character_list()
        else:
            self.send_error("Character not found or not owned by user")

    def handle_check_name(self, data):
        name = data.get("name")
        if not name:
            self.send_json({"action": "name_valid", "ok": False, "reason": "No name provided"})
            return

        ok, reason = check_name(name)
        self.send_json({"action": "name_valid", "ok": ok, "reason": reason})

    def send_character_list(self):
        if not self.user_id:
            self.send_error("Not logged in")
            return

        session = SessionLocal()
        try:
            stmt = select(User).options(selectinload(User.characters)).where(User.id == self.user_id)
            user = session.execute(stmt).scalar_one_or_none()
            if not user:
                self.send_error("User not found")
                return

            self.send_json({
                "action": "character_list",
                "user": {"id": user.id, "username": user.username},
                "characters": [char.as_dict() for char in user.characters]
            })
        finally:
            session.close()

    def send_json(self, message: dict):
        try:
            self.client_socket.sendall((json.dumps(message) + "\n").encode("utf-8"))
        except Exception as e:
            print(f"[!] Failed to send to {self.address}: {e}")

    def send_error(self, error_msg: str):
        self.send_json({"status": "error", "message": error_msg})

    def disconnect(self):
        self.running = False
        if self.username:
            print(f"[-] {self.username} disconnected")
        else:
            print(f"[-] Client {self.address} disconnected")
        self.client_socket.close()
        self.server.remove_client(self)
