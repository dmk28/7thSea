from evennia.comms.comms import DefaultChannel
from .models import ChannelMetadata


NATION_COLORS = {
    'Castille': '|Y',  # Gold
    'Montaigne': '|B',  # Blue royal
    'Vendel': '|520',  # Orange
    'Avalon': '|R',  # Dark red
    'Vodacce': '|=g',  # Mid-grey
    'Vesten': '|G',  # Green
    'Eisen': '|M'  # Light purple
}



class ExtendedChannel(DefaultChannel):
    def at_channel_creation(self):
        super().at_channel_creation()
        ChannelMetadata.objects.create(channel=self)

    def access(self, accessing_obj, access_type='listen', default=False):
        result = super().access(accessing_obj, access_type, default)
        if result:
            metadata = self.metadata
            if metadata.channel_type == 'FACTION':
                return self.check_faction_access(accessing_obj)
            elif metadata.channel_type == 'NATION':
                return self.check_nation_access(accessing_obj)
        return result

    def check_faction_access(self, accessing_obj):
        if hasattr(accessing_obj, 'character_sheet'):
            return accessing_obj.character_sheet.faction == self.metadata.faction_name
        return False

    def set_channel_color(self, color_code):
        """
        Set a custom color for the channel.
        """
        self.db.custom_color = color_code

    def channel_prefix(self):
        """
        Returns the channel prefix with appropriate color.
        """
        custom_color = self.db.custom_color
        if custom_color:
            return f"{custom_color}[{self.key}]|n "

    def check_nation_access(self, accessing_obj):
        if hasattr(accessing_obj, 'character_sheet'):
            return accessing_obj.character_sheet.nationality == self.metadata.nation_name
        elif hasattr(accessing_obj.db, 'nationality'):
            return accessing_obj.db.nationality == self.metadata.nation_name
        return False

    def msg(self, msgobj, header=None, senders=None, sender_strings=None,
            persistent=None, online=False, emit=False, external=False):
        result = super().msg(msgobj, header, senders, sender_strings,
                             persistent, online, emit, external)
        self.log_message(msgobj, header, senders)
        return result

    def log_message(self, msgobj, header, senders):
        if self.metadata.log_file:
            with open(self.metadata.log_file, 'a') as log:
                log.write(f"{header}: {msgobj}\n")

    def set_channel_type(self, channel_type, **kwargs):
        self.metadata.channel_type = channel_type
        if channel_type == 'FACTION':
            self.metadata.faction_name = kwargs.get('faction_name')
        elif channel_type == 'NATION':
            self.metadata.nation_name = kwargs.get('nation_name')
        self.metadata.save()

    def set_log_file(self, filename):
        self.metadata.log_file = filename
        self.metadata.save()