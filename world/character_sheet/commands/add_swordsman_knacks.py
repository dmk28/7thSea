from world.character_sheet.models import Skill, Knack, SwordsmanSchool, KnackValue
from typeclasses.chargen import SWORDSMAN_SCHOOLS
import logging

logger = logging.getLogger(__name__)

def populate_swordsman_schools():
    skills_created = 0
    knacks_created = 0
    schools_created = 0
    knack_values_created = 0

    # Create a 'Swordsman' skill for all swordsman knacks
    swordsman_skill, created = Skill.objects.get_or_create(name='Swordsman', category='Martial')
    if created:
        skills_created += 1

    # Populate swordsman schools and their knacks
    for school_name, details in SWORDSMAN_SCHOOLS.items():
        logger.debug(f"Processing school: {school_name}")
        logger.debug(f"School details: {details}")

        school, created = SwordsmanSchool.objects.get_or_create(name=school_name)
        if created:
            schools_created += 1

        # Check if 'knacks' is in details and is a dictionary
        if 'knacks' not in details or not isinstance(details['knacks'], dict):
            logger.warning(f"Invalid 'knacks' structure for school {school_name}: {details.get('knacks')}")
            continue

        # Create knacks for this school
        for knack_name, knack_details in details['knacks'][school_name].items():
            logger.debug(f"Processing knack: {knack_name}")
            logger.debug(f"Knack details: {knack_details}")

            if isinstance(knack_details, dict):
                # If knack_details is a dict, we assume it contains a value
                value = knack_details.get('value', 1)  # Default to 1 if no value is specified
            elif isinstance(knack_details, (int, float)):
                # If knack_details is a number, we use it as the value
                value = knack_details
            else:
                logger.warning(f"Invalid knack details for {knack_name} in {school_name}: {knack_details}")
                continue

            knack, created = Knack.objects.get_or_create(
                name=knack_name,
                skill=swordsman_skill
            )
            if created:
                knacks_created += 1
            school.knacks.add(knack)

            # Create or update KnackValue
            knack_value, created = KnackValue.objects.get_or_create(
                knack=knack,
                defaults={'value': value}
            )
            if created:
                knack_values_created += 1
            else:
                knack_value.value = value
                knack_value.save()

    return f"Swordsman schools population complete. Created: {skills_created} skills, {knacks_created} knacks, {schools_created} swordsman schools, and {knack_values_created} knack values."

def run_swordsman_population():
    try:
        result = populate_swordsman_schools()
        print(result)
        return result
    except Exception as e:
        logger.exception("An error occurred while populating swordsman schools")
        return f"An error occurred: {str(e)}"