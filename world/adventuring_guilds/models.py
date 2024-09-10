from django.db import models
from evennia.utils.idmapper.models import SharedMemoryModel
from evennia.typeclasses.models import TypedObject
from evennia.objects.models import ObjectDB
from django.db.models import Q
from django.dispatch import receiver
from django.db.models.signals import post_save
# Create your models here.

class Holding(SharedMemoryModel):
    HOLDING_TYPES = {
        "tavern": {
            "name": "Tavern",
            "description": "A bustling tavern that generates steady income.",
            "base_income": 20,
            "upgrade_cost": 1000,
            "upgrade_multiplier": 1.5
        },
        "workshop": {
            "name": "Craftsman's Workshop",
            "description": "A workshop producing high-quality goods.",
            "base_income": 30,
            "upgrade_cost": 1500,
            "upgrade_multiplier": 1.7
        },
        "farm": {
            "name": "Fertile Farm",
            "description": "A productive farm providing food and resources.",
            "base_income": 15,
            "upgrade_cost": 800,
            "upgrade_multiplier": 1.4
        },
        "mine": {
            "name": "Rich Mine",
            "description": "A mine extracting valuable minerals.",
            "base_income": 40,
            "upgrade_cost": 2000,
            "upgrade_multiplier": 2.0
        },

        "swordsman academy": {
            "name": "Swordsman's Guild Academy",
            "description": "A  swordsman's guild academy.",
            "base_income": 15,
            "upgrade_cost": 1500,
            "upgrade_multiplier": 1.3,
        },
    }

    HOLDING_TYPE_CHOICES = [(key, value['name']) for key, value in HOLDING_TYPES.items()]

    name = models.CharField(max_length=255)
    custom_name = models.CharField(max_length=255, blank=True, null=True)
    holding_type = models.CharField(max_length=50, choices=HOLDING_TYPE_CHOICES)
    description = models.TextField(blank=True)
    custom_description = models.TextField(blank=True)
    level = models.IntegerField(default=1)
    income_type = models.CharField(max_length=20, choices=[('guilders', 'Guilders'), ('doubloons', 'Doubloons')])
    base_income = models.IntegerField(default=0)
    upgrade_cost = models.IntegerField(default=0)
    upgrade_multiplier = models.FloatField(default=1.5)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    staff = models.ManyToManyField(
        'objects.ObjectDB',
        related_name='staffed_holdings',
        limit_choices_to={'db_typeclass_path': 'typeclasses.characters.Character'},
        blank=True
    )
    events = models.JSONField(default=list)
    owning_guild = models.ForeignKey('AdventuringGuild', related_name='holdings', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.custom_name or self.name

    def save(self, *args, **kwargs):
        if not self.id:  # Only set these values when the object is first created
            type_data = self.HOLDING_TYPES[self.holding_type]
            self.name = type_data['name']
            self.description = type_data['description']
            self.base_income = type_data['base_income']
            self.upgrade_cost = type_data['upgrade_cost']
            self.upgrade_multiplier = type_data['upgrade_multiplier']
        super().save(*args, **kwargs)

    def get_display_name(self):
        return self.custom_name or self.name

    def get_description(self):
        return self.custom_description or self.description

    def calculate_income_rate(self):
        base_rate = self.base_income * (self.upgrade_multiplier ** (self.level - 1))
        specialization_modifier = 1.1 if self.specialization else 1.0
        staff_modifier = 1 + (self.staff.count() * 0.05)
        event_modifier = 1 + (len(self.events) * 0.1)
        return int(base_rate * specialization_modifier * staff_modifier * event_modifier)

    def get_upgrade_cost(self):
        return int(self.upgrade_cost * (self.upgrade_multiplier ** (self.level - 1)))

    def upgrade(self):
        if self.owning_guild.db_treasury_guilders < self.get_upgrade_cost():
            return False, "Not enough guilders in the treasury."
        
        self.owning_guild.db_treasury_guilders -= self.get_upgrade_cost()
        self.level += 1
        self.owning_guild.save()
        self.save()
        
        return True, f"Holding upgraded to level {self.level}."

    def get_details(self):
        return {
            "name": self.get_display_name(),
            "type": self.holding_type,
            "description": self.get_description(),
            "level": self.level,
            "income_type": self.income_type,
            "income_rate": self.calculate_income_rate(),
            "upgrade_cost": self.get_upgrade_cost(),
            "specialization": self.specialization,
            "staff": list(self.staff.values_list('db_key', flat=True)),  # Get list of staff names
            "events": self.events
        }

# class HoldingData(models.Model):
#     holding_id = models.IntegerField(unique=True)
#     level = models.IntegerField(default=1)
#     total_income_generated = models.IntegerField(default=0)
#     last_upgrade_time = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Holding Data {self.holding_id}"

class GuildRank(SharedMemoryModel):
    name = models.CharField(max_length=100, default="Member")
    level = models.IntegerField(default=1)
    guild = models.ForeignKey('AdventuringGuild', related_name='ranks', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('guild', 'level')
        ordering = ['level']

    def __str__(self):
        return f"{self.guild.db_name} - {self.name} (Level {self.level})"

class GuildMembership(SharedMemoryModel):
    character = models.OneToOneField('objects.ObjectDB', related_name='guild_membership', on_delete=models.CASCADE)
    guild = models.ForeignKey('AdventuringGuild', related_name='memberships', on_delete=models.CASCADE)
    rank = models.ForeignKey(GuildRank, related_name='members', on_delete=models.SET_NULL, null=True)
    join_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.character.db_key} - {self.guild.db_name} ({self.rank.name if self.rank else 'No Rank'})"


class CharacterManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            db_typeclass_path__contains='typeclasses.characters'
        )

class AdventuringGuild(SharedMemoryModel):

    db_name = models.CharField(max_length=150, default="")
    # db_founder = models.CharField(max_length=100, default="")
    db_founding_date = models.PositiveIntegerField(default=1665)
    db_history = models.TextField(verbose_name="Founding History", blank=True)
    db_recent_history = models.TextField(verbose_name="Recent History", blank=True)
    db_description = models.TextField(blank=True)
    db_members = models.ManyToManyField(
        'objects.ObjectDB',
        related_name='adventuring_guilds',
        limit_choices_to=Q(db_typeclass_path__contains='typeclasses.characters'),
        blank=True
    )
    db_founder = models.ForeignKey(
        'objects.ObjectDB',
        related_name='founded_guilds',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to=Q(db_typeclass_path__contains='typeclasses.characters')
    )

    db_treasury_guilders = models.IntegerField(default=0)
    db_treasury_doubloons = models.IntegerField(default=0)
    db_org_channel = models.OneToOneField("comms.ChannelDB", blank=True, null=True,related_name="adventuring_guild", on_delete=models.SET_NULL,)

    objects = models.Manager()
    character_members = CharacterManager()

    class Meta:
        verbose_name = "Adventuring Guild"
        verbose_name_plural = "Adventuring Guilds"

    def __str__(self):
        return self.db_name

    @property
    def members(self):
        return self.db_members.all()

    def add_member(self, character, rank=None):
        self.db_members.add(character)
        if not rank:
            rank = self.ranks.order_by('level').first()  # Get the lowest rank
        GuildMembership.objects.get_or_create(
            character=character,
            guild=self,
            defaults={'rank': rank}
        )
        if self.db_channel:
            self.db_channel.connect(character)

    def remove_member(self, character):
        self.db_members.remove(character)
        GuildMembership.objects.filter(character=character, guild=self).delete()
        if self.db_channel:
            self.db_channel.disconnect(character)

    def is_member(self, character):
        return self.db_members.filter(id=character.id).exists()

    def set_member_rank(self, character, rank):
        membership, created = GuildMembership.objects.get_or_create(
            character=character,
            guild=self,
            defaults={'rank': rank}
        )
        if not created:
            membership.rank = rank
            membership.save()

    def get_member_rank(self, character):
        membership = GuildMembership.objects.filter(character=character, guild=self).first()
        return membership.rank if membership else None

    def get_member_rank_level(self, character):
        membership = GuildMembership.objects.filter(character=character, guild=self).first()
        return membership.rank.level if membership and membership.rank else 0

    def invite_member(self, inviter, invitee):
        if not self.is_member(inviter):
            return False, "You are not a member of this guild."
        
        if self.is_member(invitee):
            return False, "This character is already a member of the guild."
        
        # Set a temporary attribute on the invitee
        invitee.ndb.guild_invitation = self
        
        # Notify the invitee
        invitee.msg(f"{inviter.name} has invited you to join {self.db_name}. Use 'accept_invite' or 'reject_invite' to respond.")
        
        return True, f"Invitation sent to {invitee.name}."

    def accept_invitation(self, invitee):
        if invitee.ndb.guild_invitation != self:
            return False, "You don't have a pending invitation from this guild."
        
        membership = self.add_member(invitee)
        if membership:
            del invitee.ndb.guild_invitation
            if not self.db_channel:
                self.create_guild_channel()
            self.db_channel.connect(invitee)
            return True, f"Welcome to {self.db_name}! You've been added to the guild channel."
        else:
            return False, "Failed to add you to the guild."

    def reject_invitation(self, invitee):
        if invitee.ndb.guild_invitation != self:
            return False, "You don't have a pending invitation from this guild."
        
        del invitee.ndb.guild_invitation
        return True, "Invitation rejected."

    def add_holding(self, holding_data):
        holding = Holding.objects.create(owning_guild=self, **holding_data)
        return holding

    def remove_holding(self, holding):
        holding.owning_guild = None
        holding.save()

    def get_holdings(self):
        return self.holdings.all()


    def collect_all_income(self):
        total_guilders = 0
        total_doubloons = 0
        for holding in self.holdings.all():  # Use the related_name 'holdings' instead of 'db_holdings'
            income = holding.calculate_income_rate()
            if holding.income_type == "guilders":
                total_guilders += income
                self.db_treasury_guilders += income
            elif holding.income_type == "doubloons":
                total_doubloons += income
                self.db_treasury_doubloons += income
        self.save()  # Save the updated treasury values
        return total_guilders, total_doubloons


