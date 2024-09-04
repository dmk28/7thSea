from evennia import Command, CmdSet
from evennia import create_script
from evennia.scripts.models import ScriptDB

class SocialActionMixin:
    locks = "cmd:attr(approved) or perm(Admin)"
    help_category = "Social"

    def execute_social_action(self, action):
        repartee = get_repartee(self.caller)
        if not repartee:
            self.caller.msg("You are not in repartee.")
            return
        repartee.handle_action_input(self.caller, f"{action} {self.args}")

class CmdStartRepartee(Command):
    key = "startrepartee"
    locks = "cmd:attr(approved) or perm(Admin)"
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

        repartee = create_script("world.social_combat.SocialCombat")
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
    key = "charm"

    def func(self):
        if not self.args:
            self.caller.msg("You must specify a target to charm.")
            return
        self.execute_social_action("charm")

class CmdIntimidate(SocialActionMixin, Command):
    key = "intimidate"

    def func(self):
        if not self.args:
            self.caller.msg("You must specify a target to intimidate.")
            return
        self.execute_social_action("intimidate")

class CmdGossip(SocialActionMixin, Command):
    key = "gossip"

    def func(self):
        if not self.args:
            self.caller.msg("You must specify a target to gossip about.")
            return
        self.execute_social_action("gossip")

class CmdRidicule(SocialActionMixin, Command):
    key = "ridicule"

    def func(self):
        if not self.args:
            self.caller.msg("You must specify a target to ridicule.")
            return
        self.execute_social_action("ridicule")

class CmdBlackmail(SocialActionMixin, Command):
    key = "blackmail"

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

def get_repartee(caller):
    if hasattr(caller.db, 'repartee_id'):
        repartee_id = caller.db.repartee_id
        repartee = ScriptDB.objects.filter(id=repartee_id, db_key='SocialCombatScript').first()
        if repartee:
            return repartee
    return None

class ReparteeCmdSet(CmdSet):
    key = "repartee"

    def at_cmdset_creation(self):
        self.add(CmdStartRepartee())
        self.add(CmdTaunt())
        self.add(CmdCharm())
        self.add(CmdIntimidate())
        self.add(CmdGossip())
        self.add(CmdRidicule())
        self.add(CmdBlackmail())
        self.add(CmdPassRepartee())