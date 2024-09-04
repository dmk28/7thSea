from django.db import models
from evennia.utils.idmapper.models import SharedMemoryModel
from evennia.objects.models import ObjectDB
from world.character_sheet.models import CharacterSheet
from evennia.utils import dbserialize
from django.core.exceptions import ObjectDoesNotExist



class WeaponModification(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    damage_modifier = models.IntegerField(default=0)
    roll_keep_modifier = models.IntegerField(default=0)


class WeaponAbility(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()

class WeaponModel(SharedMemoryModel):
    evennia_object = models.OneToOneField(ObjectDB, on_delete=models.CASCADE, related_name='weapon_model', default=None)
    name = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    damage = models.PositiveIntegerField(default=1)
    roll_keep = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True)
    details = models.TextField(blank=True)  # New field for additional details
    WEAPON_CHOICES = [
        ('fencing', 'Fencing'),
        ('heavy weapon', 'Heavy Weapon'),
        ('pugilism', 'Pugilism'),
        ('firearms', 'Firearm'),
        ('polearms', 'Polearm'),
        ('knives', 'Knife'),
        ('swordcane', 'Swordcane'),
        ('fencingandknife', 'Fencing/Knife'),
    ]
    weapon_type = models.CharField(max_length=30, choices=WEAPON_CHOICES, blank=True, null=True)
    flameblade_active = models.BooleanField(default=False)
    WEAPON_ATTACK_SKILL_CHOICES = [
        ('attack (fencing)', 'Attack (Fencing)'),
        ('attack (knife)', 'Attack (Knife)'),
        ('attack (heavy weapon)', 'Attack (Heavy Weapon)'),
        ('attack (improvised weapon)', 'Attack (Improvised Weapon)'),
        ('attack (polearms)', 'Attack (Polearms)'),
        ('attack (whip)', 'Attack (Whip)'),
        ('attack (firearms)', 'Attack (Firearms)'),
        ('attack (Bow)', 'Attack (Bow)')
    ]
    attack_skill = models.CharField(max_length=50, choices=WEAPON_ATTACK_SKILL_CHOICES, blank=True, null=True)
    WEAPON_DEFENSE_SKILL_CHOICES = [
        ('parry (fencing)', 'Parry (Fencing)'),
        ('parry (knife)', 'Parry (Knife)'),
        ('parry (heavy weapon)', 'Parry (Heavy Weapon)'),
        ('parry (improvised weapon)', 'Parry (Improvised Weapon)'),
        ('parry (polearms)', 'Parry (Polearms)'),
        ('footwork', 'Footwork'),
    ]
    parry_skill = models.CharField(max_length=50, choices=WEAPON_DEFENSE_SKILL_CHOICES, blank=True, null=True)
    damage_bonus = models.PositiveIntegerField(default=0)
    cost = models.IntegerField(default=0)
    requirements = models.JSONField(default=dict, blank=True)
    material = models.ForeignKey('CraftingMaterial', on_delete=models.SET_NULL, null=True)
    crafted_by = models.ForeignKey('character_sheet.CharacterSheet', null=True, on_delete=models.SET_NULL)
    quality_level = models.PositiveIntegerField(default=0)
    abilities = models.ManyToManyField(WeaponAbility, blank=True)
    modifications = models.ManyToManyField(WeaponModification, blank=True)

    def calculate_damage(self, wielder):
        damage_total = self.damage + self.damage_bonus + wielder.brawn
        damage_keep = wielder.brawn + self.roll_keep
        pass

    def meet_requirements(self, wielder):
        # Implement requirement checking logic
        pass

    def __str__(self):
        return self.name

    @classmethod
    def create_from_typeclass(cls, weapon_typeclass):
        """Create a WeaponModel instance from a Weapon typeclass instance."""
        weapon_model, created = cls.objects.get_or_create(evennia_object=weapon_typeclass)
        if created:
            weapon_model.name = weapon_typeclass.name
            weapon_model.description = weapon_typeclass.db.desc
            weapon_model.damage = weapon_typeclass.db.damage
            weapon_model.roll_keep = weapon_typeclass.db.damage_keep
            weapon_model.weapon_type = weapon_typeclass.db.weapon_type
            weapon_model.flameblade_active = weapon_typeclass.db.flameblade_active
            weapon_model.attack_skill = weapon_typeclass.db.attack_skill
            weapon_model.parry_skill = weapon_typeclass.db.parry_skill
            weapon_model.damage_bonus = weapon_typeclass.db.damage_bonus
            weapon_model.cost = weapon_typeclass.db.cost
            weapon_model.requirements = weapon_typeclass.db.requirements
            weapon_model.save()
        return weapon_model

    @staticmethod
    def get_weapon_objects(weapon_type=None):
        """
        Retrieve weapon objects from the database.
        
        Args:
            weapon_type (str, optional): Specific weapon type to filter by.
        
        Returns:
            QuerySet: A QuerySet of WeaponModel instances.
        """
        weapons = WeaponModel.objects.all()
        
        if weapon_type:
            weapons = weapons.filter(weapon_type=weapon_type)
        
        return weapons

    def apply_modification(self, modification):
        self.modifications.add(modification)
        self.damage += modification.damage_modifier
        self.roll_keep += modification.roll_keep_modifier
        self.save()

    def remove_modification(self, modification):
        self.modifications.remove(modification)
        self.damage -= modification.damage_modifier
        self.roll_keep -= modification.roll_keep_modifier
        self.save()

    def sync_from_typeclass(self):
        if self.evennia_object:
            weapon = self.evennia_object
            self.name = weapon.name
            self.description = weapon.db.desc or ""
            
            # Use getattr with default values for optional attributes
            self.damage = getattr(weapon.db, 'damage', 0)
            self.roll_keep = getattr(weapon.db, 'damage_keep', 1)
            self.weapon_type = getattr(weapon.db, 'weapon_type', '')
            self.flameblade_active = getattr(weapon.db, 'flameblade_active', False)
            self.attack_skill = getattr(weapon.db, 'attack_skill', '')
            self.parry_skill = getattr(weapon.db, 'parry_skill', '')
            self.damage_bonus = getattr(weapon.db, 'damage_bonus', 0)
            self.cost = getattr(weapon.db, 'cost', 0)
            self.description = weapon.db.desc or ""
            self.details = weapon.db.details or ""  # Sync the new details field

            # Convert _SaverDict to regular dict for JSON fields
            requirements = getattr(weapon.db, 'requirements', {})
            self.requirements = dbserialize.to_pickle(requirements)
            
            self.weight = getattr(weapon.db, 'weight', 0.0)

    def save(self, *args, **kwargs):
        try:
            if self.evennia_object:
                self.sync_from_typeclass()
            super().save(*args, **kwargs)
        except ObjectDoesNotExist:
            # Handle the case where the Evennia object no longer exists
            self.evennia_object = None
            super().save(*args, **kwargs)
        except Exception as e:
            # Log the error or handle it as appropriate for your application
            print(f"Error saving WeaponModel: {e}")
            raise

    def sync_to_typeclass(self):
        if self.evennia_object:
            weapon = self.evennia_object
            weapon.name = self.name
            weapon.db.desc = self.description
            weapon.db.damage = self.damage
            weapon.db.damage_keep = self.roll_keep
            weapon.db.weapon_type = self.weapon_type
            weapon.db.flameblade_active = self.flameblade_active
            weapon.db.attack_skill = self.attack_skill
            weapon.db.parry_skill = self.parry_skill
            weapon.db.damage_bonus = self.damage_bonus
            weapon.db.cost = self.cost
            weapon.db.requirements = self.requirements
            weapon.db.weight = self.weight
            weapon.db.desc = self.description
            weapon.db.details = self.details  # Sync the new details field
            weapon.save()

            weapon.save()   

class CraftingMaterial(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    value = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

class CraftingRecipe(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    result_type = models.CharField(max_length=50)  # e.g., 'weapon', 'armor'
    difficulty = models.PositiveIntegerField(default=0)
    result_prototype = models.JSONField(default=dict)  # Add this field

    def __str__(self):
        return self.name

class RecipeRequirement(models.Model):
    recipe = models.ForeignKey(CraftingRecipe, on_delete=models.CASCADE, related_name='requirements')
    material = models.ForeignKey(CraftingMaterial, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=1)
    is_tool = models.BooleanField(default=False)  # Add this field to distinguish between tools and consumables

    def __str__(self):
        return f"{self.amount} {self.material.name} for {self.recipe.name}"


class ArmorModification(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    armor_modifier = models.IntegerField(default=0)
    soak_keep_modifier = models.IntegerField(default=0)

class ArmorAbility(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()

class ArmorModel(SharedMemoryModel):
    evennia_object = models.OneToOneField(ObjectDB, on_delete=models.CASCADE, related_name='armor_model', default=None)
    name = models.CharField(max_length=125, blank=True)
    description = models.TextField(max_length=300, blank=True)
    armor = models.PositiveIntegerField(default=0)
    soak_keep = models.PositiveIntegerField(default=1)
    ARMOR_CHOICES = [
        ("clothing", "Clothing"),
        ("cuirass", "Cuirass"),
        ("dracheneisen", "Dracheneisen"),
        ("reinforced_clothing", "Reinforced Clothing")
    ]
    armor_type = models.CharField(max_length=100, choices=ARMOR_CHOICES, blank=True, null=True)
    wear_location = models.JSONField(default=list, blank=True)
    traits = models.JSONField(default=dict, blank=True)
    cost = models.PositiveIntegerField(default=0)
    requirements = models.JSONField(default=dict, blank=True)
    material = models.ForeignKey('CraftingMaterial', on_delete=models.SET_NULL, null=True)
    crafted_by = models.ForeignKey('character_sheet.CharacterSheet', null=True, on_delete=models.SET_NULL)
    quality_level = models.PositiveIntegerField(default=0)
    abilities = models.ManyToManyField(ArmorAbility, blank=True)
    modifications = models.ManyToManyField(ArmorModification, blank=True)

    def __str__(self):
        return self.name

    @classmethod
    def create_from_typeclass(cls, armor_typeclass):
        """Create an ArmorModel instance from an Armor typeclass instance."""
        armor_model, created = cls.objects.get_or_create(evennia_object=armor_typeclass)
        if created:
            armor_model.name = armor_typeclass.name
            armor_model.description = armor_typeclass.db.desc
            armor_model.armor = armor_typeclass.db.armor
            armor_model.soak_keep = armor_typeclass.db.soak_keep
            armor_model.armor_type = armor_typeclass.db.armor_type
            armor_model.wear_location = armor_typeclass.db.wear_location
            armor_model.traits = armor_typeclass.db.traits
            armor_model.cost = armor_typeclass.db.cost
            armor_model.save()
        return armor_model

    @staticmethod
    def get_armor_objects(armor_type=None):
        """
        Retrieve armor objects from the database.
        
        Args:
            armor_type (str, optional): Specific armor type to filter by.
        
        Returns:
            QuerySet: A QuerySet of ArmorModel instances.
        """
        armors = ArmorModel.objects.all()
        
        if armor_type:
            armors = armors.filter(armor_type=armor_type)
        
        return armors

    def apply_modification(self, modification):
        self.modifications.add(modification)
        self.armor += modification.armor_modifier
        self.soak_keep += modification.soak_keep_modifier
        self.save()

    def remove_modification(self, modification):
        self.modifications.remove(modification)
        self.armor -= modification.armor_modifier
        self.soak_keep -= modification.soak_keep_modifier
        self.save()

    def sync_from_typeclass(self):
        if self.evennia_object:
            armor = self.evennia_object
            self.name = armor.name
            self.description = armor.db.desc or ""
            
            # Use getattr with default values for optional attributes
            self.armor = getattr(armor.db, 'armor', 0)
            self.soak_keep = getattr(armor.db, 'soak_keep', 1)
            self.armor_type = getattr(armor.db, 'armor_type', '')
            self.wear_location = getattr(armor.db, 'wear_location', [])
            self.traits = getattr(armor.db, 'traits', {})
            self.cost = getattr(armor.db, 'cost', 0)
            self.description = armor.db.desc or ""
            self.details = armor.db.details or ""  # Sync the new details field 
            # Convert _SaverDict to regular dict for JSON fields
            requirements = getattr(armor.db, 'requirements', {})
            self.requirements = dbserialize.to_pickle(requirements)

    def save(self, *args, **kwargs):
        try:
            if self.evennia_object:
                self.sync_from_typeclass()
            super().save(*args, **kwargs)
        except ObjectDoesNotExist:
            # Handle the case where the Evennia object no longer exists
            self.evennia_object = None
            super().save(*args, **kwargs)
        except Exception as e:
            # Log the error or handle it as appropriate for your application
            print(f"Error saving ArmorModel: {e}")
            raise

    def sync_to_typeclass(self):
        if self.evennia_object:
            armor = self.evennia_object
            armor.name = self.name
            armor.db.desc = self.description
            armor.db.armor = self.armor
            armor.db.soak_keep = self.soak_keep
            armor.db.armor_type = self.armor_type
            armor.db.wear_location = self.wear_location
            armor.db.traits = self.traits
            armor.db.cost = self.cost
            armor.db.requirements = self.requirements
            armor.db.desc = self.description
            armor.db.details = self.details  # Sync the new details field   
            
            armor.save()    