from evennia import Command, CmdSet

from evennia.commands.default.muxcommand import MuxCommand
from .models import ChannelMetadata
from .channels import ExtendedChannel
from evennia.comms.models import ChannelDB

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
        channel_kwargs = {
            'aliases': [name.lower()],
            'locks': "listen:all();send:all()"
        }
        metadata_kwargs = {}

        if channel_type == 'FACTION':
            if len(args) < 3:
                self.caller.msg("You must specify a faction name for a faction channel.")
                return
            metadata_kwargs['faction_name'] = args[2]
        elif channel_type == 'NATION':
            if len(args) < 3:
                self.caller.msg("You must specify a nation name for a nation channel.")
                return
            metadata_kwargs['nation_name'] = args[2]
        elif channel_type != 'OOC':
            self.caller.msg("Invalid channel type. Use FACTION, NATION, or OOC.")
            return

        if len(args) > 3:
            metadata_kwargs['custom_color'] = args[3]

        metadata, channel = ChannelMetadata.create_channel_and_metadata(
            name, channel_type, **channel_kwargs, **metadata_kwargs
        )
        
        if metadata and channel:
            self.caller.msg(f"Channel '{name}' created successfully with type {channel_type}.")
            # Automatically connect the creator to the channel
            channel.connect(self.caller)
        else:
            self.caller.msg(f"Failed to create channel '{name}'.")

class CmdSetChannelColor(Command):
    key = "setchannelcolor"
    locks = "cmd:perm(Admin)"
    help_category = "Comms"

    def func(self):
        if not self.args or len(self.args.split()) != 2:
            self.caller.msg("Usage: setchannelcolor <channel_name> <color_code>")
            return

        channel_name, color_code = self.args.split()
        channel = ChannelDB.objects.channel_search(channel_name).first()
        if not channel:
            self.caller.msg(f"Channel '{channel_name}' not found.")
            return

        metadata = ChannelMetadata.objects.get_or_create(channel=channel)[0]
        metadata.custom_color = color_code
        metadata.save()

        # Also set the color on the channel object itself
        channel.db.custom_color = color_code

        self.caller.msg(f"Color for channel '{channel_name}' set to {color_code}.")
class CommsCmdSet(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdCreateChannel())
        self.add(CmdSetChannelColor())
