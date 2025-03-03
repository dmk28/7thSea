from evennia import Command, create_script, search_script

class CmdPorteWalk(Command):
    """
    Activate the Porte Walk sorcery effect to increase your passive defense.

    Usage:
      portewalk

    This will increase your passive defense by 5 * your Walk knack rank.
    """
    key = "portewalk"
    locks = "cmd:attr(approved) or perm(Admin)"
    help_category = "Sorcery"

    def func(self):
        caller = self.caller
        character_sheet = caller.character_sheet

        if not caller.db.is_sorcerer or "Porte" not in caller.db.sorcery.get('name', ''):
            caller.msg("You don't know how to use Porte sorcery.")
            return

        walk_rank = character_sheet.get_knack_value('Walk')
        if walk_rank == 0:
            caller.msg("You haven't learned the Walk knack yet.")
            return

        if caller.db.porte_walk_active:
            caller.msg("Porte Walk is already active.")
            return

        # Create and start the Porte Walk effect script
        script = create_script(
            "typeclasses.sorcery_scripts.portewalk.PorteWalkEffect",
            obj=caller,
            attributes=[
                ("walk_rank", walk_rank)
            ]
        )
        defense_increase = 5 * walk_rank
        caller.msg(f"You open a portal, increasing your passive defense by {defense_increase}!")
        # Optionally, inform the room about the effect
        caller.location.msg_contents(f"{caller.name} opens a shimmering red portal!", exclude=caller)


