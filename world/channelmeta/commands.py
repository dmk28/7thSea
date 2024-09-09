from evennia import Command, CmdSet

from evennia.commands.default.muxcommand import MuxCommand


class CmdCreateChannel(Command):
    key = "createchannel"
    locks = "cmd:perm(Admin)"
    help_category = "Comms"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: createchannel <name> <type> [faction/nation]")
            return

        name, channel_type, *extra = self.args.split()
        channel = ExtendedChannel.create(name)
        
        if channel_type.upper() == 'FACTION':
            if not extra:
                self.caller.msg("You must specify a faction name for a faction channel.")
                return
            channel.set_channel_type('FACTION', faction_name=extra[0])
        elif channel_type.upper() == 'NATION':
            if not extra:
                self.caller.msg("You must specify a nation name for a nation channel.")
                return
            channel.set_channel_type('NATION', nation_name=extra[0])
        elif channel_type.upper() == 'OOC':
            channel.set_channel_type('OOC')
        else:
            self.caller.msg("Invalid channel type. Use FACTION, NATION, or OOC.")
            return

        self.caller.msg(f"Channel '{name}' created successfully.")

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



class CmdSetChannelColor(Command):
    key = "setchannelcolor"
    locks = "cmd:perm(Admin)"
    help_category = "Comms"

    def func(self):
        if not self.args or len(self.args.split()) != 2:
            self.caller.msg("Usage: setchannelcolor <channel_name> <color_code>")
            return

        channel_name, color_code = self.args.split()
        channel = ExtendedChannel.objects.filter(db_key__iexact=channel_name).first()
        if not channel:
            self.caller.msg(f"Channel '{channel_name}' not found.")
            return

        channel.set_channel_color(color_code)
        self.caller.msg(f"Color for channel '{channel_name}' set to {color_code}.")

class CommsCmdSet(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdCreateChannel())
        self.add(CmdOOC())
        self.add(CmdSetChannelColor())
