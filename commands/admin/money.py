from evennia import Command
from evennia.utils.search import object_search

class CmdMoney(Command):
    """
    Check your money or add money for testing.

    Usage:
      money
      money add <amount>
    """
    key = "money"
    locks = "cmd:perm(Wizards)"
    help_category = "Admin"

    def func(self):
        if not self.args:
            money = self.caller.db.money.get("guilders", 0) if self.caller.db.money else 0
            self.caller.msg(f"You have {money} guilders.")
        elif self.args.startswith("add "):
            try:
                if not caller.db.hasattr('Money', {}):
                    caller.db.money = {}
                amount = int(self.args.split()[1])
                self.caller.add_money("guilders", amount)
                self.caller.msg(f"Added {amount} guilders. You now have {self.caller.db.money['guilders']} guilders.")
            except (ValueError, IndexError):
                self.caller.msg("Usage: money add <amount>")

# Don't forget to add this command to your default command set