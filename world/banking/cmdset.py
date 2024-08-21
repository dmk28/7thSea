from evennia import CmdSet
from world.banking.commands import CmdOpenAccount, CmdDeposit, CmdWithdraw, CmdBalance, CmdTransfer

class BankingCmdSet(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdOpenAccount())
        self.add(CmdDeposit())
        self.add(CmdWithdraw())
        self.add(CmdBalance())
        self.add(CmdTransfer()) 