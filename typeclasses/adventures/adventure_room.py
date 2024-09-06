from evennia import DefaultRoom
from evennia import CmdSet
from evennia import Command
from evennia.utils import evmenu
from world.adventure_menu.adventures import start_sea_escort_adventure

class AdventureCmdSet(CmdSet):
    key = "adventure_cmdset"
    
    def at_cmdset_creation(self):
        self.add(CmdStartAdventure())

class CmdStartAdventure(Command):
    key = "start adventure"
    aliases = ["begin adventure", "adventure"]
    locks = "cmd:all()"
    
    def func(self):
        start_sea_escort_adventure(self.caller)

class AdventureRoom(DefaultRoom):
    def at_object_creation(self):
        super().at_object_creation()
        self.cmdset.add(AdventureCmdSet, permanent=True)
        self.db.adventure_state = "inactive"
        self.db.original_desc = self.db.desc

    def return_appearance(self, looker):
        appearance = super().return_appearance(looker)
        if self.db.adventure_state != "inactive":
            appearance += f"\n\n[Adventure State: {self.db.adventure_state}]"
        return appearance

    def at_object_receive(self, moved_obj, source_location, **kwargs):
        super().at_object_receive(moved_obj, source_location, **kwargs)
        if moved_obj.has_account:
            moved_obj.msg("Welcome to the Adventure Room! Type 'start adventure' to begin a sea escort mission.")

    def update_adventure_state(self, new_state):
        self.db.adventure_state = new_state
        self.msg_contents(f"The adventure state has changed to: {new_state}")