import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from radnet.captains_log import CaptainsLog
from radnet.terminal import run, interactive_log, display_log


class LogTerminalTests(unittest.TestCase):
    def session(self, db, answers):
        output = []
        choices = iter(answers)
        run(db, input_fn=lambda _: next(choices), output_fn=output.append)
        return '\n'.join(output)

    def test_create_browse_history_search_correct_export_and_reopen(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td)/'log.sqlite3'
            archive = Path(td)/'archive.json'
            output = self.session(db, ['3', '2', 'Longwood', 'Title', 'Evidence', '', '', '', '0', '0'])
            self.assertIn('Entry saved', output)
            root = CaptainsLog(db).browse()[0]['entry_id']
            output = self.session(db, ['3', '6', root, root, 'Guest', 'Revised', 'New evidence',
                                       '', '', '', 'Typo', '1', '0', '3', root, '0',
                                       '4', 'Evidence', '0', '5', str(archive), '0', '0'])
            self.assertIn('Correction saved', output)
            self.assertIn('Original', output)
            self.assertIn('Correction', output)
            self.assertIn('local_system_clock_unverified', output)
            self.assertIn('Uncertainty: unknown', output)
            self.assertTrue(archive.exists())
            self.assertEqual(len(CaptainsLog(db).history(root)), 2)

    def test_empty_read_and_interruptions_do_not_create(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td)/'missing.sqlite3'
            self.session(db, ['3', '1', '0', '4', 'needle', '0', '0', '0'])
            for exception in (EOFError, KeyboardInterrupt):
                output = []
                def interrupted(_):
                    raise exception()
                interactive_log(db, interrupted, output.append)
                self.assertIn('Log console closed', '\n'.join(output))
            self.assertFalse(db.exists())

    def test_display_sanitizes_every_untrusted_field(self):
        poison = '\x1b[31m\u202e\x00'
        record = {'id': poison, 'entry_id': poison, 'received_seq': poison,
                  'envelope': {'kind': poison, 'author': poison},
                  'data': {k: poison for k in ['title', 'body', 'claimed_time', 'time_source',
                                             'uncertainty', 'reason', 'provenance']}}
        record['data']['receipt'] = dict(time=poison, source=poison, uncertainty=poison)
        output = []
        display_log(record, output.append)
        self.assertNotIn('\x1b', ''.join(output))
        self.assertNotIn('\u202e', ''.join(output))
        self.assertNotIn('\x00', ''.join(output))

    def test_validation_errors_recover_without_echoing_input(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td)/'missing.sqlite3'
            output = self.session(db, ['3', 'x'*5000, '2', 'A', 'T', '\x1b[31m', '', '', '', '0', '0'])
            self.assertIn('rejected', output)
            self.assertNotIn('\x1b', output)
            self.assertFalse(db.exists())

    def test_local_session_does_not_open_network(self):
        with tempfile.TemporaryDirectory() as td, patch('socket.socket', side_effect=AssertionError('network')):
            self.session(Path(td)/'log.sqlite3', ['3', '2', 'A', 'T', 'B', '', '', '', '0', '0'])
