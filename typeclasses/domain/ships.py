from typeclasses.objects import DefaultObject
from evennia import AttributeProperty
from world.ships.models import Ship as ShipModel, Modification, Flaw

class Ship(DefaultObject):
    def at_object_creation(self):
        super().at_object_creation()
        ShipModel.objects.create(evennia_object=self)

    @property
    def ship_model(self):
        return ShipModel.objects.get_or_create(evennia_object=self)[0]

    @property
    def brawn(self):
        return self.ship_model.brawn

    @brawn.setter
    def brawn(self, value):
        self.ship_model.brawn = value
        self.ship_model.save()

    def finesse(self, value):
        self.ship_model.finesse = finesse
        self.ship_model.save()

    def resolve(self,value):
        self.ship_model.resolve = resolve
        self.ship_model.save()
    def wits(self, value):
        self.ship_model.wits = wits
        self.ship_model.save()
    def panache(self, value):
        self.ship_model.panache = panache
        self.ship_model.save()

    def crew(self, value):
        self.ship_model.crew = crew
        self.ship_model.save()
    # Similar properties for finesse, resolve, wits, panache, cargo, draft
    def draft(self, value):
        self.ship_model.draft = draft
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
    def add_modification(self, name):
        Modification.objects.create(ship=self.ship_model, name=name)

    def remove_modification(self, name):
        self.ship_model.modifications.filter(name=name).delete()

    def add_flaw(self, name):
        Flaw.objects.create(ship=self.ship_model, name=name)

    def remove_flaw(self, name):
        self.ship_model.flaws.filter(name=name).delete()