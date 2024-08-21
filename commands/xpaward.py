from evennia import Command
from evennia.utils.search import search_object
from evennia.accounts.models import AccountDB
from world.character_sheet.models import CharacterSheet
class CmdAwardXP(Command):
    """
    Award XP to a character.

    Usage:
      awardxp [<character>] <amount>

    Examples:
      awardxp 10
      awardxp Bob 15

    This will award the specified amount of XP to the target character.
    If no character is specified, it awards XP to the character using the command.
    """

    key = "awardxp"
    locks = "cmd:perm(Wizards)"  # Restrict this command to admin/wizard level
    help_category = "Admin"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Usage: awardxp [<character>] <amount>")
            return

        args = self.args.split()
        if len(args) == 1:
            # Award XP to the caller
            target = caller
            try:
                amount = int(args[0])
            except ValueError:
                caller.msg("The XP amount must be a number.")
                return
        elif len(args) == 2:
            # Award XP to another character
            target_name = args[0]
            targets = search_object(target_name)
            if not targets:
                caller.msg(f"Character '{target_name}' not found.")
                return
            target = targets[0]  # search_object returns a list
            try:
                amount = int(args[1])
            except ValueError:
                caller.msg("The XP amount must be a number.")
                return
        else:
            caller.msg("Too many arguments. Usage: awardxp [<character>] <amount>")
            return

        # Award the XP
        sheet, created = CharacterSheet.objects.get_or_create(db_object=target)
        sheet.xp += amount
        sheet.total_xp_accrued += amount

        # Convert XP to HP
        hp_gain = sheet.xp // 2
        sheet.hero_points += hp_gain
        sheet.xp %= 2

        sheet.save()

        # Notify the target and the caller
        target.msg(f"You've been awarded {amount} XP, converted to {hp_gain} HP. "
                   f"You now have {target.db.hero_points} HP and {target.db.xp} XP.")
        
        if target != caller:
            caller.msg(f"You've awarded {amount} XP to {target.name}, "
                       f"converted to {hp_gain} HP.")