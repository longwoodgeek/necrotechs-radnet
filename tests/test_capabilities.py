import tempfile
import unittest
from pathlib import Path
from radnet.capabilities import append_evidence, read_evidence, describe_capability, CapabilityError


class CapabilityEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "evidence.jsonl"

    def test_missing_file_is_empty_and_not_created(self):
        self.assertEqual(read_evidence(self.path), [])
        self.assertFalse(self.path.exists())

    def test_append_preserves_failures(self):
        append_evidence(self.path, "reticulum.local", "fail", "manual", "operator")
        append_evidence(self.path, "reticulum.local", "pass", "automated", "test")
        self.assertEqual([x["result"] for x in read_evidence(self.path)], ["fail", "pass"])

    def test_simulation_is_explicit(self):
        item = append_evidence(self.path, "linkprobe.rtt", "pass", "simulation", "test-suite")
        self.assertEqual(item["method"], "simulation")

    def test_history_never_implies_live_state(self):
        append_evidence(self.path, "reticulum.local", "pass", "manual", "operator")
        state = describe_capability(read_evidence(self.path), "reticulum.local")
        self.assertEqual(state["operational_now"], "NOT VERIFIED")

    def test_bad_identifiers_do_not_create_file(self):
        for value in ("", "../identity", "bad name", "bad\nname"):
            with self.assertRaises(CapabilityError):
                append_evidence(self.path, value, "pass", "manual", "operator")
        self.assertFalse(self.path.exists())

    def test_invalid_method_does_not_create_file(self):
        with self.assertRaises(CapabilityError):
            append_evidence(self.path, "radio", "pass", "real_rf", "operator")
        self.assertFalse(self.path.exists())

    def test_malformed_history_is_rejected(self):
        self.path.write_text("{bad json}\n", encoding="utf-8")
        with self.assertRaises(CapabilityError):
            read_evidence(self.path)

    def test_separate_from_station_identity(self):
        append_evidence(self.path, "station.test", "unknown", "manual", "operator")
        self.assertFalse((Path(self.tmp.name) / "radnet-station.json").exists())


if __name__ == "__main__":
    unittest.main()
