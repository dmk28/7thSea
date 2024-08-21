from evennia import Command, create_object, CmdSet
from typeclasses.armor.armor_and_clothes import DracheneisenFullPlate, DracheneisenHalfPlate, DracheneisenCuirass, DracheneisenScale, DracheneisenHelmet, DracheneisenGauntlets, DracheneisenGreaves

class CmdBuyDracheneisen(Command):
    """
    Purchase Dracheneisen armor for approved Eisen characters.

    Usage:
      buydracheneisen

    This command allows approved Eisen characters to make their one-time
    Dracheneisen armor purchase.
    """

    key = "buydracheneisen"
    locks = "cmd:is_eisen()"
    help_category = "Character"

    def func(self):
        caller = self.caller

        if not self.check_eligibility(caller):
            return

        self.start_purchase_process(caller)

    def check_eligibility(self, caller):
        if not caller.db.approved:
            caller.msg("Your character concept must be approved before you can purchase Dracheneisen armor.")
            return False

        if caller.db.nationality != "Eisen":
            caller.msg("Only Eisen characters can purchase Dracheneisen armor.")
            return False

        if caller.db.eisen_bought:
            caller.msg("You have already made your Dracheneisen purchase.")
            return False

        if not any(perk.startswith("Dracheneisen") for perk in caller.db.perks):
            caller.msg("You must have the Dracheneisen advantage to purchase Dracheneisen armor.")
            return False

        if any(perk.startswith("Dracheneisen") for perk in caller.db.perks): 
            return True     
        return True    

    def start_purchase_process(self, caller):
        dracheneisen_level = 1 if "Dracheneisen (Level 1)" in caller.db.perks else 2
        max_points = 6 if dracheneisen_level == 1 else 16

        caller.ndb.dracheneisen_purchase = {
            "points_left": max_points,
            "armor": []
        }

        self.display_armor_options(caller)

    def display_armor_options(self, caller):
        armor_options = {
            "Full Plate": DracheneisenFullPlate,
            "Half Plate": DracheneisenHalfPlate,
            "Cuirass": DracheneisenCuirass,
            "Scale": DracheneisenScale,
            "Helmet": DracheneisenHelmet,
            "Gauntlets": DracheneisenGauntlets,
            "Greaves": DracheneisenGreaves
        }

        text = "Available Dracheneisen armor pieces:\n"
        for name, armor_class in armor_options.items():
            # Create a temporary instance of the armor
            temp_armor = create_object(armor_class, key=f"Temp {name}", location=None)
            text += f"{name}: Cost: {temp_armor.db.cost}, Armor: {temp_armor.db.armor}, Soak Keep: {temp_armor.db.soak_keep}\n"
            temp_armor.delete()  # Clean up the temporary object

        text += f"\nYou have {caller.ndb.dracheneisen_purchase['points_left']} points to spend."
        text += "\nEnter the name of the armor piece you want to purchase or 'done' when finished."

        caller.msg(text)
        caller.cmdset.add("commands.crafting.dracheneisen.DracheneisenPurchaseCmdSet")



class CmdPurchaseArmorPiece(Command):
    """
    Purchase a piece of Dracheneisen armor.

    Usage:
      <armor piece name>
      done

    Purchase the specified armor piece or finish the purchase process.
    """

    key = "purchasearmor"
    locks = "cmd:is_eisen()"    
    aliases = ["done"]
    help_category = "Eisen"
    def func(self):
        caller = self.caller
        choice = self.args.strip().lower()

        if choice == "done":
            self.finish_purchase(caller)
            return

        self.process_armor_choice(caller, choice)

    def process_armor_choice(self, caller, choice):
        armor_options = {
            "full plate": DracheneisenFullPlate,
            "half plate": DracheneisenHalfPlate,
            "cuirass": DracheneisenCuirass,
            "scale": DracheneisenScale,
            "helmet": DracheneisenHelmet,
            "gauntlets": DracheneisenGauntlets,
            "greaves": DracheneisenGreaves
        }

        if choice not in armor_options:
            caller.msg("Invalid armor piece. Please choose from the available options.")
            return

        armor_class = armor_options[choice]
        
        # Create a temporary instance of the armor
        temp_armor = create_object(armor_class, key=f"Temp {choice}", location=None)
        
        if temp_armor.db.cost > caller.ndb.dracheneisen_purchase['points_left']:
            caller.msg(f"You don't have enough points to purchase {choice.title()}.")
            temp_armor.delete()  # Clean up the temporary object
            return

        caller.ndb.dracheneisen_purchase['points_left'] -= temp_armor.db.cost
        caller.ndb.dracheneisen_purchase['armor'].append(choice.title())
        caller.msg(f"You have purchased {choice.title()}. Points remaining: {caller.ndb.dracheneisen_purchase['points_left']}")

        # Clean up the temporary object
        temp_armor.delete()

        if caller.ndb.dracheneisen_purchase['points_left'] > 0:
            self.caller.cmdset.add(DracheneisenPurchaseCmdSet)  # Re-add the cmdset
            CmdBuyDracheneisen().display_armor_options(caller)  # Call display_armor_options directly
        else:
            self.finish_purchase(caller)

    def finish_purchase(self, caller):
        for armor_name in caller.ndb.dracheneisen_purchase['armor']:
            armor_class = globals()[f"Dracheneisen{armor_name.replace(' ', '')}"]
            armor = create_object(armor_class, key=f"Dracheneisen {armor_name}", location=caller)
            caller.msg(f"You have acquired {armor.name}.")

        caller.db.eisen_bought = True
        caller.msg("You have completed your Dracheneisen purchase.")

        # Remove the purchase command set
        caller.cmdset.delete("commands.crafting.dracheneisen.DracheneisenPurchaseCmdSet")

        # Clean up
        del caller.ndb.dracheneisen_purchase

class DracheneisenPurchaseCmdSet(CmdSet):
        def at_cmdset_creation(self):
            self.add(CmdBuyDracheneisen())
            self.add(CmdPurchaseArmorPiece())