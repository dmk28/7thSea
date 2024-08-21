from evennia import DefaultRoom
from world.banking.cmdset import BankingCmdSet

class BankRoom(DefaultRoom):
    def at_object_creation(self):
        super().at_object_creation()
        self.locks.add("enter:true();call:true()")  # Allow anyone to enter and use bank commands

    def return_appearance(self, looker):
        text = super().return_appearance(looker)
        text += "\nThis is a bank. You can use various banking commands here."
        return text

    def at_object_receive(self, moved_obj, source_location, **kwargs):
        """
        This is triggered when an object enters the room.
        """
        super().at_object_receive(moved_obj, source_location, **kwargs)
        if moved_obj.has_account:
            # If the object entering is a player-controlled character
            moved_obj.cmdset.add(BankingCmdSet, persistent=False)

    def at_object_leave(self, moved_obj, target_location, **kwargs):
        """
        This is triggered when an object leaves the room.
        """
        super().at_object_leave(moved_obj, target_location, **kwargs)
        if moved_obj.has_account:
            # If the object leaving is a player-controlled character
            moved_obj.cmdset.delete(BankingCmdSet)