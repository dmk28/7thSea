from evennia import CmdSet

from .shipbuilding import CmdBuildShip, CmdModifyShip
from .dracheneisen import DracheneisenPurchaseCmdSet
class CraftingCmdSet(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdBuildShip())
        self.add(CmdModifyShip())
        self.add(DracheneisenPurchaseCmdSet())
        