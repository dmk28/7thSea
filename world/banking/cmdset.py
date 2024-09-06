from evennia import CmdSet
from world.banking.commands import CmdBank

class BankingCmdSet(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdBank())