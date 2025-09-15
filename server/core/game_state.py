# Starter code for game_state.py

class GameState:
    def __init__(self):
        self.players = {}  # {player_id: {"x": 0, "y": 0, "hp": 100}}
        self.world = {}    # map tiles, items, monsters

    def get_player(self, player_id):
        return self.players.get(player_id)

    def update_player(self, player_id, data):
        if player_id in self.players:
            self.players[player_id].update(data)
