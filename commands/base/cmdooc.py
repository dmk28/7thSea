from evennia import Command

class CmdOOC(Command):
    """
    Send an out-of-character message to the room.

    Usage:
      ooc <message>
      @ooc <message>
      ooc :<emote>
      ooc ;<pose>

    This command sends an OOC message to all characters in the same room.
    You can use : for emotes and ; for poses.
    """
    key = "ooc"
    aliases = ["@ooc"]
    locks = "cmd:all()"
    help_category = "Comms"

    def func(self):
        if not self.args:
            self.caller.msg("Say what?")
            return

        location = self.caller.location
        if not location:
            self.caller.msg("You have no location to speak in!")
            return

        message = self.args.strip()
        if message.startswith(':'):
            # Emote
            emote = message[1:].strip()
            ooc_string = f"|w<OOC> {self.caller.name} {emote}|n"
            self_string = f"You emote (OOC): {self.caller.name} {emote}"
        elif message.startswith(';'):
            # Pose
            pose = message[1:].strip()
            ooc_string = f"|w<OOC> {self.caller.name}{pose}|n"
            self_string = f"You pose (OOC): {self.caller.name}{pose}"
        else:
            # Regular OOC message
            ooc_string = f'|w<OOC>|n {self.caller.name} says, "{message}"|n'
            self_string = f'|w<OOC>|n You say, "{message}"'

        # Send the message to the room
        location.msg_contents(ooc_string, exclude=self.caller)

        # Send the message to the speaker
        self.caller.msg(self_string)