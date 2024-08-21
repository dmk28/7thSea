from commands.healing.healing import CmdFirstAid, CmdSurgery

from evennia import CmdSet
from evennia import Command
from evennia.utils import delay
from evennia.utils.gametime import gametime
from evennia.utils.search import object_search


class PlayerHealCmdSet(CmdSet):

    def at_cmdset_creation(self):
        self.add(CmdFirstAid())
        self.add(CmdSurgery())