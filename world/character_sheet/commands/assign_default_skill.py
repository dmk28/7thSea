from django.core.management.base import BaseCommand
from world.character_sheet.models import Knack, Skill

class Command(BaseCommand):
    help = 'Assigns a default skill to knacks without a skill'
    key = "assign_default_skill"
    def handle(self, *args, **options):
        default_skill, _ = Skill.objects.get_or_create(name='General', category='Misc')
        knacks_updated = Knack.objects.filter(skill__isnull=True).update(skill=default_skill)
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {knacks_updated} knacks'))