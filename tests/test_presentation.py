import unittest

from radnet.presentation import normalized_width, render_remote, wrap_lines


class PresentationTests(unittest.TestCase):
    def test_width_defaults_and_clamps(self):
        self.assertEqual(normalized_width(), 36)
        self.assertEqual(normalized_width(4), 24)
        self.assertEqual(normalized_width(999), 160)

    def test_multiline_remote_rendering(self):
        text = render_remote("FIRST LINE\nSECOND LINE", 36)
        self.assertEqual(text, "FIRST LINE\nSECOND LINE\n")

    def test_newlines_are_real_not_literal_escapes(self):
        rendered = render_remote("FIRST LINE\nSECOND LINE", 36)
        self.assertNotIn(chr(92) + "n", rendered)
        self.assertEqual(rendered.count("\n"), 2)

    def test_control_characters_removed(self):
        text = render_remote("hello\x1b[31mworld", 36)
        self.assertNotIn("\x1b", text)

    def test_supported_widths(self):
        for width in (24, 36, 44, 80, 120):
            output = wrap_lines(["LOCAL SOFTWARE / NOT LIVE-VERIFIED"], width)
            self.assertTrue(all(len(line) <= width for line in output.splitlines()))
