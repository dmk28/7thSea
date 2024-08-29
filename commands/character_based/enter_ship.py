# in commands/ship_commands.py

from evennia import Command

class CmdEnterShip(Command):
    key = "enter"
    locks = "cmd:all()"
    help_category = "Ship"

    def func(self):
        if not self.args:
            self.caller.msg("Enter what?")
            return

        ship = self.caller.search(self.args)
        if not ship or not inherits_from(ship, "typeclasses.ships.Ship"):
            return

        self.caller.move_to(ship)
        # The ship's at_object_receive method will handle moving the player to the interior

class CmdExitShip(Command):
    key = "exit"
    aliases = ["leave"]
    locks = "cmd:all()"
    help_category = "Ship"

    def func(self):
        if not inherits_from(self.caller.location, "typeclasses.ships.ShipInterior"):
            self.caller.msg("You are not on a ship.")
            return

        ship = self.caller.location.db.ship
        if not ship:
            self.caller.msg("Error: Cannot find the ship object.")
            return

        self.caller.move_to(ship.location)
        # The ship's at_object_leave method will handle the messaging