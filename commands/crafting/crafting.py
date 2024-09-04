from evennia import create_object
from world.character_sheet.models import CharacterSheet
from .models import CraftingRecipe, CraftingMaterial, RecipeRequirement

def craft_item(crafter, recipe_name, *ingredients):
    try:
        recipe = CraftingRecipe.objects.get(name__iexact=recipe_name)
    except CraftingRecipe.DoesNotExist:
        return None, "That recipe doesn't exist."

    # Check if the crafter has all required ingredients and tools
    for req in recipe.requirements.all():
        found = False
        for item in ingredients:
            if item.db.crafting_material == req.material.name and item.db.amount >= req.amount:
                found = True
                break
        if not found:
            return None, f"You're missing {req.amount} {req.material.name}."

    # Consume ingredients
    for req in recipe.requirements.filter(is_tool=False):
        for item in ingredients:
            if item.db.crafting_material == req.material.name:
                item.db.amount -= req.amount
                if item.db.amount <= 0:
                    item.delete()
                else:
                    item.save()
                break

    # Create the result
    if recipe.result_type == 'weapon':
        result = create_object("typeclasses.objects.Weapon", 
                               key=recipe.result_prototype.get('name', recipe.name),
                               location=crafter)
    elif recipe.result_type == 'armor':
        result = create_object("typeclasses.objects.Armor", 
                               key=recipe.result_prototype.get('name', recipe.name),
                               location=crafter)
    else:
        return None, "Unknown result type."

    # Set attributes based on the prototype
    for key, value in recipe.result_prototype.items():
        setattr(result.db, key, value)

    return result, f"You successfully crafted {result.name}!"

def list_available_recipes(crafter):
    available_recipes = []
    for recipe in CraftingRecipe.objects.all():
        if can_craft_recipe(crafter, recipe):
            available_recipes.append(recipe)
    return available_recipes

def can_craft_recipe(crafter, recipe):
    for req in recipe.requirements.all():
        if not crafter.search(req.material.name, location=crafter):
            return False
    return True