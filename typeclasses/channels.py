"""
Channel

The channel class represents the out-of-character chat-room usable by
Accounts in-game. It is mostly overloaded to change its appearance, but
channels can be used to implement many different forms of message
distribution systems.

Note that sending data to channels are handled via the CMD_CHANNEL
syscommand (see evennia.syscmds). The sending should normally not need
to be modified.

"""

from evennia.comms.comms import DefaultChannel
# from world.channelmeta.channels import ExtendedChannel as WorldExtendedChannel
from evennia import settings
from world.adventuring_guilds.models import AdventuringGuild

from evennia.utils.utils import make_iter, lazy_property
from evennia.utils import logger
from datetime import datetime
import os 


class OldChannel(DefaultChannel):
    r"""
    This is the base class for all Channel Comms. Inherit from this to
    create different types of communication channels.

    Class-level variables:
    - `send_to_online_only` (bool, default True) - if set, will only try to
      send to subscribers that are actually active. This is a useful optimization.
    - `log_file` (str, default `"channel_{channelname}.log"`). This is the
      log file to which the channel history will be saved. The `{channelname}` tag
      will be replaced by the key of the Channel. If an Attribute 'log_file'
      is set, this will be used instead. If this is None and no Attribute is found,
      no history will be saved.
    - `channel_prefix_string` (str, default `"[{channelname} ]"`) - this is used
      as a simple template to get the channel prefix with `.channel_prefix()`. It is used
      in front of every channel message; use `{channelmessage}` token to insert the
      name of the current channel. Set to `None` if you want no prefix (or want to
      handle it in a hook during message generation instead.
    - `channel_msg_nick_pattern`(str, default `"{alias}\s*?|{alias}\s+?(?P<arg1>.+?)") -
      this is what used when a channel subscriber gets a channel nick assigned to this
      channel. The nickhandler uses the pattern to pick out this channel's name from user
      input. The `{alias}` token will get both the channel's key and any set/custom aliases
      per subscriber. You need to allow for an `<arg1>` regex group to catch any message
      that should be send to the  channel. You usually don't need to change this pattern
      unless you are changing channel command-style entirely.
    - `channel_msg_nick_replacement` (str, default `"channel {channelname} = $1"` - this
      is used by the nickhandler to generate a replacement string once the nickhandler (using
      the `channel_msg_nick_pattern`) identifies that the channel should be addressed
      to send a message to it. The `<arg1>` regex pattern match from `channel_msg_nick_pattern`
      will end up at the `$1` position in the replacement. Together, this allows you do e.g.
      'public Hello' and have that become a mapping to `channel public = Hello`. By default,
      the account-level `channel` command is used. If you were to rename that command you must
      tweak the output to something like `yourchannelcommandname {channelname} = $1`.

    * Properties:
        mutelist
        banlist
        wholist

    * Working methods:
        get_log_filename()
        set_log_filename(filename)
        has_connection(account) - check if the given account listens to this channel
        connect(account) - connect account to this channel
        disconnect(account) - disconnect account from channel
        access(access_obj, access_type='listen', default=False) - check the
                    access on this channel (default access_type is listen)
        create(key, creator=None, *args, **kwargs)
        delete() - delete this channel
        message_transform(msg, emit=False, prefix=True,
                          sender_strings=None, external=False) - called by
                          the comm system and triggers the hooks below
        msg(msgobj, header=None, senders=None, sender_strings=None,
            persistent=None, online=False, emit=False, external=False) - main
                send method, builds and sends a new message to channel.
        tempmsg(msg, header=None, senders=None) - wrapper for sending non-persistent
                messages.
        distribute_message(msg, online=False) - send a message to all
                connected accounts on channel, optionally sending only
                to accounts that are currently online (optimized for very large sends)
        mute(subscriber, **kwargs)
        unmute(subscriber, **kwargs)
        ban(target, **kwargs)
        unban(target, **kwargs)
        add_user_channel_alias(user, alias, **kwargs)
        remove_user_channel_alias(user, alias, **kwargs)


    Useful hooks:
        at_channel_creation() - called once, when the channel is created
        basetype_setup()
        at_init()
        at_first_save()
        channel_prefix() - how the channel should be
                  prefixed when returning to user. Returns a string
        format_senders(senders) - should return how to display multiple
                senders to a channel
        pose_transform(msg, sender_string) - should detect if the
                sender is posing, and if so, modify the string
        format_external(msg, senders, emit=False) - format messages sent
                from outside the game, like from IRC
        format_message(msg, emit=False) - format the message body before
                displaying it to the user. 'emit' generally means that the
                message should not be displayed with the sender's name.
        channel_prefix()

        pre_join_channel(joiner) - if returning False, abort join
        post_join_channel(joiner) - called right after successful join
        pre_leave_channel(leaver) - if returning False, abort leave
        post_leave_channel(leaver) - called right after successful leave
        at_pre_msg(message, **kwargs)
        at_post_msg(message, **kwargs)
        web_get_admin_url()
        web_get_create_url()
        web_get_detail_url()
        web_get_update_url()
        web_get_delete_url()

    """

    pass

# class NewChannel(Channel, WorldExtendedChannel):
#     """
#     This is the base channel typeclass for the game. It imports from Channel and the custom ExtendedChannel.
#     """

#     log_file = "channel_{channelname}.log"
#     filename = "channel_{channelname}.log"
#     def at_channel_creation(self):
#         """Called when the channel is created."""
#         super().at_channel_creation()
#         self.db.log_file = self.get_log_filename()

#     def get_log_filename(self):
#         """
#         Returns the filename for this channel's log file.
#         This method overrides the one from the parent class to ensure
#         we're using the correct path.
#         """
#         return self.attributes.get(
#             "log_file",
#             os.path.join(settings.LOG_DIR, f"channel_{self.key.lower()}.log")
#         )

#     def set_log_file(self, filename):
#         """
#         Set a custom log filename.

#         Args:
#             filename (str): The filename to set. This is a path starting from
#                 inside the settings.LOG_DIR location.
#         """
#         return self.set_log_filename(filename)

#     def at_post_msg(self, message, **kwargs):
#         """Log the message after it has been sent."""
#         super().at_post_msg(message, **kwargs)
#         self.log_message(message, kwargs.get("senders"))

#     def log_message(self, message, senders):
#         """Log the message to the channel's log file."""
#         log_file = self.get_log_filename()
#         if log_file:
#             timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
#             sender_names = ", ".join(sender.key for sender in make_iter(senders) if sender)
#             log_entry = f"{timestamp} [{self.key}] {sender_names}: {message}\n"
#             with open(log_file, 'a', encoding='utf-8') as log:
#                 log.write(log_entry)


class Channel(OldChannel):
    """
    Custom Channel class with additional features.
    Cribbed shamelessly from Arx-Game, altered for current-ver Evennia, so credit goes to Apostate and Tehom for this one.
    Thanks, guys.
    """
    log_file = "channel_{channelname}.log"
    mentions = ["Everyone", "All"]


    @lazy_property
    def org_channel(self):
        from world.adventuring_guilds.models import AdventuringGuild

        """Return the associated adventuring guild, if any."""
        try:
            return AdventuringGuild.objects.get(db_org_channel=self)
        except ObjectDoesNotExist:
            return None

    def at_channel_creation(self):
        super().at_channel_creation()
        self.db.is_org_channel = False
        self.db.channel_type = 'OOC'  # Default type
        self.db.faction_name = None
        self.db.nation_name = None
        self.ensure_log_file_exists()  # Set up the log file    

    def set_org(self, guild):
        """Set this channel as an organization channel."""
        self.db.is_org_channel = True
        guild.db_org_channel = self
        guild.save()
        # Clear the cached property
        if hasattr(self, '_org_channel'):
            del self._org_channel

    def remove_org(self):
        """Remove this channel's association with an organization."""
        org = self.org_channel
        if org:
            org.db_org_channel = None
            org.save()
        self.db.is_org_channel = False
        # Clear the cached property
        if hasattr(self, '_org_channel'):
            del self._org_channel

    def access(self, accessing_obj, access_type='listen', default=False):
        result = super().access(accessing_obj, access_type, default)
        if result:
            if self.db.channel_type == 'FACTION':
                return self.check_faction_access(accessing_obj)
            elif self.db.channel_type == 'NATION':
                return self.check_nation_access(accessing_obj)
        return result

    def check_faction_access(self, accessing_obj):
        if not self.db.faction_name:
            return False
        
        # Try to find the guild with the name matching faction_name
        guild = AdventuringGuild.objects.filter(db_name=self.db.faction_name).first()
        
        if not guild:
            return False
        
        # Check if the accessing_obj is a member of the guild
        return guild.is_member(accessing_obj)


    def check_nation_access(self, accessing_obj):
        if hasattr(accessing_obj, 'character_sheet'):
            return accessing_obj.character_sheet.nationality == self.db.nation_name
        elif hasattr(accessing_obj.db, 'nationality'):
            return accessing_obj.db.nationality == self.db.nation_name
        return False

    def set_faction_lock(self, faction_name):
        self.db.channel_type = 'FACTION'
        self.db.faction_name = faction_name
        self.save()

    def set_nation_lock(self, nation_name):
        self.db.channel_type = 'NATION'
        self.db.nation_name = nation_name

    def remove_lock(self):
        self.db.channel_type = 'OOC'
        self.db.faction_name = None
        self.db.nation_name = None
 
    @classmethod
    def create(cls, key, description="", typeclass=None, **kwargs):
        channel = super().create(key, description=description, typeclass=typeclass, **kwargs)
        return channel  # Return just the channel object, not a tuple


    @property
    def mutelist(self):
        """Cache mutelist to avoid expensive database operations"""
        if not hasattr(self.ndb, 'mute_list'):
            self.ndb.mute_list = list(self.db.mute_list or [])
        return self.ndb.mute_list

    @mutelist.setter
    def mutelist(self, value):
        """Set the mutelist"""
        self.ndb.mute_list = value
        self.db.mute_list = value

    @property
    def non_muted_subs(self):
        # Ensure subscriptions and mutelist are not None
        subscriptions = self.subscriptions.all() if self.subscriptions else []
        mutelist = self.mutelist if self.mutelist is not None else []

        # Iterate through subscriptions and filter out muted users
        return [ob for ob in subscriptions if ob.is_connected and ob not in mutelist]


    @staticmethod
    def format_wholist(listening):
        if listening:
            return ", ".join(sorted(player.key.capitalize() for player in listening))
        return "<None>"

    @property
    def wholist(self):
        return self.format_wholist(self.non_muted_subs)

    def temp_mute(self, subscriber):
        """Temporarily mute a channel for a subscriber"""
        if not hasattr(subscriber.db, 'temp_mute_list'):
            subscriber.db.temp_mute_list = []
        if self not in subscriber.db.temp_mute_list:
            subscriber.db.temp_mute_list.append(self)
            self.mute(subscriber)
        subscriber.msg(f"{self.key} will be muted until the end of this session.")

    def mute(self, subscriber):
        """Add subscriber to the mute list"""
        if subscriber not in self.mutelist:
            self.mutelist.append(subscriber)
            self.db.mute_list = self.mutelist
            return True
        return False

    def unmute(self, subscriber):
        """Remove subscriber from the mute list"""
        if self.mutelist is None:
                self.mutelist = []
        
        if subscriber in self.mutelist:
                self.mutelist.remove(subscriber)
                self.db.mute_list = self.mutelist
                return True
        return False

    def clear_mute(self):
        """Clear the entire mute list"""
        self.db.mute_list = []
        self.ndb.mute_list = None

    def channel_prefix(self, msg=None, emit=False):
        """Define how the channel name appears in messages"""
        if self.db.colorstr:
            return f"{self.db.colorstr}[{self.key}]|n "
        return f"|w[{self.key}]|n "

    def pose_transform(self, msg, sender_string):
        """Handle pose-style messages"""
        message = msg.lstrip()
        if message.startswith((":", ";")):
            return f"{sender_string}{message[1:]}"
        return f"{sender_string}: {message}"

    def tempmsg(self, message, header=None, senders=None):
        """Send a non-persistent message"""
        self.msg(message, senders=senders, header=header, keep_log=False)

    def format_mentions(self, message, names):
        """Format @mentions in the message"""
        if "@" not in message:
            return message
        words = message.split()
        for i, word in enumerate(words):
            if word.startswith("@"):
                mention = word[1:].rstrip(string.punctuation)
                if mention.lower() in [name.lower() for name in self.mentions + names]:
                    words[i] = f"{{c[@{mention}]{{n"
        return " ".join(words)

    def ensure_log_file_exists(self):
        """Ensure that the log file exists and is writable."""
        log_file = self.get_log_filename()
        try:
            with open(log_file, 'a') as f:
                pass  # Just to create the file if it doesn't exist
            print(f"DEBUG: Log file verified/created at {log_file}")
        except IOError as e:
            print(f"ERROR: Unable to create/access log file at {log_file}. Error: {e}")



    def msg(self, msgobj, header=None, senders=None, sender_strings=None,
        persistent=True, online=False, emit=False, external=False):
        """
        Modify the msg method to handle formatting and sending messages.
        """
        senders = make_iter(senders) if senders else []
        
        # If sender_strings is not provided, fallback to sender's key.
        sender_string = sender_strings[0] if sender_strings else (senders[0].key if senders else "Unknown")

        # Format the message with pose if emit, otherwise just the message
        if emit:
                msgobj = self.pose_transform(msgobj, sender_string)
                
        
        # Ensure the message is quoted and mentions are formatted
        message_content = self.format_mentions(f'"{msgobj}"', [sender.key for sender in senders])

        # Add channel prefix and sender name
        channel_name = self.channel_prefix()
        formatted_message = f"{channel_name} {sender_string}: {message_content}"

        # Send to all non-muted subscribers
        for subscriber in self.non_muted_subs:
                subscriber.msg(formatted_message, from_obj=senders, options={"from_channel": self.id})
        
        # Log the message if persistent
        if persistent:
                self.log_message(message_content, senders[0] if senders else None)
        super().msg(msgobj, header=header, senders=senders, sender_strings=sender_strings,
                persistent=persistent, online=online, emit=emit, external=external)


    def get_log_filename(self):
        return os.path.join(settings.LOG_DIR, f"channel_{self.key.lower()}.log")


    def log_message(self, message, sender):
        try:
            log_file = self.get_log_filename()
            sender_name = sender.key if sender else "Unknown"
            timestamp = logger.timeformat()
            log_entry = f"[{timestamp}] [{sender_name}] {message}"
            logger.log_file(log_entry, filename=log_file)
            print(f"DEBUG: Logged message to {log_file}")
        except Exception as e:
            print(f"ERROR: Failed to log message. Error: {e}")



    def get_history(self, caller, num_messages=20):
        try:
            log_file = self.get_log_filename()
            if not os.path.exists(log_file):
                caller.msg(f"No history available for channel {self.key}.")
                return

            def send_msg(lines):
                if not lines:
                    caller.msg(f"No messages found in the history of channel {self.key}.")
                else:
                    messages = "".join(lines)
                    caller.msg(f"Last {len(lines)} messages in {self.key}:\n{messages}")

            logger.tail_log_file(log_file, 0, num_messages, callback=send_msg)
        except Exception as e:
            caller.msg(f"Error retrieving channel history: {str(e)}")
            print(f"ERROR: Failed to retrieve history. Error: {e}")
