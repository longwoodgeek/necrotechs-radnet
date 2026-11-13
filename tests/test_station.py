"""Station identity invariants: explicit creation, persistence, no silent regeneration."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from radnet.station import initialize, load, status, StationError

class StationIdentityTests(unittest.TestCase):
    def test_explicit_creation_and_restart(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "station.json"
            self.assertIsNone(load(path))
            first = initialize(path, "LGL-CyberDeck-DEV-001")
            self.assertEqual(load(path), first)
            self.assertIn(first["station_id"], status(path))
            with self.assertRaises(FileExistsError):
                initialize(path, "replacement")
            self.assertEqual(load(path), first)

    def test_bad_labels_rejected_without_creating_file(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "station.json"
            for label in ("", "x" * 65, "bad\\nlabel", 42):
                with self.subTest(label=label):
                    with self.assertRaises(StationError):
                        initialize(path, label)
                    self.assertFalse(path.exists())

    def test_corrupt_identity_not_regenerated(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "station.json"
            path.write_text('{"schema":1,"station_id":"fake","label":"A"}')
            with self.assertRaises(StationError):
                load(path)
            self.assertIn("INVALID", status(path))
            self.assertEqual(json.loads(path.read_text())["station_id"], "fake")

    def test_status_does_not_claim_network_or_authentication(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "station.json"
            self.assertIn("NOT CONFIGURED", status(path))
            initialize(path, "Test")
            self.assertIn("NOT VERIFIED", status(path))
            self.assertIn("NOT IMPLEMENTED", status(path))

if __name__ == "__main__":
    unittest.main()
