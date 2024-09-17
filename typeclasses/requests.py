from evennia.utils.utils import delay
from evennia.scripts.scripts import DefaultScript
from evennia.accounts.models import AccountDB
from random import randint
from evennia import ScriptDB

class Request(DefaultScript):
    """
    This script represents a request made by a player to a GM.
    """

    def at_script_creation(self):
        self.key = "Request"
        self.persistent = True
        self.db.requester = None
        self.db.request_type = ""
        self.db.description = ""
        self.db.bucket = ""
        self.db.status = "Pending"
        self.db.gm_comments = ""
        # Initialize attributes
      

    def approve(self, gm, comments=""):
        self.db.status = "Approved"
        self.db.gm_comments = comments
        self.db.requester.msg(f"Your request '{self.db.request_type}' has been approved.")
        gm.msg(f"You have approved the request '{self.db.request_type}' from {self.db.requester}.")

    def deny(self, gm, comments=""):
        self.db.status = "Denied"
        self.db.gm_comments = comments
        self.db.requester.msg(f"Your request '{self.db.request_type}' has been denied. GM comments: {comments}")
        gm.msg(f"You have denied the request '{self.db.request_type}' from {self.db.requester}.")
