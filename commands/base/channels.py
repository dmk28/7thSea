from evennia.commands.default.muxcommand import MuxCommand
from evennia.utils.evtable import EvTable
from evennia.utils.utils import make_iter
from typeclasses.channels import Channel
from evennia.utils.search import search_channel
from world.adventuring_guilds.models import AdventuringGuild
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
    switches = [
        "create", "delete", "list", "who", "join", "leave", "mute", "unmute", 
        "history", "set_faction", "set_nation", "remove_lock"
    ]
    def func(self):
        caller = self.caller

        if not self.args and not self.switches:
            caller.msg("Usage: <channel> <message> or channel/<switch>")
            return

        if self.switches:
            switch = self.switches[0].lower()
            if switch == "create" and caller.check_permstring("Builders"):
                self.create_channel()
            elif switch == "delete"and caller.check_permstring("Builders"):
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
            elif switch == "set_faction" and caller.check_permstring("Builders"):
                  self.set_faction_lock()
            elif switch == "set_nation" and caller.check_permstring("Builders"):
                  self.set_nation_lock()
            elif switch == "remove_lock" and caller.check_permstring("Builders"):
                  self.remove_lock()
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
      
      # Check if new_channel is a tuple
      if isinstance(new_channel, tuple):
         new_channel, errors = new_channel
         if errors:
               caller.msg(f"Errors occurred while creating the channel: {errors}")
               return

      # Now we can safely use connect
      new_channel.connect(caller)
      caller.msg(f"Channel '{channel_name}' created successfully.")

    def delete_channel(self):
        """Delete an existing channel"""
        caller = self.caller
        if not self.args:
            caller.msg("Usage: channel/delete <name>")
            return
        
        channel = search_channel(self.args)
        if not channel.exists():
         caller.msg(f"No channel found with the name '{self.args}'.")
         return
        channel = channel.first()

        if not channel.access(caller, "control"):
            caller.msg("You don't have permission to delete this channel.")
            return

        channel_name = channel.key
        channel.delete()
        caller.msg(f"Channel '{channel_name}' has been deleted.")

    def list_channels(self):
        """List all available channels that the character has access to"""
        caller = self.caller
        accessible_channels = []

        for chan in Channel.objects.all():
            if chan.access(caller, "listen"):
                accessible_channels.append(chan)
        
        if not accessible_channels:
            caller.msg("No channels available to you.")
            return

        table = EvTable("Channel", "Description", "Subscribed", border="cells")
        for chan in accessible_channels:
            subscribed = "Yes" if chan.has_connection(caller) else "No"
            table.add_row(chan.key, chan.db.desc or "", subscribed)
        
        caller.msg(str(table))


    def show_who(self):
        """Show who is subscribed to a channel"""
        caller = self.caller
        if not self.args:
            caller.msg("Usage: channel/who <name>")
            return
        
        channel = search_channel(self.args)
        if not channel.exists():
            caller.msg(f"No channel found with the name '{self.args}'.")
            return
        channel = channel.first()

        if not channel.access(caller, "listen"):
            caller.msg(f"You don't have access to the channel {channel.key}.")
            return

        caller.msg(f"Subscribers of {channel.key}: {channel.wholist}")

    def join_channel(self):
        """Join a channel"""
        caller = self.caller
        if not self.args:
            caller.msg("Usage: channel/join <name>")
            return
        
        channel = search_channel(self.args).first()
        if not channel:
            caller.msg(f"No channel found with the name '{self.args}'.")
            return

        # Check channel type and access restrictions
        if channel.db.channel_type == 'NATION':
            character_nationality = caller.db.nationality if hasattr(caller.db, 'nationality') else None
            if character_nationality != channel.db.nation_name:
                caller.msg(f"You cannot join the channel {channel.key}. It's restricted to citizens of {channel.db.nation_name}.")
                return
        elif channel.db.channel_type == 'FACTION':
            if not AdventuringGuild.objects.filter(db_name=channel.db.faction_name, db_members=caller).exists():
                caller.msg(f"You cannot join the channel {channel.key}. It's restricted to members of the {channel.db.faction_name} faction.")
                return

        # If the character passes the access checks, attempt to connect them to the channel
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
        
        channel = search_channel(self.args).first()
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
        
        channel = caller.search_channel(self.args).first()
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
        
        channel = caller.search_channel(self.args).first()
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

        channel = search_channel(channel_name).first()
        if not channel:
            caller.msg("No channel with that name.")
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
        args = self.args.strip()
        
        # Find the first space that's not inside quotes
        space_index = -1
        in_quotes = False
        for i, char in enumerate(args):
            if char == '"':
                in_quotes = not in_quotes
            elif char == ' ' and not in_quotes:
                space_index = i
                break
        
        if space_index == -1:
            caller.msg("Usage: <channel> <message>")
            return
        
        channel_name = args[:space_index].strip('"')
        message = args[space_index+1:].strip()

        if not channel_name or not message:
            caller.msg("Usage: <channel> <message>")
            return

        channel = search_channel(channel_name)
        if not channel.exists():
            caller.msg(f"No channel found with the name '{channel_name}'.")
            return
        channel = channel.first()

        if not channel.access(caller, "send"):
            caller.msg("You don't have permission to send messages to this channel.")
            return

        # Handle emotes
        if message.startswith(";"):
            message = f"{caller.name} {message[1:].strip()}"
            emit = True
        elif message.startswith(":"):
            message = f"{caller.name}{message[1:]}"
            emit = True
        else:
            emit = False

        # Send the message
        channel.msg(message, senders=[caller], emit=emit)

    def set_faction_lock(self):
        if not self.args:
            self.caller.msg("Usage: channel/set_faction <channel> = <guild_name>")
            return
        channel_name, guild_name = self.args.split('=')
        channel = search_channel(channel_name.strip())
        if not channel.exists():
            self.caller.msg(f"No channel found with the name '{channel_name}'.")
            return
        channel = channel.first()
        
        # Check if the guild exists
        guild = AdventuringGuild.objects.filter(db_name=guild_name.strip()).first()
        if not guild:
            self.caller.msg(f"No guild found with the name '{guild_name}'.")
            return
        
        channel.set_faction_lock(guild.db_name)
        self.caller.msg(f"Channel '{channel.key}' is now locked to guild '{guild.db_name}'.")

    def set_nation_lock(self):
        if not self.args:
            self.caller.msg("Usage: channel/set_nation <channel> = <nation_name>")
            return
        channel_name, nation_name = self.args.split('=')
        channel = search_channel(channel_name.strip())
        if not channel.exists():
            self.caller.msg(f"No channel found with the name '{channel_name}'.")
            return
        channel = channel.first()
        channel.set_nation_lock(nation_name.strip())
        self.caller.msg(f"Channel '{channel.key}' is now locked to nation '{nation_name}'.")

    def remove_lock(self):
        if not self.args:
            self.caller.msg("Usage: channel/remove_lock <channel>")
            return
        channel = search_channel(self.args.strip())
        if not channel.exists():
            self.caller.msg(f"No channel found with the name '{self.args}'.")
            return
        channel = channel.first()
        channel.remove_lock()
        self.caller.msg(f"Lock removed from channel '{channel.key}'.")