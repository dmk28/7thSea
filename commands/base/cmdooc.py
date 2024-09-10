from evennia import Command

class CmdOOC(Command):
    """
    Send an out-of-character message to the room.

    Usage:
      ooc <message>
      @ooc <message>

    This command sends an OOC message to all characters in the same room.
    """
    key = "ooc"
    aliases = ["@ooc"]
    locks = "cmd:all()"
    help_category = "Comms"

    def func(self):
        if not self.args:
            self.caller.msg("Say what?")
            return

        # Get the caller's location (the room)
        location = self.caller.location

        if not location:
            self.caller.msg("You have no location to speak in!")
            return

        # Format the OOC message
        ooc_string = f"|w(OOC) {self.caller.name}: {self.args}|n"

        # Send the message to the room
        location.msg_contents(ooc_string, exclude=self.caller)

        # Also send the message to the speaker
        self.caller.msg(f"You say (OOC): {self.args}")