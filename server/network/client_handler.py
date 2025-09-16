# server/network/client_handler.py
import threading
import socket
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from server.network.protocol import Protocol, ProtocolError
from server.db.database import Database, SessionLocal, pwd_context
from server.db.models import User
from server.db.characters import create_character
import json

class ClientHandler(threading.Thread):
    def __init__(self, client_socket: socket.socket, address, server):
        super().__init__(daemon=True)
        self.client_socket = client_socket
        self.address = address
        self.server = server
        self.running = True
        self.username = None
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
        message = None
        try:
            message = Protocol.decode(message_str.encode("utf-8"))
        except ProtocolError:
            pass

        if message is None:
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

        if action == "login":
            self.handle_login(data)
        elif action == "create_character":
            self.handle_create_character(data)
        else:
            self.send_error(f"Unknown action: {action}")

    def handle_create_character(self, data):
        if not hasattr(self, "user_id"):
            self.send_error("Not logged in")
            return

        name = data.get("name")
        if not name:
            self.send_error("Character name missing")
            return

        try:
            char = create_character(self.user_id, name)
        except ValueError as e:
            self.send_error(str(e))
            return

        self.send_json({
            "action": "character_created",
            "character": {
                "id": char.id,
                "name": char.name,
                "x": char.x,
                "y": char.y,
                "map_id": char.map_id,
                "stats": {
                    "Level": char.level,
                    "Exp": char.exp,
                    "HP": char.hp,
                    "MP": char.mp,
                    "STR": char.str,
                    "DEX": char.dex,
                    "AGI": char.agi,
                    "VIT": char.vit,
                    "INT": char.int
                }
            }
        })

        name = data.get("name")
        if not name:
            self.send_error("Character name missing")
            return

        char = create_character(self.user_id, name)

    def handle_login(self, data):
        username = data.get("username")
        password = data.get("password")

        # Use a session to fetch user with eager-loaded characters
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

            # Save username and user_id AFTER user is verified
            self.username = user.username
            self.user_id = user.id

            # Prepare characters for client
            characters = []
            for char in user.characters:  # safe, eager-loaded
                characters.append({
                    "id": char.id,
                    "name": char.name,
                    "x": char.x,
                    "y": char.y,
                    "map_id": char.map_id,
                    "stats": {
                        "Level": char.level,
                        "Exp": char.exp,
                        "HP": char.hp,
                        "MP": char.mp,
                        "STR": char.str,
                        "DEX": char.dex,
                        "AGI": char.agi,
                        "VIT": char.vit,
                        "INT": char.int
                    }
                })

            self.send_json({
                "action": "character_list",
                "user": {"username": user.username},
                "characters": characters
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
