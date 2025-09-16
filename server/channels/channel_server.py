# server/channels/channel_server.py
import threading
from server.network.client_handler import ClientHandler

class ChannelServer:
    def __init__(self, channel_id, max_clients=100):
        self.channel_id = channel_id
        self.max_clients = max_clients
        self.clients = []  # list of ClientHandler instances
        self.lock = threading.Lock()
        self.running = True

    def add_client(self, client_handler: ClientHandler):
        with self.lock:
            if len(self.clients) >= self.max_clients:
                return False
            self.clients.append(client_handler)
            client_handler.channel = self
            return True

    def remove_client(self, client_handler: ClientHandler):
        with self.lock:
            if client_handler in self.clients:
                self.clients.remove(client_handler)
                client_handler.channel = None

    def broadcast(self, message: str, exclude_client=None):
        """Send a message to all clients in the channel except exclude_client."""
        with self.lock:
            for client in self.clients:
                if client != exclude_client:
                    client.send(message)

    def stop(self):
        """Stop the channel server and disconnect all clients."""
        with self.lock:
            self.running = False
            for client in self.clients:
                client.disconnect()
            self.clients.clear()
