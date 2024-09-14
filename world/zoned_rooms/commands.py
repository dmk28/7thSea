from evennia import Command, DefaultRoom
from evennia.utils.utils import inherits_from
from evennia.utils.ansi import strip_ansi
from typeclasses.rooms import ZonedRoom
from evennia.commands.default.muxcommand import MuxCommand
from world.zoned_rooms.models import ZonedRoomModel
import re

ZONE_COLORS = {
    "Noble District": "305",
    "Merchant District": "541",
    "Residential District": "455",
    "Slums": "320",
    "Shipyards": "015"
}

class CmdConvertToZonedRoom(MuxCommand):
    """
    Convert a room or rooms to ZonedRooms.

    Usage:
      @convertzone <room_id or name> = <zone>
      @convertzone/area = <zone>

    Examples:
      @convertzone 5 = Noble District
      @convertzone Town Square = Merchant District
      @convertzone/area = Residential District

    The /area switch will convert all rooms in the current location.
    """

    key = "@convertzone"
    locks = "cmd:perm(Builders)"
    help_category = "Building"
    switches = ["area"]

    def strip_mux_colors(self, text):
        # This regex matches MUX color codes like |123 or |n
        return re.sub(r'\|(?:\d{3}|[a-zA-Z])', '', text)

    def func(self):
        caller = self.caller

        if not self.args or "=" not in self.args:
            caller.msg("Usage: @convertzone <room_id or name> = <zone>")
            return

        if "area" in self.switches:
            rooms = [o for o in self.caller.location.contents if inherits_from(o, DefaultRoom)]
            target, zone = self.caller.location, self.rhs.strip()
        else:
            target, zone = self.lhs.strip(), self.rhs.strip()
            rooms = [caller.search(target, global_search=True)]

        if not rooms:
            caller.msg("No rooms found to convert.")
            return

        if zone not in ZonedRoom.ZONES:
            caller.msg(f"Invalid zone. Must be one of: {', '.join(ZonedRoom.ZONES)}")
            return

        converted = 0
        for room in rooms:
            if not room:
                continue

            # Strip both ANSI and MUX color codes from the old key
            old_key = strip_ansi(self.strip_mux_colors(room.key))
            old_key = old_key.split(" - ")[0]  # Remove any existing zone suffix
            color_code = ZONE_COLORS.get(zone, '')
            new_key = f"|{color_code}{old_key} - {zone}|n"

            if not inherits_from(room, ZonedRoom):
                room.swap_typeclass("typeclasses.rooms.ZonedRoom", clean_attributes=False)

            # Directly set the zone and update the key
            room.db.zone = zone
            room.key = new_key

            # Ensure the ZonedRoomModel is updated or created
            ZonedRoomModel.objects.update_or_create(
                room=room,
                defaults={'zone': zone}
            )

            # Flush the cache to ensure changes are visible immediately
            room.flush_from_cache()

            caller.msg(f"Converted {old_key} to ZonedRoom with zone {zone} and changed name to {new_key}.")
            converted += 1

        caller.msg(f"Converted {converted} rooms to ZonedRooms in the {zone}.")

# Add this command to your default command set or create a new one for builders