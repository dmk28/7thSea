from evennia import Command, CmdSet

from evennia.commands.default.muxcommand import MuxCommand



class CmdCreateChannel(Command):
    key = "createchannel"
    locks = "cmd:perm(Admin)"
    help_category = "Comms"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: createchannel <name> <type> [faction/nation] [color]")
            return

        args = self.args.split()
        if len(args) < 2:
            self.caller.msg("You must specify at least a channel name and type.")
            return

        name, channel_type = args[0], args[1].upper()
        kwargs = {}

        if channel_type == 'FACTION':
            if len(args) < 3:
                self.caller.msg("You must specify a faction name for a faction channel.")
                return
            kwargs['faction_name'] = args[2]
        elif channel_type == 'NATION':
            if len(args) < 3:
                self.caller.msg("You must specify a nation name for a nation channel.")
                return
            kwargs['nation_name'] = args[2]
        elif channel_type != 'OOC':
            self.caller.msg("Invalid channel type. Use FACTION, NATION, or OOC.")
            return

        if len(args) > 3:
            kwargs['custom_color'] = args[3]

        metadata = ChannelMetadata.create_channel_and_metadata(name, channel_type, **kwargs)
        
        self.caller.msg(f"Channel '{name}' created successfully with type {channel_type}.")




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
        self.add(CmdSetChannelColor())
