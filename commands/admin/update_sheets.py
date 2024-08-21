from evennia import Command
from evennia.objects.models import ObjectDB
from world.character_sheet.models import CharacterSheet
import traceback

class CmdUpdateCharacterSheets(Command):
    """
    Update all character sheets

    Usage:
      update_sheets
    """

    key = "update_sheets"
    locks = "cmd:perm(Wizards)"
    help_category = "Admin"

    def func(self):
        updated_count = 0
        error_count = 0
        characters = ObjectDB.objects.filter(db_typeclass_path__contains='characters.Character')
        
        for character in characters:
            try:
                self.msg(f"Updating sheet for {character.name}")
                sheet = CharacterSheet.create_from_typeclass(character)
                updated_count += 1
                self.msg(f'Updated sheet for {character.name}')
                self.msg(f"Sorcery Knacks: {', '.join([f'{sk.name}: {sk.value}' for sk in sheet.sorcery_knacks.all()])}")
                # Print out the contents of the sheet
                for field in sheet._meta.fields:
                    if field.name not in ['id', 'db_object']:
                        value = getattr(sheet, field.name)
                        self.msg(f"{field.name}: {value}")
                
            except Exception as e:
                error_count += 1
                self.msg(f'Error updating sheet for {character.name}:')
                self.msg(traceback.format_exc())

        self.msg(f'Character sheet update complete. Updated: {updated_count}, Errors: {error_count}')