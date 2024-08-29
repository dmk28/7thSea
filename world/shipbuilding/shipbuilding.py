# world/shipbuilding.py
from evennia import create_object
from typeclasses.domain.ships import Ship
from world.ships.models import Ship as ShipModel

def build_ship(character, ship_type):
    cost = get_ship_cost(ship_type)
    if character.character_sheet.money_guilders >= cost:
        character.character_sheet.money_guilders -= cost
        character.character_sheet.save()

        new_ship = create_object(Ship, key=f"{character.name}'s {ship_type.capitalize()}")
        ship_model = new_ship.ship_model
        ship_model.name = f"{character.name}'s {ship_type.capitalize()}"
        
        # Set initial attributes based on ship type
        set_initial_attributes(ship_model, ship_type)
        
        # Set the captain (owner)
        ship_model.captain = character.character_sheet.db_object
        ship_model.save()

        character.msg(f"You've built a {ship_type} for {cost} guilders!")
        character.msg("You can now use 'ship_modify <modification>' to add modifications to your ship.")
        return new_ship
    else:
        character.msg(f"You don't have enough guilders to build this ship. It costs {cost} guilders.")
        return None

def get_ship_cost(ship_type):
    costs = {
        "sloop": 15000,
        "frigate": 25000,
        "galleon": 50000,
        "galleass": 50000,
        "caravel": 75000
    }
    return costs.get(ship_type, 10000)  # Default cost if type not found

def set_initial_attributes(ship_model, ship_type):
    attributes = {
        "sloop": {"brawn": 2, "finesse": 3, "resolve": 2, "wits": 3, "panache": 3},
        "frigate": {"brawn": 3, "finesse": 2, "resolve": 4, "wits": 2, "panache": 2},
        "galleon": {"brawn": 4, "finesse": 2, "resolve": 4, "wits": 1, "panache": 1},
        "galleass": {"brawn": 1, "finesse": 4, "resolve": 2, "wits": 2, "panache": 3},
        "caravel": {"brawn": 3, "finesse": 3, "resolve": 2, "wits": 3, "panache": 4}
    }
    
    ship_attrs = attributes.get(ship_type, attributes["sloop"])  # Default to sloop if type not found
    
    for attr, value in ship_attrs.items():
        setattr(ship_model, attr, value)