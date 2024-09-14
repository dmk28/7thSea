from evennia import Command, create_object
from evennia.utils.utils import inherits_from
from typeclasses.rooms import ZonedRoom
from typeclasses.exits import Exit
from commands.property.cmdrent import ROOM_COSTS
from world.zoned_rooms.models import ZonedRoomModel

ZONE_COLORS = {
    "Noble District": "|305",
    "Merchant District": "|541",
    "Residential District": "|455",
    "Slums": "|320",
    "Shipyards": "|015"
}

class CmdBuild(Command):
    """
    Build a new room in the current zone.

    Usage:
      build <room name> = <exit name>[;<alias1>;<alias2>...][,<return exit name>[;<alias1>;<alias2>...]]

    This command creates a new room in the current zone, connects it
    to the current room, and creates a return exit (default is "Out <O>" if not specified).
    The new room's name will be colored based on its zone.

    For regular players, building a room costs guilders based on the zone and how many rooms you've already built.
    Builders and admins can create rooms without incurring costs.
    """
    key = "build"
    aliases = ["@build"]
    locks = "cmd:all()"
    help_category = "Building"

    def func(self):
        caller = self.caller
        location = caller.location

        if not inherits_from(location, ZonedRoom):
            caller.msg("You can only use this command in a zoned room.")
            return

        if not self.args or "=" not in self.args:
            caller.msg("Usage: build <room name> = <exit name>[;<alias1>;<alias2>...][,<return exit name>[;<alias1>;<alias2>...]]")
            return

        room_name, exit_defs = self.args.split("=", 1)
        room_name = room_name.strip()
        exit_defs = exit_defs.strip()

        if "," in exit_defs:
            exit_def, return_exit_def = exit_defs.split(",", 1)
        else:
            exit_def, return_exit_def = exit_defs, "Out <O>"

        exit_def = exit_def.strip()
        return_exit_def = return_exit_def.strip()

        # Get the zone from the current room
        zone = location.get_zone()
        if not zone:
            caller.msg("The current room doesn't have a valid zone.")
            return

        # Check if the caller is a builder or admin
        is_builder = caller.check_permstring("Builders") or caller.check_permstring("Admin")

        # Create the new room
        new_room = self.create_room(caller, room_name, exit_def, return_exit_def, zone, deduct_cost=not is_builder)

        if new_room:
            caller.msg(f"You have created a new room: {new_room.name}")
            caller.msg(f"You can enter it via the '{exit_def.split(';')[0]}' exit and return via the '{return_exit_def.split(';')[0]}' exit.")

    def create_room(self, caller, room_name, exit_def, return_exit_def, zone, deduct_cost=True):
        location = caller.location
        colored_room_name = f"{ZONE_COLORS.get(zone, '')}{room_name}|n"

        # Create the new room
        new_room = create_object("typeclasses.rooms.ZonedRoom", 
                                 key=colored_room_name, 
                                 location=None)
        new_room.set_zone(zone)

        # Create the exit to the new room
        exit_name, *exit_aliases = exit_def.split(";")
        new_exit = create_object(Exit, 
                                 key=exit_name, 
                                 location=location, 
                                 destination=new_room)
        if exit_aliases:
            new_exit.aliases.add(exit_aliases)

        # Create the return exit
        return_exit_name, *return_exit_aliases = return_exit_def.split(";")
        return_exit = create_object(Exit, 
                                    key=return_exit_name, 
                                    location=new_room, 
                                    destination=location)
        if return_exit_aliases:
            return_exit.aliases.add(return_exit_aliases)

        # Check if this is a residence and deduct cost if necessary
        if deduct_cost and zone in ROOM_COSTS:
            room_count = ZonedRoomModel.objects.filter(room__db_typeclass_path=new_room.db_typeclass_path, zone=zone).count()
            cost = ROOM_COSTS[zone] * 10 * (room_count + 1)  # +1 for the new room
            
            if not caller.spend_money("guilders", cost):
                caller.msg(f"You don't have enough guilders. You need {cost} guilders to build this room.")
                # Clean up the created objects
                new_room.delete()
                new_exit.delete()
                return_exit.delete()
                return None
            
            caller.msg(f"You've been charged {cost} guilders for building this room.")

        return new_room

# Add this command to your default command set