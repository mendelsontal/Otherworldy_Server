# Starter code for game_engine.py

class GameEngine:
    def __init__(self, state):
        self.state = state

    def apply_action(self, player_id, action):
        player = self.state.get_player(player_id)
        
        if action == "MOVE_UP":
            player["y"] -= 1
        elif action == "MOVE_DOWN":
            player["y"] += 1
        elif action == "ATTACK":
            # placeholder combat logic
            player["hp"] -= 1  
        
        self.state.update_player(player_id, player)
        return player
