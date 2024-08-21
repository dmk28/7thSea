"""
Scripts

Scripts are powerful jacks-of-all-trades. They have no in-game
existence and can be used to represent persistent game systems in some
circumstances. Scripts can also have a time component that allows them
to "fire" regularly or a limited number of times.

There is generally no "tree" of Scripts inheriting from each other.
Rather, each script tends to inherit from the base Script class and
just overloads its hooks to have it perform its function.

"""
from evennia.utils.utils import delay
from evennia.scripts.scripts import DefaultScript
from evennia.accounts.models import AccountDB
from evennia.utils.search import search_object
from evennia.utils import create
from random import randint
from evennia import ScriptDB
from world.combat_script.combat_system import CombatScript
from world.character_sheet.models import CharacterSheet
from evennia.commands.default.system import CmdReload

class Script(DefaultScript):
    """
    This is the base TypeClass for all Scripts. Scripts describe
    all entities/systems without a physical existence in the game world
    that require database storage (like an economic system or
    combat tracker). They
    can also have a timer/ticker component.

    A script type is customized by redefining some or all of its hook
    methods and variables.

    * available properties (check docs for full listing, this could be
      outdated).

     key (string) - name of object
     name (string)- same as key
     aliases (list of strings) - aliases to the object. Will be saved
              to database as AliasDB entries but returned as strings.
     dbref (int, read-only) - unique #id-number. Also "id" can be used.
     date_created (string) - time stamp of object creation
     permissions (list of strings) - list of permission strings

     desc (string)      - optional description of script, shown in listings
     obj (Object)       - optional object that this script is connected to
                          and acts on (set automatically by obj.scripts.add())
     interval (int)     - how often script should run, in seconds. <0 turns
                          off ticker
     start_delay (bool) - if the script should start repeating right away or
                          wait self.interval seconds
     repeats (int)      - how many times the script should repeat before
                          stopping. 0 means infinite repeats
     persistent (bool)  - if script should survive a server shutdown or not
     is_active (bool)   - if script is currently running

    * Handlers

     locks - lock-handler: use locks.add() to add new lock strings
     db - attribute-handler: store/retrieve database attributes on this
                        self.db.myattr=val, val=self.db.myattr
     ndb - non-persistent attribute handler: same as db but does not
                        create a database entry when storing data

    * Helper methods

     create(key, **kwargs)
     start() - start script (this usually happens automatically at creation
               and obj.script.add() etc)
     stop()  - stop script, and delete it
     pause() - put the script on hold, until unpause() is called. If script
               is persistent, the pause state will survive a shutdown.
     unpause() - restart a previously paused script. The script will continue
                 from the paused timer (but at_start() will be called).
     time_until_next_repeat() - if a timed script (interval>0), returns time
                 until next tick

    * Hook methods (should also include self as the first argument):

     at_script_creation() - called only once, when an object of this
                            class is first created.
     is_valid() - is called to check if the script is valid to be running
                  at the current time. If is_valid() returns False, the running
                  script is stopped and removed from the game. You can use this
                  to check state changes (i.e. an script tracking some combat
                  stats at regular intervals is only valid to run while there is
                  actual combat going on).
      at_start() - Called every time the script is started, which for persistent
                  scripts is at least once every server start. Note that this is
                  unaffected by self.delay_start, which only delays the first
                  call to at_repeat().
      at_repeat() - Called every self.interval seconds. It will be called
                  immediately upon launch unless self.delay_start is True, which
                  will delay the first call of this method by self.interval
                  seconds. If self.interval==0, this method will never
                  be called.
      at_pause()
      at_stop() - Called as the script object is stopped and is about to be
                  removed from the game, e.g. because is_valid() returned False.
      at_script_delete()
      at_server_reload() - Called when server reloads. Can be used to
                  save temporary variables you want should survive a reload.
      at_server_shutdown() - called at a full server shutdown.
      at_server_start()

    """

    pass

class ChargenScript(Script):
    def at_script_creation(self):
        self.key = "chargen_script"
        self.desc = "Handles character generation process."
        self.persistent = True

    def at_start(self):
        self.obj.cmdset.add(CharGenCmdSet, permanent=True)

    def at_stop(self):
        self.obj.cmdset.remove(CharGenCmdSet)


class WeeklyXPAward(Script):
    def at_script_creation(self):
        self.key = "weekly_xp_award"
        self.desc = "Awards XP weekly and converts it to HP"
        self.interval = 7 * 24 * 60 * 60  # 7 days in seconds
        self.persistent = True
        self.repeats = 0

    def at_repeat(self):
        for account in AccountDB.objects.filter(is_active=True):
            if account.character:
                self.award_xp(account.character)

    def award_xp(self, character):
        if not hasattr(character.db, 'xp'):
            character.db.xp = 0
        
        character.db.xp += 4  # Award 4 XP
        
        if not hasattr(character.db, 'hero_points'):
            character.db.hero_points = 0
        
        hp_gain = character.db.xp // 2  # Convert XP to HP (2 XP = 1 HP)
        character.db.hero_points += hp_gain
        character.db.xp %= 2  # Keep remaining XP

        character.msg(f"You've been awarded 4 XP, converted to {hp_gain} HP. "
                      f"You now have {character.db.hero_points} HP and {character.db.xp} XP.")



class UpdateSheetsScript(DefaultScript):
    """A script to periodically run the update_sheets command."""

    def at_script_creation(self):
        self.key = "update_sheets_script"
        self.desc = "Runs the update_sheets command every minute"
        self.interval = 10  # Run every 10 seconds
        self.persistent = True

    def at_repeat(self):
        # This simulates running the update_sheets command
        from evennia.commands.default.system import SystemCmdSet
        from evennia.utils import create
        
        # Create a temporary object to hold the command
        temp_obj = create.create_object("evennia.objects.objects.DefaultObject")
        temp_obj.cmdset.add(SystemCmdSet, persistent=False)
        
        # Find the update_sheets command
        update_cmd = temp_obj.search_cmd("update_sheets")
        if update_cmd:
            update_cmd.obj = temp_obj  # Set the object for the command
            update_cmd.caller = temp_obj  # Set the caller for the command
            update_cmd()  # Execute the command
        else:
            print("update_sheets command not found")
        
        # Clean up the temporary object
        temp_obj.delete()
        
        print("update_sheets command executed")


class Combat(CombatScript):

    '''Here is where the combat script gets loaded.
    '''

    pass


# class UpdateCharacterSheets(DefaultScript):
#     def at_script_creation(self):
#         self.key = "update_character_sheets"
#         self.desc = "Updates all character sheets"
#         self.interval = 3600  # Run every hour, adjust as needed
#         self.persistent = True

#     def at_repeat(self):
#         try:
#             call_command('update_character_sheets')
#         except Exception as e:
#             print(f"Error running update_character_sheets command: {str(e)}")

#     def at_start(self):
#         delay(0, self.at_repeat)  # Run immediately when started