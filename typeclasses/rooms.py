"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia.objects.objects import DefaultRoom

from .objects import ObjectParent
from evennia.utils import dedent

from commands.mycmdset import CharacterGenCmdSet
from commands.crafting.crafting_cmdset import CraftingCmdSet
from world.banking.rooms import BankRoom
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






class ChargenRoom(Room):
    """
    A room for character generation.
    """
    def at_object_creation(self):
        self.cmdset.add(CharacterGenCmdSet, permanent=True)
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

class ShipyardRoom(Room):
    def at_object_creation(self):
        self.db.desc = dedent("""This is a room you can use to make ships.""")

    def return_appearance(self, looker):
        text = super().return_appearance(looker)
        if hasattr(looker, 'db') and looker.db.approved:
            money = looker.db.money.get("guilders", 0)
            if money > 10000:
                text += "\n\nType |545shipbuild <ship_type>|n to begin shipbuilding!"
            else:
                text += '\n\nYou cannot afford shipbuilding, yet!'
        return text

    def at_object_receive(self, moved_obj, source_location, **kwargs):
        """Called when an object enters this room."""
        if moved_obj.has_account:
            moved_obj.cmdset.add(CraftingCmdSet, persistent=False)

    def at_object_leave(self, moved_obj, target_location, **kwargs):
        """Called when an object leaves this room."""
        if moved_obj.has_account:
            moved_obj.cmdset.delete(CraftingCmdSet)

class UsedBankRoom(BankRoom):

    pass