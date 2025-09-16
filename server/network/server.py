# server/network/server.py
import socket
import threading
from server.network.client_handler import ClientHandler

class GameServer:
    def __init__(self, host="0.0.0.0", port=5000, max_clients=50):
        self.host = host
        self.port = port
        self.max_clients = max_clients
        self.clients = []
        self.running = False
        self.lock = threading.Lock()  # Protect self.clients

    def start(self):
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.max_clients)
        print(f"[+] Server listening on {self.host}:{self.port}")

        try:
            while self.running:
                client_socket, address = self.server_socket.accept()
                handler = ClientHandler(client_socket, address, self)
                handler.start()
                with self.lock:
                    self.clients.append(handler)
        except KeyboardInterrupt:
            print("\n[!] Server shutting down")
            self.stop()

    def remove_client(self, handler: ClientHandler):
        with self.lock:
            if handler in self.clients:
                self.clients.remove(handler)

    def broadcast(self, message: dict):
        """Send a message to all connected clients."""
        with self.lock:
            for client in self.clients:
                client.send_response(message)

    def stop(self):
        self.running = False
        with self.lock:
            for client in self.clients:
                client.disconnect()
        self.server_socket.close()
        print("[+] Server stopped")

# If run directly
if __name__ == "__main__":
    server = GameServer(host="0.0.0.0", port=5000)
    server.start()
