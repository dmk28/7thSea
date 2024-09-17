"""
Server startstop hooks

This module contains functions called by Evennia at various
points during its startup, reload and shutdown sequence. It
allows for customizing the server operation as desired.

This module must contain at least these global functions:

at_server_init()
at_server_start()
at_server_stop()
at_server_reload_start()
at_server_reload_stop()
at_server_cold_start()
at_server_cold_stop()

"""
from evennia import create_script
from world.bboards import BBOARD_HANDLER
from world.dynmap.seamap import init_sea_map
from world.mailsys.cleanup import delete_old_mail
from evennia.utils import gametime
def at_server_init():
    """
    This is called first as the server is starting up, regardless of how.
    """
    create_script("world.scripts.SheetUpdateScript")
    init_sea_map()
    gametime.schedule(delete_old_mail, repeat=True, hour=0, min=0, sec=0, days=15)
    


def at_server_start():
    """
    This is called every time the server starts up, regardless of
    how it was shut down.
    """
    create_script("world.adventuring_guilds.scripts.IncomeCollectionScript")
    initial_boards = ["General", "Announcements", "Roleplay"]
    for board_name in initial_boards:
        if not BBOARD_HANDLER.get_board(board_name):
            BBOARD_HANDLER.create_board(board_name)




def at_server_stop():
    """
    This is called just before the server is shut down, regardless
    of it is for a reload, reset or shutdown.
    """


def at_server_reload_start():
    """
    This is called only when server starts back up after a reload.
    """



def at_server_reload_stop():
    """
    This is called only time the server stops before a reload.
    """
    pass


def at_server_cold_start():
    """
    This is called only when the server starts "cold", i.e. after a
    shutdown or a reset.
    """
    pass


def at_server_cold_stop():
    """
    This is called only when the server goes down due to a shutdown or
    reset.
    """
    pass
