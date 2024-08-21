from evennia import Command
from evennia.utils import evtable
from .bboards import BBOARD_HANDLER
from evennia import CmdSet
class CmdBBoardList(Command):
    """
    List all available bulletin boards.

    Usage:
      bboards
    """
    key = "bboards"
    aliases = ["boards", "bb"]

    def func(self):
        boards = BBOARD_HANDLER.list_boards()
        if not boards:
            self.caller.msg("No bulletin boards available.")
        else:
            table = evtable.EvTable("Board Name", "Unread Posts", border="cells")
            for board_name in boards:
                board = BBOARD_HANDLER.get_board(board_name)
                unread = sum(1 for post in board.db.posts if self.caller not in post["read_by"])
                table.add_row(board_name, str(unread))
            self.caller.msg(table)

class CmdBBoardRead(Command):
    """
    Read posts on a bulletin board.

    Usage:
      bread <board_name> [<post_num>]
    """
    key = "bread"
    aliases = ["read"]

    def func(self):
        if not self.args:
            self.caller.msg("Usage: bread <board_name> [<post_num>]")
            return

        args = self.args.split()
        board_name = args[0]
        board = BBOARD_HANDLER.get_board(board_name)

        if not board:
            self.caller.msg(f"Board '{board_name}' not found.")
            return

        if len(args) == 1:
            # List all posts on the board
            table = evtable.EvTable("Num", "Subject", "Poster", "Date", border="cells")
            for i, post in enumerate(board.db.posts):
                table.add_row(
                    str(i + 1),
                    post["subject"],
                    post["poster"].key,
                    post["date"].strftime("%Y-%m-%d %H:%M")
                )
            self.caller.msg(table)
        else:
            try:
                post_num = int(args[1]) - 1
                post = board.get_post(post_num)
                if post:
                    self.caller.msg(f"Subject: {post['subject']}")
                    self.caller.msg(f"Poster: {post['poster'].key}")
                    self.caller.msg(f"Date: {post['date'].strftime('%Y-%m-%d %H:%M')}")
                    self.caller.msg(f"Message:\n{post['text']}")
                    board.mark_read(self.caller, post_num)
                else:
                    self.caller.msg("Invalid post number.")
            except ValueError:
                self.caller.msg("Invalid post number.")

class CmdBBoardPost(Command):
    """
    Post a message to a bulletin board.

    Usage:
      bpost <board_name>/<subject> = <message>
    """
    key = "bpost"
    aliases = ["post"]

    def func(self):
        if "=" not in self.args:
            self.caller.msg("Usage: bpost <board_name>/<subject> = <message>")
            return

        header, message = [part.strip() for part in self.args.split("=", 1)]
        if "/" not in header:
            self.caller.msg("Usage: bpost <board_name>/<subject> = <message>")
            return

        board_name, subject = [part.strip() for part in header.split("/", 1)]
        board = BBOARD_HANDLER.get_board(board_name)

        if not board:
            self.caller.msg(f"Board '{board_name}' not found.")
            return

        post_num = BBOARD_HANDLER.post_message(board_name, self.caller, subject, message)
        if post_num is not None:
            self.caller.msg(f"Posted message {post_num + 1} to {board_name}.")
        else:
            self.caller.msg("Failed to post message.")

class BBoardCmdSet(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdBBoardList())
        self.add(CmdBBoardRead())
        self.add(CmdBBoardPost())