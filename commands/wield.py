from evennia import Command
from typeclasses.objects import Weapon, Sword, Firearm

class CmdWield(Command):
    """
    Wield a weapon.

    Usage:
      wield <weapon>

    This will wield the specified weapon, updating your combat stats.
    """
    key = "wield"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Wield what?")
            return

        weapon_name = self.args.strip()
        weapon = caller.search(weapon_name, location=caller)

        if not weapon:
            return  # caller.search() already sends an appropriate error message

        if not isinstance(weapon, (Weapon, Sword, Firearm)):
            caller.msg("That's not a weapon.")
            return

        # Unwield currently wielded weapon
        current_weapon = caller.db.wielded_weapon
        if current_weapon:
            if current_weapon.location != caller:
                caller.msg("You seem to have lost your wielded weapon.")
                caller.db.wielded_weapon = None
            elif current_weapon == weapon:
                caller.msg(f"You are already wielding {weapon.name}.")
                return
            else:
                caller.msg(f"You stop wielding {current_weapon.name}.")
                caller.db.wielded_weapon = None

        # Wield new weapon
        caller.db.wielded_weapon = weapon
        caller.msg(f"You wield {weapon.name}.")

        # Update combat stats
        if hasattr(weapon.db, 'attack_skill'):
            caller.db.current_attack_skill = weapon.db.attack_skill
        else:
            caller.msg(f"Warning: {weapon.name} has no attack skill defined.")

        if hasattr(weapon.db, 'parry_skill'):
            caller.db.current_parry_skill = weapon.db.parry_skill
        else:
            caller.msg(f"Warning: {weapon.name} has no parry skill defined.")


class CmdUnwield(Command):
    """
    Unwield your current weapon.

    Usage:
      unwield

    This will unwield your current weapon, reverting to unarmed combat stats.
    """
    key = "unwield"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not caller.db.wielded_weapon:
            caller.msg("You are not wielding any weapon.")
            return
        weapon = caller.db.wielded_weapon
        caller.msg(f"You stop wielding {weapon.name}.")
        caller.db.wielded_weapon = None
        caller.db.current_attack_skill = "Attack (Unarmed)"
        caller.db.current_parry_skill = "Parry (Unarmed)"