from django.core.management.base import BaseCommand
from evennia.objects.models import ObjectDB
from charactersheet.models import CharacterSheet

class SheetCommand(BaseCommand):
    help = 'Updates all CharacterSheet models for existing characters'
    key = "update_character_sheets"
    def handle(self, *args, **options):
        characters = ObjectDB.objects.filter(db_typeclass_path__contains='characters.Character')
        
        for character in characters:
            try:
                sheet, created = CharacterSheet.objects.get_or_create(db_object=character)
                sheet.update_from_typeclass()
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created and updated sheet for {character.name}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Updated sheet for {character.name}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error updating sheet for {character.name}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Character sheet update complete'))