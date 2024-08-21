from evennia import DefaultScript
from evennia.utils import create
from evennia.utils.utils import lazy_property
from django.utils import timezone

class BBoard(DefaultScript):
    """
    This script holds one bulletin board and its posts.
    """

    def at_script_creation(self):
        self.db.board_name = "General"
        self.db.posts = []

    def create_post(self, poster, subject, text):
        post = {
            "poster": poster,
            "subject": subject,
            "text": text,
            "date": timezone.now(),
            "read_by": set()
        }
        self.db.posts.append(post)
        return len(self.db.posts) - 1  # Return the index of the new post

    def get_post(self, post_num):
        try:
            return self.db.posts[post_num]
        except IndexError:
            return None

    def edit_post(self, post_num, new_text):
        try:
            self.db.posts[post_num]["text"] = new_text
            self.db.posts[post_num]["date"] = timezone.now()
            return True
        except IndexError:
            return False

    def delete_post(self, post_num):
        try:
            del self.db.posts[post_num]
            return True
        except IndexError:
            return False

    def mark_read(self, reader, post_num):
        try:
            self.db.posts[post_num]["read_by"].add(reader)
            return True
        except IndexError:
            return False

class BboardHandler(DefaultScript):
    """
    This handler manages all bulletin boards.
    """
    def at_script_creation(self):
        self.key = "bboard_handler"
        self.persistent = True
        self.db.boards = {}

    def at_start(self):
        self.load_boards()

    def load_boards(self):
        for script in BBoard.objects.all():
            self.db.boards[script.db.board_name] = script

    def create_board(self, board_name):
        if board_name in self.db.boards:
            return False
        board = create.create_script("world.bboards.BBoard", key=f"bboard_{board_name}")
        board.db.board_name = board_name
        self.db.boards[board_name] = board
        return True

    def get_board(self, board_name):
        return self.db.boards.get(board_name)

    def list_boards(self):
        return list(self.db.boards.keys())

    def post_message(self, board_name, poster, subject, text):
        board = self.get_board(board_name)
        if board:
            return board.create_post(poster, subject, text)
        return None

    def get_messages(self, board_name):
        board = self.get_board(board_name)
        if board:
            return board.db.posts
        return []

def get_or_create_bboard_handler():
    handler = BboardHandler.objects.first()
    if not handler:
        handler = create.create_script(BboardHandler)
    return handler

BBOARD_HANDLER = get_or_create_bboard_handler()