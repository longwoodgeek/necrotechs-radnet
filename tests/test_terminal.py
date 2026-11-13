import io
import tempfile
import unittest
from pathlib import Path
from radnet.core import EventStore
from radnet.terminal import page, read_events, run

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

    def test_unknown_choice(self):
        self.assertIn("Unknown command", page("9", "unused.sqlite3"))

    def test_no_shell_commands(self):
        self.assertIn("Unknown command", page("!sh", "unused.sqlite3"))

if __name__ == "__main__":
    unittest.main()
