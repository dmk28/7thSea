from evennia import Command
from evennia.utils.search import search_object
from world.crafting.models import CraftingRecipe, RecipeRequirement, WeaponModel

class CmdCraft(Command):
    """
    Craft an item using available materials.

    Usage:
      craft <recipe name>

    This command allows you to craft items based on known recipes and
    available materials in your inventory.
    """

    key = "craft"
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: craft <recipe name>")
            return

        recipe_name = self.args.strip().lower()
        try:
            recipe = CraftingRecipe.objects.get(name__iexact=recipe_name)
        except CraftingRecipe.DoesNotExist:
            self.caller.msg(f"No recipe found for '{recipe_name}'.")
            return

        # Check if the character has the required materials
        for requirement in recipe.requirements.all():
            material_objects = search_object(requirement.material.name, location=self.caller)
            if not material_objects or len(material_objects) < requirement.amount:
                self.caller.msg(f"You don't have enough {requirement.material.name}.")
                return

        # Craft the item
        if recipe.result_type == 'weapon':
            new_weapon = create_object(typeclass="typeclasses.weapons.Weapon", 
                                       key=recipe.name, location=self.caller)
            WeaponModel.objects.create(
                evennia_object=new_weapon,
                name=recipe.name,
                description=recipe.description,
                weapon_type=recipe.name.split()[0].lower(),  # Simplified; you might want to set this differently
                damage=5,  # Set a default value or calculate based on recipe/materials
                attack_skill="medium_wpn",  # Set default or calculate
                parry_skill="parry",  # Set default or calculate
                crafted_by=self.caller.db.character,
                quality_level=1,  # Start at 1, could be influenced by crafter's skill
            )
            self.caller.msg(f"You have crafted {new_weapon.name}!")

        # Remove used materials
        for requirement in recipe.requirements.all():
            material_objects = search_object(requirement.material.name, location=self.caller)
            for _ in range(requirement.amount):
                material_objects[0].delete()

# Add this command to your character's command set