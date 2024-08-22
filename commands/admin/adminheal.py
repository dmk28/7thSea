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
      heal John=10  (heals 10 flesh wounds by default)

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
                caller.msg("Not allowed.")
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

        # Perform the healing
        if wound_type == "flesh":
            current_wounds = target.character_sheet.flesh_wounds
            if current_wounds is None:
                caller.msg(f"{target.name} has no Flesh Wounds attribute.")
                return
            elif current_wounds == 0:
                caller.msg(f"{target.name} can't be healed for Flesh Wounds")
                return
            else:
                healed = min(amount, current_wounds)
                caller.character_sheet.heal_character(healed, "flesh")
                caller.msg(f"Healed {healed} Flesh Wounds for {target.name}.")
                target.msg(f"You have been healed for {healed} Flesh Wounds.")
        else:  # dramatic wounds
            current_wounds = target.character_sheet.dramatic_wounds
            if current_wounds is None:
                caller.msg(f"{target.name} has no Dramatic Wounds attribute.")
                return
            elif current_wounds == 0:
                caller.msg(f"{target.name} cannot be healed, he has no Dramatic Wounds.")
                return
            else:
                healed = min(amount, current_wounds)
                caller.character_sheet.heal_character(healed, "dramatic")
                if target.db.unconscious:
                    target.db.unconscious = False
                    target.msg(f"|gYou snap out of unconsciousness.|n")
                caller.msg(f"Healed {healed} Dramatic Wounds for {target.name}.")
                target.msg(f"You have been healed for {healed} Dramatic Wounds.")

        # Inform the room
       # target.location.msg_contents(f"{target.name} has been healed.", exclude=[caller, target])