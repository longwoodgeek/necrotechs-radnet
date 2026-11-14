"""Read-only Captain's Log integration and provenance regression checks."""
import hashlib
import socket
import tempfile
import threading
import unittest
from pathlib import Path

from radnet.captains_log import CaptainsLog
from radnet.interactive_doorbell import HOST, serve
from radnet.remote_log import entries, detail, revisions
from radnet.presentation import render_remote


class RemoteLogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / "log.sqlite3"

    def test_missing_journal_is_not_created(self):
        body, records = entries(self.db)
        self.assertEqual(records, [])
        self.assertIn("No entries", body)
        self.assertFalse(self.db.exists())

    def test_entry_details_preserve_provenance(self):
        eid = CaptainsLog(self.db).create("SysOp", "First log", "Archive online")
        _, records = entries(self.db)
        result = detail(records[0])
        for expected in (eid, "Archive online", "UNVERIFIED", "Claimed uncertainty:",
                         "Receipt source:", "HASHES ARE NOT SIGNATURES", "Provenance:"):
            self.assertIn(expected, result)

    def test_latest_revision_displayed_with_history_retained(self):
        log = CaptainsLog(self.db)
        original = log.create("SysOp", "Original", "First text")
        corrected = log.correct(original, original, "SysOp", "Corrected", "Second text", "Typo")
        _, records = entries(self.db)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["id"], corrected)
        _, history = revisions(self.db, original)
        self.assertEqual([r["id"] for r in history], [original, corrected])
        self.assertIn("First text", detail(history[0]))
        self.assertIn("Typo", detail(history[1]))

    def test_ten_entries_then_one(self):
        log = CaptainsLog(self.db)
        for i in range(11):
            log.create("SysOp", f"Entry {i}", "Archive")
        _, first = entries(self.db, 1)
        _, second = entries(self.db, 2)
        self.assertEqual((len(first), len(second)), (10, 1))

    def test_rendered_detail_fits_small_terminal(self):
        CaptainsLog(self.db).create("SysOp", "X" * 100, "Y" * 4000)
        _, records = entries(self.db)
        result = render_remote(detail(records[0]), 24)
        self.assertTrue(all(len(line) <= 24 for line in result.splitlines()))

    def test_read_only_projections_do_not_change_database(self):
        log = CaptainsLog(self.db)
        root = log.create("SysOp", "First", "Body")
        before = hashlib.sha256(self.db.read_bytes()).hexdigest()
        _, records = entries(self.db)
        detail(records[0])
        revisions(self.db, root)
        self.assertEqual(before, hashlib.sha256(self.db.read_bytes()).hexdigest())


class RemoteLogSessionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / "log.sqlite3"
        self.stop = threading.Event()
        ready = threading.Event()
        self.port = None

        def announce(port):
            self.port = port
            ready.set()

        self.thread = threading.Thread(target=serve, args=(str(self.db),),
                                       kwargs={"ready": announce, "stop": self.stop}, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop.set)
        self.addCleanup(self.thread.join, 2)
        self.assertTrue(ready.wait(2))

    def session(self, commands):
        with socket.create_connection((HOST, self.port), timeout=3) as sock:
            sock.settimeout(5)
            sock.sendall(commands)
            sock.shutdown(socket.SHUT_WR)
            chunks = []
            while True:
                chunk = sock.recv(8192)
                if not chunk:
                    break
                chunks.append(chunk)
        return b"".join(chunks).decode()

    def test_empty_log_back_and_disconnect(self):
        result = self.session(b"3\n0\n0\n")
        self.assertIn("No entries", result)
        self.assertIn("Disconnected.", result)
        self.assertFalse(self.db.exists())

    def test_entry_history_revision_and_return(self):
        log = CaptainsLog(self.db)
        root = log.create("SysOp", "Original", "First text")
        log.correct(root, root, "SysOp", "Revised", "Corrected text", "Typo")
        before = hashlib.sha256(self.db.read_bytes()).hexdigest()
        result = self.session(b"3\n1\nh\n1\n0\n0\n0\n0\n0\n")
        for expected in ("CAPTAIN'S LOG", "Revised", "REVISION HISTORY",
                         "ORIGINAL", "First text", "Disconnected."):
            self.assertIn(expected, result)
        self.assertEqual(before, hashlib.sha256(self.db.read_bytes()).hexdigest())
        self.assertTrue(all(len(line) <= 36 for line in result.splitlines()))

    def test_invalid_selection_does_not_exit_log(self):
        CaptainsLog(self.db).create("SysOp", "First", "Body")
        result = self.session(b"3\n9\n1\n0\n0\n0\n")
        self.assertIn("Unknown selection.", result)
        self.assertIn("First", result)
        self.assertIn("Disconnected.", result)

    def test_other_menu_remains_available_after_log(self):
        result = self.session(b"3\n0\n7\n0\n0\n")
        self.assertIn("CAPABILITY REGISTRY", result)
        self.assertIn("Disconnected.", result)


if __name__ == "__main__":
    unittest.main()
