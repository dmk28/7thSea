from evennia import Command
from evennia.utils.search import object_search
from world.character_sheet.models import CharacterSheet

class CmdHeal(Command):
    """
    Heal a character's wounds.
    Usage:
      heal <character> [flesh|dramatic]=<amount>
    Examples:
      heal Bob flesh=5
      heal Jane dramatic=1
      heal John=10 (heals 10 flesh wounds by default)
    This command allows staff to heal a character's Flesh Wounds or Dramatic Wounds.
    If no wound type is specified, it defaults to healing Flesh Wounds.
    """
    key = "heal"
    locks = "cmd:perm(Wizards)"
    help_category = "Admin"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: heal <character> [flesh|dramatic]=<amount>")
            return
        if "=" not in self.args:
            caller.msg("You must specify an amount to heal.")
            return

        target_and_type, amount = self.args.split("=", 1)
        target_and_type = target_and_type.strip()
        amount = amount.strip()

        if " " in target_and_type:
            target_name, wound_type = target_and_type.rsplit(" ", 1)
            wound_type = wound_type.lower()
        else:
            target_name = target_and_type
            wound_type = "flesh"  # Default to flesh wounds

        if wound_type not in ["flesh", "dramatic"]:
            caller.msg("Invalid wound type. Use 'flesh' or 'dramatic'.")
            return

        try:
            amount = int(amount)
            if amount <= 0:
                caller.msg("Amount to heal must be a positive number.")
                return
            elif amount > 500:
                caller.msg("Not allowed to heal more than 500 wounds at once.")
                return
        except ValueError:
            caller.msg("Amount to heal must be a number.")
            return

        # Find the target character
        target = object_search(target_name)
        if not target:
            caller.msg(f"Character '{target_name}' not found.")
            return
        target = target[0]

        # Get the character sheet
        try:
            sheet = target.character_sheet
        except AttributeError:
            caller.msg(f"{target.name} doesn't have a character sheet.")
            return

        # Perform the healing
        if wound_type == "flesh":
            current_wounds = sheet.flesh_wounds
            if current_wounds == 0:
                caller.msg(f"{target.name} doesn't have any Flesh Wounds to heal.")
                return
            healed = min(amount, current_wounds)
            sheet.heal_character(healed, "flesh")
            caller.msg(f"Healed {healed} Flesh Wounds for {target.name}.")
            target.msg(f"You have been healed for {healed} Flesh Wounds.")
        else:  # dramatic wounds
            current_wounds = sheet.dramatic_wounds
            if current_wounds == 0:
                caller.msg(f"{target.name} doesn't have any Dramatic Wounds to heal.")
                return
            healed = min(amount, current_wounds)
            sheet.heal_character(healed, "dramatic")
            caller.msg(f"Healed {healed} Dramatic Wounds for {target.name}.")
            target.msg(f"You have been healed for {healed} Dramatic Wounds.")
            if target.db.unconscious:
                target.db.unconscious = False
                target.msg("|gYou snap out of unconsciousness.|n")
                caller.msg(f"{target.name} has regained consciousness.")
