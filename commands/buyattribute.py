from evennia import Command
from evennia.commands.default.muxcommand import MuxCommand
from typeclasses.chargen import SORCERIES, SWORDSMAN_SCHOOLS, ADVANTAGES, PACKAGES
import shlex
from world.character_sheet.models import CharacterSheet, Skill, Knack, SwordsmanSchool, KnackValue
class CmdBuyAttribute(MuxCommand):
    """
    Buy or improve character attributes using Experience Points (XP).

    Usage:
    buy/skill <category> <skill>
    buy/knack <category> <skill> <knack> [<value>]
    buy/advantage <advantage>
    buy/trait <trait> <value>
    buy/sorcery <sorcery_type> <knack> [<value>]
    buy/swordsman <knack> [<value>]

    Examples:
    buy/skill Martial Fencing
    buy/knack Martial Fencing "Attack (Fencing)" 3
    buy/advantage Contact
    buy/trait Brawn 4
    buy/sorcery "El Fuego Adentro" Feed 2
    buy/swordsman "Valroux Feint" 3
    """

    key = "buy"
    locks = "cmd:all()"
    help_category = "Character Generation"
    switches = ["skill", "knack", "advantage", "trait", "sorcery", "swordsman"]

    def func(self):
        if not self.switches:
            self.caller.msg("You must specify a switch. Use 'help buy' for more information.")
            return

        switch = self.switches[0]

        if switch == "skill":
            self.buy_skill(self.args)
        elif switch == "knack":
            parts = shlex.split(self.args)
            if len(parts) < 3:
                self.caller.msg("Usage: buy/knack <category> <skill> <knack> [<value>]")
                return
            category, skill, knack = parts[:3]
            value = int(parts[3]) if len(parts) > 3 else None
            self.buy_knack(f"{category} {skill} {knack}", value)
        elif switch == "advantage":
            self.buy_advantage(self.args)
        elif switch == "trait":
            parts = self.args.split()
            if len(parts) != 2:
                self.caller.msg("Usage: buy/trait <trait> <value>")
                return
            trait, value = parts
            self.buy_trait(trait, int(value))
        elif switch == "sorcery":
            parts = shlex.split(self.args)
            if len(parts) < 2:
                self.caller.msg("Usage: buy/sorcery <sorcery_type> <knack> [<value>]")
                return
            sorcery_type = " ".join(parts[:-1])
            knack = parts[-1]
            value = int(parts[-1]) if len(parts) > 2 and parts[-1].isdigit() else None
            self.buy_sorcery(f"{sorcery_type} {knack}", value)
        elif switch == "swordsman":
            parts = self.args.split()
            knack = " ".join(parts[:-1]) if len(parts) > 1 else parts[0]
            value = int(parts[-1]) if len(parts) > 1 and parts[-1].isdigit() else None
            self.buy_swordsman(knack, value)

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
        skill_name = " ".join(parts[1:]).title()  # Use title() instead of capitalize()

        if category not in PACKAGES:
            caller.msg(f"Unknown category: {category}")
            return

        # Find the skill case-insensitively
        matching_skill = next((s for s in PACKAGES[category] if s.lower() == skill_name.lower()), None)
        if not matching_skill:
            caller.msg(f"Unknown skill '{skill_name}' in category '{category}'")
            caller.msg(f"Available skills: {', '.join(PACKAGES[category].keys())}")
            return

        skill_name = matching_skill  # Use the correct casing from PACKAGES
        package = PACKAGES[category][skill_name]
        cost = package.get("cost", 0)
        xp_cost = cost * 2

        if self.convert_xp_to_hp(xp_cost):
            caller.msg(f"Purchasing {skill_name} package from {category} category:")

            # Get or create the Skill object
            skill, _ = Skill.objects.get_or_create(name=skill_name, category=category)

            for knack_name, value in package.get("knacks", {}).items():
                knack, _ = Knack.objects.get_or_create(name=knack_name, skill=skill)
                knack_value, _ = KnackValue.objects.get_or_create(character_sheet=sheet, knack=knack)

                current_value = knack_value.value
                new_value = max(current_value, value)
                max_value = 5

                if new_value > max_value:
                    caller.msg(f"Cannot increase {knack_name} beyond {max_value}. Capping at {max_value}.")
                    new_value = max_value

                knack_value.value = new_value
                knack_value.save()
                caller.msg(f" - Set {knack_name} to {new_value}")

            advanced = package.get("advanced")
            if advanced and isinstance(advanced, dict):
                for adv_knack_name, adv_value in advanced.items():
                    adv_knack, _ = Knack.objects.get_or_create(name=adv_knack_name, skill=skill)
                    adv_knack_value, created = KnackValue.objects.get_or_create(character_sheet=sheet, knack=adv_knack)

                    if created:
                        adv_knack_value.value = min(adv_value, max_value)
                        adv_knack_value.save()
                        caller.msg(f" - Added advanced knack {adv_knack_name} at {adv_knack_value.value}")
                    else:
                        caller.msg(f" - Advanced knack {adv_knack_name} already known")

            sheet.skills.add(skill)
            sheet.save()
            caller.msg(f"You have purchased the {skill_name} skill package. You have {sheet.hero_points} hero points and {sheet.xp} XP remaining.")
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

    def buy_sorcery(self, args):
        caller = self.caller
        sheet = CharacterSheet.objects.get(db_object=caller)

        if not sheet.is_sorcerer:
            caller.msg("You are not a sorcerer and cannot buy sorcery knacks.")
            return

        parts = args.split()
        if len(parts) < 2:
            caller.msg("Usage: buy/sorcery <knack> [value]")
            return

        knack = parts[0]
        value = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None

        sorcery_type = sheet.sorceries.first().name if sheet.sorceries.exists() else None
        if not sorcery_type:
            caller.msg("You don't have a sorcery type assigned.")
            return

        if sorcery_type not in SORCERIES or knack not in SORCERIES[sorcery_type]['knacks']:
            caller.msg(f"Unknown sorcery knack: {knack}")
            return

        current_value = sheet.get_sorcery_knack_value(knack)
        new_value = current_value + 1 if value is None else value

        if new_value > 5:
            caller.msg(f"You cannot increase sorcery knacks beyond 5.")
            return

        hp_cost = (new_value - current_value) * 3
        xp_cost = hp_cost * 2

        if self.convert_xp_to_hp(xp_cost):
            sheet.set_knack_value(knack, new_value)
            sheet.save()
            caller.msg(f"You have increased {knack} to {new_value}. You have {sheet.hero_points} hero points and {sheet.xp} XP remaining.")
        else:
            caller.msg(f"You don't have enough XP to increase this sorcery knack. You need {xp_cost} XP.")

    def buy_swordsman(self, args):
        caller = self.caller
        sheet = CharacterSheet.objects.get(db_object=caller)
        school = sheet.duelist_style

        if not school or school not in SWORDSMAN_SCHOOLS:
            caller.msg("You are not a member of any swordsman school.")
            return

        parts = args.split()
        if len(parts) < 1:
            caller.msg("Usage: buy/swordsman <knack> [value]")
            return

        knack_name = " ".join(parts[:-1]) if len(parts) > 1 else parts[0]
        value = int(parts[-1]) if len(parts) > 1 and parts[-1].isdigit() else None

        swordsman_school = SwordsmanSchool.objects.get(name=school)
        matching_knack = swordsman_school.knacks.filter(name__icontains=knack_name).first()

        if matching_knack:
            knack_value, created = KnackValue.objects.get_or_create(
                character_sheet=sheet,
                knack=matching_knack,
                defaults={'value': 0}
            )
            current_value = knack_value.value
            new_value = current_value + 1 if value is None else value

            max_value = 5
            if new_value > max_value:
                caller.msg(f"You cannot increase {matching_knack.name} beyond {max_value}.")
                return

            hp_cost = (new_value - current_value) * 4
            xp_cost = hp_cost * 2

            if self.convert_xp_to_hp(xp_cost):
                knack_value.value = new_value
                knack_value.save()
                caller.msg(f"You have increased {matching_knack.name} to {new_value}. You have {sheet.hero_points} hero points and {sheet.xp} XP remaining.")
            else:
                caller.msg(f"You don't have enough XP for this swordsman knack. You need {xp_cost} XP.")
        else:
            caller.msg(f"Unknown swordsman knack: {knack_name}")
    
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