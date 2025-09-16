import sqlite3

conn = sqlite3.connect("game.db")
cursor = conn.cursor()

cursor.execute("ALTER TABLE characters ADD COLUMN x INTEGER DEFAULT 100;")
cursor.execute("ALTER TABLE characters ADD COLUMN y INTEGER DEFAULT 100;")
cursor.execute("ALTER TABLE characters ADD COLUMN level INTEGER DEFAULT 0;")

conn.commit()
conn.close()
