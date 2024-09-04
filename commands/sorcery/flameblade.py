from evennia import Command
from evennia import create_script
from evennia import search_script
from django.db import transaction
from evennia.utils.utils import inherits_from
class CmdFlameblade(Command):
    """
    Activate the Flameblade sorcery effect on your weapon.
    Usage:
      flameblade
    This will enhance your currently wielded weapon with the Flameblade effect,
    multiplying its flat damage bonus by your Flameblade knack rank x 2.
    It inflicts 6 Flesh Wounds minus your rank in the Feed knack.
    """
    key = "flameblade"
    locks = "cmd:all()"
    help_category = "Sorcery"

    def func(self):
        caller = self.caller
        if not caller.db.wielded_weapon:
            caller.msg("You must be wielding a weapon to use Flameblade.")
            return
        if not caller.db.is_sorcerer or "El Fuego Adentro" not in caller.db.sorcery.get('name', ''):
            caller.msg("You don't know how to use Flameblade.")
            return
        flameblade_rank = caller.db.sorcery_knacks.get('Flameblade', 0)
        feed_rank = caller.db.sorcery_knacks.get('Feed', 0)
        if flameblade_rank == 0:
            caller.msg("You haven't learned the Flameblade knack yet.")
            return
        flesh_wound_cost = max(6 - feed_rank, 1)  # Minimum cost of 1 Flesh Wound

        with transaction.atomic():
            # Update the CharacterSheet
            sheet = caller.character_sheet
            sheet.flesh_wounds += flesh_wound_cost
            
            # Add 'flameblade' to special_effects
            special_effects = sheet.special_effects or []
            if 'flameblade' not in special_effects:
                special_effects.append('flameblade')
                sheet.special_effects = special_effects
            
            # Check if this causes a Dramatic Wound
            while sheet.flesh_wounds >= sheet.resolve * 5:
                dramatic_wounds = sheet.flesh_wounds // (sheet.resolve * 5)
                sheet.dramatic_wounds += dramatic_wounds
                sheet.flesh_wounds %= (sheet.resolve * 5)
                caller.msg(f"You've taken {dramatic_wounds} Dramatic Wound(s) from the strain!")

            # Save only the modified fields
            sheet.save(update_fields=['flesh_wounds', 'dramatic_wounds', 'special_effects'])

        # Create and start the Flameblade effect script
        script = create_script(
            "typeclasses.sorcery_scripts.flameblade.FlamebladeEffect",
            obj=caller.db.wielded_weapon,
            attributes=[
                ("flameblade_rank", flameblade_rank)
            ]
        )
        caller.msg(f"Your weapon bursts into magical flames as you endure {flesh_wound_cost} Flesh Wounds!")
        # Optionally, inform the room about the effect
        caller.location.msg_contents(f"{caller.name}'s weapon erupts in magical flames!", exclude=caller)



class CmdExtinguishFlameblade(Command):
    """
    Deactivate all Flameblade sorcery effects on your weapons and character.

    Usage:
      extinguish_flameblade

    This will remove all Flameblade effects, stopping associated scripts and
    resetting weapons to their normal state.
    """
    key = "extinguish_flameblade"
    aliases = ["extinguish"]
    locks = "cmd:all()"
    help_category = "Sorcery"

    def func(self):
        caller = self.caller

        # Search for all FlamebladeEffect scripts on the caller and their inventory
        flameblade_scripts = list(search_script("flameblade_effect", obj=caller))
        for item in caller.contents:
            flameblade_scripts.extend(list(search_script("flameblade_effect", obj=item)))

        if not flameblade_scripts:
            caller.msg("You don't have any active Flameblade effects.")
            return

        # Stop all found FlamebladeEffect scripts
        for script in flameblade_scripts:
            script.stop()

        # Clean up any lingering effects on weapons
        for item in caller.contents:
            if inherits_from(item, "typeclasses.weapons.Weapon"):
                if hasattr(item.db, 'flameblade_active'):
                    item.db.flameblade_active = False
                if hasattr(item.db, 'damage_bonus'):
                    item.db.damage_bonus = 0
                if hasattr(item.db, 'original_damage'):
                    item.db.damage = item.db.original_damage
                    del item.db.original_damage
                if hasattr(item, 'weapon_model'):
                    item.weapon_model.damage_bonus = 0
                    item.weapon_model.flameblade_active = False
                    item.weapon_model.save(update_fields=['damage_bonus', 'flameblade_active'])

        # Remove 'flameblade' from special_effects on the character sheet
        if hasattr(caller, 'character_sheet'):
            sheet = caller.character_sheet
            special_effects = sheet.special_effects or []
            if 'flameblade' in special_effects:
                special_effects.remove('flameblade')
                sheet.special_effects = special_effects
                sheet.save(update_fields=['special_effects'])

        caller.msg("All Flameblade effects have been extinguished.")
        caller.location.msg_contents(f"The magical flames on {caller.name}'s weapons flicker and die out.", exclude=caller)