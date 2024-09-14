from evennia import Command
from evennia.utils.create import create_object
from typeclasses.rooms import ZonedRoom, NobleBedRoom, MerchantBedRoom, ResidentialBedRoom, SlumsBedRoom
from typeclasses.exits import PlayerExit as Exit
from evennia import CmdSet
from evennia.utils.search import search_object
from evennia.utils.utils import inherits_from
from world.utils.get_initials import get_initials
ROOM_COSTS = {
    "Noble District": 2000,
    "Merchant District": 1000,
    "Residential District": 500,
    "Slums": 50,
}

ROOM_TYPES = {
    "Noble District": NobleBedRoom,
    "Merchant District": MerchantBedRoom,
    "Residential District": ResidentialBedRoom,
    "Slums": SlumsBedRoom,
}

class CmdRentRoom(Command):
    """
    Rent a room at the inn.

    Usage:
      rent

    This will rent a room for you in the current inn's zone.
    """
    key = "rent"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        location = caller.location

        if not isinstance(location, InnRoom):
            caller.msg("You must be in an inn to rent a room.")
            return

        if caller.attributes.has("owns_room"):
            caller.msg("You already own a room.")
            return

        zone = location.get_zone()
        if zone not in ROOM_COSTS:
            caller.msg(f"You cannot rent a room in this area.")
            return

        cost = ROOM_COSTS[zone]
        if not caller.spend_money("guilders", cost):
            caller.msg(f"You don't have enough guilders. You need {cost} guilders to rent in {zone}.")
            return

        # Get the inn's name
        inn_name = location.key.split(" - ")[0] if " - " in location.key else location.key
        area_name = location.key.split(" - ")[1] if " - " in location.key else location.key
        # Create a new bedroom with the updated naming convention and correct room type
        room_name = f"{caller.name}'s Room - {inn_name} - {area_name} - {zone}"
        room_type = ROOM_TYPES.get(zone, ZonedRoom)  # Default to ZonedRoom if zone not found
        new_room = create_object(room_type, room_name, location=None)
        new_room.set_zone(zone)
        new_room.db.owner = caller  # Set the owner directly on the room
        new_room.db.keyholders = [caller.name]  # Initialize keyholders with the owner

        # Create exits between the inn and the new room
        exit_name = f"{caller.name}'s Room <{get_initials(caller.name)}R>"
        inn_to_room = create_object(Exit, exit_name, location=location, destination=new_room)
        room_to_inn = create_object(Exit, "Out", location=new_room, destination=location)

        # Set up the locks for the exits
        inn_to_room.locks.add(f"traverse:id({caller.id}) or keychain()")
        room_to_inn.locks.add(f"traverse:id({caller.id}) or keychain()")

        # Set the caller's attributes
        caller.attributes.add("owns_room", new_room.dbref)  # Store the dbref instead of the object
        if not caller.attributes.has("owned_rooms"):
            caller.attributes.add("owned_rooms", [new_room])
        else:
            caller.attributes.get("owned_rooms").append(new_room)

        caller.msg(f"You have rented a {room_type.__name__} in {inn_name} ({zone}) for {cost} guilders. You can enter it by typing '{exit_name}'.")

class CmdEditRoomDesc(Command):
    """
    Edit the description of your rented room.

    Usage:
      editdesc <description>

    This command allows you to change the description of your rented room.
    """
    key = "editdesc"
    locks = "cmd:attr(owns_room)"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: editdesc <description>")
            return

        room = self.caller.attributes.get("owns_room")
        if not room:
            self.caller.msg("You don't own a room.")
            return

        room.db.desc = self.args
        self.caller.msg("Room description updated.")


class CmdZoneInfo(Command):
    """
    Get information about the current zone.

    Usage:
      zoneinfo

    This will display information about the zone you're currently in.
    """
    key = "zoneinfo"
    locks = "cmd:all()"

    def func(self):
        location = self.caller.location
        if isinstance(location, ZonedRoom):
            zone = location.get_zone()
            self.caller.msg(f"You are currently in the {zone}.")
        else:
            self.caller.msg("You are not in a zoned area.")

class CmdKeychain(Command):
    """
    Manage access to your rented room.

    Usage:
      keychain add <player>
      keychain remove <player>
      keychain list

    This command allows you to give or revoke access to your rented room.
    """
    key = "keychain"
    locks = "cmd:attr(owns_room)"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: keychain add|remove|list <player>")
            return

        room_ref = self.caller.attributes.get("owns_room")
        if not room_ref:
            self.caller.msg("You don't own a room.")
            return

        # Convert room_ref to an actual room object
        if isinstance(room_ref, str):
            room = search_object(room_ref)
            if room:
                room = room[0]
            else:
                self.caller.msg("Error: Your room could not be found.")
                return
        elif inherits_from(room_ref, ZonedRoom):
            room = room_ref
        else:
            self.caller.msg("Error: Invalid room reference.")
            return

        action = self.args.split()[0].lower()
        if action == "list":
            keyholders = room.db.keyholders or []
            if keyholders:
                self.caller.msg("People with access to your room: " + ", ".join(keyholders))
            else:
                self.caller.msg("No one else has access to your room.")
        elif action in ["add", "remove"]:
            if len(self.args.split()) < 2:
                self.caller.msg(f"Usage: keychain {action} <player>")
                return
            target = self.caller.search(self.args.split()[1])
            if not target:
                return
            keyholders = room.db.keyholders or []
            if action == "add":
                if target.name in keyholders:
                    self.caller.msg(f"{target.name} already has access to your room.")
                else:
                    keyholders.append(target.name)
                    room.db.keyholders = keyholders
                    self.caller.msg(f"Granted {target.name} access to your room.")
            else:  # remove
                if target.name in keyholders:
                    keyholders.remove(target.name)
                    room.db.keyholders = keyholders
                    self.caller.msg(f"Revoked {target.name}'s access to your room.")
                else:
                    self.caller.msg(f"{target.name} doesn't have access to your room.")
        else:
            self.caller.msg("Usage: keychain add|remove|list <player>")

class InnCmdSet(CmdSet):
    """
    This cmdset is used in the InnRoom.
    """
    key = "InnCmdSet"
    
    
    def at_cmdset_creation(self):
        self.add(CmdRentRoom())
        self.add(CmdZoneInfo())
        self.add(CmdKeychain())

# Add this function to be used in the PlayerExit's lock
def keychain(accessing_obj, accessed_obj, *args, **kwargs):
    room = accessed_obj.location
    if not room or not hasattr(room, 'db') or not room.db.owner:
        return False
    keyholders = room.db.keyholders or []
    return accessing_obj.name in keyholders