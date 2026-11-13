import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from radnet.core import EventStore
from radnet.terminal import interactive_boards, page, read_events, run

class TerminalTests(unittest.TestCase):
    def test_missing_db_is_not_created(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "absent.sqlite3"
            self.assertIn("No local journal", page("1", str(db)))
            self.assertFalse(db.exists())

    def test_existing_message_visible(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "journal.sqlite3"
            store = EventStore(db)
            store.append("message.create", "Longwood", "The Network Remembers")
            store.close()
            self.assertIn("The Network Remembers", page("1", str(db)))

    def test_read_only_session(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "absent.sqlite3"
            output = []
            choices = iter(["2", "6", "0"])
            run(str(db), input_fn=lambda prompt: next(choices), output_fn=output.append)
            self.assertFalse(db.exists())
            self.assertIn("NOT AN EMERGENCY SERVICE", "\n".join(output))
            self.assertIn("Disconnecting", "\n".join(output))

    def test_session_describes_local_posting_and_unverified_identity(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "absent.sqlite3"
            output = []
            choices = iter(["2", "0"])
            run(db, input_fn=lambda prompt: next(choices), output_fn=output.append)
            text = "\n".join(output)
            self.assertIn("v0.4", text)
            self.assertIn("LOCAL POSTING ENABLED", text)
            self.assertIn("AUTHORS UNVERIFIED", text)
            self.assertIn("Identity: NOT VERIFIED", text)
            self.assertIn("Transport: NOT CONNECTED", text)
            self.assertNotIn("READ-ONLY", text)
            self.assertFalse(db.exists())

    def test_board_console_renders_lines_and_persists_posts_and_replies(self):
        # Escaped output separators must fail independently at every display site.
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "bbs.sqlite3"
            output = []
            choices = iter(["1", "n", "LongwoodGeek", "General Communications",
                            "1", "n", "LongwoodGeek", "First Transmission",
                            "RadNet operational", "0", "0", "0"])
            run(db, input_fn=lambda prompt: next(choices), output_fn=output.append)
            self.assertIn("\nBOARDS:", output)
            self.assertIn("\nGeneral Communications // PAGE 1", output)
            choices = iter(["1", "1", "1", "y", "LongwoodGeek",
                            "The Archive is alive!", "0", "0", "0"])
            run(db, input_fn=lambda prompt: next(choices), output_fn=output.append)
            self.assertIn("\nFirst Transmission", output)
            self.assertIn("By LongwoodGeek [UNVERIFIED]", output)
            self.assertIn("Reply saved locally.", output)
            self.assertFalse(any(r"\n" in line for line in output))
            from radnet.boards import Boards
            service = Boards(db)
            items = service.messages(service.boards()[0]["id"])
            self.assertEqual([item["body"] for item in items],
                             ["RadNet operational", "The Archive is alive!"])
            self.assertEqual(items[1]["parent"], items[0]["id"])
            store = EventStore(db)
            try:
                self.assertEqual(store.verify(), [])
            finally:
                store.close()

    def test_board_console_interruption_uses_real_newline_without_creating_db(self):
        for exception in (EOFError, KeyboardInterrupt):
            with self.subTest(exception=exception), tempfile.TemporaryDirectory() as td:
                db = Path(td) / "absent.sqlite3"
                output = []
                def interrupted(prompt):
                    raise exception()
                interactive_boards(db, interrupted, output.append)
                self.assertIn("\nBoard console closed.", output)
                self.assertFalse(db.exists())

    def test_terminal_help_describes_local_posting(self):
        result = subprocess.run([sys.executable, "-m", "radnet", "--help"],
                                capture_output=True, text=True, check=True)
        self.assertIn("local posting", result.stdout)
        self.assertNotIn("read-only BBS", result.stdout)

    def test_unknown_choice(self):
        self.assertIn("Unknown command", page("9", "unused.sqlite3"))

    def test_no_shell_commands(self):
        self.assertIn("Unknown command", page("!sh", "unused.sqlite3"))

if __name__ == "__main__":
    unittest.main()
