from evennia import Command
from evennia.utils.evmenu import EvMenu
from typeclasses.chargen import SORCERIES, SWORDSMAN_SCHOOLS, ADVANTAGES, PACKAGES
from evennia.utils import evtable, create
from typeclasses.requests import Request
from evennia.web.website.forms import CharacterForm
from world.utils.format import process_ansi_codes
from world.character_sheet.models import CharacterSheet, Skill, Knack, SwordsmanSchool, Sorcery, KnackValue, Advantage, CharacterAdvantage
from world.utils.formatter import process_mush_text


class CmdCharGen(Command):
    key = "chargen"
    locks = "cmd:all()"
    help_category = "Character Generation"

    def func(self):
        if not self.caller.db.approved:
            # Clear any existing EvMenu
            if hasattr(self.caller, "ndb._evmenu"):
                del self.caller.ndb._evmenu

            self.caller.ndb.chargen = None

            EvMenu(self.caller, "commands.chargen", 
                   startnode="start_chargen",
                   auto_quit=True,
                   auto_look=True,
                   auto_help=False,
                   cmdset_mergetype='Union',
                   cmd_on_exit=None,
                   persistent=False)
        else:
            self.caller.msg("Your character has already been approved. You cannot run chargen again.")


def ensure_chargen_data(caller):
    sheet, _ = CharacterSheet.objects.get_or_create(db_object=caller)
    if not sheet.hero_points:
        sheet.hero_points = 80
        sheet.save(update_fields=["hero_points"])
    return sheet

def start_chargen(caller):
    sheet, created = CharacterSheet.objects.get_or_create(db_object=caller)

    if not sheet.approved:
        if created or sheet.hero_points is None:
            sheet.hero_points = 80
        sheet.brawn = sheet.finesse = sheet.wits = sheet.resolve = sheet.panache = 1
        sheet.nationality = ""
        sheet.is_sorcerer = False
        sheet.duelist_style = ""
        
        # Clear skills
        sheet.skills.clear()
        KnackValue.objects.filter(character_sheet=sheet).delete()
        
        # Clear sorceries and swordsman schools
        sheet.sorceries.clear()
        sheet.swordsman_schools.clear()
        
        # Clear advantages
        sheet.character_advantages.all().delete()
        
        # Reset other fields
        sheet.description = ""
        sheet.personality = ""
        sheet.biography = ""
        sheet.eye_color = ""
        sheet.hair_color = ""
        sheet.skin_hue = ""
        
        sheet.save()
        
        caller.msg("Your character sheet has been reset for a new character generation process.")
    
    text = "Welcome to character creation! Let's start by choosing your gender."
    options = [
        {"key": "1", "desc": "Male", "goto": "set_gender"},
        {"key": "2", "desc": "Female", "goto": "set_gender"},
    ]
    return text, options



def set_gender(caller, raw_string):
    sheet = ensure_chargen_data(caller)
    genders = ["Male", "Female"]
    choice = int(raw_string) - 1
    if 0 <= choice < len(genders):
        gender = genders[choice]
        sheet.gender = gender
        sheet.save()
        caller.msg(f"You've chosen {gender} as your gender.")
        return choose_nationality(caller)
    else:
        caller.msg("Invalid choice. Please try again.")
        return start_chargen(caller)

def choose_nationality(caller):
    text = "Now, let's choose your nationality."
    options = [
        {"key": str(i+1), "desc": nat, "goto": "set_nationality"}
        for i, nat in enumerate(["Castille", "Montaigne", "Avalon", "Vendel", "Vesten", "Vodacce", "Eisen"])
    ]
    return text, options

def set_nationality(caller, raw_string):
    sheet = ensure_chargen_data(caller)
    nationalities = ["Castille", "Montaigne", "Avalon", "Vendel", "Vesten", "Vodacce", "Eisen"]
    choice = int(raw_string) - 1
    if 0 <= choice < len(nationalities):
        nationality = nationalities[choice]
        sheet.nationality = nationality
        
        national_trait = get_national_trait(nationality)
        if national_trait:
            current_value = getattr(sheet, national_trait)
            setattr(sheet, national_trait, current_value + 1)
        
        sheet.save()
        
        caller.msg(f"You've chosen {nationality} as your nationality.")
        return assign_traits(caller)
    else:
        caller.msg("Invalid choice. Please try again.")
        return choose_nationality(caller)

def get_national_trait(nationality):
        return {
            "Castille": "finesse", "Montaigne": "panache", "Avalon": "resolve",
            "Vendel": "wits", "Vesten": "wits", "Vodacce": "wits", "Eisen": "brawn",
        }.get(nationality, "")

def assign_traits(caller):
    sheet = ensure_chargen_data(caller)
    text = "Now let's assign your traits. You have 8 points to distribute, plus your national trait bonus.\n"
    text += "Current traits:\n"
    
    national_trait = get_national_trait(sheet.nationality)
    
    for trait in ['brawn', 'finesse', 'wits', 'resolve', 'panache']:
        value = getattr(sheet, trait)
        if trait == national_trait:
            text += f"{trait.capitalize()}: {value} (includes +1 national bonus)\n"
        else:
            text += f"{trait.capitalize()}: {value}\n"
    
    points_spent = sum(getattr(sheet, trait) - 1 for trait in ['brawn', 'finesse', 'wits', 'resolve', 'panache']) - 1
    points_remaining = 8 - points_spent
    
    text += f"\nPoints remaining: {points_remaining}"
    text += "\nEnter trait and value (e.g., 'brawn 3') or type 'done' when finished."
    options = [{"key": "_default", "goto": "trait_input"}]
    return text, options

def trait_input(caller, raw_string):
    sheet = ensure_chargen_data(caller)
    
    if raw_string.lower().strip() == "done":
        return confirm_traits(caller)
    
    parts = raw_string.split()
    if len(parts) != 2 or parts[0] not in ['brawn', 'finesse', 'wits', 'resolve', 'panache'] or not parts[1].isdigit():
        caller.msg("Invalid input. Please enter trait and value (e.g., 'brawn 3') or 'done' to finish.")
        return assign_traits(caller)
    
    trait, value = parts[0], int(parts[1])
    current_value = getattr(sheet, trait)
    points_to_add = value - current_value
    
    national_trait = get_national_trait(sheet.nationality)
    points_spent = sum(getattr(sheet, t) - 1 for t in ['brawn', 'finesse', 'wits', 'resolve', 'panache']) - 1
    points_remaining = 8 - points_spent

    if trait == national_trait and value < 2:
        caller.msg(f"{trait.capitalize()} is your national trait and cannot be less than 2.")
        return assign_traits(caller)
    
    if points_to_add > points_remaining:
        caller.msg(f"Not enough points. You have {points_remaining} points available.")
    elif value < 1:
        caller.msg("Traits cannot be less than 1.")
    elif value > 3 and trait != national_trait:
        caller.msg(f"Traits other than your national trait cannot be higher than 3.")
    else:
        setattr(sheet, trait, value)
        sheet.save()
        caller.msg(f"{trait.capitalize()} set to {value}.")
    
    return assign_traits(caller)

def confirm_traits(caller):
    sheet = ensure_chargen_data(caller)
    text = "Here are your final trait values:\n"
    
    national_trait = get_national_trait(sheet.nationality)
    total_points = 0
    
    for trait in ['brawn', 'finesse', 'wits', 'resolve', 'panache']:
        value = getattr(sheet, trait)
        if trait == national_trait:
            text += f"{trait.capitalize()}: {value} (includes +1 national bonus)\n"
            total_points += value - 2  # Subtract 2 to account for base 1 and national bonus
        else:
            text += f"{trait.capitalize()}: {value}\n"
            total_points += value - 1  # Subtract 1 to account for base 1

    text += f"\nTotal points spent: {total_points}/8"
    
    if total_points < 8:
        text += f"\nYou still have {8 - total_points} points to distribute. Are you sure you want to proceed? (yes/no)"
    elif total_points == 8:
        text += "\nAre you satisfied with these traits? (yes/no)"
    else:
        text += "\nYou've spent too many points. Please adjust your traits."
        return assign_traits(caller)
    
    options = [
        {"key": "yes", "goto": "check_sorcery"},
        {"key": "no", "goto": "assign_traits"}
    ]
    return text, options

def check_sorcery(caller):
    sheet = ensure_chargen_data(caller)
    potential_sorcery = get_potential_sorcery(sheet.nationality, sheet.gender)
    if potential_sorcery:
        text = f"Based on your nationality, you have the potential for {potential_sorcery} sorcery.\nDo you wish to be a sorcerer? (yes/no)"
        options = [
            {"key": "yes", "goto": "sorcery_blooded"},
            {"key": "no", "goto": "ask_duelist"}
        ]
        return text, options
    else:
        return ask_duelist(caller)

def get_potential_sorcery(nationality, gender):
        
        return {
            "Castille": "El Fuego Adentro", "Avalon": "Glamour",
            "Montaigne": "Porte", "Vodacce": "Sorte" if gender == "Female" else None, 
        }.get(nationality)

def sorcery_blooded(caller):
        text = "Are you full-blooded or half-blooded? (full/half)"
        options = [
            {"key": "full", "goto": "set_sorcery_blooded"},
            {"key": "half", "goto": "set_sorcery_blooded"}
        ]
        return text, options

def set_sorcery_blooded(caller, raw_string):
    sheet = ensure_chargen_data(caller)
    potential_sorcery = get_potential_sorcery(sheet.nationality, sheet.gender)
    if not potential_sorcery:
        caller.msg("Error: No potential sorcery found.")
        return check_duelist(caller)

    if raw_string.lower().strip() == "full":
        if sheet.hero_points >= 40:
            sheet.hero_points -= 40
            sheet.is_sorcerer = True
            sorcery, _ = Sorcery.objects.get_or_create(name=potential_sorcery)
            sheet.sorceries.add(sorcery)
            sheet.save()
            caller.msg(f"You have chosen full-blooded {potential_sorcery} sorcery.")
            return distribute_sorcery_points(caller, 7)
        else:
            caller.msg("You do not have enough points for full-blooded sorcery.")
            return sorcery_blooded(caller)
    elif raw_string.lower() == "half":
        if sheet.hero_points >= 20:
            sheet.hero_points -= 20
            sheet.is_sorcerer = True
            sorcery, _ = Sorcery.objects.get_or_create(name=potential_sorcery)
            sheet.sorceries.add(sorcery)
            sheet.save()
            caller.msg(f"You have chosen half-blooded {potential_sorcery} sorcery.")
            return distribute_sorcery_points(caller, 3)
        else:
            caller.msg("You do not have enough points for half-blooded sorcery.")
            return sorcery_blooded(caller)
    return ask_duelist(caller)

def distribute_sorcery_points(caller, points_available):
    sheet = ensure_chargen_data(caller)
    sorcery = sheet.sorceries.first()
    
    text = f"You have {points_available} sorcery points to distribute among your sorcerous knacks.\n"
    text += "Available knacks:\n"

    sorcery_knacks = SORCERIES[sorcery.name]['knacks']
    for knack_name in sorcery_knacks:
        knack, _ = Knack.objects.get_or_create(name=knack_name)
        sorcery.knacks.add(knack)
        knack_value, _ = KnackValue.objects.get_or_create(character_sheet=sheet, knack=knack)
        text += f"{knack_name}: Current value {knack_value.value}\n"

    text += f"\nYou have {points_available} points left to distribute. "
    text += "Enter knack name and value (e.g., 'Knack 2') or 'done' when finished."

    options = [{"key": "_default", "goto": "set_sorcery_knack"}]
    return text, options

def set_sorcery_knack(caller, raw_string):
    sheet = ensure_chargen_data(caller)
    sorcery = sheet.sorceries.first()
    
    if raw_string.lower().strip() == 'done':
        points_spent = sum(KnackValue.objects.filter(character_sheet=sheet, knack__sorceries=sorcery).values_list('value', flat=True))
        points_available = 7 if sheet.hero_points >= 40 else 3
        if points_spent == points_available:
            caller.msg("All sorcery points have been distributed.")
            return ask_duelist(caller)
        else:
            caller.msg(f"You still have {points_available - points_spent} points to distribute.")
            return distribute_sorcery_points(caller, points_available - points_spent)

    parts = raw_string.split()
    if len(parts) != 2 or not parts[1].isdigit():
        caller.msg("Invalid input. Please enter knack name and value (e.g., 'Knack 2').")
        return distribute_sorcery_points(caller, points_available)

    knack_name, value = parts[0].capitalize(), int(parts[1])
    knack = Knack.objects.filter(name=knack_name, sorceries=sorcery).first()
    if not knack:
        caller.msg(f"Invalid knack. Available knacks are: {', '.join(SORCERIES[sorcery.name]['knacks'])}")
        return distribute_sorcery_points(caller, points_available)

    knack_value, created = KnackValue.objects.get_or_create(character_sheet=sheet, knack=knack)
    points_to_add = value - knack_value.value

    points_spent = sum(KnackValue.objects.filter(character_sheet=sheet, knack__sorceries=sorcery).values_list('value', flat=True))
    points_available = 7 if sheet.hero_points >= 40 else 3

    if points_spent + points_to_add > points_available:
        caller.msg(f"Not enough points. You have {points_available - points_spent} points left to distribute.")
    else:
        knack_value.value = value
        knack_value.save()
        caller.msg(f"{knack_name} set to {value}.")

    return distribute_sorcery_points(caller, points_available - points_spent - points_to_add)

def ask_duelist(caller):
    text = "Do you wish to be a duelist? (yes/no)"
    options = [
        {"key": "yes", "goto": "choose_duelist_school"},
        {"key": "no", "goto": "select_skills"}
    ]
    return text, options

def choose_duelist_school(caller):
    sheet = ensure_chargen_data(caller)
    page = getattr(caller.ndb, 'duelist_school_page', 0)
    if page is None:
        page = 0
    caller.ndb.duelist_school_page = page  # Ensure the attribute is set

    schools = list(SWORDSMAN_SCHOOLS.items())
    schools_per_page = 7
    start_index = page * schools_per_page
    end_index = min(start_index + schools_per_page, len(schools))
    current_schools = schools[start_index:end_index]

    text = "Choose a duelist school:\n"
    options = []

    for i, (school_name, school_data) in enumerate(current_schools, start=1):
        country = school_data.get("country", [])
        if isinstance(country, str):
            country = [country]
        cost = 25 if sheet.nationality in country else 35
        requirements = ", ".join(school_data.get("requirements", []))

        text += f"{i}. {school_name} (Cost: {cost} HP, Country: {', '.join(country)}, Requirements: {requirements})\n"
        options.append({"key": str(i), "desc": school_name, "goto": "process_duelist_choice"})

    # Add navigation options
    if page > 0:
        options.append({"key": "P", "desc": "Previous schools", "goto": "previous_duelist_schools"})
    if end_index < len(schools):
        options.append({"key": "N", "desc": "Next schools", "goto": "next_duelist_schools"})

    return text, options

def next_duelist_schools(caller):
    max_pages = (len(SWORDSMAN_SCHOOLS) - 1) // 7  # 7 schools per page
    current_page = getattr(caller.ndb, 'duelist_school_page', 0)
    if current_page is None:
        current_page = 0
    caller.ndb.duelist_school_page = min(current_page + 1, max_pages)
    return choose_duelist_school(caller)

def previous_duelist_schools(caller):
    current_page = getattr(caller.ndb, 'duelist_school_page', 0)
    if current_page is None:
        current_page = 0
    caller.ndb.duelist_school_page = max(0, current_page - 1)
    return choose_duelist_school(caller)

def process_duelist_choice(caller, raw_string):
    sheet = ensure_chargen_data(caller)
    page = getattr(caller.ndb, 'duelist_school_page', 0)
    schools = list(SWORDSMAN_SCHOOLS.items())
    schools_per_page = 7
    start_index = page * schools_per_page

    try:
        choice = int(raw_string) - 1
        if 0 <= choice < schools_per_page and (start_index + choice) < len(schools):
            school_name, school_data = schools[start_index + choice]
            
            country = school_data.get("country", [])
            if isinstance(country, str):
                country = [country]
            cost = 25 if sheet.nationality in country else 35
            
            if sheet.hero_points >= cost:
                sheet.hero_points -= cost
                school, _ = SwordsmanSchool.objects.get_or_create(name=school_name)
                sheet.swordsman_schools.add(school)
                sheet.duelist_style = school_name
                
                # Add Swordsman's Guild Advantage for free
                swordsman_guild_adv, _ = Advantage.objects.get_or_create(name="Swordsman's Guild Membership")
                CharacterAdvantage.objects.get_or_create(character_sheet=sheet, advantage=swordsman_guild_adv)

                # Add required knacks and skills from SWORDSMAN_SCHOOLS
                for skill_name, knacks in school_data.get("knacks", {}).items():
                    skill, _ = Skill.objects.get_or_create(name=skill_name, category="Martial")
                    sheet.skills.add(skill)
                    for knack_name, value in knacks.items():
                        knack, _ = Knack.objects.get_or_create(name=knack_name, skill=skill)
                        KnackValue.objects.update_or_create(
                            character_sheet=sheet,
                            knack=knack,
                            defaults={'value': value}
                        )

                # Add the two free skills from the curriculum
                for req in school_data.get("requirements", []):
                    if req in PACKAGES.get("Martial", {}):
                        process_skill_package(caller, req, 'Martial', free=True)
                    elif req in PACKAGES.get("Civilian", {}):
                        process_skill_package(caller, req, 'Civilian', free=True)
                
                sheet.save()
                
                caller.msg(f"You have chosen the {school_name} school. You've received the Swordsman's Guild Membership advantage and the school's starting skills for free.")
                return select_skills(caller)
            else:
                caller.msg("You don't have enough Hero Points for this school.")
        else:
            caller.msg("Invalid choice. Please select a valid duelist school.")
    except ValueError:
        caller.msg("Invalid input. Please enter a number.")
    
    return choose_duelist_school(caller)
            

def get_duelist_style(nationality):
    for school, details in SWORDSMAN_SCHOOLS.items():
        if nationality in details.get("country", []):
            return school
    return None  # If no school is found for the nationality

def select_skills(caller):
    sheet = ensure_chargen_data(caller)
    text = "Current skills:\n"
    for skill in sheet.skills.all():
        text += f"{skill.category}:\n"
        text += f"  {skill.name}:\n"
        for knack in skill.knacks.all():
            knack_value, created = KnackValue.objects.get_or_create(character_sheet=sheet, knack=knack, defaults={'value': 0})
            text += f"    {knack.name}: {knack_value.value}\n"

    text += "\nAvailable skill packages:\n"
    for category, packages in PACKAGES.items():
        text += f"\n{category} Packages:\n"
        for package, details in packages.items():
            cost = details.get('cost', 'N/A')
            knacks = ', '.join(details['knacks'].keys())
            text += f"  {package}: Cost: {cost}, Knacks: {knacks}\n"
            if details['advanced']:
                advanced_knacks = ', '.join(details['advanced'].keys())
                text += f"    Advanced: {advanced_knacks}\n"

    text += f"\nYou have {sheet.hero_points} hero points remaining."
    text += "\nEnter the category and name of the skill package you want to choose (e.g., 'Martial Fencing'), or 'done' to finish selecting packages."
    options = [{"key": "_default", "goto": "set_skill_package"}]
    return text, options


def set_skill_package(caller, raw_string):
    if raw_string.lower().strip() == 'done':
        return buy_additional_knacks(caller)
# further retouches
    parts = raw_string.strip().split(sep=" ", maxsplit=1)
    if len(parts) != 2:
        caller.msg("Invalid input. Please enter the category and package name (e.g., 'Martial Fencing') or 'done' to finish.")
        return select_skills(caller)

    category, package = parts[0].capitalize(), parts[1].strip().title()

    if category in PACKAGES and package in PACKAGES[category]:
        if process_skill_package(caller, package, category):
            return select_skills(caller)
        else:
            # If process_skill_package returns False, we stay on the same menu
            return select_skills(caller)
    else:
        caller.msg("Invalid package. Please enter a valid category and package name or 'done' to finish selecting packages.")
        return select_skills(caller)

def process_skill_package(caller, package, category, free=False):
    sheet = ensure_chargen_data(caller)
    if category in PACKAGES and package in PACKAGES[category]:
        details = PACKAGES[category][package]
        
        # Check if the skill already exists for this character
        if sheet.skills.filter(name=package, category=category).exists():
            caller.msg(f"You have already purchased the {package} package.")
            return False

        if free or sheet.hero_points >= details["cost"]:
            if not free:
                sheet.hero_points -= details["cost"]

            skill, _ = Skill.objects.get_or_create(name=package, category=category)
            sheet.skills.add(skill)

            for knack_name, value in details["knacks"].items():
                knack, _ = Knack.objects.get_or_create(name=knack_name, skill=skill)
                KnackValue.objects.update_or_create(
                    character_sheet=sheet,
                    knack=knack,
                    defaults={'value': value}
                )

            for adv_knack, adv_value in details.get("advanced", {}).items():
                if adv_value > 0:
                    knack, _ = Knack.objects.get_or_create(name=adv_knack, skill=skill)
                    KnackValue.objects.update_or_create(
                        character_sheet=sheet,
                        knack=knack,
                        defaults={'value': adv_value}
                    )

            sheet.save()
            if not free:
                caller.msg(f"You have chosen the {package} package. You have {sheet.hero_points} hero points remaining.")
            else:
                caller.msg(f"You have received the {package} package for free as part of your duelist school curriculum.")
            return True
        else:
            caller.msg("You don't have enough hero points for this package.")
            return False
    else:
        caller.msg(f"Error: Package {package} not found in category {category}.")
        return False


def process_knack(knack):
    if '(' in knack:
        skill, specific_knack = knack.split('(', 1)
        skill = skill.strip()
        specific_knack = f"({specific_knack.strip()}"
    else:
        skill = knack
        specific_knack = knack
    return skill, specific_knack

def choose_specialty_knack(caller):
    chargen_data = ensure_chargen_data(caller)
    package = chargen_data["current_package"]
    category = chargen_data["current_category"]
    
    text = f"You've chosen a package with specialty knacks. Please choose a specialty knack to set at 2 points:\n"
    options = []
    
    for i, knack in enumerate(PACKAGES[category][package]["knacks"].keys()):
        text += f"{i+1}. {knack}\n"
        options.append({"key": str(i+1), "desc": knack, "goto": "set_specialty_knack"})
    
    return text, options


def set_specialty_knack(caller, raw_string):
    chargen_data = ensure_chargen_data(caller)
    package = chargen_data["current_package"]
    skill = "Merchant" if "Merchant" in PACKAGES[package]["knacks"] else "Artist"
    chosen_knack = PACKAGES[package]["knacks"][skill][int(raw_string) - 1]
    
    # Process the package first
    process_skill_package(caller, package)
    
    # Then set the chosen specialty knack to 2
    chargen_data["skills"][chosen_knack] = 2
    caller.msg(f"You've set {chosen_knack} to 2 points.")
    
    return select_skills(caller)

    
def buy_additional_knacks(caller):
    sheet = ensure_chargen_data(caller)
    text = "You can now buy additional knacks for skills you already have.\n"
    text += "Martial Knacks cost 2 Hero Points. Civilian Knacks cost 1 Hero Point.\n"
    text += "Available knacks:\n"

    options = []
    option_index = 1

    for skill in sheet.skills.all():
        text += f"\n{skill.category}:\n"
        text += f"  {skill.name}:\n"
        for knack in skill.knacks.all():
            knack_value = KnackValue.objects.get(character_sheet=sheet, knack=knack)
            cost = 2 if skill.category == "Martial" else 1
            text += f"    {option_index}. {knack.name}: Current value {knack_value.value}, Cost: {cost} HP\n"
            options.append((skill.category, skill.name, knack.name))
            option_index += 1

    text += f"\nYou have {sheet.hero_points} hero points remaining."
    text += "\nEnter the number of the knack you want to increase or 'done' to finish."
    
    caller.ndb.knack_options = options
    return text, [{"key": "_default", "goto": "process_knack_choice"}]

def process_knack_choice(caller, raw_string):
    sheet = ensure_chargen_data(caller)
    if raw_string.lower().strip() == "done":
        return distribute_advantages(caller)

    try:
        choice = int(raw_string.strip()) - 1
        if 0 <= choice < len(caller.ndb.knack_options):
            category, skill_name, knack_name = caller.ndb.knack_options[choice]
            cost = 2 if category == "Martial" else 1
            if sheet.hero_points >= cost:
                sheet.hero_points -= cost
                skill = sheet.skills.get(name=skill_name, category=category)
                knack = skill.knacks.get(name=knack_name)
                knack_value, created = KnackValue.objects.get_or_create(character_sheet=sheet, knack=knack)
                knack_value.value += 1
                knack_value.save()
                sheet.save()
                caller.msg(f"You have increased {category} {skill_name} - {knack_name} to {knack_value.value}. "
                           f"You have {sheet.hero_points} hero points remaining.")
            else:
                caller.msg("You don't have enough hero points for this knack.")
        else:
            caller.msg("Invalid choice. Please enter a valid number or 'done' to finish.")
    except ValueError:
        caller.msg("Invalid input. Please enter a number or 'done' to finish.")

    return buy_additional_knacks(caller)

def knack_input(caller, raw_string):
    chargen_data = ensure_chargen_data(caller)
    if raw_string.lower() == "done":
        return distribute_advantages(caller)

    parts = raw_string.strip().split(maxsplit=2)
    if len(parts) != 3:
        caller.msg("Invalid input. Please enter the category, skill, and knack (e.g., 'Martial Fencing Attack (Fencing)') or 'done' to finish.")
        return buy_additional_knacks(caller)

    category, skill, knack = parts
    if category in chargen_data['skills'] and skill in chargen_data['skills'][category]:
        if knack in chargen_data['skills'][category][skill]:
            cost = 2 if category == "Martial" else 1
            if chargen_data["hero_points"] >= cost:
                chargen_data["hero_points"] -= cost
                chargen_data['skills'][category][skill][knack] += 1
                caller.msg(f"You have increased {category} {skill} - {knack} to {chargen_data['skills'][category][skill][knack]}. "
                           f"You have {chargen_data['hero_points']} hero points remaining.")
            else:
                caller.msg("You don't have enough hero points for this knack.")
        else:
            caller.msg(f"Invalid knack. Available knacks for {skill} are: {', '.join(chargen_data['skills'][category][skill].keys())}")
    else:
        caller.msg("Invalid category or skill. Please enter a valid category, skill, and knack or 'done' to finish.")
    return buy_additional_knacks(caller)

def distribute_advantages(caller):
    sheet = ensure_chargen_data(caller)
    text = "You have the following Advantages available:\n"
    for advantage in Advantage.objects.all():
        cost = advantage.get_cost(sheet.nationality)
        if isinstance(cost, list):
            cost_str = f"{cost[0]}-{cost[-1]}"
        else:
            cost_str = str(cost)
        text += f"{advantage.name}: Cost: {cost_str}, Description: {advantage.description}\n"
    text += f"\nYou have {sheet.hero_points} hero points remaining."
    text += "\nEnter the name of the advantage you want to choose or 'done' to proceed to character description."
    options = [{"key": "_default", "goto": "advantage_input"}]
    return text, options



def choose_advantage_level(caller, advantage):
    sheet = ensure_chargen_data(caller)
    costs = advantage.get_cost(sheet.nationality)
    if not isinstance(costs, list):
        costs = [costs]
    text = f"Choose the level for {advantage.name}:\n"
    for i, cost in enumerate(costs, 1):
        text += f"{i}. Level {i} (Cost: {cost} HP)\n"
    text += f"\nYou have {sheet.hero_points} hero points remaining."
    options = [{"key": str(i), "desc": f"Level {i}", "goto": "process_advantage_level"} for i in range(1, len(costs) + 1)]
    return text, options

def process_advantage_level(caller, raw_string):
    sheet = ensure_chargen_data(caller)
    advantage = caller.ndb.current_advantage
    costs = advantage.get_cost(sheet.nationality)
    if not isinstance(costs, list):
        costs = [costs]
    try:
        choice = int(raw_string) - 1
        if 0 <= choice < len(costs):
            cost = costs[choice]
            if sheet.hero_points >= cost:
                sheet.hero_points -= cost
                CharacterAdvantage.objects.create(character_sheet=sheet, advantage=advantage, level=choice + 1)
                sheet.save()
                caller.msg(f"You have chosen {advantage.name} at level {choice + 1}. You have {sheet.hero_points} hero points remaining.")
            else:
                caller.msg("You don't have enough hero points for this Advantage level.")
        else:
            caller.msg("Invalid choice. Please select a valid level.")
    except ValueError:
        caller.msg("Invalid input. Please enter a number.")
    
    del caller.ndb.current_advantage
    if sheet.hero_points > 0:
        return distribute_advantages(caller)
    else:
        return chargen_description(caller)

def advantage_input(caller, raw_string):
    sheet = ensure_chargen_data(caller)
    if raw_string.lower().strip() == "done":
        sheet.hero_points = max(0, sheet.hero_points)  # Ensure non-negative
        sheet.save()
        return chargen_description(caller)

    advantage_name = raw_string.strip()
    try:
        advantage = Advantage.objects.get(name__iexact=advantage_name)
        cost = advantage.get_cost(sheet.nationality)
        if isinstance(cost, list):
            caller.ndb.current_advantage = advantage
            return choose_advantage_level(caller, advantage)
        else:
            if sheet.hero_points >= cost:
                sheet.hero_points -= cost
                CharacterAdvantage.objects.create(character_sheet=sheet, advantage=advantage)
                sheet.save()
                caller.msg(f"You have chosen the {advantage.name} advantage. You have {sheet.hero_points} hero points remaining.")
            else:
                caller.msg("You don't have enough hero points for this Advantage.")
    except Advantage.DoesNotExist:
        caller.msg("Invalid advantage. Please enter a valid advantage name or 'done' to finish.")

    if sheet.hero_points > 0:
        return distribute_advantages(caller)
    else:
        sheet.hero_points = 0
        sheet.save()
        return chargen_description(caller)

def chargen_description(caller):
    text = "Please enter a physical description of your character (minimum 100 characters):"
    options = [{"key": "_default", "goto": "node_store_description"}]
    return text, options

def node_store_description(caller, raw_string):
    sheet = ensure_chargen_data(caller)
    processed_string = process_ansi_codes(raw_string)
    if len(processed_string.replace('\n', '').replace('\t', '')) < 100:
        caller.msg("Your description is too short. Please provide more detail.")
        return chargen_description(caller)
    caller.ndb.temp_description = raw_string  # Store temporarily
    return confirm_description(caller)

def confirm_description(caller):
    text = f"Your character's description:\n\n{caller.ndb.temp_description}\n\nIs this correct? (yes/no)"
    options = [
        {"key": "yes", "goto": "save_description"},
        {"key": "no", "goto": "chargen_description"}
    ]
    return text, options

def save_description(caller, raw_string):
    sheet = ensure_chargen_data(caller)
    sheet.description = caller.ndb.temp_description
    sheet.save()
    del caller.ndb.temp_description
    return chargen_personality(caller)

def chargen_personality(caller):
    text = "Please describe your character's personality (minimum 150 characters):"
    options = [{"key": "_default", "goto": "node_store_personality"}]
    return text, options

def node_store_personality(caller, raw_string):
    processed_string = process_ansi_codes(raw_string)
    if len(processed_string.replace('\n', '').replace('\t', '')) < 150:
        caller.msg("Your personality description is too short. Please provide more detail.")
        return chargen_personality(caller)
    caller.ndb.temp_personality = raw_string  # Store temporarily
    return confirm_personality(caller)

def confirm_personality(caller):
    text = f"Your character's personality:\n\n{caller.ndb.temp_personality}\n\nIs this correct? (yes/no)"
    options = [
        {"key": "yes", "goto": "save_personality"},
        {"key": "no", "goto": "chargen_personality"}
    ]
    return text, options

def save_personality(caller, raw_string):
    sheet = ensure_chargen_data(caller)
    sheet.personality = caller.ndb.temp_personality
    sheet.save()
    del caller.ndb.temp_personality
    return chargen_biography(caller)

def chargen_biography(caller):
    text = "Please enter a brief biography for your character (minimum 200 characters):"
    options = [{"key": "_default", "goto": "node_store_biography"}]
    return text, options

def node_store_biography(caller, raw_string):
    processed_string = process_ansi_codes(raw_string)
    if len(processed_string.replace('\n', '').replace('\t', '')) < 200:
        caller.msg("Your biography is too short. Please provide more detail.")
        return chargen_biography(caller)
    caller.ndb.temp_biography = raw_string  # Store temporarily
    return confirm_biography(caller)

def confirm_biography(caller):
    text = f"Your character's biography:\n\n{caller.ndb.temp_biography}\n\nIs this correct? (yes/no)"
    options = [
        {"key": "yes", "goto": "save_biography"},
        {"key": "no", "goto": "chargen_biography"}
    ]
    return text, options

def save_biography(caller, raw_string):
    sheet = ensure_chargen_data(caller)
    sheet.biography = caller.ndb.temp_biography
    sheet.save()
    del caller.ndb.temp_biography
    return chargen_eye_color(caller)

def chargen_eye_color(caller):
    text = "Please enter your character's eye color:"
    options = [{"key": "_default", "goto": "node_store_eye_color"}]
    return text, options

def node_store_eye_color(caller, raw_string):
    sheet = ensure_chargen_data(caller)
    sheet.eye_color = raw_string.strip()
    sheet.save()
    return chargen_hair_color(caller)

def chargen_hair_color(caller):
    text = "Please enter your character's hair color:"
    options = [{"key": "_default", "goto": "node_store_hair_color"}]
    return text, options

def node_store_hair_color(caller, raw_string):
    sheet = ensure_chargen_data(caller)
    sheet.hair_color = raw_string.strip()
    sheet.save()
    return chargen_skin_color(caller)

def chargen_skin_color(caller):
    text = "Please enter your character's skin color:"
    options = [{"key": "_default", "goto": "node_store_skin_color"}]
    return text, options

def node_store_skin_color(caller, raw_string):
    sheet = ensure_chargen_data(caller)
    sheet.skin_hue = raw_string.strip()
    sheet.save()
    return finish_chargen(caller)


def send_approval_request(caller):
    sheet = ensure_chargen_data(caller)
    request = create.create_script(Request)
    request.db.requester = caller
    request.db.request_type = "Character Approval"
    
    request.db.description = f"""New character {caller.name} requires approval.

Biography:
{sheet.biography}

Personality:
{sheet.personality}

Description:
{sheet.description}

Traits:
{', '.join(f'{trait}: {getattr(sheet, trait)}' for trait in ['brawn', 'finesse', 'wits', 'resolve', 'panache'])}

Skills:
{', '.join(f'{skill.name}: {KnackValue.objects.get(character_sheet=sheet, knack__skill=skill).value}' for skill in sheet.skills.all())}

Perks:
{', '.join(ca.advantage.name for ca in sheet.character_advantages.all())}

Nationality: {sheet.nationality}
Sorcery: {sheet.sorceries.first().name if sheet.is_sorcerer else 'None'}
Duelist Style: {sheet.duelist_style}
"""
    request.db.status = "Pending"
    caller.msg("Your character has been submitted for staff approval. Please wait for a staff member to review your character.")



def finish_chargen(caller):
    sheet = ensure_chargen_data(caller)

    # Set final status
    sheet.complete_chargen = True
    sheet.approved = False

    # Update full_name if it hasn't been set
    if not sheet.full_name:
        sheet.full_name = caller.key
    if sheet.hero_points >= 0:
        sheet.hero_points = 0
    sheet.save()

    # Create approval request
    new_request = create.create_script("typeclasses.requests.Request")
    new_request.db.requester = caller
    new_request.db.request_type = "Character Approval"
    new_request.db.description = f"New character {caller.name} requires approval."

    # Move the character to a waiting room
    waiting_room = caller.search("Main Room", global_search=True)
    if waiting_room:
        caller.move_to(waiting_room, quiet=True)

    text = "Character creation complete! Your character has been submitted for staff approval. "
    text += "You've been moved to a waiting room. A staff member will review your character shortly."
    caller.msg(text)

    # Clean up any remaining temporary data
    if hasattr(caller.ndb, 'chargen'):
        del caller.ndb.chargen

    return text, None