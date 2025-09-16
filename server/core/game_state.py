# server/core/game_state.py

import threading
from collections import defaultdict

class GameState:
    """
    Holds the current game state: players, world, channels, etc.
    Thread-safe access for concurrent client connections.
    """
    def __init__(self):
        self.players = {}  # key: player_id, value: player object/dict
        self.world_objects = {}  # key: object_id, value: object data
        self.channels = defaultdict(list)  # key: channel_id, value: list of player_ids
        self.lock = threading.RLock()

    def add_player(self, player_id, player_data):
        with self.lock:
            self.players[player_id] = player_data

    def remove_player(self, player_id):
        with self.lock:
            if player_id in self.players:
                del self.players[player_id]
            # Remove from channels too
            for ch_players in self.channels.values():
                if player_id in ch_players:
                    ch_players.remove(player_id)

    def move_player_to_channel(self, player_id, channel_id):
        with self.lock:
            # Remove from any previous channel
            for ch_id, ch_players in self.channels.items():
                if player_id in ch_players:
                    ch_players.remove(player_id)
            # Add to new channel
            self.channels[channel_id].append(player_id)

    def get_player(self, player_id):
        with self.lock:
            return self.players.get(player_id)

    def get_players_in_channel(self, channel_id):
        with self.lock:
            return list(self.channels.get(channel_id, []))
