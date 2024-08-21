from commands.sorcery.flameblade import CmdFlameblade, CmdExtinguishFlameblade
from commands.sorcery.portewalk import CmdPorteWalk
from commands.sorcery.sortemagic import CmdSorteCast
from evennia import CmdSet

class SorceryCmdSet(CmdSet):

    def at_cmdset_creation(self):
        self.add(CmdFlameblade())
        self.add(CmdPorteWalk())
        self.add(CmdExtinguishFlameblade())
        self.add(CmdSorteCast())