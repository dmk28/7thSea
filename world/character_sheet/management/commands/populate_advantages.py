# In world/character_sheet/management/commands/populate_advantages.py

from django.core.management.base import BaseCommand
from world.character_sheet.models import Advantage
from typeclasses.chargen import ADVANTAGES

class Command(BaseCommand):
    help = 'Populates the Advantage model with data from ADVANTAGES dictionary'

    def handle(self, *args, **options):
        for name, details in ADVANTAGES.items():
            advantage, created = Advantage.objects.update_or_create(
                name=name,
                defaults={
                    'description': details.get('description', ''),
                    'cost': details.get('cost', 0),
                    'eisen_cost': details.get('eisen_cost'),
                    'bonus': details.get('bonus'),
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created advantage "{name}"'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Updated advantage "{name}"'))