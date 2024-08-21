from evennia import Command

class CmdDebugCharacter(Command):
    """
    Debug a character's attributes

    Usage:
      debug_character <character_name>
    """

    key = "debug_character"
    locks = "cmd:perm(Wizards)"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: debug_character <character_name>")
            return

        char = self.caller.search(self.args)
        if not char:
            return

        self.caller.msg(f"Attributes for {char.name}:")
        for attr in char.attributes.all():
            self.caller.msg(f"{attr.key}: {attr.value}")