# In a new file, perhaps called deadcmdset.py
from evennia import CmdSet
from evennia import Command

class CmdLook(Command):
    """
    Look around in the afterlife
    """
    key = "look"
    aliases = ["l"]
    locks = "cmd:all()"
    
    def func(self):
        self.caller.msg("You see the misty realms of the afterlife...")

class CmdSay(Command):
    """
    Say something in the afterlife
    """
    key = "say"
    aliases = ["'"]
    locks = "cmd:all()"
    
    def func(self):
        if not self.args:
            self.caller.msg("Say what?")
            return
        self.caller.location.msg_contents(f"{self.caller} says: {self.args[0]}")

class DeadCmdSet(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdLook())
        self.add(CmdSay())
        # Add other commands available to dead characters