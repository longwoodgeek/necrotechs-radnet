import tempfile
import unittest
from pathlib import Path
from radnet.core import EventStore, event_id

class TestEventStore(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "events.sqlite3"
        self.store = EventStore(self.path)

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def test_append_and_reopen(self):
        eid = self.store.append("message.create", "sparrow", "Hello IronGate")
        self.store.close()
        self.store = EventStore(self.path)
        self.assertEqual(self.store.get(eid)["body"], "Hello IronGate")
        self.assertEqual(self.store.verify(), [])

    def test_parent_reference(self):
        parent = self.store.append("message.create", "sparrow", "Hello")
        child = self.store.append("message.create", "morgan", "Received", [parent])
        self.assertEqual(self.store.get(child)["parents"], [parent])

    def test_hash_tamper_detection(self):
        eid = self.store.append("message.create", "sparrow", "Original")
        self.store.db.execute("UPDATE events SET envelope=? WHERE id=?", ('{"tampered":true}', eid))
        self.store.db.commit()
        self.assertEqual(self.store.verify(), [eid])

    def test_invalid_parent(self):
        with self.assertRaises(ValueError):
            self.store.append("message.create", "sparrow", "Hello", ["invalid"])

    def test_list_order(self):
        self.store.append("message.create", "a", "first")
        self.store.append("message.create", "b", "second")
        self.assertEqual([x["body"] for x in self.store.list()], ["second", "first"])

if __name__ == "__main__":
    unittest.main()
