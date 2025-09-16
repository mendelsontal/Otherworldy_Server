# server/channels/channel_manager.py
from server.channels.channel_server import ChannelServer
from server.network.client_handler import ClientHandler
import threading

class ChannelManager:
    def __init__(self, max_clients_per_channel=100):
        self.channels = {}  # channel_id -> ChannelServer
        self.lock = threading.Lock()
        self.max_clients_per_channel = max_clients_per_channel
        self.next_channel_id = 1

    def create_channel(self):
        """Create a new channel and return it."""
        with self.lock:
            channel_id = self.next_channel_id
            self.next_channel_id += 1
            channel = ChannelServer(channel_id, self.max_clients_per_channel)
            self.channels[channel_id] = channel
            return channel

    def get_channel(self, channel_id):
        """Retrieve a channel by its ID."""
        return self.channels.get(channel_id)

    def assign_client_to_channel(self, client: ClientHandler):
        """Assign a client to an existing channel with space, or create a new one."""
        with self.lock:
            for channel in self.channels.values():
                if len(channel.clients) < channel.max_clients:
                    channel.add_client(client)
                    return channel

            # No available channel, create a new one
            new_channel = self.create_channel()
            new_channel.add_client(client)
            return new_channel

    def remove_client_from_channel(self, client: ClientHandler):
        """Remove a client from whichever channel they belong to."""
        with self.lock:
            channel = client.channel
            if channel:
                channel.remove_client(client)
                # Optionally remove empty channels
                if len(channel.clients) == 0:
                    del self.channels[channel.channel_id]
