

from django.db import models
from world.character_sheet.models import CharacterSheet
from evennia.utils import logger

class Nation(models.Model):
    name = models.CharField(max_length=50, unique=True)
    population = models.PositiveIntegerField(default=1000)
    capital = models.CharField(max_length=100, blank=True)
    important_cities = models.JSONField(default=list, blank=True)
    government_type = models.CharField(max_length=100, blank=True)
    ruler = models.CharField(max_length=100, blank=True)
    currency = models.CharField(max_length=50, blank=True)
    major_exports = models.JSONField(default=list, blank=True)
    major_imports = models.JSONField(default=list, blank=True)
    recent_history = models.TextField(blank=True)
    notable_npcs = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.name

    def get_characters(self):
        characters = []
        character_sheets = CharacterSheet.objects.filter(nationality__iexact=self.name)
        logger.log_info(f"Found {character_sheets.count()} character sheets for {self.name}")
        
        for sheet in character_sheets:
            if sheet.db_object:
                characters.append(sheet.db_object.name)
            else:
                logger.log_warn(f"CharacterSheet {sheet.id} has no associated character object.")
        
        logger.log_info(f"Returning characters for {self.name}: {characters}")
        return characters



class Stronghold(models.Model):
    name = models.CharField(max_length=50, unique=True)
    nation = models.ForeignKey(Nation, on_delete=models.CASCADE, related_name='strongholds')
    location = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    ruler = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name