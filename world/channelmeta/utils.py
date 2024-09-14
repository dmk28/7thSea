from evennia.utils import create
from evennia.comms.models import ChannelDB
from .models import ChannelMetadata, NATION_COLORS

def create_channel_and_metadata(channel_key, channel_type, **kwargs):
    from typeclasses.channels import Channel  # Import here to avoid circular import

    # Separate channel creation args from metadata args
    channel_kwargs = {
        'key': channel_key,
        'aliases': kwargs.get('aliases', []),
        'locks': kwargs.get('locks', ''),
        'typeclass': Channel
    }

    # Try to find an existing channel
    existing_channel = ChannelDB.objects.channel_search(channel_key).first()
    if existing_channel:
        channel = existing_channel
        if not isinstance(channel, Channel):
            # If the existing channel is not of the custom type, convert it
            channel.convert_to(Channel)
    else:
        # Create a new channel using your custom Channel class
        channel = create.create_channel(**channel_kwargs)

    # Create or get the metadata
    metadata, created = ChannelMetadata.objects.get_or_create(channel=channel)
    metadata.channel_type = channel_type
    if channel_type == 'FACTION':
        metadata.faction_name = kwargs.get('faction_name')
    elif channel_type == 'NATION':
        metadata.nation_name = kwargs.get('nation_name')

    # Set custom color
    custom_color = kwargs.get('custom_color')
    if custom_color:
        metadata.custom_color = custom_color
    elif channel_type == 'NATION':
        metadata.custom_color = NATION_COLORS.get(metadata.nation_name, '|w')
    
    metadata.log_file = kwargs.get('log_file')
    metadata.save()

    # Set color on the channel object
    channel.db.custom_color = metadata.custom_color

    return metadata, channel