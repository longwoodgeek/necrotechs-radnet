"""Loopback preview invariants; no actual shell commands executed."""
import socket
import tempfile
import threading
import unittest
from pathlib import Path
from radnet.doorbell import HOST, serve


class DoorbellTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = str(Path(self.tmp.name) / "nonexistent.sqlite3")
        self.stop = threading.Event()
        self.port = None
        ready = threading.Event()

        def announce(port):
            self.port = port
            ready.set()

        thread = threading.Thread(target=serve, args=(self.db,),
                                  kwargs={"ready": announce, "stop": self.stop}, daemon=True)
        thread.start()
        self.addCleanup(self.stop.set)
        self.addCleanup(thread.join, 2)
        self.assertTrue(ready.wait(2))

    def request(self, payload):
        with socket.create_connection((HOST, self.port), timeout=2) as conn:
            conn.settimeout(2)
            greeting = conn.recv(4096)
            self.assertIn(b"READ ONLY", greeting)
            conn.sendall(payload)
            conn.shutdown(socket.SHUT_WR)
            chunks = []
            while True:
                part = conn.recv(4096)
                if not part:
                    break
                chunks.append(part)
        return b"".join(chunks).decode()

    def test_status_is_read_only(self):
        self.assertIn("NETWORK CONNECTIVITY: NOT VERIFIED", self.request(b"2\n"))
        self.assertFalse(Path(self.db).exists())

    def test_status_keeps_line_breaks(self):
        response = self.request(b"2\n")
        self.assertIn("NETWORK CONNECTIVITY: NOT VERIFIED\n", response)
        self.assertIn("Transport: NOT CONNECTED\n", response)

    def test_command_string_not_interpreted(self):
        marker = Path(self.tmp.name) / "should-not-exist"
        self.assertIn("No commands executed", self.request(("$(touch " + str(marker) + ")\n").encode()))
        self.assertFalse(marker.exists())

    def test_oversized_input_rejected(self):
        self.assertIn("Input too long", self.request(b"A" * 100 + b"\n"))

    def test_disconnect(self):
        self.assertIn("Disconnected", self.request(b"0\n"))

    def test_capabilities_do_not_create_database(self):
        self.assertIn("CAPABILITY REGISTRY", self.request(b"7\n"))
        self.assertFalse(Path(self.db).exists())


if __name__ == "__main__":
    unittest.main()
