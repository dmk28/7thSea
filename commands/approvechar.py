from evennia import Command
from evennia.utils.search import search_object
from typeclasses.characters import Character
from world.character_sheet.models import CharacterSheet

class CmdApproveCharacter(Command):
    """
    Approve a character for play.

    Usage:
      approve <character>

    Approves the specified character for play, completing their character creation process.
    """
    key = "approve"
    locks = "cmd:perm(Wizards)"
    help_category = "Admin"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: approve <character>")
            return

        character_name = self.args.strip()
        characters = search_object(character_name, typeclass=Character)
        if not characters:
            self.caller.msg(f"Could not find a character named '{character_name}'.")
            return

        character = characters[0]
        if character.db.approved:
            self.caller.msg(f"{character.name} is already approved.")
            return

        # Approve the character
        character.db.approved = True
        character.db.complete_chargen = True
        character.save()

        # Update the character sheet
        try:
            sheet = CharacterSheet.objects.get(db_object=character)
            sheet.approved = True
            sheet.save()
        except CharacterSheet.DoesNotExist:
            self.caller.msg(f"Warning: No character sheet found for {character.name}.")
            sheet = CharacterSheet.create_from_typeclass(character)
            sheet.approved = True
            sheet.save()

        # Move character to the starting room
        start_room = self.caller.search("Main Room", global_search=True)
        if start_room:
            character.move_to(start_room, quiet=True)
            self.caller.msg(f"Moved {character.name} to the starting room.")
        else:
            self.caller.msg("Could not find the starting room. Character remains in current location.")

        self.caller.msg(f"You have approved {character.name} for play.")
        character.msg("Your character has been approved! Welcome to the game!")

        # Remove any pending approval requests
        for script in character.scripts.all():
            if getattr(script, 'db', None) and script.db.get('request_type') == "Character Approval":
                script.stop()
                self.caller.msg(f"Removed approval request for {character.name}.")
                break
        else:
            self.caller.msg(f"No approval request found for {character.name}.")

        # Ensure all changes are saved
        character.save()
        sheet.save()