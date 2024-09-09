from django.core.management.base import BaseCommand
from django.core.exceptions import PermissionDenied
from evennia.accounts.models import AccountDB
from adventuring_guilds.models import AdventuringGuild, GuildMembership, GuildRank

class Command(BaseCommand):
    help = 'Initialize GuildMembership for existing guild members'

    def add_arguments(self, parser):
        parser.add_argument('--account', type=str, help='Account name to run the command')

    def handle(self, *args, **options):
        account_name = options['account']
        if not account_name:
            raise PermissionDenied("This command must be run by an admin account.")

        account = AccountDB.objects.filter(username=account_name).first()
        if not account or not account.is_superuser:
            raise PermissionDenied("This command can only be run by an admin account.")

        guilds_updated = 0
        memberships_created = 0

        for guild in AdventuringGuild.objects.all():
            default_rank = guild.ranks.order_by('level').first()
            if not default_rank:
                self.stdout.write(self.style.WARNING(f"Guild '{guild.db_name}' has no ranks. Creating default rank."))
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

        self.stdout.write(self.style.SUCCESS(f'Successfully processed {guilds_updated} guilds'))
        self.stdout.write(self.style.SUCCESS(f'Created {memberships_created} new GuildMembership entries'))