"""Adversarial, persistence and boundary checks for read-only remote boards."""
import hashlib
import socket
import tempfile
import threading
import unittest
from pathlib import Path

from radnet.boards import Boards
from radnet.interactive_doorbell import HOST, serve
from radnet.remote_boards import board_list, post_list, post_detail
from radnet.presentation import render_remote


class RemoteBoardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / "journal.sqlite3"

    def make_board(self, name="General Communications"):
        return Boards(self.db).create_board(name, "SysOp")

    def add_post(self, board, title="First Transmission", body="RadNet operational"):
        return Boards(self.db).post(board, "LongwoodGeek", title, body)

    def test_missing_database_is_not_created(self):
        body, boards = board_list(self.db)
        self.assertEqual(boards, [])
        self.assertIn("No local boards yet.", body)
        self.assertFalse(self.db.exists())

    def test_empty_existing_journal_has_no_boards(self):
        from radnet.core import EventStore
        store = EventStore(self.db)
        store.close()
        body, boards = board_list(self.db)
        self.assertEqual(boards, [])
        self.assertIn("No local boards yet.", body)

    def test_two_boards_have_distinct_ordered_indices(self):
        first = self.make_board("General Communications")
        second = self.make_board("Archive")
        body, boards = board_list(self.db)
        self.assertEqual([b["id"] for b in boards], [first, second])
        self.assertIn("[1] General Communications", body)
        self.assertIn("[2] Archive", body)

    def test_posts_are_isolated_by_board(self):
        first = self.make_board()
        second = self.make_board("Archive")
        self.add_post(first, "Alpha")
        self.add_post(second, "Beta")
        _, a = post_list(self.db, {"id": first, "title": "General Communications"})
        _, b = post_list(self.db, {"id": second, "title": "Archive"})
        self.assertEqual([p["title"] for p in a], ["Alpha"])
        self.assertEqual([p["title"] for p in b], ["Beta"])

    def test_post_detail_has_full_id_and_unverified_author(self):
        board = self.make_board()
        eid = self.add_post(board, body="THE NETWORK REMEMBERS")
        _, posts = post_list(self.db, {"id": board, "title": "General Communications"})
        detail = post_detail(posts[0])
        self.assertIn(eid, detail)
        self.assertIn("[UNVERIFIED]", detail)
        self.assertIn("THE NETWORK REMEMBERS", detail)
        self.assertIn("Reply to: none", detail)

    def test_reply_parent_is_preserved(self):
        board = self.make_board()
        parent = self.add_post(board)
        Boards(self.db).post(board, "The Geese", "Honk?", "HONK!", parent=parent)
        _, posts = post_list(self.db, {"id": board, "title": "General Communications"})
        self.assertIn("Reply to: " + parent, post_detail(posts[1]))

    def test_pagination_ten_then_one(self):
        board = self.make_board()
        for i in range(11):
            self.add_post(board, f"Message {i:02d}")
        selected = {"id": board, "title": "General Communications"}
        first, items1 = post_list(self.db, selected, 1)
        second, items2 = post_list(self.db, selected, 2)
        self.assertEqual((len(items1), len(items2)), (10, 1))
        self.assertIn("PAGE 1", first)
        self.assertIn("PAGE 2", second)
        self.assertEqual(items2[0]["title"], "Message 10")

    def test_empty_page_does_not_invent_posts(self):
        board = self.make_board()
        body, posts = post_list(self.db, {"id": board, "title": "General Communications"}, 2)
        self.assertEqual(posts, [])
        self.assertIn("No posts on this page.", body)

    def test_untrusted_display_text_has_no_escape_sequences(self):
        board = self.make_board("General Communications")
        self.add_post(board, "A\u001b[31mB", "C\u001b[2JD")
        _, posts = post_list(self.db, {"id": board, "title": "General Communications"})
        self.assertNotIn("\u001b", post_detail(posts[0]))
        self.assertNotIn("\u001b", render_remote(post_detail(posts[0]), 24))

    def test_rendered_post_is_bounded_to_small_screen(self):
        board = self.make_board()
        self.add_post(board, "T" * 100, "X" * 4000)
        _, posts = post_list(self.db, {"id": board, "title": "General Communications"})
        output = render_remote(post_detail(posts[0]), 24)
        self.assertTrue(all(len(line) <= 24 for line in output.splitlines()))

    def test_read_only_views_preserve_database_hash(self):
        board = self.make_board()
        self.add_post(board)
        before = hashlib.sha256(self.db.read_bytes()).hexdigest()
        body, boards = board_list(self.db)
        _, posts = post_list(self.db, boards[0])
        post_detail(posts[0])
        self.assertIn("General Communications", body)
        self.assertEqual(before, hashlib.sha256(self.db.read_bytes()).hexdigest())


class RemoteBoardSessionTests(RemoteBoardTests):
    def setUp(self):
        super().setUp()
        self.stop = threading.Event()
        self.ready = threading.Event()
        self.port = None

        def announced(port):
            self.port = port
            self.ready.set()

        self.thread = threading.Thread(
            target=serve, args=(str(self.db),),
            kwargs={"ready": announced, "stop": self.stop}, daemon=True
        )
        self.thread.start()
        self.addCleanup(self.stop.set)
        self.addCleanup(self.thread.join, 2)
        self.assertTrue(self.ready.wait(2))

    def session(self, selections):
        with socket.create_connection((HOST, self.port), timeout=3) as s:
            s.settimeout(5)
            s.sendall(selections)
            s.shutdown(socket.SHUT_WR)
            parts = []
            while True:
                chunk = s.recv(8192)
                if not chunk:
                    break
                parts.append(chunk)
        return b"".join(parts).decode()

    def test_complete_two_post_navigation(self):
        board = self.make_board()
        self.add_post(board)
        self.add_post(board, "Honk?", "HONK!")
        before = hashlib.sha256(self.db.read_bytes()).hexdigest()
        result = self.session(b"1\n1\n2\n0\n0\n0\n0\n")
        self.assertIn("General Communications", result)
        self.assertIn("Honk?", result)
        self.assertIn("HONK!", result)
        self.assertIn("Disconnected.", result)
        self.assertTrue(all(len(line) <= 36 for line in result.splitlines()))
        self.assertEqual(before, hashlib.sha256(self.db.read_bytes()).hexdigest())

    def test_invalid_board_selection_does_not_change_screen(self):
        self.make_board()
        result = self.session(b"1\n9\n1\n0\n0\n0\n")
        self.assertIn("Unknown selection.", result)
        self.assertIn("BOARD: General Communications", result)
        self.assertIn("Disconnected.", result)

    def test_invalid_post_selection_does_not_change_screen(self):
        board = self.make_board()
        self.add_post(board)
        result = self.session(b"1\n1\n9\n1\n0\n0\n0\n0\n")
        self.assertIn("Unknown selection.", result)
        self.assertIn("RadNet operational", result)
        self.assertIn("Disconnected.", result)

    def test_next_page_and_previous_page(self):
        board = self.make_board()
        for i in range(11):
            self.add_post(board, f"Message {i:02d}")
        result = self.session(b"1\n1\n>\n1\n0\n<\n1\n0\n0\n0\n0\n")
        self.assertIn("POSTS // PAGE 2", result)
        self.assertIn("Message 10", result)
        self.assertIn("POSTS // PAGE 1", result)
        self.assertIn("Message 00", result)
        self.assertIn("Disconnected.", result)

    def test_next_page_rejected_without_ten_posts(self):
        board = self.make_board()
        self.add_post(board)
        result = self.session(b"1\n1\n>\n0\n0\n0\n")
        self.assertIn("Unknown selection.", result)
        self.assertNotIn("POSTS // PAGE 2", result)
        self.assertIn("Disconnected.", result)

    def test_previous_page_rejected_on_first_page(self):
        board = self.make_board()
        self.add_post(board)
        result = self.session(b"1\n1\n<\n0\n0\n0\n")
        self.assertIn("Unknown selection.", result)
        self.assertIn("Disconnected.", result)

    def test_shell_like_input_in_nested_menu_is_not_executed(self):
        self.make_board()
        result = self.session(b"1\n$(touch /tmp/radnet-do-not-create)\n0\n0\n")
        self.assertIn("No commands executed.", result)
        self.assertIn("Disconnected.", result)

    def test_non_ascii_numeric_selection_is_rejected(self):
        self.make_board()
        result = self.session("1\n\u0661\n0\n0\n".encode())
        self.assertIn("Unknown selection.", result)
        self.assertIn("Disconnected.", result)

    def test_oversized_nested_selection_disconnects(self):
        self.make_board()
        result = self.session(b"1\n" + b"X" * 100 + b"\n")
        self.assertIn("Input too long.", result)

    def test_each_connection_starts_at_main(self):
        self.make_board()
        first = self.session(b"1\n0\n0\n")
        second = self.session(b"2\n0\n")
        self.assertIn("MESSAGE BOARDS", first)
        self.assertIn("STATION STATUS", second)
        self.assertNotIn("Unknown selection.", second)

    def test_empty_board_navigation_can_return_and_disconnect(self):
        result = self.session(b"1\n0\n0\n")
        self.assertIn("No local boards yet.", result)
        self.assertIn("Disconnected.", result)
        self.assertFalse(self.db.exists())


if __name__ == "__main__":
    unittest.main()
