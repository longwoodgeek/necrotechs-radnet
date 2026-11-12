"""Run: python -m unittest discover -s tests -v"""
import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("linkprobe", Path(__file__).resolve().parents[1] / "tools" / "linkprobe.py")
linkprobe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(linkprobe)

class LinkProbeTests(unittest.TestCase):
    def test_synthetic_repeatability(self):
        a = linkprobe.simulate(count=10, seed=42, loss=.3)
        b = linkprobe.simulate(count=10, seed=42, loss=.3)
        self.assertEqual([(r["acknowledged"],r["rtt_ms"]) for r in a],
                         [(r["acknowledged"],r["rtt_ms"]) for r in b])
        self.assertEqual({r["mode"] for r in a}, {"simulation"})

    def test_summary_and_duplicate_rejection(self):
        rows = linkprobe.simulate(count=3, loss=0)
        self.assertEqual(linkprobe.summarize(rows)["acknowledged"], 3)
        self.assertAlmostEqual(linkprobe.summarize(rows, elapsed_s=3)["paced_goodput_bps"], 512)
        with self.assertRaises(ValueError):
            linkprobe.summarize(rows + [rows[0]])

    def test_all_losses(self):
        rows = linkprobe.simulate(count=2, loss=1)
        self.assertIsNone(linkprobe.summarize(rows)["median_rtt_ms"])

    def test_non_destructive_export(self):
        with tempfile.TemporaryDirectory() as directory:
            rows = linkprobe.simulate(count=2)
            prefix = Path(directory) / "probe"
            csv_path, json_path = linkprobe.export(rows, prefix)
            self.assertTrue(csv_path.exists() and json_path.exists())
            self.assertEqual(linkprobe.main(["summarize", str(csv_path)]), 0)
            with self.assertRaises(FileExistsError):
                linkprobe.export(rows, prefix)

    def test_bad_config(self):
        with self.assertRaises(ValueError):
            linkprobe.simulate(count=0)

if __name__ == "__main__":
    unittest.main()
