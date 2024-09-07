from evennia import Command
from typeclasses.chargen import SORCERIES, SWORDSMAN_SCHOOLS, ADVANTAGES, PACKAGES
import shlex
from world.character_sheet.models import CharacterSheet, Skill, Knack, SwordsmanSchool


class CmdBuyAttribute(Command):
    """
    Buy or improve character attributes using Experience Points (XP).

    Usage:
    buy <category> <name> [<value>]

    Categories: knack, advantage, skill, trait, sorcery, swordsman

    Examples:
    buy knack Martial Fencing "Attack (Fencing)" 3
    buy advantage Contact
    buy skill Martial Fencing
    buy trait Brawn 4
    buy sorcery "El Fuego Adentro" Feed 2
    buy swordsman "Valroux Feint" 3
    """

    key = "buy"
    locks = "cmd:all()"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: buy <category> <name> [<value>]")
            return

        parts = self.args.split()
        if len(parts) < 2:
            self.caller.msg("Usage: buy <category> <name> [<value>]")
            return

        category = parts[0].lower()
        value = parts[-1] if parts[-1].isdigit() else None
        name = " ".join(parts[1:-1] if value else parts[1:])

        methods = {
            "trait": self.buy_trait,
            "skill": self.buy_skill,
            "knack": self.buy_knack,
            "advantage": self.buy_advantage,
            "sorcery": self.buy_sorcery,
            "swordsman": self.buy_swordsman
        }

        method = methods.get(category)
        if method:
            if value:
                method(name, int(value))
            else:
                method(name)
        else:
            self.caller.msg(f"Unknown category: {category}")

    def convert_xp_to_hp(self, xp_cost):
        caller = self.caller
        sheet = CharacterSheet.objects.get(db_object=caller)
        
        total_xp = sheet.xp + (sheet.hero_points * 2)
        if total_xp >= xp_cost:
            sheet.hero_points = (total_xp - xp_cost) // 2
            sheet.xp = (total_xp - xp_cost) % 2
            sheet.save()
            return True
        return False

    def buy_knack(self, name, value=None):
        caller = self.caller
        sheet = CharacterSheet.objects.get(db_object=caller)

        try:
            parts = shlex.split(name)  # This handles quoted strings correctly
        except ValueError:
            caller.msg("Error: Unmatched quotation marks in your input.")
            return

        if len(parts) < 3:
            caller.msg("Usage: buy knack <category> <skill> <knack> [value]")
            caller.msg("Use double quotes for compound names, e.g., \"Dirty Fighting\"")
            return

        category = parts[0].title()
        skill_name = parts[1].title()
        
        if len(parts) > 3 and parts[-1].isdigit():
            knack_name = " ".join(parts[2:-1]).title()
            value = int(parts[-1])
        else:
            knack_name = " ".join(parts[2:]).title()
            value = None

        caller.msg(f"Debug: Attempting to buy knack '{knack_name}' for skill '{skill_name}' in category '{category}'")

        # Get the skill
        try:
            skill = Skill.objects.get(name=skill_name, category=category)
        except Skill.DoesNotExist:
            caller.msg(f"Error: The skill '{skill_name}' in category '{category}' does not exist.")
            return

        # Get the knack, handling the case of multiple knacks
        knacks = Knack.objects.filter(name=knack_name, skill=skill)
        if not knacks.exists():
            caller.msg(f"Error: The knack '{knack_name}' does not exist for the skill '{skill_name}'.")
            return
        elif knacks.count() > 1:
            caller.msg(f"Warning: Multiple knacks found with the name '{knack_name}'. Using the first one.")
        knack = knacks.first()

        # Get or create the KnackValue
        knack_value, created = sheet.knack_values.get_or_create(knack=knack, defaults={'value': 0})

        current_value = knack_value.value
        new_value = current_value + 1 if value is None else value
        max_value = 5

        if new_value > max_value:
            caller.msg(f"You cannot increase {knack_name} beyond {max_value}.")
            return

        hp_cost = self.calculate_knack_cost(category, skill_name, knack_name)
        xp_cost = hp_cost * 2

        if self.convert_xp_to_hp(xp_cost):
            knack_value.value = new_value
            knack_value.save()
            sheet.save()
            caller.msg(f"You have increased {knack_name} to {new_value}. You have {sheet.hero_points} hero points and {sheet.xp} XP remaining.")
        else:
            caller.msg(f"You don't have enough XP for this knack. You need {xp_cost} XP.")

    def buy_advantage(self, name):
        caller = self.caller
        sheet = CharacterSheet.objects.get(db_object=caller)

        advantage = next((adv for adv in ADVANTAGES if adv.lower() == name.lower()), None)
        if not advantage:
            caller.msg(f"Unknown advantage: {name}")
            return

        if advantage in sheet.advantages:
            caller.msg(f"You already have the {advantage} advantage.")
            return

        hp_cost = ADVANTAGES[advantage].get('cost', 0)
        if isinstance(hp_cost, list):
            hp_cost = hp_cost[0]
        xp_cost = hp_cost * 300

        if self.convert_xp_to_hp(xp_cost):
            if advantage not in ["Twisted Blade", "Unbound", "Left-Handed", "Foul Weather Jack", "Faith"]:
                sheet.advantages.append(advantage)
                sheet.save(update_fields=['advantages'])
                caller.msg(f"You have purchased the {advantage} advantage. You have {sheet.hero_points} hero points and {sheet.xp} XP remaining.")
        else:
            caller.msg(f"You don't have enough XP for this advantage. You need {xp_cost} XP.")

    def buy_skill(self, name):
        caller = self.caller
        sheet = CharacterSheet.objects.get(db_object=caller)
        parts = name.split()
        if len(parts) < 2:
            caller.msg("Usage: buy skill <category> <skill>")
            return

        category = parts[0].capitalize()
        skill = " ".join(parts[1:]).title()  # Use title() instead of capitalize()


        if category not in PACKAGES:
            caller.msg(f"Unknown category: {category}")
            return

        # Find the skill case-insensitively
        matching_skill = next((s for s in PACKAGES[category] if s.lower() == skill.lower()), None)
        
        if not matching_skill:
            caller.msg(f"Unknown skill '{skill}' in category '{category}'")
            caller.msg(f"Available skills: {', '.join(PACKAGES[category].keys())}")
            return

        skill = matching_skill  # Use the correct casing from PACKAGES

        package = PACKAGES[category][skill]
        cost = package.get("cost", 0)
        xp_cost = cost * 2


        if self.convert_xp_to_hp(xp_cost):
            caller.msg(f"Purchasing {skill} package from {category} category:")
            if skill.lower() == "dirty fighting":
                skill = "Dirty Fighting"
            if category not in sheet.skills:
                sheet.skills[category] = {}
            
            if skill not in sheet.skills[category]:
                sheet.skills[category][skill] = {}

            for knack, value in package.get("knacks", {}).items():
                current_value = sheet.skills[category][skill].get(knack, 0)
                new_value = max(current_value, value)
                max_value = 5
                
                if new_value > max_value:
                    caller.msg(f"Cannot increase {knack} beyond {max_value}. Capping at {max_value}.")
                    new_value = max_value
                
                sheet.skills[category][skill][knack] = new_value
                caller.msg(f" - Set {knack} to {new_value}")

            advanced = package.get("advanced")
            if advanced and isinstance(advanced, dict):
                for adv_knack, adv_value in advanced.items():
                    if adv_knack not in sheet.skills[category][skill]:
                        sheet.skills[category][skill][adv_knack] = min(adv_value, max_value)
                        caller.msg(f" - Added advanced knack {adv_knack} at {sheet.skills[category][skill][adv_knack]}")
                    else:
                        caller.msg(f" - Advanced knack {adv_knack} already known")
            sheet.save()
            caller.msg(f"You have purchased the {skill} skill package. You have {sheet.hero_points} hero points and {sheet.xp} XP remaining.")
        else:
            caller.msg(f"You don't have enough XP for this skill package. You need {xp_cost} XP.")

    def buy_trait(self, name, value):
        caller = self.caller
        sheet = CharacterSheet.objects.get(db_object=caller)

        if not hasattr(sheet, name.lower()):
            caller.msg(f"Unknown trait: {name}")
            return

        current_value = getattr(sheet, name.lower())
        max_value = 6 if sheet.advantages.filter(name="Legendary Trait").exists() else 5
        if value > max_value:
            caller.msg(f"You cannot increase {name} beyond {max_value}.")
            return

        hp_cost = sum(i * 8 for i in range(current_value + 1, value + 1))
        xp_cost = hp_cost * 2

        if self.convert_xp_to_hp(xp_cost):
            setattr(sheet, name.lower(), value)
            sheet.save()
            caller.msg(f"You have increased {name} to {value}. You have {sheet.hero_points} hero points remaining.")
        else:
            caller.msg(f"You don't have enough XP to increase this trait. You need {round(xp_cost/2)} HP.")


# to do - URGENTLY CHANGE BUY_KNACK, BUY_SWORDSMAN, BUY_SKILL

    def buy_sorcery(self, name, value=None):
        caller = self.caller
        sheet = CharacterSheet.objects.get(db_object=caller)

        if not sheet.is_sorcerer:
            caller.msg("You are not a sorcerer and cannot buy sorcery knacks.")
            return

        parts = name.split()
        if len(parts) < 2:
            caller.msg("Usage: buy sorcery <sorcery_type> <knack> [value]")
            return

        sorcery_type = " ".join(parts[:-1])
        knack = parts[-1]

        if sorcery_type != caller.db.sorcery.get('name'):
            caller.msg(f"You are not a {sorcery_type} sorcerer.")
            return

        if sorcery_type not in SORCERIES or knack not in SORCERIES[sorcery_type]['knacks']:
            caller.msg(f"Unknown sorcery knack: {knack}")
            return

        current_value = sheet.sorcery_knacks.get(knack, 0)
        new_value = current_value + 1 if value is None else value

        if new_value > 5:
            caller.msg(f"You cannot increase sorcery knacks beyond 5.")
            return

        hp_cost = (new_value - current_value) * 3
        xp_cost = hp_cost * 2

        if self.convert_xp_to_hp(xp_cost):
            sheet.sorcery_knacks[knack] = new_value
            sheet.save()
            caller.msg(f"You have increased {knack} to {new_value}. You have {sheet.hero_points} hero points and {sheet.xp} XP remaining.")
        else:
            caller.msg(f"You don't have enough XP to increase this sorcery knack. You need {xp_cost} XP.")

    def buy_swordsman(self, name, value=None):
        caller = self.caller
        school = caller.db.duelist_style
        if not school or school not in SWORDSMAN_SCHOOLS:
            caller.msg("You are not a member of any swordsman school.")
            return

        if 'Martial' in caller.db.skills and school in caller.db.skills['Martial']:
            school_knacks = caller.db.skills['Martial'][school]
            matching_knack = next((k for k in school_knacks if name.lower() in k.lower()), None)
            
            if matching_knack:
                current_value = school_knacks[matching_knack]
                new_value = current_value + 1 if value is None else value

                max_value = 5
                if new_value > max_value:
                    caller.msg(f"You cannot increase {matching_knack} beyond {max_value}.")
                    return

                hp_cost = (new_value - current_value) * 4
                xp_cost = hp_cost * 2

                if self.convert_xp_to_hp(xp_cost):
                    caller.db.skills['Martial'][school][matching_knack] = new_value
                    caller.msg(f"You have increased {matching_knack} to {new_value}. You have {caller.db.hero_points} hero points and {caller.db.xp} XP remaining.")
                else:
                    caller.msg(f"You don't have enough XP for this swordsman knack. You need {xp_cost} XP.")
            else:
                caller.msg(f"Unknown swordsman knack: {name}")
        else:
            caller.msg(f"You don't have any knacks for the {school} school.")
    
    def calculate_knack_cost(self, category, skill, knack):
        if category == "Martial":
            if skill in SWORDSMAN_SCHOOLS:
                return 4  # Swordsman knacks
            elif knack in PACKAGES[category][skill].get('advanced', {}):
                return 3  # Advanced Martial knacks
            else:
                return 2  # Regular Martial knacks
        elif category == "Civilian":
            if knack in PACKAGES[category][skill].get('advanced', {}):
                return 3  # Advanced Civilian knacks
            else:
                return 1  # Regular Civilian knacks
        else:
            return 1  # Default cost

    def find_knack(self, name):
        for category, skills in PACKAGES.items():
            for skill, details in skills.items():
                for knack in details.get('knacks', {}):
                    if knack.lower() == name.lower():
                        return category, skill, knack
                for adv_knack in details.get('advanced', {}):
                    if adv_knack.lower() == name.lower():
                        return category, skill, adv_knack
        return None, None, None