from evennia import Command, CmdSet
from evennia.utils.utils import inherits_from
from typeclasses.armor.armor_and_clothes import Armor, DracheneisenArmor
from evennia import Command
from typeclasses.objects import Armor

class CmdWear(Command):
    """
    Wear a piece of armor or clothing.

    Usage:
      wear <item>
      wear/examine <item>

    This will wear the specified item, adding its armor value to your total armor.
    Use 'wear/examine <item>' to see detailed information about the item before wearing it.
    """
    key = "wear"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Wear what?")
            return

        if "examine" in self.switches:
            self.examine_item()
        else:
            self.wear_item()

    def examine_item(self):
        item = self.caller.search(self.args, location=self.caller)
        if not item:
            return

        if not isinstance(item, Armor):
            self.caller.msg("That's not a piece of armor or clothing.")
            return

        # Display detailed information about the item
        self.caller.msg(f"|cItem:|n {item.name}")
        self.caller.msg(f"|cDescription:|n {item.db.desc}")
        if item.db.details:
            self.caller.msg(f"|cDetails:|n {item.db.details}")
        self.caller.msg(f"|cArmor Value:|n {item.db.armor}")
        self.caller.msg(f"|cSoak Keep:|n {item.db.soak_keep}")
        self.caller.msg(f"|cWear Location:|n {', '.join(item.db.wear_location) if isinstance(item.db.wear_location, list) else item.db.wear_location}")

    def wear_item(self):
        if not location and isinstance(item.db.wear_location, list):
            location = item.db.wear_location[0]
        elif not location:
            location = item.db.wear_location

        if location in self.caller.db.worn_items:
            self.caller.msg(f"You are already wearing something on your {location}.")
            return False

        if item.wear(self.caller):
            self.caller.db.worn_items[location] = item
            self.caller.calc_total_armor()
            return True
        return False

class CmdRemove(Command):
    """
    Remove a worn piece of armor or clothing.

    Usage:
      remove <item>

    This will remove the specified worn item, subtracting its armor value from your total armor.
    """
    key = "remove"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Remove what?")
            return

        item_name = self.args.strip().lower()
        for location, item in caller.db.worn_items.items():
            if item.name.lower() == item_name:
                if item.remove():
                    del caller.db.worn_items[location]
                    caller.calc_total_armor()
                    caller.msg(f"You remove {item.name}.")
                    caller.location.msg_contents(f"{caller.name} removes {item.name}.", exclude=caller)
                else:
                    caller.msg(f"You can't remove {item.name}.")
                return

        caller.msg(f"You're not wearing {item_name}.")

# This is a new command to handle multi-location wear choices
class CmdWearChoice(Command):
    """
    Hidden command to handle wear location choices for multi-location items.
    """
    key = "wear_choice"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        item = caller.ndb._wear_choice
        if not item:
            caller.msg("Wear what?")
            return

        try:
            choice = int(self.args) - 1
            location = item.db.wear_location[choice]
        except (ValueError, IndexError):
            caller.msg("Invalid choice.")
            del caller.ndb._wear_choice
            return

        if CmdWear.wear_item(self, item, location):
            caller.msg(f"You wear {item.name} on your {location}.")
            caller.location.msg_contents(f"{caller.name} wears {item.name} on their {location}.", exclude=caller)
        else:
            caller.msg(f"You can't wear {item.name} on your {location}.")

        del caller.ndb._wear_choice


class WearCmdset(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdWear())
        self.add(CmdRemove())
        self.add(CmdWearChoice())
