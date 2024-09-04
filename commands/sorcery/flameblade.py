from evennia import Command
from evennia import create_script
from evennia import search_script
from django.db import transaction

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
    Deactivate the Flameblade sorcery effect on your weapon.

    Usage:
      extinguish_flameblade

    This will remove the Flameblade effect from your currently wielded weapon,
    returning it to its normal state and stopping all associated Flameblade scripts.
    """
    key = "extinguish_flameblade"
    aliases = ["extinguish"]
    locks = "cmd:all()"
    help_category = "Sorcery"

    def func(self):
        caller = self.caller

        if not caller.db.wielded_weapon:
            caller.msg("You're not wielding any weapon.")
            return

        weapon = caller.db.wielded_weapon

        # Search for all FlamebladeEffect scripts associated with the caller
        flameblade_scripts = search_script("flameblade_effect", obj=caller)

        if not flameblade_scripts:
            caller.msg("You don't have any active Flameblade effects.")
            return

        # Remove 'flameblade' from special_effects
        sheet = caller.character_sheet
        special_effects = sheet.special_effects or []
        if 'flameblade' in special_effects:
            special_effects.remove('flameblade')
            sheet.special_effects = special_effects
            sheet.save(update_fields=['special_effects'])

        # Reset weapon damage bonus
        weapon.db.damage_bonus = 0

        # Stop all FlamebladeEffect scripts
        for script in flameblade_scripts:
            script.stop()

        caller.msg("The magical flames on your weapon flicker and die out.")
        caller.location.msg_contents(f"The magical flames on {caller.name}'s weapon flicker and die out.", exclude=caller)

        # Clear the flameblade_active flag on the weapon
        weapon.db.flameblade_active = False