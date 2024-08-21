from .models import AdventuringGuild

class AdventuringGuildHandler:
    """
    Handler for managing Adventuring Guilds.
    """
    @classmethod
    def create_guild(cls, name, description=""):
        return AdventuringGuild.objects.create(db_name=name, db_description=description)

    @classmethod
    def get_guild(cls, name):
        return AdventuringGuild.objects.filter(db_name=name).first()

    @classmethod
    def get_all_guilds(cls):
        return AdventuringGuild.objects.all()

    @classmethod
    def delete_guild(cls, name):
        guild = cls.get_guild(name)
        if guild:
            guild.delete()
            return True
        return False

    @classmethod
    def add_member_to_guild(cls, guild_name, character):
        guild = cls.get_guild(guild_name)
        if guild:
            try:
                guild.add_member(character)
                return True
            except ValueError:
                return False
        return False

    @classmethod
    def remove_member_from_guild(cls, guild_name, character):
        guild = cls.get_guild(guild_name)
        if guild:
            guild.remove_member(character)
            return True
        return False

    @classmethod
    def get_character_guilds(cls, character):
        return character.adventuring_guilds.all()

    @classmethod
    def is_member_of_guild(cls, guild_name, character):
        guild = cls.get_guild(guild_name)
        return guild.is_member(character) if guild else False

    @classmethod
    def get_guild_members(cls, guild_name):
        guild = cls.get_guild(guild_name)
        return guild.character_members.all() if guild else []