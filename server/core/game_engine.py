# server/core/game_engine.py

import threading
import time
from server.core.game_state import GameState

class GameEngine:
    """
    Main game loop & logic handler.
    """
    TICK_RATE = 20  # ticks per second

    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.running = False
        self.thread = None

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.run_loop, daemon=True)
            self.thread.start()
            print("[GameEngine] Started.")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
            print("[GameEngine] Stopped.")

    def run_loop(self):
        tick_interval = 1.0 / self.TICK_RATE
        while self.running:
            start_time = time.time()
            self.update()
            elapsed = time.time() - start_time
            time.sleep(max(0, tick_interval - elapsed))

    def update(self):
        """
        Main game update logic: update players, world, handle events.
        """
        # Example: iterate all players
        for player_id, player_data in self.game_state.players.items():
            self.update_player(player_id, player_data)

        # Here you can add world updates, NPC movements, events, etc.

    def update_player(self, player_id, player_data):
        # Example placeholder logic
        # Could be movement, health regen, buffs, etc.
        player_data['last_tick'] = time.time()
