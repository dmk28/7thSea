from evennia import default_cmds
from textwrap import wrap
from world.character_sheet.models import CharacterSheet
from typeclasses.characters import Character

class CmdLook(default_cmds.CmdLook):
    """
    look at location or object
    Usage:
      look
      look <obj>
      look *<account>
    
    Observes your location or objects in your vicinity.
    """

    def func(self):
        """
        Handle the looking.
        """
        caller = self.caller
        args = self.args.strip()

        if not args:
            target = caller.location
        else:
            target = caller.search(args)
        
        if not target:
            return

        if isinstance(target, Character):
            self.show_character(target)
        else:
            # for all other objects, use the default look
            super().func()

    def show_character(self, character):
        """
        Display character information in a formatted string.
        """
        try:
            sheet = CharacterSheet.objects.get(db_object=character)
        except CharacterSheet.DoesNotExist:
            self.caller.msg(f"No character sheet found for {character.name}.")
            return

        width = 78  # Total width of the display

        # Header
        output = "+" + "-" * width + "+\n"
        output += f"|{character.name.capitalize():^{width}}|\n"
        output += "+" + "-" * width + "+\n"

        # Physical Attributes
        output += "| Physical Attributes:                                                         |\n"
        output += f"| Eye Color: |W{sheet.eye_color:<12}|n Hair Color: |W{sheet.hair_color:<12}|n Skin Hue: |W{sheet.skin_hue:<17}|n |\n"
        output += "+" + "-" * width + "+\n"

        # Description
        output += "| Description:                                                                 |\n"
        desc = character.db.description or "You see nothing special about them."
        wrapped_desc = wrap(desc, width - 4)  # -4 for the border characters and spaces
        for line in wrapped_desc:
            output += f"| {line:<{width-2}} |\n"

        output += "+" + "-" * width + "+\n"

        self.caller.msg(output)