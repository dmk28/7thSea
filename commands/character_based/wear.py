from evennia import Command, CmdSet
from evennia.utils.utils import inherits_from
from evennia.commands.default.muxcommand import MuxCommand
from typeclasses.objects import Armor
from evennia.utils.evmenu import EvMenu
from evennia.utils.dbserialize import _SaverList

class CmdWear(MuxCommand):
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
    switches = ["examine"]

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
        wear_locations = item.db.wear_location
        if wear_locations:
            if isinstance(wear_locations, (list, _SaverList)):
                self.caller.msg(f"|cWear Location(s):|n {', '.join(map(str, wear_locations))}")
            else:
                self.caller.msg(f"|cWear Location:|n {wear_locations}")
        else:
            self.caller.msg("|cWear Location:|n Not specified")

    def wear_item(self):
        item = self.caller.search(self.args, location=self.caller)
        if not item:
            return

        if not isinstance(item, Armor):
            self.caller.msg("That's not a piece of armor or clothing.")
            return

        wear_locations = item.db.wear_location
        if not wear_locations:
            self.caller.msg(f"Error: {item.name} doesn't have a valid wear location.")
            return

        if isinstance(wear_locations, (list, _SaverList)) and len(wear_locations) > 1:
            # If the item can be worn in multiple locations, start a menu to choose
            self.caller.ndb._wear_choice = item
            EvMenu(self.caller, "commands.wear", "wear_location_menu",
                   item=item, wear_locations=wear_locations)
        else:
            # If it's a single location (either a string or a list with one item), wear it there
            location = wear_locations[0] if isinstance(wear_locations, (list, _SaverList)) else wear_locations
            self.do_wear(item, location)

    def do_wear(self, item, location):
        caller = self.caller
        if not hasattr(caller.db, 'equipped_armor'):
            caller.db.equipped_armor = {}

        # Convert location to a string representation if it's a list or _SaverList
        location_key = ','.join(map(str, location)) if isinstance(location, (list, _SaverList)) else str(location)

        if location_key in caller.db.equipped_armor:
            caller.msg(f"You are already wearing something on your {location}.")
            return

        if item.wear(caller):
            caller.db.equipped_armor[location_key] = item
            caller.calculate_total_armor()
            caller.msg(f"You wear {item.name} on your {location}.")
            caller.location.msg_contents(f"{caller.name} wears {item.name} on their {location}.", exclude=caller)
        else:
            caller.msg(f"You can't wear {item.name}.")






class CmdRemove(MuxCommand):
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
        for location_key, item in caller.db.equipped_armor.items():
            if item.name.lower() == item_name:
                if item.remove():
                    del caller.db.equipped_armor[location_key]
                    caller.calculate_total_armor()
                    
                    # Convert the location_key back to a more readable format
                    location_display = location_key.split(',') if ',' in location_key else location_key
                    if isinstance(location_display, list) and len(location_display) == 1:
                        location_display = location_display[0]
                    
                    caller.msg(f"You remove {item.name} from your {location_display}.")
                    caller.location.msg_contents(f"{caller.name} removes {item.name} from their {location_display}.", exclude=caller)
                else:
                    caller.msg(f"You can't remove {item.name}.")
                return

        caller.msg(f"You're not wearing {item_name}.")

def wear_location_menu(caller, raw_string, **kwargs):
    item = kwargs.get("item")
    wear_locations = kwargs.get("wear_locations")

    if not item or not wear_locations:
        return "exit"

    text = f"Where do you want to wear {item.name}?\n"
    options = []

    for i, location in enumerate(wear_locations, 1):
        text += f"{i}. {location}\n"
        options.append({"key": str(i), "desc": location, "goto": "do_wear_from_menu"})

    options.append({"key": "q", "desc": "Quit", "goto": "exit"})

    return text, options

def do_wear_from_menu(caller, raw_string, **kwargs):
    item = kwargs.get("item")
    wear_locations = kwargs.get("wear_locations")

    try:
        choice = int(raw_string) - 1
        location = wear_locations[choice]
    except (ValueError, IndexError):
        caller.msg("Invalid choice.")
        return "wear_location_menu"

    CmdWear.do_wear(CmdWear(), item, location)
    return "exit"


class WearCmdset(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdWear())
        self.add(CmdRemove())