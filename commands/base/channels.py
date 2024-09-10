# commands/channel_commands.py
from django.conf import settings
from django.db.models import Q
from evennia.commands.default.comms import CmdChannel as OldCmdChannel
from evennia.utils import create, logger
from evennia.accounts import bots
from evennia.utils.utils import make_iter
from evennia.utils.evtable import EvTable
from evennia.comms.models import ChannelDB, Msg
from world.channelmeta.models import ChannelMetadata
from typeclasses.channels import NewChannel
from evennia.utils.evmenu import ask_yes_no
from evennia.utils.logger import tail_log_file
from evennia.utils.utils import class_from_module, strip_unsafe_input
import os
class CmdChannel(OldCmdChannel):
    """
    Overloaded channel command to work with NewChannel typeclass.

    Usage:
      channel
      channel <channel>
      channel <channel> = <message>
      channel/create <channel> [= description]
      channel/delete <channel>
      channel/desc <channel> = <description>
      channel/lock <channel> = <lockstring>
      channel/unlock <channel> = <lockstring>
      channel/history <channel>
      channel/ban <channel> = <account>
      channel/unban <channel> = <account>
      channel/mute <channel>
      channel/unmute <channel>
      channel/who <channel>
      channel/list
      channel/sub <channel>
      channel/unsub <channel>

    Manage and use channels. The channel system also supports the use of
    aliases to reduce confusion when chanels are similarly named. To use
    channel aliases, add them after the channel name like this: 
    channelname;alias;othealias
    """

    def func(self):
        """Implement the command"""
        caller = self.caller
        args = self.args

        if not args:
            self.list_channels()
            return

        if '=' in args:
            channel, message = [part.strip() for part in args.split('=', 1)]
            self.msg_channel(channel, message)
        else:
            switch = self.switches and self.switches[0] or None
            if not switch:
                # Check if this is an attempt to send a message
                channel = args
                self.msg_channel(channel, "")
            else:
                # Process switches
                if switch in ("create", "new"):
                    self.create_channel()
                elif switch in ("delete", "del", "destroy"):
                    self.delete_channel()
                elif switch == "desc":
                    self.set_channel_desc()
                elif switch == "lock":
                    self.set_channel_lock()
                elif switch == "unlock":
                    self.unset_channel_lock()
                elif switch == "ban":
                    self.ban_account()
                elif switch == "unban":
                    self.unban_account()
                elif switch == "mute":
                    self.mute_channel()
                elif switch == "unmute":
                    self.unmute_channel()
                elif switch == "who":
                    self.list_channel_users()
                elif switch == "list":
                    self.list_channels()
                elif switch == "sub":
                    self.join_channel()
                elif switch == "unsub":
                    self.leave_channel()
                elif switch == "history":
                     self.show_history()
                else:
                    caller.msg(f"Unknown switch: {switch}")

    def create_channel(self):
      """Create a new channel"""
      caller = self.caller
      if not self.args:
         caller.msg("Usage: channel/create <name> [= description]")
         return

      channel_name = self.lhs
      description = self.rhs or ""

      # Check if the channel already exists
      existing_channel = ChannelDB.objects.channel_search(channel_name)
      if existing_channel:
         caller.msg(f"Channel '{channel_name}' already exists.")
         return

      # Create the new channel
      new_channel = create.create_channel(channel_name, typeclass=NewChannel, desc=description)
      
      # Use get_or_create instead of create
      metadata, created = ChannelMetadata.objects.get_or_create(
         channel=new_channel,
         defaults={'channel_type': 'OOC'}
      )
      
      if not created:
         # If the metadata already existed, update it
         metadata.channel_type = 'OOC'
         metadata.save()

      new_channel.connect(caller)
      caller.msg(f"Created new channel '{channel_name}'.")
   
    def show_history(self):
        """Show the history of a channel."""
        if not self.args:
            self.caller.msg("Usage: channel/history <channel> [= <number of lines>]")
            return

        channel_name, _, lines = self.args.partition("=")
        channel_name = channel_name.strip()
        lines = lines.strip()

        channel = self.search_channel(channel_name)
        if not channel:
            return

        try:
            num_lines = int(lines) if lines else 20
        except ValueError:
            self.caller.msg("Invalid number of lines. Using default of 20.")
            num_lines = 20

        log_file = channel.log_file
        if not log_file or not os.path.exists(log_file):
            self.caller.msg(f"No history found for channel '{channel.key}'.")
            return

        def send_msg(lines):
            self.caller.msg(f"Last {len(lines)} messages in {channel.key}:")
            self.caller.msg("\n".join(lines))

        tail_log_file(log_file, 0, num_lines, callback=send_msg)


    def msg_channel(self, channelname, msg):
        """Send a message to a channel"""
        caller = self.caller
        channel = self.search_channel(channelname)
        if not channel:
            return

        if not channel.access(caller, 'send'):
            caller.msg("You don't have permission to send messages to this channel.")
            return

        channel.msg(msg, senders=caller)

    def delete_channel(self):
        """Delete a channel"""
        caller = self.caller
        if not self.args:
            caller.msg("Usage: channel/delete <name>")
            return

        channel = self.search_channel(self.args)
        if not channel:
            return

        if not channel.access(caller, 'control'):
            caller.msg("You don't have permission to delete this channel.")
            return

        channel.delete()
        caller.msg(f"Channel '{channel.key}' was destroyed.")

    def set_channel_desc(self):
        """Set a channel's description"""
        caller = self.caller
        if not self.args or not self.rhs:
            caller.msg("Usage: channel/desc <name> = <description>")
            return

        channel = self.search_channel(self.lhs)
        if not channel:
            return

        if not channel.access(caller, 'control'):
            caller.msg("You don't have permission to change this channel's description.")
            return

        channel.db.desc = self.rhs
        caller.msg(f"Description of channel '{channel.key}' set to: {self.rhs}")

    def set_channel_lock(self):
        """Set a lock on the channel"""
        caller = self.caller
        if not self.args or not self.rhs:
            caller.msg("Usage: channel/lock <name> = <lockstring>")
            return

        channel = self.search_channel(self.lhs)
        if not channel:
            return

        if not channel.access(caller, 'control'):
            caller.msg("You don't have permission to change this channel's locks.")
            return

        channel.locks.add(self.rhs)
        caller.msg(f"Lock(s) applied to channel '{channel.key}': {self.rhs}")

    def unset_channel_lock(self):
        """Remove a lock from the channel"""
        caller = self.caller
        if not self.args or not self.rhs:
            caller.msg("Usage: channel/unlock <name> = <lockstring>")
            return

        channel = self.search_channel(self.lhs)
        if not channel:
            return

        if not channel.access(caller, 'control'):
            caller.msg("You don't have permission to change this channel's locks.")
            return

        channel.locks.remove(self.rhs)
        caller.msg(f"Lock(s) removed from channel '{channel.key}': {self.rhs}")

    def ban_account(self):
        """Ban an account from a channel"""
        caller = self.caller
        if not self.args or not self.rhs:
            caller.msg("Usage: channel/ban <name> = <account>")
            return

        channel = self.search_channel(self.lhs)
        if not channel:
            return

        if not channel.access(caller, 'control'):
            caller.msg("You don't have permission to ban users from this channel.")
            return

        target = caller.search(self.rhs)
        if not target:
            return

        channel.ban(target)
        caller.msg(f"{target.key} was banned from channel '{channel.key}'.")

    def unban_account(self):
        """Unban an account from a channel"""
        caller = self.caller
        if not self.args or not self.rhs:
            caller.msg("Usage: channel/unban <name> = <account>")
            return

        channel = self.search_channel(self.lhs)
        if not channel:
            return

        if not channel.access(caller, 'control'):
            caller.msg("You don't have permission to unban users from this channel.")
            return

        target = caller.search(self.rhs)
        if not target:
            return

        channel.unban(target)
        caller.msg(f"{target.key} was unbanned from channel '{channel.key}'.")

    def mute_channel(self):
        """Mute a channel"""
        caller = self.caller
        if not self.args:
            caller.msg("Usage: channel/mute <name>")
            return

        channel = self.search_channel(self.args)
        if not channel:
            return

        if channel.mute(caller):
            caller.msg(f"You have muted channel '{channel.key}'.")
        else:
            caller.msg(f"You were already muting channel '{channel.key}'.")

    def unmute_channel(self):
        """Unmute a channel"""
        caller = self.caller
        if not self.args:
            caller.msg("Usage: channel/unmute <name>")
            return

        channel = self.search_channel(self.args)
        if not channel:
            return

        if channel.unmute(caller):
            caller.msg(f"You have unmuted channel '{channel.key}'.")
        else:
            caller.msg(f"You were not muting channel '{channel.key}'.")

    def list_channel_users(self):
        """List users subscribed to a channel"""
        caller = self.caller
        if not self.args:
            caller.msg("Usage: channel/who <name>")
            return

        channel = self.search_channel(self.args)
        if not channel:
            return

        if not channel.access(caller, 'listen'):
            caller.msg("You don't have permission to see who's on this channel.")
            return

        subs = channel.subscriptions.all()
        table = EvTable("Channel", "Subscribers", border="cells")
        table.add_row(channel.key, ", ".join([sub.key for sub in subs]) or "None")
        caller.msg(str(table))

    def list_channels(self):
        """List all available channels"""
        caller = self.caller
        channels = [chan for chan in ChannelDB.objects.get_all_channels()
                    if chan.access(caller, 'listen')]
        table = EvTable("Channel", "Description", border="cells")
        for channel in channels:
            table.add_row(channel.key, channel.db.desc or "")
        caller.msg(str(table))
      
    def get_channel_history(self, channel, start_index=0):
        """
        View a channel's history.
        """
        from evennia.utils.utils import tail_log_file

        log_file = channel.get_log_filename()

        def send_msg(lines):
            return self.msg(
                "".join(line.split("[-]", 1)[1] if "[-]" in line else line for line in lines)
            )

        # asynchronously tail the log file
        tail_log_file(log_file, start_index, 20, callback=send_msg)

    def join_channel(self):
        """Join a channel"""
        caller = self.caller
        if not self.args:
            caller.msg("Usage: channel/sub <name>")
            return

        channel = self.search_channel(self.args)
        if not channel:
            return

        if not channel.access(caller, 'listen'):
            caller.msg("You don't have permission to join this channel.")
            return

        if channel.connect(caller):
            caller.msg(f"You have joined channel '{channel.key}'.")
        else:
            caller.msg(f"You were already on channel '{channel.key}'.")

    def leave_channel(self):
        """Leave a channel"""
        caller = self.caller
        if not self.args:
            caller.msg("Usage: channel/unsub <name>")
            return

        channel = self.search_channel(self.args)
        if not channel:
            return

        if channel.disconnect(caller):
            caller.msg(f"You have left channel '{channel.key}'.")
        else:
            caller.msg(f"You were not on channel '{channel.key}'.")

    def msg_channel(self, channelname, msg):
      """Send a message to a channel"""
      caller = self.caller
      channel = self.search_channel(channelname)
      if not channel:
         return

      if not channel.access(caller, 'send'):
         caller.msg("You don't have permission to send messages to this channel.")
         return

      channel.msg(msg, senders=caller)

    def search_channel(self, channelname, exact=False):
        """
        Search for a channel and handle errors.
        """
        caller = self.caller
        channels = ChannelDB.objects.channel_search(channelname)
        if not channels:
            caller.msg(f"Channel '{channelname}' not found.")
            return None
        if len(channels) > 1:
            matches = ", ".join(chan.key for chan in channels)
            caller.msg(f"Multiple channels match '{channelname}': {matches}")
            return None
        return channels[0]

# Remember to update your command set to use this new CmdChannel