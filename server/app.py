# main entrypoint (starts server, listens for clients)

from server.network.server import GameServer
from server.db.database import init_db

if __name__ == "__main__":
    init_db()
    GameServer().start()
