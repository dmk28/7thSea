from evennia import DefaultObject
from world.adventuring_guilds.models import Holding as HoldingModel

class Holding(DefaultObject):
    """
    A typeclass for holdings that links to the Holding model.
    """
    
    def at_object_creation(self):
        """Set up the basic properties of the holding."""
        self.db.model_id = None

    def link_model(self, model_instance):
        """Link this typeclass instance to a Holding model instance."""
        self.db.model_id = model_instance.id

    def get_model(self):
        """Retrieve the linked Holding model instance."""
        if self.db.model_id:
            return HoldingModel.objects.get(id=self.db.model_id)
        return None

    # Delegate methods to the model
    def get_display_name(self):
        model = self.get_model()
        return model.get_display_name() if model else super().get_display_name()

    def get_description(self):
        model = self.get_model()
        return model.get_description() if model else super().get_description()

    def calculate_income_rate(self):
        model = self.get_model()
        return model.calculate_income_rate() if model else 0

    def upgrade(self):
        model = self.get_model()
        return model.upgrade() if model else (False, "No linked model found.")

    def get_details(self):
        model = self.get_model()
        return model.get_details() if model else {}