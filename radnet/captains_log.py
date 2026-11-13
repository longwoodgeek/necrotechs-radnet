"""Local append-only log projections. Hashes detect changes, not authenticity."""
import json
from contextlib import closing
import re
import sqlite3
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from .core import EventStore, event_id


class LogError(ValueError):
    """An archive operation could not be completed safely."""


def text(value, name, limit):
    if (not isinstance(value, str) or not value.strip() or len(value) > limit
            or any(unicodedata.category(ch).startswith('C') and ch not in '\n\t'
                   for ch in value)):
        raise LogError(f'{name} must be 1..{limit} characters without control/format characters')
    return value.strip()


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{64}', value):
        raise LogError('Use a complete 64-character event ID')
    return value


def page_number(page):
    if type(page) is not int or not 1 <= page <= 10000:
        raise LogError('Page must be 1..10000')
    return (page - 1) * 10


def timestamp(value):
    value = text(value, 'claimed time', 64)
    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None or 'T' not in value:
            raise ValueError()
    except ValueError as exc:
        raise LogError('Time must be ISO 8601 with T and an explicit UTC offset') from exc
    return value


class CaptainsLog:
    def __init__(self, path):
        self.path = Path(path)

    def _snapshot(self, db=None):
        """One ordered SQLite snapshot, validated before projection or export."""
        if db is None:
            if not self.path.exists():
                return []
            try:
                with closing(sqlite3.connect(self.path.resolve().as_uri() + '?mode=ro', uri=True)) as reader:
                    return self._snapshot(reader)
            except (sqlite3.Error, OSError) as exc:
                raise LogError('Journal unavailable') from exc
        records, chains = [], {}
        try:
            for eid, raw, seq in db.execute('SELECT id,envelope,received_seq FROM events ORDER BY received_seq'):
                envelope = json.loads(raw)
                if not isinstance(envelope, dict) or event_id(envelope) != eid:
                    raise LogError('Journal content hash mismatch or invalid envelope')
                kind = envelope.get('kind')
                if kind not in ('log.create', 'log.correct'):
                    continue
                data = json.loads(envelope['body'])
                if not isinstance(data, dict) or data['schema'] != 1:
                    raise LogError('Unsupported log schema')
                for key, limit in [('title', 100), ('body', 4000), ('time_source', 200), ('uncertainty', 200)]:
                    text(data[key], key, limit)
                text(envelope['author'], 'operator', 32)
                if data['claimed_time'] is not None:
                    timestamp(data['claimed_time'])
                receipt = data['receipt']
                timestamp(receipt['time'])
                if (receipt['source'] != 'local_system_clock_unverified'
                        or receipt['uncertainty'] != 'unknown'
                        or data['provenance'] != 'local_terminal_unverified_operator'
                        or envelope['local_seq'] != seq):
                    raise LogError('Invalid log provenance')
                if kind == 'log.create':
                    if (data['entry_id'] is not None or data['previous'] is not None
                            or data['reason'] is not None or envelope['parents'] != []):
                        raise LogError('Invalid original entry')
                    root = eid
                    chains[root] = eid
                else:
                    root = identifier(data['entry_id'])
                    previous = identifier(data['previous'])
                    text(data['reason'], 'correction reason', 500)
                    if chains.get(root) != previous or envelope['parents'] != [previous]:
                        raise LogError('Broken or conflicting correction history')
                    chains[root] = eid
                records.append({'id': eid, 'entry_id': root, 'received_seq': seq,
                                'envelope': envelope, 'data': data})
        except (KeyError, ValueError, TypeError, AttributeError, RecursionError) as exc:
            raise LogError('Invalid or damaged log journal') from exc
        return records

    def _append(self, author, title, body, claimed_time, time_source, uncertainty,
                entry_id=None, previous=None, reason=None):
        author = text(author, 'operator', 32)
        data = {'schema': 1, 'title': text(title, 'title', 100), 'body': text(body, 'body', 4000),
                'claimed_time': timestamp(claimed_time) if claimed_time is not None else None,
                'time_source': text(time_source, 'time source', 200),
                'uncertainty': text(uncertainty, 'time uncertainty', 200),
                'provenance': 'local_terminal_unverified_operator',
                'entry_id': entry_id, 'previous': previous, 'reason': reason}
        if entry_id is not None:
            identifier(entry_id)
            identifier(previous)
            data['reason'] = text(reason, 'correction reason', 500)
        store = None
        try:
            store = EventStore(self.path)
            # Serialize validation and append, including local receipt sequence allocation.
            store.db.execute('BEGIN IMMEDIATE')
            records = self._snapshot(store.db)
            if entry_id is not None:
                history = [r for r in records if r['entry_id'] == entry_id]
                if not history or history[-1]['id'] != previous:
                    raise LogError('Entry missing or revision changed; reload history before correcting')
            data['receipt'] = {'time': datetime.now(timezone.utc).isoformat(),
                               'source': 'local_system_clock_unverified', 'uncertainty': 'unknown'}
            return store.append('log.correct' if entry_id else 'log.create', author,
                                json.dumps(data, ensure_ascii=False), [previous] if previous else [])
        except (sqlite3.Error, OSError) as exc:
            raise LogError('Journal write unavailable') from exc
        finally:
            if store is not None:
                store.close()

    def create(self, author, title, body, *, claimed_time=None,
               time_source='not supplied', uncertainty='unknown'):
        return self._append(author, title, body, claimed_time, time_source, uncertainty)

    def correct(self, entry_id, previous, author, title, body, reason, *, claimed_time=None,
                time_source='not supplied', uncertainty='unknown'):
        # Reject missing targets without creating a new journal.
        identifier(entry_id)
        identifier(previous)
        if not self.path.exists():
            raise LogError('Entry missing')
        return self._append(author, title, body, claimed_time, time_source, uncertainty,
                            entry_id, previous, reason)

    def browse(self, page=1):
        start = page_number(page)
        latest = {}
        for record in self._snapshot():
            latest[record['entry_id']] = record
        return sorted(latest.values(), key=lambda r: r['received_seq'], reverse=True)[start:start+10]

    def history(self, entry_id, page=None):
        identifier(entry_id)
        start = page_number(page) if page is not None else None
        records = [r for r in self._snapshot() if r['entry_id'] == entry_id]
        if not records:
            raise LogError('Entry missing')
        return records if start is None else records[start:start+10]

    def search(self, query, page=1):
        start = page_number(page)
        query = text(query, 'search', 200).casefold()
        # Search all revisions, including superseded originals and correction reasons.
        records = [r for r in self._snapshot() if query in ' '.join(
            [r['data']['title'], r['data']['body'], r['envelope']['author'],
             r['data'].get('reason') or '']).casefold()]
        return list(reversed(records))[start:start+10]

    def export(self, target):
        target = Path(target)
        database = self.path.resolve()
        reserved = {database, *(Path(str(database) + suffix)
                                for suffix in ('-wal', '-shm', '-journal'))}
        if target.resolve() in reserved:
            raise LogError('Export cannot use the journal or its SQLite sidecar filenames')
        archive = {'schema': 1, 'notice': 'Local archive; authors and times are not authenticated. '
                   'Hashes are not signatures. Receipt sequence is local ordering only.',
                   'events': self._snapshot()}
        try:
            # Exclusive creation rejects existing files, hard links, and symlinks.
            with target.open('x', encoding='utf-8') as output:
                json.dump(archive, output, ensure_ascii=True, indent=2)
                output.write('\n')
        except (OSError, ValueError) as exc:
            raise LogError('Export failed; choose a new writable filename') from exc
