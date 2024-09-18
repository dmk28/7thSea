from typeclasses.requests  import Request
from evennia import Command
from evennia.utils.create import create_script
from evennia import ScriptDB
from evennia import DefaultScript
from evennia.commands.default.muxcommand import MuxCommand
from django.db.models import Q
from evennia.utils.evtable import EvTable
from world.character_sheet.models import CharacterSheet
from django.utils import timezone
import datetime

class CmdRequest(MuxCommand):
    """
    Create or manage requests for GM approval.

    Usage:
      request <type> = <description>
      request/list
      request/approve <id>[=<comments>]
      request/deny <id>[=<comments>]
      request/view <id>
      request/cancel <id>

    Switches:
      list - List all pending requests
      approve - Approve a request
      deny - Deny a request
      view - View details of a specific request
      cancel - Cancel your own request

    Examples:
      request Skill Increase = I'd like to increase my Fencing skill.
      request New Advantage = I want to purchase the "Noble" advantage.
      request/list
      request/approve 5=Looks good!
      request/deny 3=Please revise and resubmit.
      request/view 2
      request/cancel 4
    """

    key = "request"
    locks = "cmd:all()"
    help_category = "Requests"
    switches = ["list", "approve", "deny", "view", "cancel"]

    def func(self):
        if not self.switches:
            self.create_request()
        elif "list" in self.switches:
            self.list_requests()
        elif "approve" in self.switches:
            self.approve_request()
        elif "deny" in self.switches:
            self.deny_request()
        elif "view" in self.switches:
            self.view_request()
        elif "cancel" in self.switches:
            self.cancel_request()

    def create_request(self):
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
        new_request.db.date_created = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

        self.caller.msg(f"Your request '{request_type}' has been submitted for GM approval.")

    
    def list_requests(self):
        # First, get all Request scripts
        requests = ScriptDB.objects.filter(db_typeclass_path__contains='Request')
        
        # Then, filter for pending status
        pending_requests = [
            req for req in requests 
            if req.db.status == "Pending"
        ]
        
        if not pending_requests:
            self.caller.msg("There are no pending requests.")
            return
        
        table = EvTable("|500ID|n", "|500Requester|n", "|500Type|n", "|500Date|n", "|500Description|n", border="cells")
        for req in pending_requests:
            table.add_row(
                req.id,
                req.db.requester,
                req.db.request_type,
                req.db.date_created,
                req.db.description[:30] + "..." if len(req.db.description) > 30 else req.db.description
            )
        self.caller.msg(str(table))

    def approve_request(self):
        if not self.args:
            self.caller.msg("Usage: request/approve <id>[=<comments>]")
            return

        args = self.args.split("=", 1)
        try:
            request_id = int(args[0].strip())
            comments = args[1].strip() if len(args) > 1 else ""
        except ValueError:
            self.caller.msg("Invalid request ID. Please provide a number.")
            return

        try:
            req = Request.objects.get(id=request_id)
            if req.db.request_type == "Character Approval":
                self.approve_character(req, comments)
            else:
                req.approve(self.caller, comments)
            self.caller.msg(f"Request {request_id} approved. Comments: {comments}")
        except Request.DoesNotExist:
            self.caller.msg("Invalid request ID.")

    def deny_request(self):
        if not self.args:
            self.caller.msg("Usage: request/deny <id>[=<comments>]")
            return

        args = self.args.split("=", 1)
        try:
            request_id = int(args[0].strip())
            comments = args[1].strip() if len(args) > 1 else ""
        except ValueError:
            self.caller.msg("Invalid request ID. Please provide a number.")
            return

        try:
            req = Request.objects.get(id=request_id)
            req.deny(self.caller, comments)
            self.caller.msg(f"Request {request_id} denied. Comments: {comments}")
        except Request.DoesNotExist:
            self.caller.msg("Invalid request ID.")

    def view_request(self):
        if not self.args:
            self.caller.msg("Usage: request/view <id>")
            return

        try:
            request_id = int(self.args.strip())
            req = Request.objects.get(id=request_id)

            table = EvTable(border="cells")
            table.add_row("ID:", req.id)
            table.add_row("Requester:", req.db.requester)
            table.add_row("Type:", req.db.request_type)
            table.add_row("Description:", req.db.description)
            table.add_row("Status:", req.db.status)
            table.add_row("Date Created:", req.db.date_created)
            if req.db.gm_comments:
                table.add_row("GM Comments:", req.db.gm_comments)

            self.caller.msg(str(table))

        except ValueError:
            self.caller.msg("Invalid request ID. Please provide a number.")
        except Request.DoesNotExist:
            self.caller.msg("Request not found.")

    def cancel_request(self):
        if not self.args:
            self.caller.msg("Usage: request/cancel <id>")
            return

        try:
            request_id = int(self.args.strip())
            req = Request.objects.get(id=request_id)

            if req.db.requester != self.caller:
                self.caller.msg("You can only cancel your own requests.")
                return

            req.delete()
            self.caller.msg(f"Request {request_id} has been cancelled.")

        except ValueError:
            self.caller.msg("Invalid request ID. Please provide a number.")
        except Request.DoesNotExist:
            self.caller.msg("Request not found.")

    def approve_character(self, req, comments):
        character = req.db.requester
        character.db.approved = True
        character.db.complete_chargen = True
        character.save()

        try:
            sheet = CharacterSheet.objects.get(db_object=character)
            sheet.approved = True
            sheet.save()
        except CharacterSheet.DoesNotExist:
            self.caller.msg(f"Warning: No character sheet found for {character.name}.")
            sheet = CharacterSheet.create_from_typeclass(character)
            sheet.approved = True
            sheet.save()

        start_room = self.caller.search("Main Room", global_search=True)
        if start_room:
            character.move_to(start_room, quiet=True)
            self.caller.msg(f"Moved {character.name} to the starting room.")
        else:
            self.caller.msg("Could not find the starting room. Character remains in current location.")

        req.approve(self.caller, comments)
        character.msg("Your character has been approved! Welcome to the game!")