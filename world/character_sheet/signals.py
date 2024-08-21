from django.db.models.signals import post_save
from django.dispatch import receiver
from evennia.objects.models import ObjectDB
from .models import CharacterSheet

@receiver(post_save, sender=ObjectDB)
def update_character_sheet(sender, instance, **kwargs):
    if instance.typeclass_path.endswith('characters.Character'):
        sheet, created = CharacterSheet.objects.get_or_create(db_object=instance)
        sheet.update_from_typeclass()
        sheet.save()  # Ensure changes are saved to the database

@receiver(post_save, sender=CharacterSheet)
def update_character_object(sender, instance, **kwargs):
    instance.update_typeclass()