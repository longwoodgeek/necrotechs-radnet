import unittest
from radnet.colors import severity, colorize_status


class SeverityColorTests(unittest.TestCase):
    def test_plain_mode_retains_severity(self):
        self.assertEqual(severity("ERROR", "Integrity failed"), "[ERROR] Integrity failed")
        self.assertNotIn("\x1b", severity("CRITICAL", "Archive failed"))

    def test_ansi_red_and_amber(self):
        self.assertEqual(severity("ERROR", "Bad", ansi=True), "\x1b[31m[ERROR] Bad\x1b[0m")
        self.assertEqual(severity("CRITICAL", "Bad", ansi=True), "\x1b[1;31m[CRITICAL] Bad\x1b[0m")
        self.assertEqual(severity("WARN", "Stale", ansi=True), "\x1b[33m[WARN] Stale\x1b[0m")

    def test_controls_are_neutralized(self):
        rendered = severity("ERROR", "bad\x1b[2J\ntext", ansi=False)
        self.assertNotIn("\x1b", rendered)
        self.assertNotIn("\n", rendered)

    def test_unconfigured_transport_is_not_error(self):
        text = "Transport: NOT CONNECTED\nNETWORK CONNECTIVITY: NOT VERIFIED"
        self.assertEqual(colorize_status(text, ansi=True), text)

    def test_invalid_identity_is_error(self):
        text = colorize_status("IDENTIFICATION: INVALID / UNREADABLE", ansi=True)
        self.assertIn("\x1b[31m[ERROR]", text)
        self.assertIn("INVALID / UNREADABLE", text)

    def test_unknown_level_rejected(self):
        with self.assertRaises(ValueError):
            severity("SUCCESSFULISH", "no")


if __name__ == "__main__":
    unittest.main()
