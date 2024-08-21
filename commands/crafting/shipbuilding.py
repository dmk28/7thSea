# commands/default_cmds.py
from evennia import Command
from world.shipbuilding.shipbuilding import build_ship
from world.shipbuilding.modifications import MODIFICATIONS


class CmdBuildShip(Command):
    """
    Build a ship at the shipyard.
    
    Usage:
      shipbuild <ship_type>
    
    Available ship types: sloop, frigate, galleon
    """
    key = "shipbuild"
    help_category = "Shipyard"
    locks = "cmd:all()"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: shipbuild <ship_type>")
            return
        ship_type = self.args.strip().lower()
        build_ship(self.caller, ship_type)

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
        ships = [obj for obj in self.caller.contents if isinstance(obj, Ship) and obj.db.owner == self.caller]
        
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
        
        if self.caller.db.money.get("guilders", 0) >= cost:
            self.caller.db.money["guilders"] -= cost
            ship.add_modification(modification, mod_type)
            self.caller.msg(f"Added {modification} to your ship for {cost} guilders.")
        else:
            self.caller.msg("You don't have enough guilders for this modification.")