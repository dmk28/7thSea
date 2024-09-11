from evennia.commands.default.muxcommand import MuxCommand
from evennia.utils.evtable import EvTable
from evennia.utils.utils import make_iter
from typeclasses.channels import Channel

class CmdChannel(MuxCommand):
    """
    Channel commands

    Usage:
      <channel> <message>
      channel/create <name> [= description]
      channel/delete <name>
      channel/list
      channel/who <name>
      channel/join <name>
      channel/leave <name>
      channel/mute <name>
      channel/unmute <name>
      channel/history <name> [= <number of messages>]

    Manages communication channels and sends messages to them.
    """

    key = "channel"
    aliases = ["chan", "@channel", "@chan", "+channel"]
    locks = "cmd:all()"
    help_category = "Communication"
    switches = ["create", "delete", "list", "who", "join", "leave", "mute", "unmute", "history"]
    def func(self):
        caller = self.caller

        if not self.args and not self.switches:
            caller.msg("Usage: <channel> <message> or channel/<switch>")
            return

        if self.switches:
            switch = self.switches[0].lower()
            if switch == "create":
                self.create_channel()
            elif switch == "delete":
                self.delete_channel()
            elif switch == "list":
                self.list_channels()
            elif switch == "who":
                self.show_who()
            elif switch == "join":
                self.join_channel()
            elif switch == "leave":
                self.leave_channel()
            elif switch == "mute":
                self.mute_channel()
            elif switch == "unmute":
                self.unmute_channel()
            elif switch == "history":
                self.show_history()
            else:
                caller.msg(f"Unknown switch: {switch}")
        else:
            # No switch; treat as a message to a channel
            self.send_message()

    def create_channel(self):
        """Create a new channel"""
        caller = self.caller
        if not self.args:
            caller.msg("Usage: channel/create <name> [= description]")
            return
        
        channel_name, sep, description = self.args.partition("=")
        channel_name = channel_name.strip()
        description = description.strip()

        if Channel.objects.filter(db_key__iexact=channel_name).exists():
            caller.msg(f"A channel named '{channel_name}' already exists.")
            return

        new_channel = Channel.create(channel_name, description=description)
        new_channel.connect(caller)
        caller.msg(f"Channel '{channel_name}' created successfully.")

    def delete_channel(self):
        """Delete an existing channel"""
        caller = self.caller
        if not self.args:
            caller.msg("Usage: channel/delete <name>")
            return
        
        channel = caller.search(self.args, global_search=True, typeclass=Channel)
        if not channel:
            return

        if not channel.access(caller, "control"):
            caller.msg("You don't have permission to delete this channel.")
            return

        channel_name = channel.key
        channel.delete()
        caller.msg(f"Channel '{channel_name}' has been deleted.")

    def list_channels(self):
        """List all available channels"""
        caller = self.caller
        channels = [chan for chan in Channel.objects.all() if chan.access(caller, "listen")]
        
        if not channels:
            caller.msg("No channels available.")
            return

        table = EvTable("Channel", "Description", "Subscribed", border="cells")
        for chan in channels:
            subscribed = "Yes" if chan.has_connection(caller) else "No"
            table.add_row(chan.key, chan.db.desc or "", subscribed)
        
        caller.msg(str(table))

    def show_who(self):
        """Show who is subscribed to a channel"""
        caller = self.caller
        if not self.args:
            caller.msg("Usage: channel/who <name>")
            return
        
        channel = caller.search(self.args, global_search=True, typeclass=Channel)
        if not channel:
            return

        caller.msg(f"Subscribers of {channel.key}: {channel.wholist}")

    def join_channel(self):
        """Join a channel"""
        caller = self.caller
        if not self.args:
            caller.msg("Usage: channel/join <name>")
            return
        
        channel = caller.search(self.args, global_search=True, typeclass=Channel)
        if not channel:
            return

        if channel.connect(caller):
            caller.msg(f"You have joined the channel {channel.key}.")
        else:
            caller.msg(f"You are already subscribed to {channel.key}.")

    def leave_channel(self):
        """Leave a channel"""
        caller = self.caller
        if not self.args:
            caller.msg("Usage: channel/leave <name>")
            return
        
        channel = caller.search(self.args, global_search=True, typeclass=Channel)
        if not channel:
            return

        if channel.disconnect(caller):
            caller.msg(f"You have left the channel {channel.key}.")
        else:
            caller.msg(f"You are not subscribed to {channel.key}.")

    def mute_channel(self):
        """Mute a channel"""
        caller = self.caller
        if not self.args:
            caller.msg("Usage: channel/mute <name>")
            return
        
        channel = caller.search(self.args, global_search=True, typeclass=Channel)
        if not channel:
            return

        if channel.mute(caller):
            caller.msg(f"You have muted {channel.key}.")
        else:
            caller.msg(f"You were already muting {channel.key}.")

    def unmute_channel(self):
        """Unmute a channel"""
        caller = self.caller
        if not self.args:
            caller.msg("Usage: channel/unmute <name>")
            return
        
        channel = caller.search(self.args, global_search=True, typeclass=Channel)
        if not channel:
            return

        if channel.unmute(caller):
            caller.msg(f"You have unmuted {channel.key}.")
        else:
            caller.msg(f"You were not muting {channel.key}.")

    def show_history(self):
        """Show channel history"""
        caller = self.caller
        if not self.args:
            caller.msg("Usage: channel/history <name> [= <number of messages>]")
            return
        
        channel_name, sep, num_messages = self.args.partition("=")
        channel_name = channel_name.strip()
        num_messages = num_messages.strip()

        channel = caller.search(channel_name, global_search=True, typeclass=Channel)
        if not channel:
            return

        try:
            num_messages = int(num_messages) if num_messages else 20
        except ValueError:
            caller.msg("Invalid number of messages. Using default of 20.")
            num_messages = 20

        channel.get_history(caller, num_messages)

    def send_message(self):
        """Send a message to a Channel"""
        caller = self.caller
        channel_name, sep, message = self.args.partition(" ")
        channel_name = channel_name.strip()
        message = message.strip()

        if not channel_name or not message:
            caller.msg("Usage: <channel> <message>")
            return

        channel = caller.search(channel_name, global_search=True, typeclass=Channel)
        if not channel:
            return

        if not channel.access(caller, "send"):
            caller.msg("You don't have permission to send messages to this channel.")
            return

        channel.msg(message, senders=[caller])