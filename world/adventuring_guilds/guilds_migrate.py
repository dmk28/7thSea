from django.core.management.base import BaseCommand
from django.core.exceptions import PermissionDenied
from evennia.accounts.models import AccountDB
from .models import AdventuringGuild, GuildMembership, GuildRank
def migrate_guild_memberships():
    from evennia.utils import logger

    guilds_updated = 0
    memberships_created = 0

    for guild in AdventuringGuild.objects.all():
        default_rank = guild.ranks.order_by('level').first()
        if not default_rank:
            logger.log_info(f"Guild '{guild.db_name}' has no ranks. Creating default rank.")
            default_rank = GuildRank.objects.create(name="Initiate", level=1, guild=guild)

        for member in guild.db_members.all():
            membership, created = GuildMembership.objects.get_or_create(
                character=member,
                guild=guild,
                defaults={'rank': default_rank}
            )
            if created:
                memberships_created += 1

        guilds_updated += 1

    logger.log_info(f'Successfully processed {guilds_updated} guilds')
    logger.log_info(f'Created {memberships_created} new GuildMembership entries')