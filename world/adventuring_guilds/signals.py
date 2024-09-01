from django.db.models.signals import post_save
from django.dispatch import receiver
from world.adventuring_guilds.models import AdventuringGuild
from world.banking.models import Bank

@receiver(post_save, sender=AdventuringGuild)
def create_guild_account(sender, instance, created, **kwargs):
    if created:
        from world.banking.models import GuildAccount  # Import here to avoid circular import
        
        default_bank = Bank.objects.first()  # You might want to choose a specific bank
        if default_bank:
            GuildAccount.objects.create(
                bank=default_bank,
                guild=instance,
                account_number=f"G-{instance.id}-{default_bank.id}",
                guilders_balance=instance.db_treasury_guilders,
                doubloons_balance=instance.db_treasury_doubloons
            )