from evennia import Command
from world.shipbuilding.shipbuilding import build_ship
from world.shipbuilding.modifications import MODIFICATIONS
from evennia import default_cmds
from typeclasses.domain.ships import Ship
from world.character_sheet.models import CharacterSheet

from evennia import Command
from world.shipbuilding.shipbuilding import build_ship
from world.shipbuilding.modifications import MODIFICATIONS

class CmdBuildShip(Command):
    """
    Build a ship at the shipyard.

    Usage:
      shipbuild <ship_type>

    Available ship types: sloop, frigate, galleon, galleass, caravel
    """
    key = "shipbuild"
    help_category = "Shipyard"
    locks = "cmd:all()"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: shipbuild <ship_type>")
            return
        ship_type = self.args.strip().lower()
        
        new_ship = build_ship(self.caller, ship_type)
        if new_ship:
            self.caller.msg(f"Your new {ship_type} has been built and is now in your possession.")
        else:
            self.caller.msg("Ship building failed.")

class CmdModifyShip(Command):
    """
    Modify your ship with additional features.

    Usage:
      ship_modify <modification>

    Adds a modification to your ship if you can afford it.
    """
    key = "ship_modify"
    help_category = "Shipyard"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: ship_modify <modification>")
            return

        modification = self.args.strip().lower()
        
        # Get the character's ships
        ships = [obj for obj in self.caller.contents if isinstance(obj, Ship) and obj.captain == self.caller]

        if not ships:
            self.caller.msg("You don't have a ship to modify.")
            return

        ship = ships[0]  # Assume the player only has one ship for simplicity

        if modification in MODIFICATIONS['light']:
            mod_type = 'light'
        elif modification in MODIFICATIONS['medium']:
            mod_type = 'medium'
        elif modification in MODIFICATIONS['large']:
            mod_type = 'large'
        else:
            self.caller.msg(f"Unknown modification: {modification}")
            return

        cost = MODIFICATIONS[mod_type][modification]['cost']

        if self.caller.character_sheet.money_guilders >= cost:
            self.caller.character_sheet.money_guilders -= cost
            self.caller.character_sheet.save()
            ship.add_modification(modification)
            self.caller.msg(f"Added {modification} to your ship for {cost} guilders.")
        else:
            self.caller.msg("You don't have enough guilders for this modification.")