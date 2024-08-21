from evennia.utils import dedent
from commands.shipyard_commands import ShipyardCmdSet
from typeclasses.rooms import Room


class ShipyardRoom(Room):
    def at_object_creation(self):
        self.db.desc = dedent("""This is a room you can use to make ships.""")

    def return_appearance(self, looker):
        text = super().return_appearance(looker)
        if hasattr(looker, 'db') and looker.db.approved:
            money = looker.db.money.get("guilders", 0)
            if money > 10000:
                text += "\n\nType |545shipbuild <ship_type>|n to begin shipbuilding!"
            else:
                text += '\n\nYou cannot afford shipbuilding, yet!'
        return text

    def at_object_receive(self, moved_obj, source_location, **kwargs):
        """Called when an object enters this room."""
        if moved_obj.has_account:
            moved_obj.cmdset.add(ShipyardCmdSet, persistent=False)

    def at_object_leave(self, moved_obj, target_location, **kwargs):
        """Called when an object leaves this room."""
        if moved_obj.has_account:
            moved_obj.cmdset.delete(ShipyardCmdSet)