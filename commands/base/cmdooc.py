class CmdOOC(Command):
    key = "ooc"
    aliases = ["@ooc"]
    locks = "cmd:all()"
    help_category = "Comms"

    def func(self):
        ooc_channel = ExtendedChannel.objects.filter(db_key__iexact="OOC").first()
        if not ooc_channel:
            self.caller.msg("OOC channel not found.")
            return

        if not self.args:
            self.caller.msg("Say what?")
            return

        # Use the channel's msg method, which will use our custom formatting
        ooc_channel.msg(self.args, senders=[self.caller])
