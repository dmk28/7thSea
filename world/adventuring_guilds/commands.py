from evennia import Command
from .handlers import AdventuringGuildHandler
from evennia.utils.create import create_object
from .models import AdventuringGuild, Holding
from typeclasses.holdings import Holding as HoldingTypeClass


class CmdCreateGuild(Command):
    """
    Create a new adventuring guild.

    Usage:
      createguild <name> = <description>

    Creates a new adventuring guild with the given name and description.
    """
    key = "createguild"
    locks = "cmd:perm(Wizards)"
    help_category = "Admin"

    def func(self):
        if not self.args or "=" not in self.args:
            self.caller.msg("Usage: createguild <name> = <description>")
            return

        name, description = self.args.split("=", 1)
        name = name.strip()
        description = description.strip()

        if AdventuringGuildHandler.get_guild(name):
            self.caller.msg(f"A guild named '{name}' already exists.")
            return

        guild = AdventuringGuildHandler.create_guild(name, description)
        self.caller.msg(f"Created new guild: {guild.db_name}")

class CmdJoinGuild(Command):
    """
    Join an adventuring guild.

    Usage:
      joinguild <guild name>

    Joins the specified adventuring guild.
    """
    key = "joinguild"
    locks = "cmd:all()"
    help_category = "Adventuring"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: joinguild <guild name>")
            return

        guild_name = self.args.strip()
        if AdventuringGuildHandler.add_member_to_guild(guild_name, self.caller):
            self.caller.msg(f"You have joined the {guild_name} guild.")
        else:
            self.caller.msg(f"Could not join the guild '{guild_name}'. It may not exist.")

class CmdLeaveGuild(Command):
    """
    Leave an adventuring guild.

    Usage:
      leaveguild <guild name>

    Leaves the specified adventuring guild.
    """
    key = "leaveguild"
    locks = "cmd:all()"
    help_category = "Adventuring"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: leaveguild <guild name>")
            return

        guild_name = self.args.strip()
        if AdventuringGuildHandler.remove_member_from_guild(guild_name, self.caller):
            self.caller.msg(f"You have left the {guild_name} guild.")
        else:
            self.caller.msg(f"Could not leave the guild '{guild_name}'. You may not be a member or it may not exist.")

class CmdListGuilds(Command):
    """
    List all adventuring guilds.

    Usage:
      listguilds

    Shows a list of all existing adventuring guilds.
    """
    key = "listguilds"
    locks = "cmd:all()"
    help_category = "Adventuring"

    def func(self):
        guilds = AdventuringGuildHandler.get_all_guilds()
        if guilds:
            self.caller.msg("Adventuring Guilds:")
            for guild in guilds:
                self.caller.msg(f"- {guild.db_name}: {guild.db_description}")
        else:
            self.caller.msg("There are no adventuring guilds.")

class CmdMyGuilds(Command):
    """
    List guilds you're a member of.

    Usage:
      myguilds

    Shows a list of all adventuring guilds you're a member of.
    """
    key = "myguilds"
    locks = "cmd:all()"
    help_category = "Adventuring"

    def func(self):
        guilds = AdventuringGuildHandler.get_character_guilds(self.caller)
        if guilds:
            self.caller.msg("You are a member of the following guilds:")
            for guild in guilds:
                self.caller.msg(f"- {guild.db_name}")
        else:
            self.caller.msg("You are not a member of any adventuring guilds.")

class CmdCreateHolding(Command):
    """
    Create a new holding for an adventuring guild.

    Usage:
      createholding <guild_name> = <holding_type>, <income_type>, <custom_name>

    Available holding types: tavern, workshop, farm, mine
    Income types: guilders, doubloons

    Example:
      createholding Adventurers Guild = tavern, guilders, The Golden Goblin
    """
    key = "createholding"
    locks = "cmd:perm(Wizards)"
    help_category = "Admin"

    def func(self):
        if not self.args or "=" not in self.args:
            self.caller.msg("Usage: createholding <guild_name> = <holding_type>, <income_type>, <custom_name>")
            return

        guild_name, holding_info = self.args.split("=", 1)
        guild_name = guild_name.strip()
        holding_info = holding_info.strip().split(",")

        if len(holding_info) != 3:
            self.caller.msg("Invalid holding information. Please provide holding type, income type, and custom name.")
            return

        holding_type, income_type, custom_name = map(str.strip, holding_info)

        if holding_type not in HoldingTypeclass.HOLDING_TYPES:
            self.caller.msg(f"Invalid holding type. Available types: {', '.join(HoldingTypeclass.HOLDING_TYPES.keys())}")
            return

        if income_type not in ["guilders", "doubloons"]:
            self.caller.msg("Income type must be either 'guilders' or 'doubloons'.")
            return

        guild = AdventuringGuild.objects.filter(db_name=guild_name).first()
        if not guild:
            self.caller.msg(f"Guild '{guild_name}' not found.")
            return

        type_data = HoldingTypeclass.HOLDING_TYPES[holding_type]
        holding_data = {
            "name": type_data["name"],
            "custom_name": custom_name,
            "holding_type": holding_type,
            "description": type_data["description"],
            "base_income": type_data["base_income"],
            "upgrade_cost": type_data["upgrade_cost"],
            "upgrade_multiplier": type_data["upgrade_multiplier"],
            "income_type": income_type,
        }

        holding_model = guild.add_holding(holding_data)
        
        # Create the typeclass and link it to the model
        holding_obj = create_object(HoldingTypeclass, key=custom_name)
        holding_obj.link_model(holding_model)

        self.caller.msg(f"Created {holding_type} holding '{custom_name}' for guild '{guild_name}'.")

class CmdListHoldings(Command):
    """
    List all holdings of an adventuring guild.

    Usage:
      listholdings <guild_name>
    """
    key = "listholdings"
    locks = "cmd:all()"
    help_category = "Adventuring"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: listholdings <guild_name>")
            return

        guild_name = self.args.strip()
        try:
            guild = AdventuringGuild.objects.get(db_name=guild_name)
        except AdventuringGuild.DoesNotExist:
            self.caller.msg(f"Guild '{guild_name}' not found.")
            return

        holdings = Holding.objects.filter(owning_guild=guild)
        if not holdings:
            self.caller.msg(f"Guild '{guild_name}' has no holdings.")
            return

        table = self.styled_table("Name", "Type", "Level", "Income", "Specialization", "Staff", "Events")
        for holding in holdings:
            details = holding.get_details()
            table.add_row(
                details["name"],
                details["type"],
                details["level"],
                f"{details['income_rate']} {details['income_type']}/day",
                details["specialization"] or "None",
                len(details["staff"]),
                len(details["events"])
            )

        self.caller.msg(f"Holdings of {guild_name}:")
        self.caller.msg(str(table))



class CmdUpgradeHolding(Command):
    """
    Upgrade a holding of an adventuring guild.

    Usage:
      upgradeholding <guild_name> = <holding_name>
    """
    key = "upgradeholding"
    locks = "cmd:all()"
    help_category = "Adventuring"

    def func(self):
        if not self.args or "=" not in self.args:
            self.caller.msg("Usage: upgradeholding <guild_name> = <holding_name>")
            return

        guild_name, holding_name = self.args.split("=", 1)
        guild_name = guild_name.strip()
        holding_name = holding_name.strip()

        guild = AdventuringGuild.objects.filter(db_name=guild_name).first()
        if not guild:
            self.caller.msg(f"Guild '{guild_name}' not found.")
            return

        holding = guild.db_holdings.filter(db_key=holding_name).first()
        if not holding:
            self.caller.msg(f"Holding '{holding_name}' not found in guild '{guild_name}'.")
            return

        success, message = holding.upgrade()
        self.caller.msg(message)
        if success:
            self.caller.msg(f"New income rate: {holding.calculate_income_rate()} {holding.db.income_type} per day.")

class CmdHoldingDetails(Command):
    """
    View detailed information about a specific holding.

    Usage:
      holdingdetails <guild_name> = <holding_name>
    """
    key = "holdingdetails"
    locks = "cmd:all()"
    help_category = "Adventuring"

    def func(self):
        if not self.args or "=" not in self.args:
            self.caller.msg("Usage: holdingdetails <guild_name> = <holding_name>")
            return

        guild_name, holding_name = self.args.split("=", 1)
        guild_name = guild_name.strip()
        holding_name = holding_name.strip()

        guild = AdventuringGuild.objects.filter(db_name=guild_name).first()
        if not guild:
            self.caller.msg(f"Guild '{guild_name}' not found.")
            return

        holding = guild.db_holdings.filter(db_key=holding_name).first()
        if not holding:
            self.caller.msg(f"Holding '{holding_name}' not found in guild '{guild_name}'.")
            return

        details = holding.get_details()
        self.caller.msg(f"Details for {details['name']}:")
        self.caller.msg(f"Type: {details['type']}")
        self.caller.msg(f"Description: {details['description']}")
        self.caller.msg(f"Level: {details['level']}")
        self.caller.msg(f"Income: {details['income_rate']} {details['income_type']}/day")
        self.caller.msg(f"Upgrade Cost: {details['upgrade_cost']} {details['income_type']}")
        self.caller.msg(f"Specialization: {details['specialization'] or 'None'}")
        self.caller.msg(f"Staff: {', '.join(details['staff']) if details['staff'] else 'None'}")
        self.caller.msg(f"Active Events: {', '.join(details['events']) if details['events'] else 'None'}")
