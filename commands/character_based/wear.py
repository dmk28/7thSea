from evennia import Command, CmdSet
from evennia.utils.utils import inherits_from
from typeclasses.armor.armor_and_clothes import Armor, DracheneisenArmor

class CmdWear(Command):
    """
    Wear a piece of armor.

    Usage:
      wear <armor>

    This will wear the specified armor piece, updating your combat stats.
    """
    key = "wear"
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Wear what?")
            return

        armor_name = self.args.strip()
        armor = caller.search(armor_name, location=caller)
        if not armor:
            return  # caller.search() already sends an appropriate error message

        if not inherits_from(armor, Armor) and not inherits_from(armor, DracheneisenArmor):
            caller.msg("That's not a piece of armor.")
            return

        # Initialize equipped_armor if it doesn't exist
        if not hasattr(caller.db, 'equipped_armor'):
            caller.db.equipped_armor = {}

        # Check if the wear location exists and is not already occupied
        wear_location = getattr(armor.db, 'wear_location', None)
        if not wear_location:
            caller.msg(f"Error: {armor.name} doesn't have a valid wear location.")
            return

        if wear_location in caller.db.equipped_armor:
            caller.msg(f"You are already wearing armor on your {wear_location}.")
            return

        # Wear the new armor
        caller.db.equipped_armor[wear_location] = armor
        caller.msg(f"You wear {armor.name} on your {wear_location}.")

        # Update combat stats
        self.update_armor_stats(caller)


    def update_armor_stats(self, character):
        total_armor = sum(getattr(piece.db, 'armor', 0) for piece in character.db.equipped_armor.values())
        max_soak_keep = max((getattr(piece.db, 'soak_keep', 0) for piece in character.db.equipped_armor.values()), default=0)
        character.db.total_armor = total_armor
        character.db.armor_soak_keep = max_soak_keep
        character.msg(f"Your total armor is now {total_armor} and your armor soak keep is {max_soak_keep}.")
    
class CmdRemove(Command):
    """
    Remove a piece of worn armor.

    Usage:
      remove <armor>

    This will remove the specified armor piece, updating your combat stats.
    """
    key = "remove"
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Remove what?")
            return

        armor_name = self.args.strip()
        
        if not hasattr(caller.db, 'equipped_armor'):
            caller.db.equipped_armor = {}

        # Find the armor piece by name
        armor_to_remove = None
        for location, armor in caller.db.equipped_armor.items():
            if armor.name.lower() == armor_name.lower():
                armor_to_remove = armor
                break

        if not armor_to_remove:
            caller.msg(f"You are not wearing {armor_name}.")
            return

        # Remove the armor
        wear_location = getattr(armor_to_remove.db, 'wear_location', None)
        if wear_location:
            del caller.db.equipped_armor[wear_location]
            caller.msg(f"You remove {armor_to_remove.name} from your {wear_location}.")
        else:
            caller.msg(f"Error: {armor_to_remove.name} doesn't have a valid wear location.")

        # Update combat stats
        self.update_armor_stats(caller)

    def update_armor_stats(self, character):
        total_armor = sum(getattr(piece.db, 'armor', 0) for piece in character.db.equipped_armor.values())
        max_soak_keep = max((getattr(piece.db, 'soak_keep', 0) for piece in character.db.equipped_armor.values()), default=0)
        character.db.total_armor = total_armor
        character.db.armor_soak_keep = max_soak_keep
        character.msg(f"Your total armor is now {total_armor} and your armor soak keep is {max_soak_keep}.")


class WearCmdset(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdRemove())
        self.add(CmdWear())