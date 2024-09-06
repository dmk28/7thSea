from django.db import models
from evennia.utils.idmapper.models import SharedMemoryModel
from world.nations.models import Nation
from world.adventuring_guilds.models import AdventuringGuild

class Commodity(SharedMemoryModel):
    name = models.CharField(max_length=50, unique=True)
    base_price = models.IntegerField()
    description = models.TextField(blank=True)
    class Meta:
        verbose_name_plural = "Commodities"

    def __str__(self):
        return self.name

class Company(SharedMemoryModel):
    name = models.CharField(max_length=100, unique=True)
    nation = models.ForeignKey(Nation, on_delete=models.CASCADE)
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE)
    current_price = models.IntegerField()
    last_updated = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True)
    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return f"{self.name} ({self.nation.name})"
    

class Investment(SharedMemoryModel):
    character = models.ForeignKey('objects.ObjectDB', on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    shares = models.IntegerField()
    buy_price = models.IntegerField()
    date_invested = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('character', 'company')

    def __str__(self):
        return f"{self.character.name}'s investment in {self.company.name}"

class GuildInvestment(SharedMemoryModel):
    guild = models.ForeignKey(AdventuringGuild, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    shares = models.IntegerField()
    buy_price = models.IntegerField()
    date_invested = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('guild', 'company')

    def __str__(self):
        return f"{self.guild.db_name}'s investment in {self.company.name}"

class Market(SharedMemoryModel):
    last_update = models.DateTimeField(auto_now=True)

    @classmethod
    def get_or_create(cls):
        market, created = cls.objects.get_or_create(pk=1)
        return market

    def __str__(self):
        return f"Commodity Market (Last updated: {self.last_update})"