from evennia import Command
from evennia.commands.default.muxcommand import MuxCommand
from world.combat_script.combat_system import get_combat
from evennia import create_script

class CombatCommand(MuxCommand):
    """
    Handle all combat-related actions.

    Usage:
      combat/attack <target>
      combat/defend
      combat/hold
      combat/pass
      combat/feint <target>
      combat/stopthrust
      combat/riposte
      combat/doubleparry
      combat/lunge <target>
      combat/tag <target>
      combat/doubleattack <target>
      combat/pommelstrike <target>
      combat/start <target1> [<target2> ...]
      combat/join <combat_id>
      combat/force_end (admin only)
      combat/end

    This command handles all combat actions, including starting, joining, and ending combat.
    """
    key = "+combat"
    aliases = ["@combat"]
    locks = "cmd:all()"
    help_category = "Combat Commands"
    switches = ["attack", "defend", "hold", "pass", "feint", "stopthrust", "riposte", 
                "doubleparry", "lunge", "tag", "doubleattack", "pommelstrike", "start", "join", "force_end", "end"]

    def func(self):
        combat = get_combat(self.caller)
        
        if "start" in self.switches:
            self.start_combat()
            return
        
        if "join" in self.switches:
            self.join_combat()
            return
        
        if "force_end" in self.switches and self.caller.check_permstring("Builders"):
            self.end_combat(combat)
            return

        if "end" in self.switches:
            self.vote_end_combat(combat)
            return

        if not combat:
            self.caller.msg("You are not in combat.")
            return

        if combat.db.current_actor != self.caller and self.cmdstring != "combat":
            self.caller.msg("It's not your turn to act.")
            return

        action = self.cmdstring if self.cmdstring != "combat" else (self.switches[0] if self.switches else None)

        if not action:
            self.caller.msg("You must specify a combat action.")
            return

        if action in ["attack", "feint", "lunge", "tag", "doubleattack", "pommelstrike"]:
            if not self.args:
                self.caller.msg(f"You must specify a target for {action}.")
                return
            combat.handle_action_input(self.caller, f"{action} {self.args}")
        elif action in ["defend", "hold", "pass", "stopthrust", "riposte", "doubleparry"]:
            combat.handle_action_input(self.caller, action)
        else:
            self.caller.msg(f"Unknown combat action: {action}")

    def start_combat(self):
        if not self.args:
            self.caller.msg("You must specify at least one target to start combat with.")
            return
        
        targets = [self.caller.search(arg) for arg in self.args.split()]
        targets = [t for t in targets if t]  # Remove any None values
        
        if len(targets) < 1:
            self.caller.msg("You need to specify at least one valid target.")
            return
        
        existing_combat = get_combat(self.caller)
        if existing_combat:
            self.caller.msg("You are already in combat.")
            return

        combat = create_script("typeclasses.scripts.CombatScript")
        if not combat:
            self.caller.msg("Failed to create combat.")
            return

        combat.db.participants = [self.caller] + targets
        combat.start_combat()
        
        self.caller.msg(f"You have initiated combat with {', '.join(t.name for t in targets)}!")
        for target in targets:
            target.msg(f"{self.caller.name} has initiated combat with you!")

    def join_combat(self):
        if not self.args:
            self.caller.msg("You must specify a combat ID to join.")
            return
        
        try:
            combat_id = int(self.args)
        except ValueError:
            self.caller.msg("Invalid combat ID. Please provide a number.")
            return

        combat = get_combat(combat_id)
        if not combat:
            self.caller.msg(f"No combat found with ID {combat_id}")
            return

        if self.caller in combat.db.participants:
            self.caller.msg("You are already in this combat.")
            return

        combat.db.participants.append(self.caller)
        self.caller.db.combat_id = combat.id
        self.caller.msg(f"You have joined the combat with ID {combat_id}")
        combat.msg_all(f"{self.caller.name} has joined the combat!")

    def end_combat(self, combat):
        if combat:
            combat.force_end_combat()
            self.caller.msg("You have forcefully ended the combat.")
        else:
            self.caller.msg("You are not in an active combat.")

    def vote_end_combat(self, combat):
        if not combat:
            self.caller.msg("You are not in an active combat.")
            return
        
        combat.vote_end_combat(self.caller)

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