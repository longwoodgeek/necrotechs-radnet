"""Station status presentation remains honest and non-destructive."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from radnet.station import initialize
from radnet.terminal import station_status

class StationStatusTests(unittest.TestCase):
    def test_missing_identity_and_database_are_not_created(self):
        with TemporaryDirectory() as tmp:
            db = Path(tmp) / "empty.sqlite3"
            output = station_status(db)
            self.assertIn("NOT CONFIGURED", output)
            self.assertIn("NETWORK CONNECTIVITY: NOT VERIFIED", output)
            self.assertFalse(db.exists())
            self.assertFalse((Path(tmp) / "radnet-station.json").exists())

    def test_configured_identity_and_humor(self):
        with TemporaryDirectory() as tmp:
            db = Path(tmp) / "empty.sqlite3"
            identity = initialize(Path(tmp) / "radnet-station.json", "LGL-CyberDeck-DEV-001")
            output = station_status(db)
            self.assertIn(identity["station_id"], output)
            self.assertIn("DRINKING PRIVILEGES: DENIED", output)
            self.assertIn("LOCAL / UNVERIFIED", output)
            self.assertFalse(db.exists())

    def test_corrupt_identity_never_claims_present(self):
        with TemporaryDirectory() as tmp:
            db = Path(tmp) / "empty.sqlite3"
            (Path(tmp) / "radnet-station.json").write_text("broken")
            output = station_status(db)
            self.assertIn("IDENTIFICATION: INVALID / UNREADABLE", output)
            self.assertNotIn("IDENTIFICATION: PRESENT", output)

if __name__ == "__main__":
    unittest.main()
