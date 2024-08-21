from typeclasses.requests  import Request
from evennia import Command
from evennia.utils.create import create_script
from evennia import ScriptDB
from evennia import DefaultScript


class CmdRequest(Command):
    """
    Create a new request for GM approval.

    Usage:
      request <type> = <description>

    Examples:
      request Skill Increase = I'd like to increase my Fencing skill.
      request New Advantage = I want to purchase the "Noble" advantage.
    """

    key = "request"
    locks = "cmd:all()"

    def func(self):
        if not self.args or "=" not in self.args:
            self.caller.msg("Usage: request <type> = <description>")
            return

        request_type, description = self.args.split("=", 1)
        request_type = request_type.strip()
        description = description.strip()

        new_request = create_script("typeclasses.requests.Request")
        new_request.db.requester = self.caller
        new_request.db.request_type = request_type
        new_request.db.description = description

        self.caller.msg(f"Your request '{request_type}' has been submitted for GM approval.")

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




class CmdReviewList(Command):
    """
    List all pending requests.

    Usage:
      review
    review/approve <request_id>[=<comments>]
    review/deny <request_id>[=<comments>]
    review <request_id>


    """
    key = "review"
    aliases = ["review/list"]
    locks = "cmd:perm(Wizards)"

    def func(self):
        requests = ScriptDB.objects.filter(db_typeclass_path__contains='Request')
        pending_requests = [req for req in requests if req.db.status == "Pending"]
        
        if not pending_requests:
            self.caller.msg("There are no pending requests.")
            return
        
        table = self.styled_table("ID", "Requester", "Type", "Description")
        for req in pending_requests:
            table.add_row(req.id, req.db.requester, req.db.request_type, req.db.description[:30])
        self.caller.msg(str(table))



class CmdReviewApprove(Command):

    key = "review/approve"
    locks = "cmd:perm(Wizards)"

    def func(self):
        args = self.args.strip()
        if "=" in args:
            request_id, comments = args.split("=", 1)
            request_id = request_id.strip()
            comments = comments.strip()
        else:
            request_id = args
            comments = ""

        try:
            request_id = int(request_id)
        except ValueError:
            self.caller.msg("Invalid request ID. Usage: review/approve <request_id>[=<comments>]")
            return

        try:
            req = ScriptDB.objects.get(id=request_id)
            req.approve(self.caller, comments)
            self.caller.msg(f"Request {request_id} approved. Comments: {comments}")
        except ScriptDB.DoesNotExist:
            self.caller.msg("Invalid request ID.")

class CmdReviewDeny(Command):


    key = "review/deny"
    locks = "cmd:perm(Wizards)"

    def func(self):
        args = self.args.strip()
        if "=" in args:
            request_id, comments = args.split("=", 1)
            request_id = request_id.strip()
            comments = comments.strip()
        else:
            request_id = args
            comments = ""

        try:
            request_id = int(request_id)
        except ValueError:
            self.caller.msg("Invalid request ID. Usage: review/deny <request_id>[=<comments>]")
            return

        try:
            req = ScriptDB.objects.get(id=request_id)
            req.deny(self.caller, comments)
            self.caller.msg(f"Request {request_id} denied. Comments: {comments}")
        except ScriptDB.DoesNotExist:
            self.caller.msg("Invalid request ID.")

class CmdReviewView(Command):
    """
    View details of a specific request.

    Usage:
      review <request_id>
    """

    key = "review/view"
    locks = "cmd:perm(Wizards)"

    def func(self):
        try:
            request_id = int(self.args.strip())
            req = ScriptDB.objects.get(id=request_id)

            self.caller.msg(f"Request ID: {req.id}")
            self.caller.msg(f"Requester: {req.db.requester}")
            self.caller.msg(f"Type: {req.db.request_type}")
            self.caller.msg(f"Description: {req.db.description}")
            self.caller.msg(f"Status: {req.db.status}")
            if req.db.gm_comments:
                self.caller.msg(f"GM Comments: {req.db.gm_comments}")
            else:
                self.caller.msg("GM Comments: No comments.")

        except ValueError:
            self.caller.msg("Invalid request ID. Please provide a valid integer ID.")
        except ScriptDB.DoesNotExist:
            self.caller.msg("Request not found.")
