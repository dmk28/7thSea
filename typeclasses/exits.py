"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""

from evennia.objects.objects import DefaultExit

from .objects import ObjectParent


class Exit(ObjectParent, DefaultExit):
    """
    Exits are connectors between rooms. Exits are normal Objects except
    they defines the `destination` property and overrides some hooks
    and methods to represent the exits.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Objects child classes like this.

    """

    pass
class PlayerExit(Exit):
    """
    This exit can only be used by the room owner and those they've given permission to.
    """
    def at_object_creation(self):
        """
        Called when the exit is first created.
        """
        self.locks.add("traverse:roomowner() or keychain() or perm(Admin)")

    def at_failed_traverse(self, traversing_object):
        """
        Called when an object fails to traverse this exit.
        """
        traversing_object.msg("You don't have permission to enter this room.")


