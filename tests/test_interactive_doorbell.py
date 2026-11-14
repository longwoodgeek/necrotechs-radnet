"""Tests for isolated interactive loopback preview."""
import socket
import tempfile
import threading
import unittest
from pathlib import Path

from radnet.interactive_doorbell import serve, HOST


class InteractiveDoorbellTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = str(Path(self.tmp.name) / "absent.sqlite3")
        self.stop = threading.Event()
        ready = threading.Event()
        self.port = None

        def announce(port):
            self.port = port
            ready.set()

        self.thread = threading.Thread(target=serve, args=(self.db,),
                                       kwargs={"ready": announce, "stop": self.stop}, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop.set)
        self.addCleanup(self.thread.join, 2)
        self.assertTrue(ready.wait(2))

    def connect(self):
        s = socket.create_connection((HOST, self.port), timeout=2)
        s.settimeout(2)
        self.addCleanup(s.close)
        self.assertIn(b"READ ONLY", s.recv(4096))
        return s

    def receive_all(self, s):
        chunks = []
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks).decode()

    def test_multiple_selections_same_connection(self):
        s = self.connect()
        s.sendall(b"2\n7\n0\n0\n")
        s.shutdown(socket.SHUT_WR)
        text = self.receive_all(s)
        self.assertIn("STATION STATUS", text)
        self.assertIn("CAPABILITY REGISTRY", text)
        self.assertIn("Disconnected.", text)
        self.assertFalse(Path(self.db).exists())

    def test_remote_capability_output_uses_compact_width(self):
        s = self.connect()
        s.sendall(b"7\n0\n0\n")
        s.shutdown(socket.SHUT_WR)
        text = self.receive_all(s)
        self.assertIn("CAPABILITY REGISTRY", text)
        self.assertTrue(all(len(line) <= 36 for line in text.splitlines()))
        self.assertIn("NOT LIVE-VERIFIED", text)

    def test_nested_evidence_and_back_navigation(self):
        s = self.connect()
        s.sendall(b"7\n1\n0\n0\n0\n")
        s.shutdown(socket.SHUT_WR)
        text = self.receive_all(s)
        self.assertIn("CAPABILITY EVIDENCE", text)
        self.assertIn("No evidence recorded.", text)
        self.assertGreaterEqual(text.count("CAPABILITY REGISTRY"), 2)
        self.assertIn("Returned to main menu.", text)
        self.assertIn("Disconnected.", text)

    def test_nested_navigation_has_single_prompt_per_screen(self):
        s = self.connect()
        s.sendall(b"7\n1\n0\n0\n0\n")
        s.shutdown(socket.SHUT_WR)
        text = self.receive_all(s)
        self.assertNotIn("[1] VIEW CAPABILITY EVIDENCE", text)
        self.assertEqual(text.count("[1] EVIDENCE  [0] RETURN"), 2)
        self.assertEqual(text.count("[0] RETURN TO REGISTRY"), 1)
        self.assertNotIn("> > ", text)
        self.assertIn("Disconnected.", text)

    def test_registry_zero_returns_not_disconnects(self):
        s = self.connect()
        s.sendall(b"7\n0\n2\n0\n")
        s.shutdown(socket.SHUT_WR)
        text = self.receive_all(s)
        self.assertIn("Returned to main menu.", text)
        self.assertIn("STATION STATUS", text)
        self.assertIn("Disconnected.", text)

    def test_shell_looking_input_is_data(self):
        s = self.connect()
        s.sendall(b"$(id)\n0\n")
        s.shutdown(socket.SHUT_WR)
        self.assertIn("No commands executed", self.receive_all(s))

    def test_oversized_selection_disconnects(self):
        s = self.connect()
        s.sendall(b"X" * 100 + b"\n")
        s.shutdown(socket.SHUT_WR)
        self.assertIn("Input too long", self.receive_all(s))

    def test_eof_ends_session(self):
        s = self.connect()
        s.shutdown(socket.SHUT_WR)
        self.assertEqual(self.receive_all(s), "")


if __name__ == "__main__":
    unittest.main()
