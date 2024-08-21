# in mygame/commands/management/commands/update_characters.py
from django.core.management.base import BaseCommand
from evennia.objects.models import ObjectDB
from typeclasses.characters import Character
from world.character_sheet.models import CharacterSheet
import traceback

class Command(BaseCommand):
    help = "Updates all character objects and their character sheets to the new standard"

    def handle(self, *args, **options):
        updated_count = 0
        error_count = 0
        characters = ObjectDB.objects.filter(db_typeclass_path__contains='characters.Character')

        for obj in characters:
            try:
                char = Character.objects.get(id=obj.id)
                self.stdout.write(f"Updating character: {char.name}")

                # Update the character object
                char.at_object_creation()  # This will reinitialize the character

                # Update or create the character sheet
                sheet, created = CharacterSheet.objects.get_or_create(db_object=char)
                sheet.update_from_typeclass()

                # Print out the contents of the sheet
                self.stdout.write(f"Full Name: {sheet.full_name}")
                self.stdout.write(f"Gender: {sheet.gender}")
                self.stdout.write(f"Hero Points: {sheet.hero_points}")
                self.stdout.write(f"Money: Guilders: {sheet.money_guilders}, Doubloons: {sheet.money_doubloons}")
                self.stdout.write(f"Traits: Brawn: {sheet.brawn}, Finesse: {sheet.finesse}, Wits: {sheet.wits}, Resolve: {sheet.resolve}, Panache: {sheet.panache}")
                self.stdout.write(f"Skills:\n{sheet.get_formatted_skills()}")
                self.stdout.write(f"Perks: {sheet.perks}")
                self.stdout.write(f"Sorcery Knacks: {', '.join([str(knack) for knack in sheet.sorcery_knacks.all()])}")
                self.stdout.write(f"Flesh Wounds: {sheet.flesh_wounds}")
                self.stdout.write(f"Dramatic Wounds: {sheet.dramatic_wounds}")
                self.stdout.write(f"Nationality: {sheet.nationality}")
                self.stdout.write(f"Is Sorcerer: {sheet.is_sorcerer}")
                self.stdout.write(f"Duelist Style: {sheet.duelist_style}")
                self.stdout.write(f"Sorte Magic Effects: {sheet.sorte_magic_effects}")
                self.stdout.write(f"Approved: {sheet.approved}")
                self.stdout.write(f"Unconscious: {sheet.unconscious}")
                self.stdout.write(f"Eisen Bought: {sheet.eisen_bought}")
                self.stdout.write(f"Dracheneisen Slots: {sheet.dracheneisen_slots}")
                self.stdout.write(f"Armor Soak Keep: {sheet.armor_soak_keep}")
                self.stdout.write(f"Move Dice: {sheet.move_dice}")
                self.stdout.write(f"XP: {sheet.xp}")

                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f"Successfully updated character and sheet for: {char.name}"))

            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f'Error updating character {obj.name}:'))
                self.stdout.write(self.style.ERROR(traceback.format_exc()))

        self.stdout.write(self.style.SUCCESS(f'Character update complete. Updated: {updated_count}, Errors: {error_count}'))