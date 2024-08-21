
from evennia import Script

class PorteWalkEffect(Script):
    def at_script_creation(self):
        self.key = "porte_walk_effect"
        self.desc = "Increases passive defense using Porte Walk"
        self.interval = 3600 # 5 minutes, adjust as needed
        self.persistent = False

    def at_start(self):
        """Apply the Porte Walk effect."""
        character = self.obj
        if not character:
            self.stop()
            return
        
        walk_rank = self.attributes.get('walk_rank', 0)
        defense_increase = 5 * walk_rank
        
        # Store the original passive defense
        character.db.total_armor = defense_increase

        # Increase the passive defense
        character.db.special_effects += ['portewalk']
        character.db.porte_walk_active = True

        character.msg(f"Your passive defense has been increased by {defense_increase}.")

    def at_repeat(self):
        """Check if the effect should still be active."""
        character = self.obj
        if not character or not character.db.porte_walk_active:
            self.stop()

    def at_stop(self):
        """Remove the Porte Walk effect."""
        character = self.obj
        if character and character.db.porte_walk_active:
            # Restore the original passive defense
            character.db.special_effects.remove('portewalk')
            character.db.total_armor -= defense_increase
            character.db.porte_walk_active = False
            character.msg("The Porte Walk effect has worn off. Your passive defense has returned to normal.")