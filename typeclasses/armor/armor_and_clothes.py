from typeclasses.objects import Armor

class DracheneisenArmor(Armor):
    def at_object_creation(self):
        super().at_object_creation()
        self.db.material = "Dracheneisen"
        self.db.description = "A piece of armor made from the legendary Dracheneisen metal."

class DracheneisenFullPlate(DracheneisenArmor):
    def at_object_creation(self):
        super().at_object_creation()
        self.db.armor = 12
        self.db.soak_keep = 3
        self.db.cost = 12
        self.db.description = "A full suit of Dracheneisen plate armor, offering maximum protection."
        self.db.wear_location = "body"

class DracheneisenHalfPlate(DracheneisenArmor):
    def at_object_creation(self):
        super().at_object_creation()
        self.db.armor = 8
        self.db.soak_keep = 2
        self.db.cost = 8
        self.db.description = "A partial suit of Dracheneisen plate armor, balancing protection and mobility."
        self.db.wear_location = "body"
        self.db.material = "Dracheneisen"




class DracheneisenCuirass(DracheneisenArmor):
    def at_object_creation(self):
        super().at_object_creation()
        self.db.armor = 6
        self.db.soak_keep = 1
        self.db.cost = 6
        self.db.wear_location = "torso"
        self.db.description = "A Dracheneisen breastplate, offering good torso protection."
        self.db.material = "Dracheneisen"


class DracheneisenScale(DracheneisenArmor):
    def at_object_creation(self):
        super().at_object_creation()
        self.db.armor = 5
        self.db.soak_keep = 1
        self.db.cost = 5
        self.db.description = "Flexible Dracheneisen scale armor, providing a balance of protection and agility."
        self.db.wear_location = "torso"

# Additional armor pieces
class DracheneisenHelmet(DracheneisenArmor):
    def at_object_creation(self):
        super().at_object_creation()
        self.db.armor = 3
        self.db.soak_keep = 1
        self.db.cost = 3
        self.db.description = "A Dracheneisen helmet, offering crucial head protection."
        self.db.wear_location = "head"

class DracheneisenGauntlets(DracheneisenArmor):
    def at_object_creation(self):
        super().at_object_creation()
        self.db.armor = 2
        self.db.soak_keep = 1
        self.db.cost = 2
        self.db.description = "Dracheneisen gauntlets, protecting the hands and forearms."
        self.db.wear_location = "hands"

class DracheneisenGreaves(DracheneisenArmor):
    def at_object_creation(self):
        super().at_object_creation()
        self.db.armor = 2
        self.db.soak_keep = 1
        self.db.cost = 2
        self.db.description = "Dracheneisen greaves, guarding the legs."
        self.db.wear_location = "legs"


