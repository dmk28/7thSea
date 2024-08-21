from evennia import default_cmds
from evennia.utils import evtable
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
        args = self.args
        if args:
            # looking at something specific
            target = caller.search(args)
            if not target:
                return
        else:
            target = caller.location if caller.location else caller

        if isinstance(target, Character):  # Assuming you have a Character class
            self.show_character(target)
        else:
            # for all other objects, use the default look
            super().func()

    def show_character(self, character):
        """
        Display character information in a formatted table.
        """
        try:
            sheet = CharacterSheet.objects.get(db_object=character)
        except CharacterSheet.DoesNotExist:
            self.caller.msg("No character sheet found for {}.".format(character.name))
            return

        table = evtable.EvTable(border="table", width=78)
        
        # Header
        table.add_row("|W{}|n".format(character.name.capitalize()))
        
        # Physical attributes
        table.add_row(
            "Eye Color: |W{}|n".format(sheet.eye_color),
            "Hair Color: |W{}|n".format(sheet.hair_color)
        )
        table.add_row("Skin Hue: |c{}|n".format(sheet.skin_hue))
        
        # Description
        desc = character.db.description or "You see nothing special about them."
        table.add_row(desc)
        
       
        self.caller.msg(str(table)) 