from django.core.management.base import BaseCommand
from character_sheet.models import Knack, Skill

class Command(BaseCommand):
    help = 'Cleans up duplicate Knacks and updates related Skills'

    def handle(self, *args, **options):
        # Get all knacks grouped by name
        knack_groups = {}
        for knack in Knack.objects.all():
            if knack.name not in knack_groups:
                knack_groups[knack.name] = []
            knack_groups[knack.name].append(knack)

        # For each group of knacks with the same name
        for name, knacks in knack_groups.items():
            if len(knacks) > 1:
                # Keep the first knack, delete the rest
                kept_knack = knacks[0]
                for knack in knacks[1:]:
                    # Update all skills that reference the duplicate knack
                    for skill in Skill.objects.filter(knacks=knack):
                        skill.knacks.remove(knack)
                        skill.knacks.add(kept_knack)
                    knack.delete()
                self.stdout.write(f"Cleaned up duplicate knacks for '{name}'")

        self.stdout.write(self.style.SUCCESS('Successfully cleaned up knacks'))