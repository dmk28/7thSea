from django.db import models
from evennia.utils.idmapper.models import SharedMemoryModel
from evennia.typeclasses.models import TypedObject
from evennia.objects.models import ObjectDB
from django.db.models import Q
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
        }
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

    def add_member(self):
        self.db_members.add(character)
    def remove_member(self):
        self.db_members.remove(character)

    def is_member(self):
        return self.db_members.filter(id=character.id).exists()

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


