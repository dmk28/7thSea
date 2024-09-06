from evennia import Command, CmdSet
from evennia import create_script
from evennia.scripts.models import ScriptDB

class SocialActionMixin:
    locks = "cmd:attr(approved) or perm(Admin)"
    help_category = "Social"

    def func(self):
        action = self.key.split('_')[1] if '_' in self.key else self.key
        if not self.args:
            self.caller.msg(f"You must specify a target to {action}.")
            return
        self.execute_social_action(action)

    def execute_social_action(self, action):
        repartee = get_repartee(self.caller)
        if not repartee:
            self.caller.msg("You are not in repartee.")
            return
        repartee.handle_action_input(self.caller, f"{action} {self.args}")

class CmdStartRepartee(Command):
    key = "startrepartee"
    # locks = "cmd:attr(approved) or perm(Admin)"
    help_category = "Social"

    def func(self):
        if not self.args:
            self.caller.msg("You must specify a target.")
            return

        target = self.caller.search(self.args)
        if not target:
            return

        if self.caller == target:
            self.caller.msg("You cannot start repartee with yourself.")
            return

        existing_repartee = get_repartee(self.caller)
        if existing_repartee:
            self.caller.msg("You are already in repartee.")
            return

        repartee = create_script("world.combat_script.social_combat.SocialCombat")
        repartee.db.participants = [self.caller, target]
        repartee.start_repartee()

        self.caller.msg(f"You have initiated repartee with {target.name}!")
        target.msg(f"{self.caller.name} has initiated repartee with you!")

class CmdTaunt(SocialActionMixin, Command):
    key = "taunt"

    def func(self):
        if not self.args:
            self.caller.msg("You must specify a target to taunt.")
            return
        self.execute_social_action("taunt")

class CmdCharm(SocialActionMixin, Command):
    key = "repartee_charm"
    aliases = ["charm"]
    def func(self):
        if not self.args:
            self.caller.msg("You must specify a target to charm.")
            return
        self.execute_social_action("charm")

class CmdIntimidate(SocialActionMixin, Command):
    key = "repartee_intimidate"
    aliases = ["intimidate"]
    def func(self):
        if not self.args:
            self.caller.msg("You must specify a target to intimidate.")
            return
        self.execute_social_action("intimidate")

class CmdGossip(SocialActionMixin, Command):
    key = "repartee_gossip"
    aliases = ["gossip"]
    def func(self):
        if not self.args:
            self.caller.msg("You must specify a target to gossip about.")
            return
        self.execute_social_action("gossip")

class CmdRidicule(SocialActionMixin, Command):
    key = "repartee_ridicule"
    aliases = ["ridicule"]
    def func(self):
        if not self.args:
            self.caller.msg("You must specify a target to ridicule.")
            return
        self.execute_social_action("ridicule")

class CmdBlackmail(SocialActionMixin, Command):
    key = "repartee_blackmail"
    aliases = ["blackmail"]
    def func(self):
        if not self.args:
            self.caller.msg("You must specify a target to blackmail.")
            return
        self.execute_social_action("blackmail")

class CmdPassRepartee(Command):
    key = "pass"
    locks = "cmd:attr(approved) or perm(Admin)"
    help_category = "Social"

    def func(self):
        repartee = get_repartee(self.caller)
        if not repartee:
            self.caller.msg("You are not in repartee.")
            return
        repartee.handle_action_input(self.caller, "pass")



class CmdEndRepartee(Command):
    """
    End the current repartee.

    Usage:
      endrepartee

    This command ends the current repartee that you're participating in.
    """
    key = "endrepartee"
    locks = "cmd:attr(approved) or perm(Admin)"
    help_category = "Social"

    def func(self):
        from world.combat_script.social_combat import SocialCombat
        repartee_id = self.caller.db.repartee_id
        if not repartee_id:
            self.caller.msg("You are not in repartee.")
            return

        repartee = SocialCombat.get_or_create(repartee_id)
        if not repartee:
            self.caller.msg(f"Error: Could not find the repartee script with ID {repartee_id}.")
            return


        if hasattr(repartee, 'end_repartee'):
            repartee.end_repartee()
            self.caller.msg("You have ended the repartee.")
        else:
            self.caller.msg("Error: The repartee script doesn't have an end_repartee method.")
            self.caller.msg(f"Available methods: {[method for method in dir(repartee) if callable(getattr(repartee, method))]}")

            
def get_repartee(caller):
    from world.combat_script.social_combat import SocialCombat
    if hasattr(caller.db, 'repartee_id'):
        repartee_id = caller.db.repartee_id
        repartee = ScriptDB.objects.filter(id=repartee_id, db_typeclass_path__endswith='SocialCombat').first()
        if repartee:
        
            return repartee
        else:
            caller.msg(f"Debug: No repartee script found for ID {repartee_id}")
    else:
        caller.msg("Debug: caller.db has no repartee_id attribute")
    return None



class ReparteeCmdSet(CmdSet):
    key = "repartee"
    mergetype = 'Union'
    duplicates = False
    priority = 1
    key_mergetype = {"ReparteeCmdSet": "Replace"}

    def at_cmdset_creation(self):
        self.add(CmdStartRepartee())
        self.add(CmdTaunt())
        self.add(CmdCharm())
        self.add(CmdIntimidate())
        self.add(CmdGossip())
        self.add(CmdRidicule())
        self.add(CmdBlackmail())
        self.add(CmdPassRepartee())
        self.add(CmdEndRepartee())

    def at_cmdset_add(self, obj):
        logger.debug(f"ReparteeCmdSet added to {obj}")
        # Remove any existing ReparteeCmdSet before adding this one
        existing = obj.cmdset.get("repartee_cmdset")
        if existing:
            obj.cmdset.remove(existing)

    def at_cmdset_remove(self, obj):
        logger.debug(f"ReparteeCmdSet removed from {obj}")