# server/network/client_handler.py
import threading
import socket
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from server.network.protocol import Protocol, ProtocolError
from server.db.database import SessionLocal, pwd_context
from server.db.models import User
from server.db.characters import create_character, delete_character, check_name
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

    def handle_check_name(self, data):
        name = data.get("name")
        if not name:
            self.send_json({
                "action": "name_valid",
                "ok": False,
                "reason": "No name provided"
            })
            return

        ok, reason = check_name(name)
        self.send_json({
            "action": "name_valid",
            "ok": ok,
            "reason": reason
    })

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
        elif action == "delete_character":
            self.handle_delete_character(data)
        elif action == "check_name":
            self.handle_check_name(data)
        else:
            self.send_error(f"Unknown action: {action}")

    def send_character_list(self):
        """Send the full character list for the logged-in user."""
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

            characters = []
            for char in user.characters:
                characters.append({
                    "id": char.id,
                    "name": char.name,
                    "x": char.x,
                    "y": char.y,
                    "map_id": char.map_id,
                    "appearance": char.appearance,
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
                "user": {"id": user.id, "username": user.username},
                "characters": characters
            })
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

            # Send full character list
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
            "character": {
                "id": char.id,
                "name": char.name,
                "x": char.x,
                "y": char.y,
                "map_id": char.map_id,
                "appearance": char.appearance,
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

        # Send updated character list
        self.send_character_list()

    def handle_delete_character(self, data):
        if not hasattr(self, "user_id"):
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
            # Send updated character list
            self.send_character_list()
        else:
            self.send_error("Character not found or not owned by user")

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
