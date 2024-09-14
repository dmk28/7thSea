from evennia import Command, CmdSet
from evennia.utils.utils import class_from_module
from evennia.utils.search import search_channel

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

        if channel_type == 'FACTION':
            if len(args) < 3:
                self.caller.msg("You must specify a faction name for a faction channel.")
                return
            channel_kwargs['db_channel_type'] = 'FACTION'
            channel_kwargs['db_faction_name'] = args[2]
            channel_kwargs['db_custom_color'] = Channel.generate_random_color()
        elif channel_type == 'NATION':
            if len(args) < 3:
                self.caller.msg("You must specify a nation name for a nation channel.")
                return
            channel_kwargs['db_channel_type'] = 'NATION'
            channel_kwargs['db_nation_name'] = args[2]
            channel_kwargs['db_custom_color'] = NATION_COLORS.get(args[2], '|w')
        elif channel_type == 'OOC':
            channel_kwargs['db_channel_type'] = 'OOC'
        else:
            self.caller.msg("Invalid channel type. Use FACTION, NATION, or OOC.")
            return

        if len(args) > 3:
            channel_kwargs['db_custom_color'] = args[3]

        channel_typeclass = class_from_module(settings.BASE_CHANNEL_TYPECLASS)
        new_channel = channel_typeclass.create(name, **channel_kwargs)

        if new_channel:
            self.caller.msg(f"Channel '{name}' created successfully with type {channel_type}.")
            new_channel.connect(self.caller)
        else:
            self.caller.msg(f"Failed to create channel '{name}'.")

class CmdSetChannelColor(Command):
    """
    Syntax: setchannelcolor channel_name color_code
    """
    key = "setchannelcolor"
    locks = "cmd:perm(Admin)"
    help_category = "Comms"

    def func(self):
        if not self.args or len(self.args.split()) != 2:
            self.caller.msg("Usage: setchannelcolor <channel_name> <color_code>")
            return

        channel_name, color_code = self.args.split()
        channel = search_channel(channel_name).first()

        if not channel:
            self.caller.msg(f"Channel '{channel_name}' not found.")
            return

        channel.set_color(color_code)
        self.caller.msg(f"Color for channel '{channel_name}' set to {color_code}.")

class CommsCmdSet(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdCreateChannel())
        self.add(CmdSetChannelColor())