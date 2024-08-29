from typeclasses.objects import DefaultObject
from evennia import AttributeProperty, create_object
from world.ships.models import Ship as ShipModel, Modification, Flaw
from django.db import transaction



class Ship(DefaultObject):  # Changed from Object to DefaultObject
    def at_object_creation(self):
        from typeclasses.rooms import ShipInterior

        super().at_object_creation()
        self.db.ship_type = ""
        self.db.captain = None
        self.db.modifications = []
        # Create the ship's interior
        self.db.interior = create_object(ShipInterior, key=f"{self.name} - Main Deck")
        self.db.interior.db.ship = self
        # Create the associated ShipModel
        ShipModel.objects.create(evennia_object=self)

    def return_appearance(self, looker):
        desc = super().return_appearance(looker)
        desc += f"\nType 'enter {self.name}' to board the ship."
        return desc

    def at_object_receive(self, moved_obj, source_location, **kwargs):
        if moved_obj.has_account:  # If it's a player
            moved_obj.move_to(self.db.interior, quiet=True)
            moved_obj.msg(f"You board {self.name}.")

    def at_object_leave(self, moved_obj, target_location, **kwargs):
        if moved_obj.has_account:  # If it's a player
            moved_obj.msg(f"You disembark from {self.name}.")

    @property
    def ship_model(self):  # Changed to property
        return ShipModel.objects.get_or_create(evennia_object=self)[0]

    @property
    def brawn(self):
        return self.ship_model.brawn

    @brawn.setter
    def brawn(self, value):
        self.ship_model.brawn = value
        self.ship_model.save()

    # Similar properties for finesse, resolve, wits, panache
    @property
    def finesse(self):
        return self.ship_model.finesse

    @finesse.setter
    def finesse(self, value):
        self.ship_model.finesse = value
        self.ship_model.save()

    # Add similar properties for resolve, wits, panache

    @property
    def cargo(self):
        return self.ship_model.cargo

    @cargo.setter
    def cargo(self, value):
        self.ship_model.cargo = value
        self.ship_model.save()

    @property
    def draft(self):
        return self.ship_model.draft

    @draft.setter
    def draft(self, value):
        self.ship_model.draft = value
        self.ship_model.save()

    @property
    def captain(self):
        return self.ship_model.captain

    @captain.setter
    def captain(self, value):
        self.ship_model.captain = value
        self.ship_model.save()

    @property
    def modifications(self):
        return self.ship_model.modifications.all()

    @property
    def flaws(self):
        return self.ship_model.flaws.all()

    @property
    def crew(self):
        return (self.resolve + self.brawn) * 50

    def get_ship_stats(self):
        return {
            "Brawn": self.brawn,
            "Finesse": self.finesse,
            "Resolve": self.resolve,
            "Wits": self.wits,
            "Panache": self.panache,
            "Cargo": self.cargo,
            "Crew": self.crew,
            "Draft": self.draft,
            "Captain": self.captain.name if self.captain else "None",
            "Modifications": [mod.name for mod in self.modifications],
            "Flaws": [flaw.name for flaw in self.flaws]
        }

    # Methods to add/remove modifications and flaws
    @transaction.atomic
    def update_attributes(self, **kwargs):
        for attr, value in kwargs.items():
            if hasattr(self.ship_model, attr):
                setattr(self.ship_model, attr, value)
        self.ship_model.save()

    def add_modification(self, name):
        try:
            Modification.objects.create(ship=self.ship_model, name=name)
        except Exception as e:
            self.msg(f"Error adding modification: {str(e)}")

    def add_flaw(self, name):
        try:
            Flaw.objects.create(ship=self.ship_model, name=name)
        except Exception as e:
            self.msg(f"Error adding flaw: {str(e)}")

    def move_to(self, destination):
        if super().move_to(destination):
            self.db.interior.db.location = destination
            return True
        return False
        
    def move_to_coordinates(self, coordinates):
        sea_map = search_script("SeaMap")[0]
        target_room = sea_map.get_sea_room(coordinates)
        
        if target_room:
            self.move_to(target_room)
            return True
        else:
            return False