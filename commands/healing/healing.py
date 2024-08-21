from evennia import Command
from evennia.utils import delay
from evennia.utils.gametime import gametime
from evennia.utils.search import object_search
import random

class CmdFirstAid(Command):
    """
    Attempt to heal one Dramatic Wound using First Aid.

    Usage:
      firstaid <target>

    This command allows you to attempt to heal one Dramatic Wound on a target.
    It uses your Wits + First Aid skill against a target number of 
    20 + 5 for each Dramatic Wound on the target.
    This command has a cooldown of 8 hours between uses.
    """
    key = "firstaid"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: firstaid <target>")
            return

        target = caller.search(self.args)
        if not target:
            return

        # Check cooldown
        last_heal_time = caller.db.last_firstaid_time
        current_time = gametime()
        if last_heal_time and (current_time - last_heal_time) <  8 * 3600:
            time_left = 8 * 3600 - (current_time - last_heal_time)
            hours, remainder = divmod(time_left, 3600)
            minutes, _ = divmod(remainder, 60)
            caller.msg(f"You must wait {int(hours)} hours and {int(minutes)} minutes before you can use First Aid again.")
            return

        # Perform skill check
        wits = caller.db.traits.get('wits', 1)
        first_aid = caller.db.skills.get('Civilian', {}).get('Medicine', {}).get('First Aid', 0)
        roll = sum(sorted([random.randint(1, 10) for _ in range(wits + first_aid)], reverse=True)[:wits])
        
        target_dramatic_wounds = target.db.dramatic_wounds
        target_number = 20 + (5 * target_dramatic_wounds)

        if roll >= target_number:
            if target_dramatic_wounds > 0:
                target.db.dramatic_wounds -= 1
                caller.msg(f"Success! You've healed one Dramatic Wound on {target.name}.")
                target.msg(f"{caller.name} has successfully treated one of your Dramatic Wounds.")
            else:
                caller.msg(f"{target.name} has no Dramatic Wounds to heal.")
        else:
            caller.msg(f"Your attempt to heal {target.name} has failed.")

        # Set cooldown
        caller.db.last_firstaid_time = current_time
        caller.msg("You will be able to use First Aid again in 8 hours.")

class CmdSurgery(Command):
    """
    Attempt to heal Dramatic Wounds using Surgery.

    Usage:
      surgery <target>

    This command allows you to attempt to heal Dramatic Wounds on a target.
    It uses your Wits + Surgery skill against a target number of 
    20 + 5 for each Dramatic Wound on the target.
    On success, it heals 2 Dramatic Wounds.
    This command has a cooldown of 24 hours between uses.
    """
    key = "surgery"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: surgery <target>")
            return

        target = caller.search(self.args)
        if not target:
            return

        # Check cooldown
        last_surgery_time = caller.db.last_surgery_time
        current_time = gametime()
        if last_surgery_time and (current_time - last_surgery_time) < 24 * 3600:
            time_left = 24 * 3600 - (current_time - last_surgery_time)
            hours, remainder = divmod(time_left, 3600)
            minutes, _ = divmod(remainder, 60)
            caller.msg(f"You must wait {int(hours)} hours and {int(minutes)} minutes before you can perform Surgery again.")
            return

        # Perform skill check
        wits = caller.db.traits.get('wits', 1)
        surgery = caller.db.skills.get('Civilian', {}).get('Medicine', {}).get('Surgery', 0)
        roll = sum(sorted([random.randint(1, 10) for _ in range(wits + surgery)], reverse=True)[:wits])
        
        target_dramatic_wounds = target.db.dramatic_wounds
        target_number = 20 + (5 * target_dramatic_wounds)

        if roll >= target_number:
            if target_dramatic_wounds > 0:
                healed = min(2, target_dramatic_wounds)
                target.db.dramatic_wounds -= healed
                caller.msg(f"Success! You've healed {healed} Dramatic Wound(s) on {target.name}.")
                target.msg(f"{caller.name} has successfully treated {healed} of your Dramatic Wounds through surgery.")
            else:
                caller.msg(f"{target.name} has no Dramatic Wounds to heal.")
        else:
            caller.msg(f"Your attempt to perform surgery on {target.name} has failed.")

        # Set cooldown
        caller.db.last_surgery_time = current_time
        caller.msg("You will be able to perform Surgery again in 24 hours.")    