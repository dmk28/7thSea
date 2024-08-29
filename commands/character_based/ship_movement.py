# in commands/ship_commands.py

from evennia import Command

class CmdSail(Command):
    key = "sail"
    locks = "cmd:all()"
    help_category = "Ship"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: sail <x> <y>")
            return

        try:
            x, y = map(int, self.args.split())
        except ValueError:
            self.caller.msg("Invalid coordinates. Use two numbers separated by a space.")
            return

        ship = self.caller.search(self.caller.location, quiet=True)
        if not ship or not inherits_from(ship, "typeclasses.ships.Ship"):
            self.caller.msg("You must be on a ship to sail.")
            return

        if ship.move_to_coordinates((x, y)):
            self.caller.msg(f"You've sailed to coordinates ({x}, {y}).")
        else:
            self.caller.msg("You cannot sail to those coordinates.")

class CmdBoard(Command):
    key = "board"
    locks = "cmd:all()"
    help_category = "Ship"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: board <ship name>")
            return

        ship = self.caller.search(self.args)
        if not ship or not inherits_from(ship, "typeclasses.ships.Ship"):
            return

        self.caller.move_to(ship)
        self.caller.msg(f"You board {ship.name}.")

class CmdDisembark(Command):
    key = "disembark"
    locks = "cmd:all()"
    help_category = "Ship"

    def func(self):
        ship = self.caller.location
        if not ship or not inherits_from(ship, "typeclasses.ships.Ship"):
            self.caller.msg("You are not on a ship.")
            return

        if not ship.location:
            self.caller.msg("The ship is not at a valid location.")
            return

        self.caller.move_to(ship.location)
        self.caller.msg(f"You disembark from {ship.name}.")