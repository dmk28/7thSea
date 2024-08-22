from django.db import models
from evennia.utils.idmapper.models import SharedMemoryModel
from evennia.utils.dbserialize import from_pickle
from django.dispatch import receiver
from django.db.models.signals import post_save

def convert_to_dict(value):
    if isinstance(value, dict):
        return {k: convert_to_dict(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [convert_to_dict(v) for v in value]
    elif hasattr(value, '_data'):  # This is likely a _SaverDict
        return convert_to_dict(value._data)
    else:
        return value



class Skill(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)

    class Meta:
        unique_together = ['name', 'category']

    def __str__(self):
        return f"{self.name} ({self.category})"

class Knack(models.Model):
    name = models.CharField(max_length=100)
    skill = models.ForeignKey(Skill, related_name='knacks', on_delete=models.CASCADE)

    class Meta:
        unique_together = ['name', 'skill']

    def __str__(self):
        return f"{self.name} ({self.skill.name})"



class SwordsmanSchool(models.Model):
    name = models.CharField(max_length=100, unique=True)
    country = models.JSONField(default=list)
    knacks = models.ManyToManyField(Knack, related_name='swordsman_schools')

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "Swordsman School"
        verbose_name_plural = "Swordsman Schools"

class Sorcery(models.Model):
    name = models.CharField(max_length=100, unique=True)
    knacks = models.ManyToManyField(Knack, related_name='sorceries')

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "Sorcery"
        verbose_name_plural = "Sorceries"
        
class Advantage(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    cost = models.JSONField(default=dict)  # This will store costs for different nationalities
    bonus = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

    def get_cost(self, nationality):
        if isinstance(self.cost, int):
            return self.cost
        return self.cost.get(nationality, self.cost.get('default', 0))


class CharacterSheet(SharedMemoryModel):
    """

    The web-facing side of the character sheet.

    """

    biography = models.TextField(blank=True)
    personality = models.TextField(blank=True)
    description = models.TextField(blank=True)
    eye_color = models.CharField(blank=True, max_length=30)
    hair_color = models.CharField(blank=True, max_length=30)
    skin_hue = models.CharField(blank=True, max_length=30)

    db_object = models.OneToOneField('objects.ObjectDB', related_name='character_sheet', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=50, blank=True)
    hero_points = models.IntegerField(default=0)
    money_guilders = models.IntegerField(default=0)
    money_doubloons = models.IntegerField(default=0)
    
    # Individual trait fields
    brawn = models.IntegerField(default=1)
    finesse = models.IntegerField(default=1)
    wits = models.IntegerField(default=1)
    resolve = models.IntegerField(default=1)
    panache = models.IntegerField(default=1)
    
    swordsman_schools = models.ManyToManyField(SwordsmanSchool, blank=True, related_name='character_sheets') 
    sorceries = models.ManyToManyField(Sorcery, blank=True, related_name='character_sheets') 

    skills = models.ManyToManyField(Skill, blank=True, related_name='character_sheets')
    advantages = models.ManyToManyField(Advantage, through='CharacterAdvantage', related_name='character_sheets', blank=True)
    flesh_wounds = models.PositiveIntegerField(default=0)
    dramatic_wounds = models.PositiveIntegerField(default=0)
    special_effects = models.JSONField(default=list, blank=True)
    
    nationality = models.CharField(max_length=100, blank=True)
    is_sorcerer = models.BooleanField(default=False)
    duelist_style = models.CharField(max_length=100, blank=True)
    total_xp_accrued = models.PositiveIntegerField(default=0)
    
    SORTE_MAGIC_CHOICES = [
        ('cups_boost', 'Cups (Boost)'),
        ('cups_curse', 'Cups (Curse)'),
        ('swords_boost', 'Swords (Boost)'),
        ('swords_curse', 'Swords (Curse)'),
        ('staves', 'Staves'),
        ('coins', 'Coins'),
        ('arcana', 'Arcana'),
    ]
    sorte_magic_effects = models.CharField(max_length=20, choices=SORTE_MAGIC_CHOICES, blank=True, null=True)
    
    approved = models.BooleanField(default=False)
    unconscious = models.BooleanField(default=False)
    eisen_bought = models.BooleanField(default=False)
    
    dracheneisen_slots = models.JSONField(default=dict, blank=True)
    armor_soak_keep = models.IntegerField(default=0)
    move_dice = models.IntegerField(default=0)
    xp = models.IntegerField(default=0)


    def format_text_field(self, field_name):
        text = getattr(self, field_name, '')
        return text.replace('%r', '|\n')

    def get_biography(self):
        return self.format_text_field('biography')

    def get_personality(self):
        return self.format_text_field('personality')

    def get_description(self):
        return self.format_text_field('description')

    def get_web_biography(self):
        return self.biography.replace('%r', '<br>')

    def get_web_personality(self):
        return self.personality.replace('%r', '<br>')

    def get_web_description(self):
        return self.description.replace('%r', '<br>')

    def heal_character(self, value, type):
        if type == "dramatic" and self.dramatic_wounds > 0:
            self.dramatic_wounds -= value
            self.save(update_fields=["dramatic_wounds"])
        elif type == "flesh" and self.flesh_wounds > 0:
            self.flesh_wounds -= value
            self.save(update_fields=["flesh_wounds"])
        else:
            return 0
        

    def update_swordsman_knacks(self, swordsman_knacks_data):
        # Clear existing swordsman schools
        self.swordsman_schools.clear()
        
        for school_name, knacks in swordsman_knacks_data.items():
            school, _ = SwordsmanSchool.objects.get_or_create(name=school_name)
            self.swordsman_schools.add(school)
            
            for knack_name, value in knacks.items():
                knack, _ = Knack.objects.get_or_create(name=knack_name)
                KnackValue.objects.update_or_create(
                    character_sheet=self,
                    knack=knack,
                    defaults={'value': value}
                )

    def update_from_typeclass(self):
        char = self.db_object
        
        self.full_name = char.db.full_name 
        self.gender = char.db.gender
        self.hero_points = char.db.hero_points or 0
        money = char.db.money or {}
        self.money_guilders = money.get('guilders', 0)
        self.money_doubloons = money.get('doubloons', 0)
        
        traits = char.db.traits or {}
        self.brawn = traits.get('brawn', 1)
        self.finesse = traits.get('finesse', 1)
        self.wits = traits.get('wits', 1)
        self.resolve = traits.get('resolve', 1)
        self.panache = traits.get('panache', 1)
        
        self.update_skills(char.db.skills or {})
       
        advantages_data = char.get_advantages()
        advantages_to_set = []
        for adv_data in advantages_data:
            advantage, created = Advantage.objects.get_or_create(name=adv_data['name'])
            
            if created or advantage.description != adv_data.get('description', ''):
                advantage.description = adv_data.get('description', '')
                advantage.save()

            # We're not updating cost and bonus here as they should be managed separately
            
            CharacterAdvantage.objects.update_or_create(
                character_sheet=self,
                advantage=advantage,
                defaults={'level': adv_data.get('level', 1)}
            )
            
            advantages_to_set.append(advantage)
    
        self.advantages.set(advantages_to_set)
                

        self.advantages.set(advantages_to_set)
        self.flesh_wounds = char.db.flesh_wounds or 0
        self.dramatic_wounds = char.db.dramatic_wounds or 0
        self.total_armor = char.db.total_armor
        self.armor_soak_keep = char.db.armor_soak_keep
        self.nationality = char.db.nationality or ""
        self.is_sorcerer = char.db.is_sorcerer or False
        self.duelist_style = char.db.duelist_style or ""
        self.sorte_magic_effects = char.db.sorte_magic_effects or ""
        self.approved = char.db.approved or False
        self.unconscious = char.db.unconscious or False
        self.eisen_bought = char.db.eisen_bought or False
        if self.nationality == "Eisen":
            self.dracheneisen_slots = char.db.dracheneisen_slots or {}
        else:
            self.dracheneisen_slots = {}
        self.armor_soak_keep = char.db.armor_soak_keep or 0
        self.move_dice = char.db.move_dice or 0
        self.xp = char.db.xp or 0
        self.update_skills(char.db.skills or {})
        self.update_swordsman_knacks(char.db.swordsman_knacks or {})
        self.total_xp_accrued = char.db.total_xp_accrued or 0
        self.special_effects = char.db.special_effects
        self.move_dice = char.db.move_dice

        self.save()

    def update_typeclass(self):
        """Update the character typeclass with the sheet information."""
        char = self.db_object
        
        # Update basic information
        char.db.full_name = self.full_name
        char.db.gender = self.gender
        char.db.hero_points = self.hero_points
        char.db.nationality = self.nationality
        
        # Update traits
        char.db.traits = {
            'brawn': self.brawn,
            'finesse': self.finesse,
            'wits': self.wits,
            'resolve': self.resolve,
            'panache': self.panache,
        }
        
        # Update descriptions
        char.db.description = self.description
        char.db.personality = self.personality
        char.db.biography = self.biography
        
        # Update physical attributes
        char.db.eye_color = self.eye_color
        char.db.hair_color = self.hair_color
        char.db.skin_hue = self.skin_hue
        
        # Update other fields
        char.db.is_sorcerer = self.is_sorcerer
        char.db.duelist_style = self.duelist_style
        char.db.approved = self.approved
        
        # Update skills
        char.db.skills = self.get_skills_by_category()
        
        # Update advantages
        char.db.advantages = [
            {
                'name': ca.advantage.name,
                'level': ca.level,
                'description': ca.advantage.description
            }
            for ca in self.character_advantages.all()
        ]
        
        # Update sorcery
        if self.is_sorcerer:
            sorcery = self.sorceries.first()
            if sorcery:
                char.db.sorcery = {
                    'name': sorcery.name,
                    'knacks': {
                        kv.knack.name: kv.value
                        for kv in self.knack_values.filter(knack__sorceries=sorcery)
                    }
                }
        else:
            char.db.sorcery = None
        
        # Save the character
        char.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_typeclass()


    def update_knack_value(self, knack_name, value):
        knack, _ = Knack.objects.get_or_create(name=knack_name)
        KnackValue.objects.update_or_create(
            knack=knack, 
            character_sheet=self, 
            defaults={'value': value}
        )

    def get_knack_value(self, knack_name):
        try:
            knack_value = self.knack_values.get(knack__name=knack_name)
            return knack_value.value
        except KnackValue.DoesNotExist:
            return 0
    def set_knack_value(self, knack_name, value):
        knack, _ = Knack.objects.get_or_create(name=knack_name)
        knack_value, _ = KnackValue.objects.get_or_create(character_sheet=self, knack=knack)
        knack_value.value = value
        knack_value.save()


    def update_skills(self, skills_data):
        self.skills.clear()  # Remove existing skills
        for category, skills in skills_data.items():
            for skill_name, knacks in skills.items():
                skill, _ = Skill.objects.get_or_create(name=skill_name, category=category)
                for knack_name, value in knacks.items():
                    knack, _ = Knack.objects.get_or_create(
                        name=knack_name,
                        skill=skill
                    )
                    KnackValue.objects.update_or_create(
                        character_sheet=self,
                        knack=knack,
                        defaults={'value': value}
                    )
                self.skills.add(skill)

    def get_skills_by_category(self):
        skills_dict = {}
        for skill in self.skills.all():
            if skill.category not in skills_dict:
                skills_dict[skill.category] = {}

            knacks_dict = {}
            for knack in skill.knacks.all():
                # Retrieve the corresponding KnackValue
                knack_value = KnackValue.objects.filter(character_sheet=self, knack=knack).first()
                if knack_value:
                    knacks_dict[knack.name] = knack_value.value
                else:
                    knacks_dict[knack.name] = 0  # Default value if KnackValue is missing

            skills_dict[skill.category][skill.name] = knacks_dict

        return skills_dict

    def get_formatted_skills(self):
        formatted_skills = []
        skills_by_category = self.get_skills_by_category()
        for category, skills in skills_by_category.items():
            category_skills = []
            for skill_name, knacks in skills.items():
                knacks_str = ", ".join([f"{k} ({v})" for k, v in knacks.items()])
                category_skills.append(f"{skill_name}: {knacks_str}")
            formatted_skills.append(f"{category}:\n  " + "\n  ".join(category_skills))
        return "\n".join(formatted_skills)

    @classmethod
    def create_from_typeclass(cls, character):
        sheet, created = cls.objects.get_or_create(db_object=character)
        if created or character.db.create_character_sheet:
            sheet.update_from_typeclass()
            character.db.create_character_sheet = False
        return sheet

    def __str__(self):
        return f"Character Sheet for {self.db_object.name}"

    def save(self, *args, **kwargs):
        for field in self._meta.fields:
            if isinstance(field, models.JSONField):
                value = getattr(self, field.name)
                setattr(self, field.name, convert_to_dict(value))
        super().save(*args, **kwargs)
        self.update_typeclass()

class KnackValue(models.Model):
    character_sheet = models.ForeignKey(CharacterSheet, related_name='knack_values', on_delete=models.CASCADE)
    knack = models.ForeignKey(Knack, related_name='knack_values', on_delete=models.CASCADE)
    value = models.IntegerField(default=0)

    class Meta:
        unique_together = ['character_sheet', 'knack']

    def __str__(self):
        return f"{self.character_sheet.db_object.name} - {self.knack.name}: {self.value}"

class CharacterAdvantage(models.Model):
    character_sheet = models.ForeignKey(CharacterSheet, related_name='character_advantages', on_delete=models.CASCADE)
    advantage = models.ForeignKey(Advantage, on_delete=models.CASCADE)
    level = models.IntegerField(default=1)

    class Meta:
        unique_together = ['character_sheet', 'advantage']

    def __str__(self):
        return f"{self.character_sheet.db_object.name} - {self.advantage.name} (Level {self.level})"

