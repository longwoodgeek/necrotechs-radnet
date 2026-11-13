import tempfile
import unittest
from pathlib import Path
from radnet.boot import render_boot

class BootTests(unittest.TestCase):
    def test_missing_db_does_not_create_db(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "absent.sqlite3"
            output = render_boot(str(db))
            self.assertFalse(db.exists())
            self.assertIn("No local journal yet", output)
            self.assertIn("AXIS connector not installed", output)

    def test_existing_valid_db(self):
        from radnet.core import EventStore
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "test.sqlite3"
            store = EventStore(str(db))
            store.close()
            self.assertIn("Existing SQLite journal readable", render_boot(str(db)))
