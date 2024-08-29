# in commands/ship_commands.py

from evennia import CmdSet
from .ship_movement import CmdSail
class ShipCmdSet(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdEnterShip())
        self.add(CmdExitShip())
        self.add(CmdSail())
        # Add other ship-related commands here


