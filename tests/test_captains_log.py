"""Archive behavior: deleting append/link/time/export protections breaks these tests."""
import json
from contextlib import closing
import sqlite3
import tempfile
import unittest
from pathlib import Path
from radnet.core import EventStore
from radnet.captains_log import CaptainsLog, LogError


class LogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'journal.sqlite3'
        self.log = CaptainsLog(self.path)

    def create(self, **kwargs):
        return self.log.create('Longwood', 'First transmission', 'Original evidence', **kwargs)

    def test_read_missing_has_no_side_effect(self):
        self.assertEqual(self.log.browse(), [])
        self.assertEqual(self.log.search('evidence'), [])
        with self.assertRaises(LogError):
            self.log.history('a' * 64)
        self.assertFalse(self.path.exists())

    def test_revision_persistence_and_original_unchanged(self):
        root = self.create()
        original = self.log.history(root)[0]
        correction = self.log.correct(root, root, 'Guest', 'Corrected', 'Amended evidence', 'Typo')
        history = CaptainsLog(self.path).history(root)
        self.assertEqual(history[0], original)
        self.assertEqual(history[1]['id'], correction)
        self.assertEqual(history[1]['envelope']['parents'], [root])
        self.assertEqual(history[1]['data']['reason'], 'Typo')
        self.assertEqual(self.log.browse()[0]['id'], correction)
        self.assertEqual(self.log.search('Original')[0]['id'], root)
        self.assertEqual(self.log.search('amended')[0]['id'], correction)
        store = EventStore(self.path)
        self.addCleanup(store.close)
        self.assertEqual(store.verify(), [])

    def test_stale_or_wrong_entry_corrections_rejected(self):
        root = self.create()
        other = self.create()
        self.log.correct(root, root, 'Guest', 'New', 'Body', 'Reason')
        for entry, previous in [(root, root), (root, other), ('a'*64, other)]:
            with self.assertRaises(LogError):
                self.log.correct(entry, previous, 'Guest', 'No', 'Body', 'Reason')
        self.assertEqual(len(self.log.history(root)), 2)

    def test_claimed_time_separate_from_local_receipt(self):
        root = self.create(claimed_time='2001-02-03T04:05:06-05:00',
                           time_source='handwritten notebook', uncertainty='about five minutes')
        item = self.log.history(root)[0]
        self.assertEqual(item['data']['claimed_time'], '2001-02-03T04:05:06-05:00')
        self.assertEqual(item['data']['time_source'], 'handwritten notebook')
        self.assertEqual(item['data']['receipt']['source'], 'local_system_clock_unverified')
        self.assertEqual(item['data']['receipt']['uncertainty'], 'unknown')
        self.assertTrue(item['data']['receipt']['time'].endswith('+00:00'))
        self.assertEqual(item['received_seq'], item['envelope']['local_seq'])
        self.assertEqual(item['data']['provenance'], 'local_terminal_unverified_operator')
        self.assertIsNone(self.log.history(self.create())[0]['data']['claimed_time'])

    def test_bounds_and_invalid_times_do_not_write(self):
        cases = [dict(title='x'*101), dict(author='x'*33), dict(body='x'*4001),
                 dict(body=' '), dict(body='a\x1b[31m'), dict(body='a\u202eb'),
                 dict(claimed_time='yesterday'), dict(claimed_time='2026-01-01T00:00:00'),
                 dict(time_source='x'*201), dict(uncertainty='x'*201)]
        for override in cases:
            args = dict(author='A', title='T', body='B')
            args.update(override)
            with self.subTest(override=override), self.assertRaises(LogError):
                self.log.create(**args)
        self.assertFalse(self.path.exists())
        for bad in [0, -1, 10001, True, '1']:
            with self.assertRaises(LogError):
                self.log.browse(bad)
        with self.assertRaises(LogError):
            self.log.search('x'*201)

    def test_paging(self):
        for i in range(11):
            self.log.create('A', f'Title {i}', 'Body')
        self.assertEqual(len(self.log.browse()), 10)
        self.assertEqual(len(self.log.browse(2)), 1)
        self.assertEqual(len(self.log.search('body', 2)), 1)

    def test_non_destructive_export_preserves_envelopes(self):
        root = self.create()
        self.log.correct(root, root, 'B', 'New', 'New body', 'Correction')
        before = self.path.read_bytes()
        target = Path(self.temp.name) / 'archive.json'
        self.log.export(target)
        archive = json.loads(target.read_text())
        self.assertEqual(archive['events'], self.log.history(root))
        self.assertIn('not authenticated', archive['notice'])
        self.assertEqual(self.path.read_bytes(), before)
        for protected in [target, self.path, Path(str(self.path)+'-wal')]:
            protected.touch(exist_ok=True)
            original = protected.read_bytes()
            with self.assertRaises(LogError):
                self.log.export(protected)
            self.assertEqual(protected.read_bytes(), original)
        link = Path(self.temp.name) / 'alias.json'
        link.symlink_to(target)
        with self.assertRaises(LogError):
            self.log.export(link)

    def test_boards_and_legacy_data_survive(self):
        from radnet.boards import Boards
        boards = Boards(self.path)
        board = boards.create_board('General', 'A')
        post = boards.post(board, 'A', 'Title', 'Message')
        root = self.create()
        self.log.correct(root, root, 'A', 'New', 'Body', 'Reason')
        self.assertEqual(boards.messages(board)[0]['id'], post)
        self.assertEqual(len(self.log.browse()), 1)

    def test_corrupt_journal_fails_closed(self):
        root = self.create()
        with closing(sqlite3.connect(self.path)) as db:
            db.execute('UPDATE events SET envelope=? WHERE id=?', ('{}', root))
            db.commit()
        with self.assertRaises(LogError):
            self.log.browse()
        target = Path(self.temp.name) / 'bad.json'
        with self.assertRaises(LogError):
            self.log.export(target)
        self.assertFalse(target.exists())

    def test_unavailable_journal(self):
        self.path.write_text('not sqlite')
        with self.assertRaises(LogError):
            self.log.browse()
        with self.assertRaises(LogError):
            self.create()

    def test_reserved_export_names_never_created(self):
        for target in [self.path, Path(str(self.path)+'-wal'), Path(str(self.path)+'-shm'),
                       Path(str(self.path)+'-journal')]:
            with self.subTest(target=target), self.assertRaises(LogError):
                self.log.export(target)
            self.assertFalse(target.exists())
        self.assertFalse(self.path.exists())

    def test_missing_correction_does_not_create_journal(self):
        with self.assertRaises(LogError):
            self.log.correct('a'*64, 'a'*64, 'A', 'T', 'B', 'R')
        self.assertFalse(self.path.exists())

    def test_concurrent_correction_accepts_only_one_successor(self):
        from concurrent.futures import ThreadPoolExecutor
        root = self.create()
        def correct(number):
            try:
                return CaptainsLog(self.path).correct(root, root, 'A', 'T', str(number), 'Reason')
            except LogError:
                return None
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(correct, range(2)))
        self.assertEqual(sum(result is not None for result in results), 1)
        self.assertEqual(len(self.log.history(root)), 2)

    def test_hash_valid_but_invalid_payloads_fail_closed(self):
        from radnet.core import canonical, event_id
        root = self.create()
        record = self.log.history(root)[0]
        for invalid in [[], None, {'schema': 99}, {'schema': 1}]:
            envelope = dict(record['envelope'], body=json.dumps(invalid))
            with closing(sqlite3.connect(self.path)) as db:
                db.execute('UPDATE events SET id=?,envelope=?', (event_id(envelope), canonical(envelope)))
                db.commit()
            with self.assertRaises(LogError):
                self.log.browse()

    def test_revision_metadata_is_not_silently_inherited(self):
        root = self.create(claimed_time='2026-11-13T10:00:00-05:00', time_source='watch')
        self.log.correct(root, root, 'B', 'T', 'B', 'Reason')
        correction = self.log.history(root)[1]['data']
        self.assertIsNone(correction['claimed_time'])
        self.assertEqual(correction['time_source'], 'not supplied')

    def test_invalid_original_reason_rejected_before_search_or_export(self):
        from radnet.core import canonical, event_id
        root = self.create()
        record = self.log.history(root)[0]
        payload = dict(record['data'], reason={'unexpected': 'object'})
        envelope = dict(record['envelope'], body=json.dumps(payload))
        with closing(sqlite3.connect(self.path)) as db:
            db.execute('UPDATE events SET id=?,envelope=?', (event_id(envelope), canonical(envelope)))
            db.commit()
        for operation in [self.log.browse, lambda: self.log.search('evidence'),
                          lambda: self.log.export(Path(self.temp.name)/'bad.json'), self.create]:
            with self.assertRaises(LogError):
                operation()

    def test_unavailable_journal_closes_failed_writer_connection(self):
        from unittest.mock import patch
        self.path.write_text('not sqlite')
        connection = sqlite3.connect(self.path)
        self.addCleanup(connection.close)
        with patch('radnet.core.sqlite3.connect', return_value=connection):
            with self.assertRaises(LogError):
                self.create()
        with self.assertRaises(sqlite3.ProgrammingError):
            connection.execute('SELECT 1')
