# commands/mycmdset.py

from evennia import CmdSet
from commands.rollkeep import CmdRollKeep, CmdRollNumberKeep
from commands.seventhsheetch import CmdCharacterSheet, CmdCombatSheet
from commands.chargen import CmdCharGen
from commands.xpaward import CmdAwardXP
from commands.buyattribute import CmdBuyAttribute
from commands.cmdattack import CombatCommand
# from commands.combatcmdset import MovesCmdSet
from commands.request import CmdRequest, CmdReviewApprove, CmdReviewList, CmdReviewDeny, CmdReviewView
from commands.approvechar import CmdApproveCharacter
from commands.wield import WeaponCommand
from commands.sorcery.sorcerycmdset import SorceryCmdSet
from commands.admin.admincmdset import AdminCmdSet
from commands.base.emit import CmdEmit
from commands.crafting.crafting_cmdset import CraftingCmdSet
from commands.healing.healingcmdset import PlayerHealCmdSet
from commands.base.channels import MyCustomChannelCmd
from commands.character_based.wear import WearCmdset
from world.adventuring_guilds.commands import CmdCreateGuild, CmdJoinGuild, CmdLeaveGuild, CmdListGuilds, CmdMyGuilds
from world.adventuring_guilds.commands import CmdCreateHolding, CmdListHoldings
from world.banking.cmdset import BankingCmdSet
from world.boards.bboard_commands import BBoardCmdSet
from commands.base.cmdlook import CmdLook
from commands.base.cmdooc import CmdOOC
class GuildCmdSet(CmdSet):
  def at_cmdset_creation(self):
    self.add(CmdCreateGuild())
    self.add(CmdJoinGuild())
    self.add(CmdListGuilds())
    self.add(CmdMyGuilds())
    self.add(CmdLeaveGuild())
    self.add(CmdCreateHolding())
    self.add(CmdListHoldings())

class CharacterGenCmdSet(CmdSet):
    """
    This is the command set that contains character generation commands.
    """
    key = "CharacterGenCmdSet"
    priority = 1

    def at_cmdset_creation(self):
        """Populates the cmdset"""
        self.add(CmdCharGen())


class CombatCmdSet(CmdSet):
    key = "CombatCmdSet"
    priority = 1
    def at_cmdset_creation(self):
        self.add(CombatCommand())
        self.add(WeaponCommand())
       

   
class RequestCmdSet(CmdSet):
    key = "RequestCmdSet"
    priority = 1
    def at_cmdset_creation(self):
        self.add(CmdReviewApprove())
        self.add(CmdReviewDeny())
        self.add(CmdReviewList())
        self.add(CmdReviewView())

class MyCmdSet(CmdSet):
    """
    This is a custom command set that includes custom commands.
    """
    key = "MyCmdSet"
    def at_cmdset_creation(self):
        self.add(CmdBuyAttribute())
        self.add(CmdAwardXP())
        self.add(CmdRollKeep())
        self.add(CmdRollNumberKeep())
        self.add(CmdCharacterSheet())
        self.add(CharacterGenCmdSet())
        self.add(CmdCombatSheet())
        # Remove this line:
        self.add(CmdOOC())
        self.add(CombatCmdSet())
        self.add(CmdEmit())
        self.add(CmdLook())
        self.add(CmdRequest())
        self.add(RequestCmdSet())
        self.add(CmdApproveCharacter())
        self.add(AdminCmdSet())
        self.add(CraftingCmdSet())
        self.add(PlayerHealCmdSet())
        # self.add(MyCustomChannelCmd())
        self.add(WearCmdset())
        self.add(GuildCmdSet())
        self.add(BankingCmdSet())
        self.add(BBoardCmdSet())

