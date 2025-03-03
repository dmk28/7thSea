"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia.objects.objects import DefaultRoom

from .objects import ObjectParent
from evennia.utils import dedent
import logging
from commands.crafting.crafting_cmdset import CraftingCmdSet, ShipBuildCmdset
from world.banking.rooms import BankRoom
from evennia.utils.utils import inherits_from
from world.combat_script.repartee_cmdset import ReparteeCmdSet
logger = logging.getLogger("evennia")
from evennia.utils import list_to_string
from world.zoned_rooms.models import ZonedRoomModel
from typeclasses.exits import PlayerExit
class Room(ObjectParent, DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Objects.
    """

    pass
class MainRoom(Room):
    """
    The main room where characters start after chargen.
    """
    def at_object_creation(self):
        self.db.desc = "This is the main room. Welcome to the game!"


class ShipInterior(Room):

    def at_object_creation(self):
        super().at_object_creation()
        self.db.ship = None  # Will be set to the parent ship object




class ChargenRoom(Room):
    """
    A room for character generation.
    """
    

    def at_object_creation(self):
        from commands.mycmdset import CharacterGenCmdSet
        super().at_object_creation()
        self.cmdset.add(CharacterGenCmdSet, persistent=True)
        self.db.desc = dedent("""
            Welcome to the character generation room!
            Here you will create your 7th Sea character step by step.
            Type 'chargen' to begin or continue the process.
            
           
        """)

    def return_appearance(self, looker):
        """
        This is called when someone looks at the room.
        """
        text = super().return_appearance(looker)
        
        # Check if chargen attribute exists and is not None
        if hasattr(looker, 'ndb') and looker.ndb.chargen is not None:
            state = looker.ndb.chargen.get("state", "")
            text += "\n\n" + self.get_chargen_status(state)
        else:
            text += "\n\nType 'chargen' to begin character generation."
        
        return text

    def get_chargen_status(self, state):
        """
        Returns instructions based on the current character generation state.
        """
        status_messages = {
            "nationality": dedent("""
                Current step: Choose your nationality
                Command: nationality <name>
                Available nationalities: Castille, Montaigne, Avalon, Vendel, Vesten, Vodacce, Eisen
            """),
            "traits": dedent("""
                Current step: Assign trait points
                Command: settrait <trait> <value>
                Available traits: Brawn, Finesse, Wits, Resolve, Panache
            """),
            "packages": dedent("""
                Current step: Choose your packages
                Command: buypackage <package>
                Type 'list packages' to see available packages
            """),
            "advantages": dedent("""
                Current step: Choose your advantages
                Command: buyadvantage <advantage> [level]
                Type 'list advantages' to see available advantages
            """),
            "sorceries": dedent("""
                Current step: Choose your sorceries (if applicable)
                Command: buysorcery <sorcery>
                Type 'list sorceries' to see available sorceries
            """),
            "complete": "Character generation is complete! Type 'sheet' to view your character sheet."
        }
        
        return status_messages.get(state, "Type 'chargen' to begin or continue character generation.")


# class CmdSetRoom(DefaultRoom):
#     def at_object_creation(self):
#         super().at_object_creation()
#         self.db.room_cmdset = None  # This will store the cmdset class

#     def at_object_receive(self, moved_obj, source_location, **kwargs):
#         if moved_obj.has_account and self.db.room_cmdset:
#             moved_obj.cmdset.add(self.db.room_cmdset)
#         super().at_object_receive(moved_obj, source_location, **kwargs)

#     def at_object_leave(self, moved_obj, target_location, **kwargs):
#         if moved_obj.has_account and self.db.room_cmdset:
#             moved_obj.cmdset.delete(self.db.room_cmdset)
#         super().at_object_leave(moved_obj, target_location, **kwargs)

# class ShipyardRoom(Room):
#     def at_object_creation(self):
#         self.db.desc = dedent("""This is a room you can use to make ships.""")

#     def return_appearance(self, looker):
#         text = super().return_appearance(looker)
#         if hasattr(looker, 'db') and looker.db.approved:
#             money = looker.db.money.get("guilders", 0)
#             if money > 10000:
#                 text += "\n\nType |545shipbuild <ship_type>|n to begin shipbuilding!"
#             else:
#                 text += '\n\nYou cannot afford shipbuilding, yet!'
#         return text

#     def at_object_receive(self, moved_obj, source_location, **kwargs):
#         """Called when an object enters this room."""
#         if moved_obj.has_account:
#             moved_obj.cmdset.add(CraftingCmdSet, persistent=False)

#     def at_object_leave(self, moved_obj, target_location, **kwargs):
#         """Called when an object leaves this room."""
#         if moved_obj.has_account:
#             moved_obj.cmdset.delete(CraftingCmdSet)

# class UsedBankRoom(BankRoom):

#     pass
class SalonRoom(Room):
    def at_object_creation(self):
        super().at_object_creation()
        self.cmdset.add(ReparteeCmdSet, persistent=True)
                
class ShipyardRoom(Room):
    def at_object_creation(self):
        super().at_object_creation()
        self.cmdset.add(ShipBuildCmdset, persistent=True)

# class TavernRoom(CmdSetRoom):
#     def at_object_creation(self):
#         super().at_object_creation()
#         self.db.desc = "A cozy tavern filled with the smell of ale and roasted meat."
#         self.db.room_cmdset = TavernCmdSet  # You'd need to create this cmdset

# class MarketRoom(CmdSetRoom):
#     def at_object_creation(self):
#         super().at_object_creation()
#         self.db.desc = "A bustling market with vendors hawking their wares."
#         self.db.room_cmdset = MarketCmdSet  # You'd need to create this cmdset

class ZonedRoom(DefaultRoom):
    ZONES = [
        "Noble District",
        "Merchant District",
        "Residential District",
        "Shipyards",
        "Slums"
    ]

    def at_object_creation(self):
        super().at_object_creation()
        self.db.is_main_zone_room = False
        if not ZonedRoomModel.objects.filter(room=self).exists():
            ZonedRoomModel.objects.create(room=self, zone="")
        self.db.zone = None
        self.db.owner = None
        self.db.keyholders = []

    def set_zone(self, zone):
        if zone in self.ZONES:
            zoned_room, _ = ZonedRoomModel.objects.get_or_create(room=self)
            zoned_room.zone = zone
            zoned_room.save()
            self.db.zone = zone
        else:
            raise ValueError(f"Invalid zone. Must be one of: {', '.join(self.ZONES)}")

    def get_zone(self):
        try:
            return self.zoned_room.zone, self.db.zone

        except ZonedRoomModel.DoesNotExist:
            return ""
    def at_init(self):
        """
        This is called when the object is re-cached from memory. We ensure
        the ZonedRoomModel exists here.
        """
        super().at_init()
        ZonedRoomModel.objects.get_or_create(room=self)

    def return_appearance(self, looker):
        """
        This is called when someone looks at the room.
        """
        string = super().return_appearance(looker)
        if self.db.zone:
            string += f"\n|cZone:|n {self.db.zone}"
        return string

    def get_zone(self):
        return self.db.zone

    def set_owner(self, owner):
        self.db.owner = owner

    def get_owner(self):
        return self.db.owner

class SeaRoom(DefaultRoom):
    def at_object_creation(self):
        super().at_object_creation()
        self.db.coordinates = (0, 0)  # Default coordinates
        self.db.is_port = False
        self.db.port_name = ""

    def at_object_receive(self, moved_obj, source_location, **kwargs):
        if inherits_from(moved_obj, "typeclasses.ships.Ship"):
            # A ship has entered this room
            self.msg_contents(f"{moved_obj.name} has sailed into the area.")

    def at_object_leave(self, moved_obj, target_location, **kwargs):
        if inherits_from(moved_obj, "typeclasses.ships.Ship"):
            # A ship has left this room
            self.msg_contents(f"{moved_obj.name} has sailed away.")

    def return_appearance(self, looker):
        # Customize the room description based on its properties
        desc = super().return_appearance(looker)
        if self.db.is_port:
            desc += f"\nYou are at the port of {self.db.port_name}."
        desc += f"\nCoordinates: {self.db.coordinates}"
        return desc




class NobleDistrictRoom(ZonedRoom):
    def at_object_creation(self):
        super().at_object_creation()
        self.set_zone("Noble District")

class MerchantDistrictRoom(ZonedRoom):
    def at_object_creation(self):
        super().at_object_creation()
        self.set_zone("Merchant District")

class ResidentialDistrictRoom(ZonedRoom):
    def at_object_creation(self):
        super().at_object_creation()
        self.set_zone("Residential District")

class ShipyardsRoom(ZonedRoom):
    def at_object_creation(self):
        super().at_object_creation()
        self.set_zone("Shipyards")

class SlumsRoom(ZonedRoom):
    def at_object_creation(self):
        super().at_object_creation()
        self.set_zone("Slums")

class InnRoom(ZonedRoom):
    

    """
    This room represents the main area of the inn where players can rent rooms.
    """
    def at_object_creation(self):
        from commands.property.cmdrent import InnCmdSet
        """
        Called when the room is first created.
        """
        super().at_object_creation()
        self.cmdset.add(InnCmdSet, persistent=True)

class BedRoom(ZonedRoom):
    """
    This room represents a rented bedroom that players can customize.
    """
    def at_object_creation(self):
        """
        Called when the room is first created.
        """
        super().at_object_creation()
        self.locks.add("edit:id(%s) or perm(Admin);call:id(%s) or perm(Admin)" % (self.id, self.id))

    def return_appearance(self, looker):
        """
        This is called when someone looks at the room.
        """
        string = super().return_appearance(looker)
        if looker.attributes.has("owns_room") and looker.db.owns_room == self:
            string += "\n\nThis is your rented room. You can use 'editdesc' to change its description."
        return string

class NobleBedRoom(BedRoom, NobleDistrictRoom):
    pass

class MerchantBedRoom(BedRoom, MerchantDistrictRoom):
    pass

class ResidentialBedRoom(BedRoom, ResidentialDistrictRoom):
    pass

class SlumsBedRoom(BedRoom, SlumsRoom):
    pass


