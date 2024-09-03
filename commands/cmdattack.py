from evennia import Command
from world.combat_script.combat_system import get_combat
from evennia import create_script



class CmdAttack(Command):
    """
    Attack another character in combat.

    Usage:
      attack <target>


    This command lets you attack another character or perform special moves during combat.
    """
    key = "attack"
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        combat = get_combat(self.caller)
        if not combat:
            self.caller.msg("You are not in combat.")
            return

        cmd = self.cmdstring.lower()

        if cmd == "attack":
            if not self.args:
                self.caller.msg("You must specify a target to attack.")
                return
            combat.handle_action_input(self.caller, f"attack {self.args}")
       

class CmdFullDefense(Command):
    '''When in combat, use 'defend' to trigger a full defense'''
    key = "defend"
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        combat = get_combat(self.caller)
        if not combat:
            self.caller.msg("You are not in combat.")
            return
        if combat.db.current_actor != self.caller:
            self.caller.msg("It's not your turn to act.")
            return
        if combat.db.action_state == "choosing_action":
            combat.handle_action_input(self.caller, "defend")  # Changed from "2" to "defend"
        else:
            self.caller.msg("You can't defend right now.")

class CmdHoldAction(Command):
    '''When in combat, use 'hold' to hold a full action'''
    key = "hold"
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        combat = get_combat(self.caller)
        if not combat:
            self.caller.msg("You are not in combat.")
            return
        if combat.db.current_actor != self.caller:
            self.caller.msg("It's not your turn to act.")
            return
        if combat.db.action_state == "choosing_action":
            combat.handle_action_input(self.caller, "hold")  # Changed from "3" to "hold"
        else:
            self.caller.msg("You can't hold your action right now.")

class CmdPassTurn(Command):
    '''Pass the turn with pass, when in combat.'''
    key = "pass"
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        combat = get_combat(self.caller)
        if not combat:
            self.caller.msg("You are not in combat.")
            return
        if combat.db.current_actor != self.caller:
            self.caller.msg("It's not your turn to act.")
            return
        if combat.db.action_state == "choosing_action":
            combat.handle_action_input(self.caller, "pass")  # Changed from "4" to "pass"
        else:
            self.caller.msg("You can't pass your turn right now.")

class CmdStartCombat(Command):
    key = "startcombat"
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        self.caller.msg("Debug: StartCombat command initiated.")
        
        if not self.args:
            self.caller.msg("You must specify a target.")
            return
        
        target = self.caller.search(self.args)
        if not target:
            self.caller.msg("Debug: Target not found.")
            return
        
        if self.caller == target:
            self.caller.msg("You cannot start combat with yourself.")
            return
        
        existing_combat = get_combat(self.caller)
        if existing_combat:
            self.caller.msg("You are already in combat.")
            return

        self.caller.msg("Debug: Creating new CombatScript.")
        combat = create_script("typeclasses.scripts.CombatScript")
        
        if not combat:
            self.caller.msg("Debug: Failed to create CombatScript.")
            return

        self.caller.msg(f"Debug: CombatScript created with ID {combat.id}")
        
        combat.db.participants = [self.caller, target]
        combat.start_combat()
        
        self.caller.msg(f"Debug: Combat started. Your combat_id is set to {self.caller.db.combat_id}")
        self.caller.msg(f"You have initiated combat with {target.name}!")
        target.msg(f"{self.caller.name} has initiated combat with you!")


class CmdEndCombat(Command):
    key = "endcombat"
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        combat = get_combat(self.caller)
        if combat:
            combat.end_combat()
            self.caller.msg("You have ended the combat.")
        else:
            self.caller.msg("You are not in an active combat.")

class CmdFeint(Command):
    key = "feint"
    help_category = "Swordsman"
    def func(self):
        combat = get_combat(self.caller)
        if combat:
            combat.handle_action_input(self.caller, f"feint {self.args}")
        else:
            self.caller.msg("You are not in combat.")
class CmdStopThrust(Command):
    help_category = "Swordsman"
    key="stopthrust"
    def func(self):
        combat = get_combat(self.caller)
        if combat:
            combat.handle_action_input(self.caller, f"stopthrust {self.args}")
        else:
            self.caller.msg("You are not in combat.")
class CmdRiposte(Command):
    key="riposte"
    help_category = "Swordsman"

    def func(self):
        combat = get_combat(self.caller)
        if combat:
            combat.handle_action_input(self.caller, f"riposte {self.args}")
        else:
            self.caller.msg("You are not in combat.")
class CmdDoubleParry(Command):
    key="doubleparry"
    help_category = "Swordsman"
    def func(self):
        combat = get_combat(self.caller)
        if combat:
            combat.handle_action_input(self.caller, f"doubleparry {self.args}")
        else:
            self.caller.msg("You are not in combat.")
class CmdLunge(Command):
    key="lunge"
    help_category = "Swordsman"
    def func(self):
        combat = get_combat(self.caller)
        if combat:
            combat.handle_action_input(self.caller, f"lunge {self.args}")
        else:
            self.caller.msg("You are not in combat.")

class CmdTag(Command):
    key="tag"
    help_category = "Swordsman"
    def func(self):
        combat = get_combat(self.caller)
        if combat:
            combat.handle_action_input(self.caller, f"tag {self.args}")
        else:
            self.caller.msg("You are not in combat.")
class CmdDoubleAttack(Command):
    key = "double-attack"
    aliases = ["doubleattack"]
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        combat = get_combat(self.caller)
        if combat:
            if not self.args:
                self.caller.msg("You must specify a target for double-attack.")
                return
            if not self.caller.character_sheet.get_knack_value("Double-Attack (Fencing)"):
                self.caller.msg("You don't know how to perform a Double-Attack.")
                return
            combat.handle_action_input(self.caller, f"double-attack {self.args}")
        else:
            self.caller.msg("You are not in combat.")
# Similar classes for Riposte, Lunge, etc.

# class CmdSpecial(Command):
#     """
#     Use a special combat move.

#     Usage:
#       special
#     """
#     key = "special"
#     locks = "cmd:all()"

#     def func(self):
#         combat = self.caller.ndb.combat
#         if combat:
#             combat.handle_action_input(self.caller, "special")
#         else:
#             self.caller.msg("You are not in combat.")

class CmdViewCombatEffects(Command):
    """
    View your active combat effects.

    Usage:
      combat_effects
    """
    key = "combat_effects"
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        combat_effects = [effect for effect in self.caller.db.special_effects]
        if len(combat_effects) < 1:
            self.caller.msg("You are not in combat.")
        if combat_effects:
            self.caller.msg("Your active combat effects:")
            for effect in combat_effects:
                self.caller.msg(f"- {effect.replace('_', ' ').title()}")
        else:
            self.caller.msg("You have no active combat effects.")