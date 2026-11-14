import tempfile
import unittest
from pathlib import Path
from radnet.terminal import page, run
from radnet.capabilities import append_evidence
from radnet.capability_screen import evidence_listing, evidence_path


class CapabilityScreenTests(unittest.TestCase):
    def test_empty_dashboard_does_not_create_files(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "missing.sqlite3"
            screen = page("7", db)
            self.assertIn("EVIDENCE RECORDS: 0", screen)
            self.assertIn("NOT CONNECTED", screen)
            self.assertIn("NOT LIVE-VERIFIED", screen)
            self.assertFalse(db.exists())
            self.assertFalse(evidence_path(db).exists())

    def test_historical_success_not_live_status(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "bbs.sqlite3"
            append_evidence(evidence_path(db), "reticulum.local", "pass", "simulation", "unit-test")
            screen = page("7", db)
            self.assertIn("1 historical observation(s)", screen)
            self.assertIn("LIVE VERIFICATION: NONE", screen)
            listing = evidence_listing(db)
            self.assertIn("simulation", listing)
            self.assertIn("NOT PROOF OF CURRENT CONNECTIVITY", listing)

    def test_unreadable_evidence_is_error_not_empty(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "bbs.sqlite3"
            evidence_path(db).write_text("{bad json}", encoding="utf-8")
            self.assertIn("[ERROR]", page("7", db))
            self.assertIn("[ERROR]", evidence_listing(db))

    def test_interactive_option_and_return(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "missing.sqlite3"
            output = []
            selections = iter(["7", "1", "0"])
            run(db, input_fn=lambda prompt: next(selections), output_fn=output.append)
            rendered = "\n".join(output)
            self.assertIn("CAPABILITY REGISTRY", rendered)
            self.assertIn("No evidence recorded.", rendered)
            self.assertFalse(db.exists())


if __name__ == "__main__":
    unittest.main()
