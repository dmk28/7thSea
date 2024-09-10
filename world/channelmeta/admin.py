# world/comms/admin.py

from django.contrib import admin
from .models import ChannelMetadata

@admin.register(ChannelMetadata)
class ChannelMetadataAdmin(admin.ModelAdmin):
    list_display = ('channel', 'channel_type', 'faction_name', 'nation_name')
    list_filter = ('channel_type',)
    search_fields = ('channel__db_key', 'faction_name', 'nation_name')