from django.db import models
from evennia.utils.idmapper.models import SharedMemoryModel

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

    class Meta:
        verbose_name = "Channel Metadata"
        verbose_name_plural = "Channel Metadata"