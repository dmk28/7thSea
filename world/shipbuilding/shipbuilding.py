# world/shipbuilding.py
from evennia import create_object
from typeclasses.domain.ships import Ship

def build_ship(character, ship_type):
    cost = get_ship_cost(ship_type)
    if character.spend_money("guilders", cost):
        new_ship = create_object(Ship, key=f"{character.name}'s {ship_type.capitalize()}")
        new_ship.db.ship_type = ship_type
        new_ship.db.owner = character
        
        # Set initial attributes based on ship type
        set_initial_attributes(new_ship, ship_type)
        
        character.msg(f"You've built a {ship_type} for {cost} guilders!")
        character.msg("You can now use 'ship_modify <modification>' to add modifications to your ship.")
    else:
        character.msg(f"You don't have enough guilders to build this ship. It costs {cost} guilders.")

def get_ship_cost(ship_type):
    costs = {
        "sloop": 15000,
        "frigate": 25000,
        "galleon": 50000,
        "galleass": 50000,
        "caravel": 75000
    }
    return costs.get(ship_type, 10000)  # Default cost if type not found

def set_initial_attributes(ship, ship_type):
    # Set initial attributes based on ship type
    if ship_type == "sloop":
        ship.db.brawn = 2
        ship.db.finesse = 3
        ship.db.resolve = 2
        ship.db.wits = 3
        ship.db.panache = 3
    elif ship_type == "frigate":
        ship.db.brawn = 3
        ship.db.finesse = 2
        ship.db.resolve = 4
        ship.db.wits = 2
        ship.db.panache = 2
    elif ship_type == "galleon":
        ship.db.brawn = 4
        ship.db.finesse = 2
        ship.db.resolve = 4
        ship.db.wits = 1
        ship.db.panache = 1
    elif ship_type == "galleass":
        ship.db.brawn = 1
        ship.db.finesse = 4
        ship.db.resolve = 2
        ship.db.wits = 2
        ship.db.panache = 3
    elif ship_type == "caravel":
        ship.db.brawn = 3
        ship.db.finesse = 3
        ship.db.resolve = 2
        ship.db.wits = 3
        ship.db.panache = 4