# In typeclasses/scripts.py

from evennia import ScriptDB
from typeclasses.scripts import Script
from world.crafts.models import WeaponModel
class FlamebladeEffect(Script):
    def at_script_creation(self):
        self.key = "flameblade_effect"
        self.desc = "Enhances weapon damage with magical flames"
        self.interval = 600  # 10 minutes, adjust as needed
        self.persistent = False

    def at_start(self):
        """Apply the Flameblade effect."""
        weapon = self.obj
        if not weapon:
            self.stop()
            return
        
        flameblade_rank = self.attributes.get('flameblade_rank', 0)
        original_damage_bonus = weapon.db.damage_bonus 
        weapon.db.damage_bonus = flameblade_rank * 2

        original_damage = weapon.db.damage or 0
        original_keep_dice = weapon.db.keep_dice or 1
        weapon.db.original_damage = original_damage
        weapon.db.damage = original_damage
        weapon.db.keep_dice = original_keep_dice
        weapon.db.flameblade_active = True

    def at_repeat(self):
        """Check if the effect should still be active."""
        weapon = self.obj
        if not weapon or not weapon.db.flameblade_active:
            self.stop()

    def at_stop(self):
        """Remove the Flameblade effect."""
        weapon = self.obj
        if weapon and weapon.db.flameblade_active:
            weapon.weapon_model.damage_bonus = 0
            weapon.db.damage = weapon.db.original_damage
            weapon.db.damage_bonus = 0
            del weapon.db.original_damage
            weapon.db.flameblade_active = False
            weapon.weapon_model.flameblade_active = False
            weapon.weapon_model.save(update_fields=['damage_bonus', 'flameblade_active'])