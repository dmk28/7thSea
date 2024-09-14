from evennia.objects.objects import DefaultCharacter
from .objects import ObjectParent
from evennia.utils import create, lazy_property
from world.combat_script.combat_system import get_combat
from typeclasses.weapons.unarmed_types import WEAPON_TYPES
HERO_POINTS_INITIAL = 120
from django.core.exceptions import ObjectDoesNotExist
from evennia.utils.dbserialize import _SaverDict, _SaverList   
from commands.character_based.ship_commands import ShipCmdSet

class Character(ObjectParent, DefaultCharacter):
    @lazy_property
    def character_sheet(self):
        return CharacterSheet.create_from_typeclass(self)

    def at_object_creation(self):
        super().at_object_creation()
        self.db.full_name = ""
        self.db.gender = ""
        self.db.hero_points = 0
        self.db.traits = {
            "brawn": 1, "finesse": 1, "wits": 1, "resolve": 1, "panache": 1,
        }
        self.db.skills = {
            'Martial': {}, 'Civilian': {}, 'Professional': {}, 'Artist': {}
        }
        self.db.flesh_wounds = 0
        self.db.dramatic_wounds = 0
        self.db.armor_soak_keep = 0
        self.db.nationality = ""
        self.db.is_sorcerer = False
        self.db.potential_sorcery = ""
        self.db.sorcery_knacks = {}
        self.db.complete_chargen = False
        self.db.xp = 0
        self.db.money = {"guilders": 0, "doubloons": 0}
        self.db.wielded_weapon = None
        self.db.current_attack_skill = "Attack (Unarmed)"
        self.db.current_parry_skill = "Footwork"
        self.db.trait_bonuses = {}
        self.db.sorte_magic_effects = {}
        self.db.duelist_style = ""
        self.db.approved = False
        self.db.unconscious = False
        self.db.equipped_armor = {}
        self.db.desc = self.db.description
        self.db.description = ""
        self.db.personality = ""
        self.db.biography = ""
        self.db.eye_color = ""
        self.db.hair_color = ""
        self.db.skin_hue = ""
        self.db.special_effects = []
        self.db.move_dice = 0
        self.db.total_armor = 0
        self.db.eisen_bought = False
        self.db.dracheneisen_slots = {}
        self.db.total_xp_accrued = 0
        self.db.create_character_sheet = True
        self.db.update_model_task = None

    def at_init(self):
        super().at_init()
        if self.db.create_character_sheet:
            # This will lazily create the character sheet if it doesn't exist
            _ = self.character_sheet
            self.db.create_character_sheet = False

    def at_hurt(self, damtype, value):
        self.msg(f"Debug: Entering at_hurt method. damtype: {damtype}, value: {value}")
        self.msg(f"Debug: Type of self.hurt_levels: {type(self.hurt_levels)}")
        
        if callable(self.hurt_levels):
            self.msg("Debug: hurt_levels is callable")
        else:
            self.msg(f"Debug: hurt_levels is not callable, it is: {self.hurt_levels}")

        match damtype:
            case "dramatic":
                self.character_sheet.hurt_character(value, "dramatic")
                self.msg(f"|500You've been hurt for {value} dramatic wound{'s' if value > 1 else ''}!|n")
            case "flesh":
                self.character_sheet.hurt_character(value, "flesh")
                self.msg(f"|412You take {value} flesh wound{'s' if value > 1 else ''}!|n")
            case _:
                self.msg(f"Unknown damage type: {damtype}")
        
        try:
            if callable(self.hurt_levels):
                hurt_level = self.hurt_levels()
                self.msg(f"You are {hurt_level}.")
            else:
                self.msg(f"Error: hurt_levels is not callable, current value: {self.hurt_levels}")
        except Exception as e:
            self.msg(f"Error when calling hurt_levels: {str(e)}")
            import traceback
            self.msg(f"Traceback: {traceback.format_exc()}")

        self.msg("Debug: Exiting at_hurt method")

    def get_advantages(self):
        """
        Get the character's advantages.
        """
        advantages = self.db.advantages or []
        
  
        
        if isinstance(advantages, (_SaverList, list)):
            valid_advantages = []
            
            for i, adv in enumerate(advantages):
             
                
                if isinstance(adv, (_SaverDict, dict)):
                    if 'name' in adv:
                        valid_advantages.append(dict(adv))
                    else:
                        self.msg(f"Debug: Advantage {i} does not have a 'name' key")
                else:
                    self.msg(f"Debug: Advantage {i} is not a dictionary or _SaverDict")
            
            if len(valid_advantages) == len(advantages):
                return valid_advantages
        else:
            self.msg(f"Debug: Advantages is neither a list nor a _SaverList")
        
        self.msg(f"Unexpected advantage structure: {advantages}")
        return []
            
        # If the structure is unexpected, log an error and return an empty list

    def get_advantage_names(self):
        """
        Get just the names of the character's advantages.
        """
        advantages = self.get_advantages()
        
        if isinstance(advantages, list) and all(isinstance(adv, dict) and 'name' in adv for adv in advantages):
            return [adv['name'] for adv in advantages]
        
        # If the structure is unexpected, log an error and return an empty list
        self.msg(f"Unexpected advantage structure: {advantages}")
        return []


    def get_swordsman_knacks(self):
        knacks = {}
        for school in self.character_sheet.swordsman_schools.all():
            school_knacks = {}
            for knack in school.knacks.all():
                knack_value = self.character_sheet.knack_values.filter(knack=knack).first()
                if knack_value:
                    school_knacks[knack.name] = knack_value.value
            if school_knacks:
                knacks[school.name] = school_knacks
        return knacks
    def get_attack_dice_pool(self, weapon=None):
        """
        Calculate the attack dice pool based on the character's skills and weapon.
        """
        weapon_type = weapon.db.weapon_type if weapon else "Unarmed"
        attack_skill = 0
        
        martial_skills = self.db.skills.get('Martial', {})
        for skill, knacks in martial_skills.items():
            if f'Attack ({weapon_type})' in knacks:
                attack_skill = knacks[f'Attack ({weapon_type})']
                break
        
        finesse = self.db.traits.get('finesse', 1)
        return attack_skill, finesse

    def get_defense_dice_pool(self, weapon=None):
        """
        Calculate the defense dice pool based on the character's skills and weapon.
        """
        weapon_type = weapon.db.weapon_type if weapon else "Unarmed"
        defense_skill = 0
        
        martial_skills = self.db.skills.get('Martial', {})
        if weapon:
            for skill, knacks in martial_skills.items():
                if f'Parry ({weapon_type})' in knacks:
                    defense_skill = knacks[f'Parry ({weapon_type})']
                    break
        else:
            footwork = max(
                martial_skills.get('Athletics', {}).get('Footwork', 0),
                martial_skills.get('Fencing', {}).get('Footwork', 0)
            )
            defense_skill = footwork
        
        wits = self.db.traits.get('wits', 1)
        return defense_skill, wits

    def get_swordsman_schools(self):
        return list(self.character_sheet.swordsman_schools.values_list('name', flat=True))

    def get_weapon_type(self):
        """
        Get the type of weapon the character is currently wielding.
        """
        weapon = self.db.wielded_weapon
        return weapon.db.weapon_type if weapon else "Unarmed"

    def calculate_passive_defense(self):
        """
        Calculate the character's passive defense based on weapon type and Defensive Knack.
        """
        weapon = self.db.wielded_weapon
        weapon_type = weapon.db.weapon_type if weapon else "Unarmed"
        martial_skills = self.db.skills.get('Martial', {})
        
        defensive_knack = 0
        
        if weapon_type == "Unarmed":
            defensive_knack = max(
                martial_skills.get('Athletics', {}).get('Footwork', 0),
                martial_skills.get('Pugilism', {}).get('Footwork', 0)
            )
        else:
            # Look for the appropriate Parry knack based on weapon type
            for skill, knacks in martial_skills.items():
                parry_knack = knacks.get(f'Parry ({weapon_type})', 0)
                if parry_knack > defensive_knack:
                    defensive_knack = parry_knack
        
        return 5 + (defensive_knack * 5)

    def check_knack(self, knack_name):
        """
        Check if the character has a specific knack.
        """
        martial_skills = self.db.skills.get('Martial', {})
        for skill, knacks in martial_skills.items():
            if knack_name.lower() in [k.lower() for k in knacks.keys()]:
                return True
        return False

    def at_attribute_change(self, key, value, *args, **kwargs):
        """Called when an attribute is changed."""
        super().at_attribute_change(key, value, *args, **kwargs)
        self.update_model()

    def update_sheet(self):
        """Update the character sheet."""
        from world.character_sheet.models import CharacterSheet
        sheet, created = CharacterSheet.objects.get_or_create(db_object=self)
        sheet.update_from_typeclass()


    def nationality_check(self, nationality):
        self.db.nationality = nationality
        if nationality == "Eisen":
            self.dracheneisen_check()
        self.update_model()
    def dracheneisen_check(self):
        if self.db.nationality == "Eisen":
            self.db.dracheneisen_slots = {}
            self.db.eisen_bought = False

    def equip_armor(self, armor):
        if armor.db.wear_location not in self.db.equipped_armor:
            self.db.equipped_armor[armor.db.wear_location] = armor
            self.msg(f"You equip {armor.name} on your {armor.db.wear_location}.")
            self.calculate_total_armor()
            self.update_model()
        else:
            self.msg(f"You are already wearing armor on your {armor.db.wear_location}")

    def unequip_armor(self, armor):
        if armor.db.wear_location in self.db.equipped_armor:
            del self.db.equipped_armor[armor.db.wear_location]
            self.msg(f"You remove {armor.name} from your {armor.db.wear_location}.")
            self.calculate_total_armor()
            self.update_model()
        else:
            self.msg(f"You are not wearing {armor.name}.")

    def calculate_total_armor(self):
        total_armor = sum(piece.db.armor for piece in self.db.equipped_armor.values())
        max_soak_keep = max((piece.db.soak_keep for piece in self.db.equipped_armor.values()), default=0)
        self.db.armor = total_armor
        self.db.armor_soak_keep = max_soak_keep
        
    def calculate_soak(self):
        # Ensure equipped_armor exists
        if not hasattr(self.db, 'equipped_armor'):
            self.db.equipped_armor = {}

        # Calculate total_armor if it doesn't exist
        if not hasattr(self.db, 'total_armor'):
            self.db.total_armor = sum(getattr(armor, 'db', {}).get('armor', 0) for armor in self.db.equipped_armor.values())

        # Ensure armor_soak_keep exists
        if not hasattr(self.db, 'armor_soak_keep'):
            self.db.armor_soak_keep = max((getattr(armor, 'db', {}).get('soak_keep', 0) for armor in self.db.equipped_armor.values()), default=0)

        resolve = self.db.traits.get('resolve', 1)
        armor_value = self.db.total_armor
        armor_soak_keep = self.db.armor_soak_keep

        # Debug output
        print(f"Debug: calculate_soak for {self.name}")
        print(f"Debug: Resolve: {resolve}, Armor Value: {armor_value}, Armor Soak Keep: {armor_soak_keep}")

        return resolve + armor_value, max(resolve, armor_soak_keep)


    def at_hurt(self, damtype, value):
        match damtype:
            case "dramatic":
                self.character_sheet.hurt_character(value, "dramatic")
                self.msg(f"|500You've been hurt for {value} dramatic wound{'s' if value > 1 else ''}!|n")
                self.msg(f"You are {self.hurt_levels()}.")
            case "flesh":
                self.character_sheet.hurt_character(value, "flesh")
                self.msg(f"|412You take {value} flesh wound{'s' if value > 1 else ''}!|n")
                self.msg(f"You are {self.hurt_levels()}.")
            case _:
                pass  # Handle unexpected damage types if needed
        

    def get_personality(self):
        return self.db.personality

    def get_biography(self):
        return self.db.biography


        

    def enter_combat(self):
        self.cmdset.add(CombatCmdSet, persistent=False)

    def exit_combat(self):
        self.cmdset.delete(CombatCmdSet)
    def at_input(self, message, **kwargs):
        combat = get_combat(self)
        if combat and combat.db.current_actor == self:
            combat.handle_action_input(self, message)
            return True
        return False

    def get_money(self):
        if not self.db.money:
            self.db.money = {}
        return self.db.money.get(currency, 0)
        
    def add_money(self, currency, amount):
        if not self.db.money:
            self.db.money = {}
        self.db.money[currency] = self.db.money.get(currency, 0) + amount
        self.character_sheet.save(update_fields=['money_guilders', 'money_doubloons'])

    def spend_money(self, currency, amount):
        if not self.db.money:
            return False
        current = self.db.money.get(currency, 0)
        if current >= amount:
            self.db.money[currency] = current - amount
            self.character_sheet.save(update_fields=['money_guilders', 'money_doubloons'])
            return True
        return False

    def at_desc(self, looker=None):
        """
        This is called when someone looks at the character.
        """
        return self.db.description

    def at_post_puppet(self):
        super().at_post_puppet()
        self.check_combat_status()

    def at_post_login(self):
        super().at_post_login()
        if self.approved == True:
            self.cmdset.add(ShipCmdSet())


    def check_combat_status(self):
        from commands.mycmdset import CombatCmdSet
        if hasattr(self.db, 'combat_id'):
            combat = get_combat(self)
            if combat:
                self.msg(f"Debug: You are in combat with ID {self.db.combat_id}")
                if not self.cmdset.has(CombatCmdSet):
                    self.cmdset.add(CombatCmdSet, persistent=False)
                    self.msg("Debug: Combat cmdset added.")
            else:
                self.msg(f"Debug: Combat with ID {self.db.combat_id} not found. Removing combat_id attribute.")
                del self.db.combat_id
        else:
            self.msg("Debug: You are not in combat.")
    def get_pugilism_skill(self):
        return self.db.skills.get('Martial', {}).get('Pugilism', {}).get('Attack (Pugilism)', 0)
    def has_pugilism(self):
        return self.get_pugilism_skill() > 0
    

    def get_dirty_fighting_skill(self):
        return self.db.skills.get('Martial', {}).get('Dirty Fighting', {}).get('Attack (Dirty Fighting)', 0)

    def has_dirty_fighting(self):
        return self.get_dirty_fighting_skill() > 0

    def set_armor(self, value):
        """Set the character's armor value."""
        self.db.total_armor = max(0, int(value))  # Ensure it's a non-negative integer
        self.update_model()

    def is_approved(self):
        """Check if the character is approved."""
        return self.db.approved


    def get_armor(self):
        """Get the character's armor value."""
        return getattr(self.db, 'armor', 0)  # Default to 0 if not set

    def at_death(self):
        self.location.msg_contents(f"|500$You() $conj(die)!|n", from_obj=self)
        self.character_sheet.approved = False
        self.character_sheet.save(update_fields=["approved"])
        
        # If the character is in combat, remove them
        combat = self.ndb.combat
        if combat:
            combat.remove_participant(self)

        # Reset any combat-related attributes
        self.db.wielded_weapon = None
        self.db.current_attack_skill = "Attack (Unarmed)"
        self.db.current_parry_skill = "Footwork"

    def at_first_login(self):
        super().at_first_login()
        chargen_room = create.create_object("typeclasses.rooms.ChargenRoom", key="Chargen Room")
        self.move_to(chargen_room, quiet=True)
        self.msg("Welcome to the character generation process. Type 'chargen' to begin.")

    def has_completed_chargen(self):
        return self.db.complete_chargen

    def complete_chargen(self):
        self.db.complete_chargen = True

    

    def get_character_sheet(self):
        """
        Returns a string representation of the character sheet.
        """
        sheet = f"Name: {self.key}\n"
        
        # Traits
        if hasattr(self.db, 'traits'):
            sheet += "Traits:\n"
            for trait, value in self.db.traits.items():
                sheet += f"{trait.capitalize()}: {value}\n"
        else:
            sheet += "Traits: Not set\n"

        # Skills
        sheet += "\nSkills:\n"
        if hasattr(self.db, 'skills') and self.db.skills:
            for category, skills in self.db.skills.items():
                sheet += f"{category}:\n"
                for skill, knacks in skills.items():
                    sheet += f"  {skill}:\n"
                    for knack, rank in knacks.items():
                        sheet += f"    {knack}: {rank}\n"
        else:
            sheet += " No skills yet.\n"

        # Perks (Advantages)
        sheet += "\nAdvantages:\n"
        if hasattr(self.db, 'advantages') and self.db.advantages:
            for advantage in self.db.advantages:
                sheet += f" {advantage}\n"
        else:
            sheet += " No perks yet.\n"

        # Hero Points
        if hasattr(self.db, 'hero_points'):
            sheet += f"\nHero Points: {self.db.hero_points}\n"
        else:
            sheet += "\nHero Points: Not set\n"

        # Dramatic Wounds
        if hasattr(self.db, 'dramatic_wounds'):
            sheet += f"Dramatic Wounds: {self.db.dramatic_wounds}\n"
        else:
            sheet += "Dramatic Wounds: Not set\n"

        # Nationality
        if hasattr(self.db, 'nationality'):
            sheet += f"Nationality: {self.db.nationality}\n"
        else:
            sheet += "Nationality: Not set\n"

        # Sorcery
        if hasattr(self.db, 'is_sorcerer'):
            if self.db.is_sorcerer:
                sheet += f"Sorcery: {self.db.potential_sorcery}\n"
            else:
                sheet += "Sorcery: Not a sorcerer\n"
        else:
            sheet += "Sorcery: Not determined\n"

        return sheet
    
    
    def get_combat_stats(self):
        '''Gets weapon's current combat stats'''
        stats = super().get_combat_stats()    
        if self.has_dirty_fighting():
            stats['dirty_fighting'] = {
                
                "attack_skill": "Attack (Dirty Fighting)",
                "damage": WEAPON_TYPES["Dirty Fighting"]["damage"],
                "keep": WEAPON_TYPES["Dirty Fighting"]["keep"],
            
            }
        elif self.has_pugilism():
            stats['pugilism'] =  {
                "attack_skill": "Attack (Pugilism)",
                "damage": WEAPON_TYPES["Pugilism"]["damage"],
                "keep": WEAPON_TYPES["Pugilism"]["keep"]
            }

            
        weapon = self.db.wielded_weapon
        attack_skill = self.db.current_attack_skill
        parry_skill = self.db.current_parry_skill
        damage = weapon.db.damage if weapon else 0
        return  {
            "weapon": weapon.name if weapon else "Unarmed",
            "attack_skill": attack_skill,
            "parry_skill": parry_skill,
            "damage": damage,
            

        }

    def equip_armor(self):
        if isinstance(armor, Armor):
            self.db.equipped_armor = armor
            self.msg(f"You have equipped {armor.name}")
        else:
            self.msg("That is not a valid piece of armor.")
    def unequip_armor(self):
        if self.db.equipped_armor:
            armor = self.db.equipped_armor
            self.db.equipped_armor = None
            self.msg(f"You've unequipped {armor}")

    def get_armor_value(self):
        if self.db.equipped_armor:
            return self.db.equipped_armor.db.armor
        return 0

    def get_armor_soak_keep(self):
        if self.db.equipped_armor:
            return self.db.equipped_armor.db.soak_keep
        return 1
    

            
    def ensure_combat_attributes(self):
        """
        Check for necessary combat attributes and initialize them if missing.
        This method should be called before combat calculations.
        """
        if not hasattr(self.db, 'equipped_armor'):
            self.db.equipped_armor = {}
        
        if not hasattr(self.db, 'total_armor'):
            self.db.total_armor = sum(getattr(armor, 'db', {}).get('armor', 0) for armor in self.db.equipped_armor.values())
        
        if not hasattr(self.db, 'armor_soak_keep'):
            self.db.armor_soak_keep = max((getattr(armor, 'db', {}).get('soak_keep', 0) for armor in self.db.equipped_armor.values()), default=0)
        
        if not hasattr(self.db, 'flesh_wounds'):
            self.db.flesh_wounds = 0
        
        if not hasattr(self.db, 'dramatic_wounds'):
            self.db.dramatic_wounds = 0
        
        if not hasattr(self.db, 'special_effects'):
            self.db.special_effects = []

        # Ensure all necessary traits are initialized
        for trait in ['brawn', 'finesse', 'wits', 'resolve', 'panache']:
            if trait not in self.db.traits:
                self.db.traits[trait] = 1

        print(f"Debug: Combat attributes ensured for {self.name}")
        print(f"Debug: Total Armor: {self.db.total_armor}, Armor Soak Keep: {self.db.armor_soak_keep}")


    @property
    def character_sheet(self):
        from world.character_sheet.models import CharacterSheet
        try:
            return CharacterSheet.create_from_typeclass(self)
        except ObjectDoesNotExist:
            return CharacterSheet.create_from_typeclass(self)

   
    def update_model(self):
        self.character_sheet.create_from_typeclass(self)


    def _do_update_model(self):
        try:
            sheet = CharacterSheet.objects.get(db_object=self)
        except CharacterSheet.DoesNotExist:
            sheet = CharacterSheet.create_from_typeclass(self)
        sheet.update_from_typeclass()
        self.db.update_model_task = None

    def get_hurt_level(self):
        """
        Calculates and returns the character's current hurt level as a string.
        """
        try:
            dramatic_wounds = self.character_sheet.dramatic_wounds
            resolve = self.db.traits.get('resolve', 1)  # Default to 1 if not set
            death_threshold = resolve * 2 + 2

            hurt_levels = [
                (0, "|555Healthy|n"),
                (1, "|252Scratched|n"),
                (2, "|352Wounded|n"),
                (resolve // 2, "|320Hurt|n"),
                (resolve, "|400Badly Wounded|n"),
                (resolve + (resolve // 2), "|411Gravely Injured|n"),
                (death_threshold - 1, "|500Near Death|n"),
                (death_threshold, "|511Dead|n")
            ]

            for threshold, level in hurt_levels:
                if dramatic_wounds <= threshold:
                    return level

            return "|511Dead|n"  # If somehow above all thresholds
        except Exception as e:
            print(f"Error in get_hurt_level for {self.name}: {str(e)}")
            return "Error: Unable to determine hurt level"

    def hurt_levels(self):
        """
        Returns the character's current hurt level.
        This method ensures hurt_levels remains callable.
        """
        return self.get_hurt_level()
    # def msg(self, text=None, from_obj=None, session=None, **kwargs):
    #     """
    #     Emits something to a session attached to the object.
    #     Overloaded to include MUSH token conversion.
    #     """
    #     if text and isinstance(text, str):
    #         text = convert_mush_tokens(text)
    #     super().msg(text, from_obj=from_obj, session=session, **kwargs)

    def at_death(self):
        self.location.msg_contents(f"|500$You() $conj(die)!|n", from_obj=self)
        self.character_sheet.approved = False
        self.character_sheet.save(update_fields=["approved"])
        
        # If the character is in combat, remove them
        combat = self.ndb.combat
        if combat:
            combat.remove_participant(self)

        # Reset any combat-related attributes
        self.db.wielded_weapon = None
        self.db.current_attack_skill = "Attack (Unarmed)"
        self.db.current_parry_skill = "Footwork"

        # Remove the default cmdset and add the dead cmdset
        self.cmdset.delete("commands.default_cmdsets.CharacterCmdSet")
        self.cmdset.add(DeadCmdSet, permanent=True)

        # Move the character to the afterlife location
        afterlife = self.search("Afterlife", global_search=True)
        if afterlife:
            self.move_to(afterlife, quiet=True)
        else:
            self.msg("The afterlife seems to be missing. You remain where you are.")

        self.msg("You have died and entered the afterlife.")

    def resurrect(self):
        """
        Resurrect the character
        """
        # Remove the dead cmdset and add back the default cmdset
        self.cmdset.delete(DeadCmdSet)
        self.cmdset.add("commands.default_cmdsets.CharacterCmdSet", permanent=True)

        # Reset health attributes
        self.db.dramatic_wounds = 0
        self.db.flesh_wounds = 0

        # Move the character back to a starting location
        start_location = self.search("Main Room", global_search=True)
        if start_location:
            self.move_to(start_location, quiet=True)
        
        self.msg("You have been resurrected!")
        self.location.msg_contents(f"{self.name} has returned to life!", exclude=[self])