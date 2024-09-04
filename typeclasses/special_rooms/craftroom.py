from typeclasses.rooms import Room
from evennia.utils.evmenu import EvMenu
from world.crafting import craft_item, list_available_recipes
from world.crafting.models import CraftingRecipe, CraftingMaterial

class CraftRoom(Room):
    def at_object_creation(self):
        super().at_object_creation()
        self.db.wares = []  # List to store available items for buying
        self.db.recipes = list(CraftingRecipe.objects.all())  # All available recipes

    def return_appearance(self, looker):
        text = super().return_appearance(looker)
        text += "\nType 'craft' to open the crafting menu."
        text += "\nType 'shop' to view purchasable items."
        return text

def craft_menu(caller):
    def _craft_submenu(caller, raw_string):
        recipe_name = raw_string.strip().lower()
        recipe = CraftingRecipe.objects.filter(name__iexact=recipe_name).first()
        if not recipe:
            caller.msg("That recipe doesn't exist.")
            return "craft_menu"

        ingredients = [obj for obj in caller.contents if obj.db.crafting_material]
        result, message = craft_item(caller, recipe_name, *ingredients)
        caller.msg(message)
        return "craft_menu"

    available_recipes = list_available_recipes(caller)
    text = "Available recipes:\n"
    options = []
    for i, recipe in enumerate(available_recipes, 1):
        text += f"{i}. {recipe.name}\n"
        options.append({"key": str(i), "desc": recipe.name, "goto": (_craft_submenu, {"raw_string": recipe.name})})
    
    options.append({"key": "q", "desc": "Quit", "goto": "exit"})
    return text, options

def shop_menu(caller):
    def _buy_item(caller, raw_string):
        try:
            index = int(raw_string) - 1
            item = caller.location.db.wares[index]
            if caller.db.money >= item['cost']:
                caller.db.money -= item['cost']
                new_item = create_object(item['typeclass'], key=item['name'], location=caller)
                for key, value in item.items():
                    if key not in ['typeclass', 'name', 'cost']:
                        setattr(new_item.db, key, value)
                caller.msg(f"You bought {new_item.name} for {item['cost']} coins.")
            else:
                caller.msg("You don't have enough money.")
        except (ValueError, IndexError):
            caller.msg("Invalid choice.")
        return "shop_menu"

    text = "Available items for purchase:\n"
    options = []
    for i, item in enumerate(caller.location.db.wares, 1):
        text += f"{i}. {item['name']} - Cost: {item['cost']} coins\n"
        options.append({"key": str(i), "desc": item['name'], "goto": (_buy_item, {"raw_string": str(i)})})
    
    options.append({"key": "q", "desc": "Quit", "goto": "exit"})
    return text, options

class CmdCraft(Command):
    key = "craft"
    locks = "cmd:all()"
    
    def func(self):
        EvMenu(self.caller, "typeclasses.rooms", "craft_menu", persistent=False)

class CmdShop(Command):
    key = "shop"
    locks = "cmd:all()"
    
    def func(self):
        EvMenu(self.caller, "typeclasses.rooms", "shop_menu", persistent=False)

class CraftRoomCmdSet(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdCraft())
        self.add(CmdShop())

CraftRoom.cmdset.add(CraftRoomCmdSet, permanent=True)



class WeaponCraftRoom(CraftRoom):
    self.db.wares = [
        {
            "name": "Steel Rapier",
            "typeclass": "typeclasses.objects.Sword",
            "cost": 20,
            "description": "A standard steel rapier, about the size of the wielder's arm. Used for cutting and thrusting.",
            "damage": 2,
            "damage_keep": 2
        },
        {
            "name": "Longsword",
            "typeclass": "typeclasses.objects.HeavyWeapon",
            "cost": 20,
            "description": "A standard longsword made of steel, Vesten provenance.",
            "damage": 3,
            "damage_keep": 2
        },
        {
            "name": "a set of linen clothes",
            "typeclass": "typeclasses.objects.Armor",
            "cost": 10,
            "description": "Basic linen clothes",
            "details": "This set of clothes are made of linen and grant basic protection.",
            "armor": 1,
            "soak_keep": 1
        }


    ]