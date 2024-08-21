from django.core.management.base import BaseCommand
from world.character_sheet.models import Knack, Skill, KnackValue

class Command(BaseCommand):
    help = 'Cleans up knacks by associating them with the correct skills'

    def handle(self, *args, **options):
        for knack in Knack.objects.all():
            # Find all skills that might be associated with this knack
            potential_skills = Skill.objects.filter(name__icontains=knack.name)
            
            if potential_skills.exists():
                # If we find potential skills, create a knack for each
                for skill in potential_skills:
                    Knack.objects.get_or_create(name=knack.name, skill=skill)
                
                # Update KnackValues to point to the correct Knack
                for kv in KnackValue.objects.filter(knack=knack):
                    correct_knack = Knack.objects.filter(name=knack.name, skill__in=potential_skills).first()
                    if correct_knack and correct_knack != knack:
                        kv.knack = correct_knack
                        kv.save()
            else:
                # If no skill found, associate with a generic skill
                generic_skill, _ = Skill.objects.get_or_create(name='Generic', category='Misc')
                knack.skill = generic_skill
                knack.save()

        # Remove any knacks that aren't associated with any KnackValues
        for knack in Knack.objects.all():
            if not KnackValue.objects.filter(knack=knack).exists():
                knack.delete()

        self.stdout.write(self.style.SUCCESS('Successfully cleaned up knacks'))