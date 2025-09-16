# server/core/world.py
from .utils import generate_id

class Entity:
    """Base class for all entities in the game world."""
    def __init__(self, name, x=0, y=0):
        self.id = generate_id()
        self.name = name
        self.x = x
        self.y = y

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def __repr__(self):
        return f"<Entity id={self.id} name={self.name} x={self.x} y={self.y}>"

class Zone:
    """A zone in the game world."""
    def __init__(self, name, width, height):
        self.name = name
        self.width = width
        self.height = height
        self.entities = {}

    def add_entity(self, entity: Entity):
        self.entities[entity.id] = entity

    def remove_entity(self, entity_id):
        if entity_id in self.entities:
            del self.entities[entity_id]

    def get_entities(self):
        return list(self.entities.values())

    def __repr__(self):
        return f"<Zone {self.name} ({self.width}x{self.height}) entities={len(self.entities)}>"

class World:
    """The main game world containing multiple zones."""
    def __init__(self):
        self.zones = {}

    def add_zone(self, zone: Zone):
        self.zones[zone.name] = zone

    def get_zone(self, name):
        return self.zones.get(name)

    def remove_zone(self, name):
        if name in self.zones:
            del self.zones[name]

    def __repr__(self):
        return f"<World zones={len(self.zones)}>"
