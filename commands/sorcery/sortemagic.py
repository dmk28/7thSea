from evennia import Command
from evennia.utils import delay
import random

class CmdSorteCast(Command):
    """
    Cast a Sorte sorcery effect.

    Usage:
      sorte <effect> [<target>]

    Available effects:
      cups_boost, cups_curse, swords_boost, swords_curse, staves, coins, arcana

    Some effects require a target.
    """

    key = "sorte"
    locks = "cmd:all()"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: sorte <effect> [<target>]")
            return

        args = self.args.split()
        effect = args[0].lower()
        target = self.caller.search(args[1]) if len(args) > 1 else None

        if effect not in ['cups_boost', 'cups_curse', 'swords_boost', 'swords_curse', 'staves', 'coins', 'arcana']:
            self.caller.msg("Invalid Sorte effect. Choose from: cups_boost, cups_curse, swords_boost, swords_curse, staves, coins, arcana")
            return

        if effect in ['cups_boost', 'cups_curse', 'swords_boost', 'swords_curse'] and not target:
            self.caller.msg(f"{effect} requires a target.")
            return

        # Check if the character is a Sorte sorcerer
        if not self.caller.db.is_sorcerer or 'Sorte' not in self.caller.db.sorcery_knacks:
            self.caller.msg("You are not a Sorte sorcerer.")
            return

        # Get the Sorte knack rank
        sorte_rank = self.caller.db.sorcery_knacks.get('Sorte', 0)

        # Calculate duration
        duration = 86400 * sorte_rank  # 1 day (in seconds) times knack rank

        # Apply the effect
        if effect == 'cups_boost':
            self.apply_effect(target, 'cups_boost', duration, defense_mod=1)
        elif effect == 'cups_curse':
            self.apply_effect(target, 'cups_curse', duration, defense_mod=-2)
        elif effect == 'swords_boost':
            self.apply_effect(target, 'swords_boost', duration, attack_mod=2)
        elif effect == 'swords_curse':
            self.apply_effect(target, 'swords_curse', duration, attack_mod=-1)
        elif effect == 'staves':
            self.apply_effect(self.caller, 'staves', duration, attack_mod=1, defense_mod=1)
        elif effect == 'coins':
            self.apply_effect(self.caller, 'coins', 1, dice_kept=2)  # Coins effect lasts for 1 turn
        elif effect == 'arcana':
            self.cast_arcana()

        self.caller.msg(f"You cast {effect}.")

    def apply_effect(self, target, effect_name, duration, attack_mod=0, defense_mod=0, dice_kept=0):
        if not hasattr(target.db, 'special_effects'):
            target.db.special_effects = []

        effect = {
            'name': effect_name,
            'duration': duration,
            'attack_mod': attack_mod,
            'defense_mod': defense_mod,
            'dice_kept': dice_kept
        }

        target.db.special_effects.append(effect)
        target.msg(f"You are under the influence of {effect_name} for {duration/86400:.1f} days.")

        # Schedule effect removal
        delay(duration, self.remove_effect, target, effect)

    def remove_effect(self, target, effect):
        if hasattr(target.db, 'special_effects'):
            target.db.special_effects = [e for e in target.db.special_effects if e != effect]
            target.msg(f"The {effect['name']} effect has worn off.")

    def cast_arcana(self):
        roll = random.randint(1, 10)
        if roll == 10:
            self.apply_effect(self.caller, 'arcana_boost', 86400, attack_mod=5, defense_mod=5)
            self.caller.msg("Arcana: You gain +5 to attack and defense for 1 day!")
        elif roll == 1:
            self.caller.db.dramatic_wounds += 4
            self.caller.msg("Arcana: You take 4 dramatic wounds!")
        else:
            self.caller.msg("Arcana: No effect.")