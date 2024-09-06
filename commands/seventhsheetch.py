from evennia import Command
from evennia.utils import evtable
from textwrap import wrap
from world.character_sheet.models import CharacterSheet, KnackValue

class CmdCharacterSheet(Command):
    """
    Display the character sheet for a 7th Sea character.
    Usage:
      sheet
    """
    key = "sheet"
    locks = "cmd:all()"
    help_category = 'Character'

    def func(self):
        try:
            sheet = CharacterSheet.objects.get(db_object=self.caller)
        except CharacterSheet.DoesNotExist:
            self.caller.msg("You don't have a character sheet. Use the 'chargen' command to create your character.")
            return

        if not sheet.approved:
            self.caller.msg("Your character hasn't been approved yet. Please wait for staff approval.")
            return

        width = 80

        def create_header(title):
            return f"|y{'═' * 3} {title.upper()} {'═' * (width - len(title) - 5)}|n"

        def create_section(title, content):
            table = evtable.EvTable(border="table", width=width)
            table.add_row(f"|c{title}|n")
            for item in content:
                table.add_row(item)
            return str(table)

        sheet_display = []

        # Header
        sheet_display.append(create_header("CHARACTER SHEET"))

        # Basic Information
        basic_info = [
            f"Name: |c{sheet.full_name}|n",
            f"Nationality: |c{sheet.nationality}|n",
            f"Hero Points: |c{sheet.hero_points}|n"
        ]
        sheet_display.append(create_section("BASIC INFORMATION", basic_info))

        # Traits
        traits = [f"{trait.capitalize()}: |c{getattr(sheet, trait)}|n" for trait in ['brawn', 'finesse', 'wits', 'resolve', 'panache']]
        sheet_display.append(create_section("TRAITS", traits))

        # Skills and Knacks
        skills_by_category = sheet.get_skills_by_category()
        for category in ["Civilian", "Martial", "Professional"]:
            skills = []
            for skill, knacks in skills_by_category.get(category, {}).items():
                skill_str = f"|c{skill}|n: " + ", ".join(f"{k} ({v})" for k, v in knacks.items())
                skills.append(skill_str)
            sheet_display.append(create_section(f"{category.upper()} SKILLS", skills))

        # Advantages
        advantages = [f"|c{adv.advantage.name}|n" for adv in sheet.character_advantages.all()]
        sheet_display.append(create_section("ADVANTAGES", advantages))

        # Sorcery
        if sheet.is_sorcerer:
            sorcery = sheet.sorceries.first()
            if sorcery:
                sorcery_knacks = KnackValue.objects.filter(character_sheet=sheet, knack__sorceries=sorcery)
                sorcery_info = [
                    f"Type: |c{sorcery.name}|n",
                    "Knacks: " + ", ".join(f"|c{kv.knack.name}|n ({kv.value})" for kv in sorcery_knacks)
                ]
            else:
                sorcery_info = ["Sorcerer, but no sorcery type set"]
        else:
            sorcery_info = ["Not a sorcerer"]
        sheet_display.append(create_section("SORCERY", sorcery_info))

        # Duelist
        if sheet.duelist_style:
            duelist_info = [f"Style: |c{sheet.duelist_style}|n"]
        else:
            duelist_info = ["Not a duelist"]
        sheet_display.append(create_section("DUELIST", duelist_info))

        # Send the sheet to the caller
        self.caller.msg("\n".join(sheet_display))

class CmdCombatSheet(Command):
    """
    Display the combat sheet for a 7th Sea character.
    Usage:
      combatsheet
    """
    key = "sheet/combat"
    aliases = ["@combatsheet", "+combatsheet"]
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        try:
            sheet = CharacterSheet.objects.get(db_object=self.caller)
        except CharacterSheet.DoesNotExist:
            self.caller.msg("You don't have a character sheet. Use the 'chargen' command to create your character.")
            return

        if not sheet.approved:
            self.caller.msg("Your character hasn't been approved yet. Please wait for staff approval.")
            return

        width = 80

        def format_section(title, content):
            lines = [f"│ {line:<{width-4}} │" for line in content]
            return [f"┌─{title:─<{width-4}}─┐"] + lines + [f"└{'─':{width-2}}┘"]

        combat_sheet = []

        # Basic Information
        combat_sheet.extend(format_section("Combat Information", [
            f"Name: {sheet.full_name}",
            f"Nationality: {sheet.nationality}",
            f"Dramatic Wounds: {sheet.dramatic_wounds}",
            f"Flesh Wounds: {sheet.flesh_wounds}"
        ]))

        # Wielded Weapon
        weapon = self.caller.db.wielded_weapon if hasattr(self.caller.db, 'wielded_weapon') else None
        if weapon:
            combat_sheet.extend(format_section("Wielded Weapon", [
                f"Weapon: {weapon.name}",
                f"Type: {weapon.db.weapon_type}",
                f"Damage: {weapon.db.damage}"
            ]))
        else:
            combat_sheet.extend(format_section("Wielded Weapon", ["No weapon wielded"]))

        # Combat Skills
        combat_skills = []
        skills_by_category = sheet.get_skills_by_category()
        if 'Martial' in skills_by_category:
            for skill, knacks in skills_by_category['Martial'].items():
                for knack, value in knacks.items():
                    if 'Attack' in knack or 'Parry' in knack:
                        combat_skills.append(f"{skill} {knack}: {value}")

        combat_sheet.extend(format_section("Combat Skills", combat_skills))

        # Active Defenses
        active_defenses = []
        if 'Martial' in skills_by_category:
            for skill, knacks in skills_by_category['Martial'].items():
                for knack, value in knacks.items():
                    if 'Parry' in knack or knack == '(Martial)' and skill == 'Footwork':
                        active_defenses.append(f"{skill} {knack}: {value}")

        combat_sheet.extend(format_section("Active Defenses", active_defenses))

        # Current Attack and Parry
        if weapon:
            attack_skill = weapon.db.attack_skill
            parry_skill = weapon.db.parry_skill
            attack_value = self.get_skill_value(sheet, 'Martial', attack_skill)
            parry_value = self.get_skill_value(sheet, 'Martial', parry_skill)
            finesse = sheet.finesse
            
            current_attack = f"{attack_skill}: {attack_value + finesse}k{finesse}"
            current_parry = f"{parry_skill}: {parry_value + finesse}k{finesse}"
        else:
            finesse = sheet.finesse
            footwork_value = self.get_skill_value(sheet, 'Martial', 'Footwork')
            current_attack = "Unarmed Attack"
            current_parry = f"Footwork: {footwork_value + finesse}k{finesse}"
        
        combat_sheet.extend(format_section("Current Attack/Parry", [current_attack, current_parry]))

        # Passive Defense
        if weapon:
            defense_knack = self.get_skill_value(sheet, 'Martial', weapon.db.parry_skill)
        else:
            defense_knack = self.get_skill_value(sheet, 'Martial', 'Footwork')
        passive_defense = 5 + (defense_knack * 5)
        
        combat_sheet.extend(format_section("Passive Defense", [f"Passive Defense: {passive_defense}"]))

        # Send the sheet to the caller
        self.caller.msg("\n".join(combat_sheet))

    def get_skill_value(self, sheet, category, skill_name):
        skills_by_category = sheet.get_skills_by_category()
        if category in skills_by_category:
            for skill, knacks in skills_by_category[category].items():
                if skill_name in knacks:
                    return knacks[skill_name]
                elif skill == skill_name and '(Martial)' in knacks:
                    return knacks['(Martial)']
        return 0