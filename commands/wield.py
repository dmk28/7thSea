from evennia.commands.default.muxcommand import MuxCommand
from typeclasses.objects import Weapon, Sword, Firearm

class WeaponCommand(MuxCommand):
    """
    Handle wielding and unwielding weapons.

    Usage:
      weapon/wield <weapon>
      weapon/unwield

    Switches:
      wield - Wield the specified weapon
      unwield - Unwield your current weapon

    This command allows you to wield or unwield weapons, updating your combat stats accordingly.
    """
    key = "weapon"
    aliases = ["wield", "unwield"]
    locks = "cmd:all()"
    help_category = "Combat Commands"
    switches = ["wield", "unwield"]

    def func(self):
        caller = self.caller

        if "wield" in self.switches:
            self.do_wield()
        elif "unwield" in self.switches:
            self.do_unwield()
        else:
            caller.msg("You must specify either /wield or /unwield.")

    def do_wield(self):
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

    def do_unwield(self):
        caller = self.caller
        if not caller.db.wielded_weapon:
            caller.msg("You are not wielding any weapon.")
            return

        weapon = caller.db.wielded_weapon
        caller.msg(f"You stop wielding {weapon.name}.")
        caller.db.wielded_weapon = None
        caller.db.current_attack_skill = "Attack (Unarmed)"
        caller.db.current_parry_skill = "Parry (Unarmed)"