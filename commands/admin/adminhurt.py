from evennia import Command
from evennia.utils.search import object_search

class CmdHurt(Command):
    """
    Inflict wounds on a character, taking into account their soak ability.

    Usage:
      hurt <character> [flesh|dramatic]=<amount>

    Examples:
      hurt Bob flesh=10
      hurt Jane dramatic=2
      hurt John=15 (defaults to flesh wounds)
    """
    key = "hurt"
    locks = "cmd:perm(Wizards)"
    help_category = "Admin"

    def func(self):
        caller = self.caller
        if not self.args or "=" not in self.args:
            caller.msg("Usage: hurt <character> [flesh|dramatic]=<amount>")
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
                caller.msg("Amount of damage must be a positive number.")
                return
        except ValueError:
            caller.msg("Amount of damage must be a number.")
            return

        # Find the target character
        target = object_search(target_name)
        if not target:
            caller.msg(f"Character '{target_name}' not found.")
            return
        target = target[0]

        # Calculate soak
        soak = self.calculate_soak(target)
        actual_damage = max(0, amount - soak)

        # Inflict the damage
        if wound_type == "flesh":
            current_wounds = target.db.flesh_wounds or 0
            target.db.flesh_wounds = current_wounds + actual_damage
            caller.msg(f"Inflicted {actual_damage} Flesh Wounds on {target.name}. (Soaked: {amount - actual_damage})")
            target.msg(f"You have received {actual_damage} Flesh Wounds. (Soaked: {amount - actual_damage})")
        else:  # dramatic wounds
            current_wounds = target.db.dramatic_wounds or 0
            target.db.dramatic_wounds = current_wounds + actual_damage
            caller.msg(f"Inflicted {actual_damage} Dramatic Wounds on {target.name}. (Soaked: {amount - actual_damage})")
            target.msg(f"You have received {actual_damage} Dramatic Wounds. (Soaked: {amount - actual_damage})")

        # Check if critically injured
        if target.db.dramatic_wounds >= target.db.traits['resolve']:
            caller.msg(f"{target.name} is critically injured!")
            target.msg("You are critically injured!")
            # Trigger the critically injured command
            self.caller.execute_cmd(f"criticallyinjured {target.name}")

    def calculate_soak(self, character):
        # Base soak calculation
        resolve = character.db.traits.get('resolve', 1)
        armor_value = character.get_armor_value()
        
        # Additional effects
        soak_bonus = 0
        if "tough" in character.db.special_effects:
            soak_bonus += 1

        # You can add more conditions here based on other effects

        return resolve + armor_value + soak_bonus


class CmdCriticallyInjured(Command):
    """
    Handle a character becoming critically injured.

    Usage:
      criticallyinjured <character>
    """
    key = "criticallyinjured"
    locks = "cmd:perm(Wizards)"
    help_category = "Admin"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: criticallyinjured <character>")
            return

        target = object_search(self.args)
        if not target:
            self.caller.msg(f"Character '{self.args}' not found.")
            return
        target = target[0]

        # Set the character as unapproved
        target.db.approved = False

        # Notify the character and the room
        target.msg("|rYou are critically injured and must seek medical attention before continuing to play.|n")
        target.location.msg_contents(f"|r{target.name} is critically injured and needs medical attention.|n", exclude=[target])

        # Notify staff
        self.caller.msg(f"{target.name} has been marked as critically injured and unapproved.")