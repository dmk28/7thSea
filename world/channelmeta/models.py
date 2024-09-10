# world/comms/models.py
from django.db import models
from evennia.utils.idmapper.models import SharedMemoryModel
from evennia.comms.models import ChannelDB
from .channels import ExtendedChannel

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
    channel = models.OneToOneField('comms.Channel', on_delete=models.CASCADE, related_name='metadata')
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
        return f"{self.channel.key} Metadata"

    def get_channel_color(self):
        if self.custom_color:
            return self.custom_color
        if self.channel_type == 'NATION':
            return NATION_COLORS.get(self.nation_name, '|w')
        return '|w'  # default to white

    @classmethod
    def create_channel_and_metadata(cls, channel_key, channel_type, **kwargs):
        from evennia.utils import create  # Import here to avoid circular import
        
        channel = ChannelDB.objects.channel_search(channel_key).first()
        if not channel:
            channel = create.create_channel(channel_key)
        
        metadata, created = cls.objects.get_or_create(channel=channel)
        metadata.channel_type = channel_type
        
        if channel_type == 'FACTION':
            metadata.faction_name = kwargs.get('faction_name')
        elif channel_type == 'NATION':
            metadata.nation_name = kwargs.get('nation_name')
        
        # Explicitly set the custom color
        custom_color = kwargs.get('custom_color')
        if custom_color:
            metadata.custom_color = custom_color
        elif channel_type == 'NATION':
            # Set default color for nation if not provided
            metadata.custom_color = NATION_COLORS.get(metadata.nation_name, '|w')
        
        metadata.log_file = kwargs.get('log_file')
        metadata.save()
        
        # Ensure the channel object also has the color information
        channel.db.custom_color = metadata.custom_color
        
        return metadata

    @classmethod
    def get_or_create_metadata(cls, channel_key):
        channel = ChannelDB.objects.channel_search(channel_key).first()
        if not channel:
            return None
        return cls.objects.get_or_create(channel=channel)[0]