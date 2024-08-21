from evennia import DefaultScript
from evennia.utils import delay
from django.core.management import call_command

class UpdateCharacterSheets(DefaultScript):
    def at_script_creation(self):
        self.key = "update_character_sheets"
        self.desc = "Updates all character sheets"
        self.interval = 3600  # Run every hour, adjust as needed
        self.persistent = True

    def at_repeat(self):
        try:
            call_command('update_character_sheets')
        except Exception as e:
            print(f"Error running update_character_sheets command: {str(e)}")

    def at_start(self):
        delay(0, self.at_repeat)  # Run immediately when started