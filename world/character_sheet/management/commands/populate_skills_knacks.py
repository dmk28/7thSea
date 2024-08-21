from django.core.management.base import BaseCommand
from world.character_sheet.models import Skill, Knack, SwordsmanSchool
from typeclasses.chargen import PACKAGES, SORCERIES, SWORDSMAN_SCHOOLS

def populate_skills_knacks():
    # Populate skills and knacks from PACKAGES
    for category, skills in PACKAGES.items():
        for skill_name, details in skills.items():
            skill, _ = Skill.objects.get_or_create(name=skill_name, category=category)
            for knack_name in details['knacks']:
                Knack.objects.get_or_create(name=knack_name, skill=skill)
            for adv_knack_name in details.get('advanced', {}).keys():
                Knack.objects.get_or_create(name=adv_knack_name, skill=skill)

    # Populate sorcery knacks
    for sorcery, details in SORCERIES.items():
        skill, _ = Skill.objects.get_or_create(name=sorcery, category='Sorcery')
        for knack_name in details['knacks']:
            Knack.objects.get_or_create(name=knack_name, skill=skill)

    # Populate swordsman schools
    for school_name in SWORDSMAN_SCHOOLS.keys():
        SwordsmanSchool.objects.get_or_create(name=school_name)

    # Populate swordsman school knacks
    for school, details in SWORDSMAN_SCHOOLS.items():
        skill, _ = Skill.objects.get_or_create(name=school, category='Swordsman School')
        for knack_name in details['knacks']:
            Knack.objects.get_or_create(name=knack_name, skill=skill)

    return "Successfully populated skills, knacks, and swordsman schools"

class Command(BaseCommand):
    help = 'Populates the database with skills, knacks, and swordsman schools from chargen.py'

    def handle(self, *args, **options):
        result = populate_skills_knacks()
        self.stdout.write(self.style.SUCCESS(result))