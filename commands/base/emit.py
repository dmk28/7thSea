from evennia.commands.command import Command as BaseCommand
from evennia.commands.default.muxcommand import MuxCommand
from typeclasses.characters import Character


class CmdEmit(MuxCommand):
    """
    @emit

    Usage: 
    @emit allows you to broadcast poses to the room. It will not have your username attached.

    Algorithm cribbed from Arx. Credit to Tehom and Apostate.

    """

    key = "@emit"
    aliases = ["emit", "+emit"]
    locks = "cmd():all()"
    switches = ["pemit", "stemit", "remit"]
    help_category = "Social"
    perm_for_switches = "Builders"
    def func(self):
        caller = self.caller
        if caller.check_permstring(self.perm_for_switches):
            args = self.args
        else:
            args = self.raw.lstrip(" ")

        if not args:
            string = "Usage:"
            string += "\n@emit[/switches] [<obj>, <obj>, ... =] <message>"
            caller.msg(string)
            return
        rooms_only = "rooms" in self.switches
        players_only = "players" in self.switches 
        send_to_contents = "contents" in self.switches
        events_only = "story" in self.switches 
        perm = self.perm_for_switches
        normal_emit = False
        has_perms = caller.check_permstring(perm)

        cmdstring = self.cmdstring.lstrip("@").lstrip("+")

        if (cmdstring in  ("remit", "pemit", "stemit")) and not caller.check_permstring(perm):
            caller.msg("Options are restricted to Staff Only.")
            return

        if cmdstring == "remit":
            rooms_only = True
            send_to_contents = True
        elif cmdstring == "pemit":
            players_only = True
        elif cmdstring == "stemit":
            events_only = True

        if not caller.check_permstring(perm):
            rooms_only = False
            players_only = False
            events_only = False
        if not self.rhs or not has_perms:
            message = args
            normal_emit = True
            objnames = []
            do_global = False
        else:
            do_global = True
            message = self.rhs
            if caller.check_permstring(perm):
                objnames = self.lhslist
            else: 
                objnames = [x.key for x in caller.location.contents if x.player]
        
        if do_global:
            do_global = has_perms

        if events_only:
            from datetime import datetime

            events = RPEvent.objects.filter(
                finished=False, gm_event=True, date__lte=datetime.now()
            )
            for event in events:
                obj = event.location
                if not obj:
                    continue
                obj.msg_contents(message, from_obj=caller, kwargs={"options": {"is_pose": True}})
                caller.msg("Emitted to event " + str(event) + " and contents:\n" + message)
            return
        # normal emits by players are just sent to the room
        if normal_emit:
            gms = [ob for ob in caller.location.contents if ob.check_permstring("builders")]
            non_gms = [ob for ob in caller.location.contents if "emit_label" in ob.tags.all() and ob.player]
            gm_msg = "|w(|c" + caller.name + "|w)|n " + message
            
            # Send to GMs and non-GMs
            for ob in gms + non_gms:
                ob.msg(gm_msg, from_obj=caller, options={"is_pose": True})
            
            # Send to others
            others = [ob for ob in caller.location.contents if ob not in gms and ob not in non_gms]
            for ob in others:
                ob.msg(message, from_obj=caller, options={"is_pose": True})
            
            return    # send to all objects
        for objname in objnames:
            if players_only:
                obj = caller.player.search(objname)
                if obj:
                    obj = obj.character
            else:
                obj = caller.search(objname, global_search=do_global)
            if not obj:
                caller.msg("Could not find " + objname + ".")
                continue
            if rooms_only and obj.location:
                caller.msg(objname + " is not a room. Ignored.")
                continue
            if players_only and not obj.player:
                caller.msg(objname + " has no active player. Ignored.")
                continue
            if obj.access(caller, "tell"):
                if obj.check_permstring(perm):
                    bmessage = "|w[Emit by: |c" + caller.name + "|w]|n " + message
                    obj.msg(bmessage, options={"is_pose": True})
                else:
                    obj.msg(message, options={"is_pose": True})
                if send_to_contents and hasattr(obj, "msg_contents"):
                    obj.msg_contents(message, from_obj=caller, kwargs={"options": {"is_pose": True}})
                    caller.msg("Emitted to " + objname + " and contents:\n" + message)
                elif caller.check_permstring(perm):
                    caller.msg("Emitted to " + objname + ":\n" + message)
            else:
                caller.msg("You are not allowed to emit to " + objname + ".")