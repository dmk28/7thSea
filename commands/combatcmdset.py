from evennia import CmdSet
from commands.cmdattack import CmdDoubleParry, CmdStopThrust, CmdFeint, CmdRiposte, CmdViewCombatEffects, CmdLunge, CmdTag, CmdDoubleAttack, CmdPommelStrike

class MovesCmdSet(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdDoubleParry())
        self.add(CmdStopThrust())
        self.add(CmdFeint())
        self.add(CmdRiposte())
        self.add(CmdViewCombatEffects())
        self.add(CmdLunge())
        self.add(CmdTag())
        self.add(CmdDoubleAttack())
        self.add(CmdPommelStrike())