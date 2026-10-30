"""Local one-shot request journal; durability is SQLite FULL, not external proof."""

import sqlite3
from contextlib import closing
from pathlib import Path

from .protocol import InputError, canonical, decode_json, digest


STATES = {"dispatch_intent", "blocked_after_intent", "receipt_confirmed", "outcome_unknown"}
MAX_JOURNAL_JSON = 32 * 1024 * 1024


class JournalError(RuntimeError):
    """The local journal could not establish a usable persisted state."""


def _encoded(value):
    raw = canonical(value)
    if len(raw) > MAX_JOURNAL_JSON:
        raise JournalError("Journal entry exceeds the supported size")
    return raw.decode("utf-8")


def _identifier(value):
    if type(value) is not str or not value.strip() or len(value) > 16384:
        raise InputError("Invalid journal request identifier")


def _fingerprint(value):
    if type(value) is not str or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise InputError("Invalid journal fingerprint")


class Journal:
    """Each operation uses its own connection; claim is atomic across callers."""

    def __init__(self, path):
        self.path = str(Path(path))
        if self.path == ":memory:":
            raise InputError("A persistent file is required for the one-shot journal")
        with closing(self._connect()) as connection:
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, 1):
                raise JournalError("Unsupported journal schema version")
            connection.execute(
                "CREATE TABLE IF NOT EXISTS request_journal ("
                "request_id TEXT PRIMARY KEY NOT NULL, fingerprint TEXT NOT NULL, "
                "state TEXT NOT NULL CHECK(state IN "
                "('dispatch_intent','blocked_after_intent','receipt_confirmed','outcome_unknown')), "
                "snapshot_json TEXT NOT NULL, details_json TEXT)"
            )
            columns = connection.execute("PRAGMA table_info(request_journal)").fetchall()
            if [(r[1], r[2]) for r in columns] != [
                ("request_id", "TEXT"), ("fingerprint", "TEXT"), ("state", "TEXT"),
                ("snapshot_json", "TEXT"), ("details_json", "TEXT"),
            ] or columns[0][5] != 1:
                raise JournalError("Journal table layout differs from the supported schema")
            if version == 0:
                connection.execute("PRAGMA user_version=1")

    def _connect(self):
        connection = sqlite3.connect(self.path, timeout=5.0, isolation_level=None)
        try:
            mode = connection.execute("PRAGMA journal_mode=WAL").fetchone()[0]
            connection.execute("PRAGMA synchronous=FULL")
            synchronous = connection.execute("PRAGMA synchronous").fetchone()[0]
            connection.execute("PRAGMA busy_timeout=5000")
            if str(mode).lower() != "wal" or synchronous != 2:
                raise JournalError("Required SQLite WAL/FULL mode is unavailable")
            return connection
        except Exception:
            connection.close()
            raise

    def _commit(self, connection):
        """Separate seam for trusted fault-injection tests, not request input."""
        connection.commit()

    @staticmethod
    def _row(row):
        if row is None:
            return None
        request_id, fingerprint, state, snapshot_json, details_json = row
        _identifier(request_id)
        _fingerprint(fingerprint)
        if state not in STATES:
            raise JournalError("Unknown persisted journal state")
        snapshot = decode_json(snapshot_json, max_bytes=MAX_JOURNAL_JSON)
        details = None if details_json is None else decode_json(details_json, max_bytes=MAX_JOURNAL_JSON)
        if type(snapshot) is not dict or (details is not None and type(details) is not dict):
            raise JournalError("Malformed journal entry")
        # Snapshots produced by this gateway have a self-consistent measured binding.
        # Other test snapshots remain opaque; they can never authorize a send by themselves.
        if snapshot.get("format") == "upload-pilot-intent/0.1":
            try:
                subject = snapshot["evidence"]["target"]["subject"]
                measured = {
                    "evaluation_id": snapshot["evidence"]["evaluation_id"],
                    "subject": subject, "byte_length": snapshot["byte_length"],
                }
                consistent = (
                    subject["request_id"] == request_id == snapshot["request_id"]
                    and subject["payload_sha256"] == snapshot["payload_sha256"]
                    and digest(subject) == snapshot["subject_sha256"]
                    and type(snapshot["byte_length"]) is int
                    and 0 <= snapshot["byte_length"] <= 1024 * 1024
                    and digest(measured) == fingerprint
                )
            except (KeyError, TypeError, InputError) as exc:
                raise JournalError("Malformed measured journal binding") from exc
            if not consistent:
                raise JournalError("Persisted measured journal binding is inconsistent")
        return {"request_id": request_id, "fingerprint": fingerprint, "state": state,
                "snapshot": snapshot, "details": details}

    def get(self, request_id):
        _identifier(request_id)
        with closing(self._connect()) as connection:
            return self._row(connection.execute(
                "SELECT request_id,fingerprint,state,snapshot_json,details_json "
                "FROM request_journal WHERE request_id=?", (request_id,)
            ).fetchone())

    def claim(self, request_id, fingerprint, snapshot):
        _identifier(request_id)
        _fingerprint(fingerprint)
        if type(snapshot) is not dict:
            raise InputError("Journal snapshot must be an object")
        serialized = _encoded(snapshot)
        with closing(self._connect()) as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                existing = self._row(connection.execute(
                    "SELECT request_id,fingerprint,state,snapshot_json,details_json "
                    "FROM request_journal WHERE request_id=?", (request_id,)
                ).fetchone())
                if existing is not None:
                    connection.rollback()
                    existing["claim_status"] = "REPLAY" if existing["fingerprint"] == fingerprint else "CONFLICT"
                    return existing
                connection.execute(
                    "INSERT INTO request_journal(request_id,fingerprint,state,snapshot_json,details_json) "
                    "VALUES(?,?, 'dispatch_intent', ?, NULL)", (request_id, fingerprint, serialized)
                )
                self._commit(connection)
                persisted = self._row(connection.execute(
                    "SELECT request_id,fingerprint,state,snapshot_json,details_json "
                    "FROM request_journal WHERE request_id=?", (request_id,)
                ).fetchone())
                if persisted is None:
                    raise JournalError("Committed request intent is not readable")
                persisted["claim_status"] = "CLAIMED"
                return persisted
            except Exception:
                connection.rollback()
                raise

    def finish(self, request_id, state, details):
        _identifier(request_id)
        if state not in STATES - {"dispatch_intent"} or type(details) is not dict:
            raise InputError("Invalid terminal journal result")
        serialized = _encoded(details)
        with closing(self._connect()) as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                existing = self._row(connection.execute(
                    "SELECT request_id,fingerprint,state,snapshot_json,details_json "
                    "FROM request_journal WHERE request_id=?", (request_id,)
                ).fetchone())
                if existing is None:
                    raise JournalError("Cannot finish an unclaimed request")
                if existing["state"] != "dispatch_intent":
                    if existing["state"] == state and digest(existing["details"]) == digest(details):
                        connection.rollback()
                        return existing
                    raise JournalError("A terminal journal result cannot be overwritten")
                connection.execute(
                    "UPDATE request_journal SET state=?,details_json=? WHERE request_id=? AND state='dispatch_intent'",
                    (state, serialized, request_id),
                )
                self._commit(connection)
                return self._row(connection.execute(
                    "SELECT request_id,fingerprint,state,snapshot_json,details_json "
                    "FROM request_journal WHERE request_id=?", (request_id,)
                ).fetchone())
            except Exception:
                connection.rollback()
                raise
