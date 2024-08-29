# in world/sea_map.py

from evennia import DefaultScript
from typeclasses.rooms import SeaRoom

class SeaMap(DefaultScript):
    def at_script_creation(self):
        self.persistent = True
        self.db.sea_rooms = {}  # Dictionary to store rooms by coordinates

    def create_sea_room(self, coordinates, is_port=False, port_name=""):
        x, y = coordinates
        if coordinates not in self.db.sea_rooms:
            room = create_object(SeaRoom, key=f"Sea at {x}, {y}")
            room.db.coordinates = coordinates
            room.db.is_port = is_port
            room.db.port_name = port_name
            self.db.sea_rooms[coordinates] = room
        return self.db.sea_rooms[coordinates]

    def get_sea_room(self, coordinates):
        return self.db.sea_rooms.get(coordinates)

    def create_port(self, coordinates, port_name):
        return self.create_sea_room(coordinates, is_port=True, port_name=port_name)