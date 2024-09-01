from django.db import models
from evennia.utils.idmapper.models import SharedMemoryModel
from world.adventuring_guilds.models import AdventuringGuild, Holding

class Bank(SharedMemoryModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    guilders_balance = models.IntegerField(default=0)
    doubloons_balance = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class BankAccount(SharedMemoryModel):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='accounts')
    account_holder = models.ForeignKey('objects.ObjectDB', on_delete=models.CASCADE, related_name='bank_accounts')
    account_number = models.CharField(max_length=20, unique=True)
    guilders_balance = models.IntegerField(default=0)
    doubloons_balance = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.account_holder}'s account at {self.bank}"

class GuildAccount(SharedMemoryModel):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='guild_accounts')
    guild = models.OneToOneField(AdventuringGuild, on_delete=models.CASCADE, related_name='bank_account')
    account_number = models.CharField(max_length=20, unique=True)
    guilders_balance = models.IntegerField(default=0)
    doubloons_balance = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.guild}'s account at {self.bank}"

class HoldingAccount(SharedMemoryModel):
    guild_account = models.ForeignKey(GuildAccount, on_delete=models.CASCADE, related_name='holding_accounts', default=0)
    holding = models.OneToOneField(Holding, on_delete=models.CASCADE, related_name='bank_account')
    account_number = models.CharField(max_length=20, unique=True)
    guilders_balance = models.IntegerField(default=0)
    doubloons_balance = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.holding}'s account under {self.guild_account}"