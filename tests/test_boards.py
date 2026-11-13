import tempfile
import unittest
from pathlib import Path
from radnet.boards import Boards, BoardError

class BoardTests(unittest.TestCase):
    def test_create_post_reopen_and_reply(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "bbs.sqlite3"
            b = Boards(path)
            board = b.create_board("General", "Longwood")
            first = b.post(board, "Longwood", "Welcome", "THE NETWORK REMEMBERS")
            b.post(board, "Guest", "Re: Welcome", "Copy that", parent=first)
            reopened = Boards(path)
            self.assertEqual(reopened.boards()[0]["title"], "General")
            self.assertEqual(len(reopened.messages(board)), 2)
            self.assertEqual(reopened.messages(board)[1]["parent"], first)

    def test_invalid_board_rejected_without_db_creation(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "missing.sqlite3"
            with self.assertRaises(BoardError):
                Boards(path).post("bad", "Guest", "Hi", "Hello")
            self.assertFalse(path.exists())

    def test_bounded_inputs(self):
        with tempfile.TemporaryDirectory() as td:
            b = Boards(Path(td) / "bbs.sqlite3")
            with self.assertRaises(BoardError):
                b.create_board("X" * 101, "Guest")
            board = b.create_board("General", "Guest")
            with self.assertRaises(BoardError):
                b.post(board, "Guest", "Hi", "A" * 4001)
            with self.assertRaises(BoardError):
                b.post(board, "Guest", "Hi", "\x1b[31m")

    def test_cross_board_reply_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            b = Boards(Path(td) / "bbs.sqlite3")
            a = b.create_board("A", "Guest")
            c = b.create_board("C", "Guest")
            first = b.post(a, "Guest", "Hello", "A")
            with self.assertRaises(BoardError):
                b.post(c, "Guest", "Re", "No", parent=first)

    def test_page_bounds(self):
        with tempfile.TemporaryDirectory() as td:
            b = Boards(Path(td) / "bbs.sqlite3")
            board = b.create_board("General", "Guest")
            for i in range(11):
                b.post(board, "Guest", f"Post {i}", "Message")
            self.assertEqual(len(b.messages(board, 1)), 10)
            self.assertEqual(len(b.messages(board, 2)), 1)
            with self.assertRaises(BoardError):
                b.messages(board, 0)

if __name__ == "__main__":
    unittest.main()
