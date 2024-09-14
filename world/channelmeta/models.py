from django.db import models
from evennia.utils.idmapper.models import SharedMemoryModel
from evennia.comms.models import ChannelDB
NATION_COLORS = {
    'Castille': '|Y',  # Gold
    'Montaigne': '|B',  # Blue royal
    'Vendel': '|520',  # Orange
    'Avalon': '|R',  # Dark red
    'Vodacce': '|=g',  # Mid-grey
    'Vesten': '|G',  # Green
    'Eisen': '|M'  # Light purple
}

class ChannelMetadata(SharedMemoryModel):

    channel = models.OneToOneField(ChannelDB, on_delete=models.CASCADE, related_name='channel_metadata')
    channel_type = models.CharField(max_length=20, choices=[
        ('FACTION', 'Faction'),
        ('NATION', 'Nation'),
        ('OOC', 'Out of Character'),
    ])
    faction_name = models.CharField(max_length=100, blank=True, null=True)
    nation_name = models.CharField(max_length=100, blank=True, null=True)
    log_file = models.CharField(max_length=255, blank=True, null=True)
    custom_color = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = "Channel Metadata"
        verbose_name_plural = "Channel Metadata"

    def __str__(self):
        return f"{self.channel.db_key} Metadata"

    def get_channel_color(self):
        if self.custom_color:
            return self.custom_color
        if self.channel_type == 'NATION':
            return NATION_COLORS.get(self.nation_name, '|w')
        return '|w'  # default to white

    @classmethod
    def get_or_create_metadata(cls, channel_key):
        from evennia.comms.models import ChannelDB
        channel = ChannelDB.objects.channel_search(channel_key).first()
        if not channel:
            return None
        return cls.objects.get_or_create(channel=channel)[0]