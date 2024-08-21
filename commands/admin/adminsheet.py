from evennia import Command
from evennia.utils.search import search_object
from evennia.utils import evtable
from typeclasses.characters import Character

class CmdAdminSheet(Command):
    """
    Display the character sheet of any player.

    Usage:
      adminsheet <character_name>

    This command allows admins to view the character sheet of any player.
    """
    key = "adminsheet"
    aliases = ["admin_sheet"]
    locks = "cmd:perm(Wizards)"
    help_category = "Admin"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: adminsheet <character_name>")
            return

        target = search_object(self.args.strip(), typeclass=Character)
        if not target:
            self.caller.msg(f"Character '{self.args.strip()}' not found.")
            return
        
        target = target[0]  # search_object returns a list

        width = 72  # Adjusted width

        sheet = []

        # Header
        sheet.append("=" * width)
        sheet.append(f"{'Character Sheet for ' + target.key:^{width}}")
        sheet.append("=" * width)

        # Basic Information
        basic_info = evtable.EvTable(border="table", width=width)
        basic_info.add_row("Name:", target.key, "Nationality:", target.db.nationality)
        basic_info.add_row("Hero Points:", str(target.db.hero_points))
        sheet.append(str(basic_info))

        # Traits
        traits = evtable.EvTable(border="table", width=width)
        traits.add_row(*[f"{trait.capitalize()}: {value}" for trait, value in target.db.traits.items()])
        sheet.append(str(traits))

        # Knacks
        knacks = evtable.EvTable(border="table", width=width)
        knacks.add_row("Civilian Knacks", "Martial Knacks", "Professional Knacks")
        
        knack_data = {
            "Civilian": target.db.skills.get("Civilian", {}),
            "Martial": target.db.skills.get("Martial", {}),
            "Professional": target.db.skills.get("Professional", {})
        }
        
        max_knacks = max(len(knacks) for knacks in knack_data.values())
        
        for i in range(max_knacks):
            row = []
            for category in ["Civilian", "Martial", "Professional"]:
                if i < len(knack_data[category]):
                    skill, skill_knacks = list(knack_data[category].items())[i]
                    knack_str = ", ".join(f"{k}: {v}" for k, v in skill_knacks.items())
                    row.append(f"{skill}: {knack_str}")
                else:
                    row.append("")
            knacks.add_row(*row)
        
        sheet.append(str(knacks))

        # Advantages
        advantages = evtable.EvTable(border="table", width=width)
        advantages.add_row("Advantages")
        adv_rows = [target.db.perks[i:i+3] for i in range(0, len(target.db.perks), 3)]
        for row in adv_rows:
            advantages.add_row(*row)
        sheet.append(str(advantages))

        # Sorcery and Duelist
        sorcery_duelist = evtable.EvTable(border="table", width=width)
        sorcery_duelist.add_row("Sorcery", "Duelist")
        if target.db.is_sorcerer:
            sorcery_info = [f"Type: {target.db.potential_sorcery}"] + [f"{k}: {v}" for k, v in target.db.sorcery_knacks.items()]
        else:
            sorcery_info = ["Not a sorcerer"]
        
        duelist_info = [f"Style: {target.db.duelist_style}"] if target.db.duelist_style else ["Not a duelist"]
        
        max_rows = max(len(sorcery_info), len(duelist_info))
        for i in range(max_rows):
            sorcery_row = sorcery_info[i] if i < len(sorcery_info) else ""
            duelist_row = duelist_info[i] if i < len(duelist_info) else ""
            sorcery_duelist.add_row(sorcery_row, duelist_row)
        
        sheet.append(str(sorcery_duelist))

        self.caller.msg("\n".join(sheet))