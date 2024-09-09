"""

Lockfuncs

Lock functions are functions available when defining lock strings,
which in turn limits access to various game systems.

All functions defined globally in this module are assumed to be
available for use in lockstrings to determine access. See the
Evennia documentation for more info on locks.

A lock function is always called with two arguments, accessing_obj and
accessed_obj, followed by any number of arguments. All possible
arguments should be handled with *args, **kwargs. The lock function
should handle all eventual tracebacks by logging the error and
returning False.

Lock functions in this module extend (and will overload same-named)
lock functions from evennia.locks.lockfuncs.

"""

# def myfalse(accessing_obj, accessed_obj, *args, **kwargs):
#    """
#    called in lockstring with myfalse().
#    A simple logger that always returns false. Prints to stdout
#    for simplicity, should use utils.logger for real operation.
#    """
#    print "%s tried to access %s. Access denied." % (accessing_obj, accessed_obj)
#    return False

def has_nationality(accessing_obj, accessed_obj, *args, **kwargs):
    if hasattr(accessing_obj, 'character_sheet'):
        return accessing_obj.character_sheet.nationality == args[0]
    elif hasattr(accessing_obj.db, 'nationality'):
        return accessing_obj.db.nationality == args[0]
    return False
def has_guild_rank(accessing_obj, accessed_obj, *args, **kwargs):
    guild = accessed_obj
    if not isinstance(guild, AdventuringGuild):
        return False
    min_rank, max_rank = map(int, args[0].split('-'))
    member_rank = guild.get_member_rank_level(accessing_obj)
    return min_rank <= member_rank <= max_rank
def is_castillian(accessing_obj, accessed_obj, *args, **kwargs):
    return (hasattr(accessing_obj, 'character') and 
            accessing_obj.character and 
            accessing_obj.character.db.nationality == "Castille")

def is_montaigne(accessing_obj, accessed_obj, *args, **kwargs):
    return (hasattr(accessing_obj, 'character') and 
            accessing_obj.character and 
            accessing_obj.character.db.nationality == "Montaigne")
def is_vodacce(accessing_obj, accessed_obj, *args, **kwargs):
    return (hasattr(accessing_obj, 'character') and 
            accessing_obj.character and 
            accessing_obj.character.db.nationality == "Vodacce")    
def is_eisen(accessing_obj, accessed_obj, *args, **kwargs):
    return (hasattr(accessing_obj, 'character') and 
            accessing_obj.character and
            accessing_obj.character.db.nationality == "Eisen")
