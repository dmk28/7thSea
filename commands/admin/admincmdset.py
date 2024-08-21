from commands.admin.adminheal import CmdHeal
from evennia import CmdSet
from commands.admin.adminhurt import CmdHurt, CmdCriticallyInjured
from commands.admin.money import CmdMoney
from commands.admin.adminsheet import CmdAdminSheet
from commands.admin.update_sheets import CmdUpdateCharacterSheets
from commands.admin.debug_data import CmdDebugCharacter

class AdminCmdSet(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdHeal())
        self.add(CmdHurt())
        self.add(CmdCriticallyInjured())
        self.add(CmdMoney())
        self.add(CmdAdminSheet())
        self.add(CmdUpdateCharacterSheets())
        self.add(CmdDebugCharacter())