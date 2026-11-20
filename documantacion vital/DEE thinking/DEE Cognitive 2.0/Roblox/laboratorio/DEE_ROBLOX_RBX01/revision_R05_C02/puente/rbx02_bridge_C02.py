"""RBX01.v1 restricted, durable HTTP transport. No cognitive policy lives here.

Python 3.11+, standard library only. The adapter is supplied by the single Native
owner; importing this module never opens a DEE owner. Unit doubles must identify
themselves as CONTROL. See CONTRACT.md before operating a Roblox server.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import hmac
import http.server
import json
import math
import os
import pathlib
import re
import secrets
import socketserver
import sqlite3
import threading
import time
import uuid
import urllib.request
from typing import Any, Protocol

API_VERSION = "RBX01.C02.v1"
MAX_PAYLOAD = 16_384
MAX_DECISIONS = 48  # One prospectively fixed C02 main, not an adaptive increase.
MAX_TICKS = 200_000
DATABASE_SCHEMA = 'DEE.RBX01.bridge_database.C02.R01'
# Prospective finite HOST quotas: state polling consumes requests, never Native ticks.
MAX_REQUESTS = 32_768
MAX_SESSION_SECONDS = 28_800  # Eight hours; global Native cutoff remains independent.
BOOTSTRAP_IDLE_SECONDS = 900  # Before first session only; no Native idle evolution.
DRAIN_SECONDS = 1000  # R04 material900s plus bounded host drain.
ID_RE = re.compile(r"[A-Za-z0-9_-]{8,80}\Z")
BASE = pathlib.Path(__file__).resolve().parent.parent
PRIVATE = BASE / "configuracion_privada"
ROUTES = frozenset({"session/start", "observation", "decision", "query_sensor",
                    "function", "tool_ack", "feedback", "ack", "state", "pause",
                    "suspend", "resume", "stop"})
ACTIONS = frozenset({"ASK_STATION", "SKIP_STATION", "EXIT_0", "EXIT_1", "SAFE_WAIT"})
SENSOR_KEYS = frozenset({"station", "stage", "contact", "inventoryKey",
                        "inventoryResource", "queryAvailable", "stationSignal",
                        "permissionStock", "publicContactCode", "lastFailure"})
MODES = frozenset({'LIVE_NATIVE', 'PROGRAMMED', 'CONVENTIONAL_AI'})


class BridgeError(Exception):
    def __init__(self, status: int, code: str):
        self.status, self.code = status, code
        super().__init__(code)


class NativeUnavailable(RuntimeError):
    """No Native writer is available; transport must pause, never substitute."""


class BridgeDrainTimeout(RuntimeError):
    """The writer still runs: retain its owner and database for reconciliation."""
    def __init__(self, bridge):
        self.bridge = bridge
        self.owner_must_remain_open = True
        super().__init__("HOST_SAFETY_STOP: bridge writer did not drain within400s; "
                         "database and owner preserved, do not close/restart the owner")


class Adapter(Protocol):
    identity: str  # LIVE_NATIVE or CONTROL, fixed by operator, not by the client.

    def execute(self, kind: str, payload: dict, context: dict) -> dict: ...


class UnavailableAdapter:
    identity = "UNAVAILABLE"

    def execute(self, kind, payload, context):
        raise NativeUnavailable("Native adapter not attached")


class ProcessLease:
    """OS-released exclusive writer lease; stale files do not imply stale locks."""
    def __init__(self, database_path):
        self.handle = open(str(database_path) + ".owner-lock", "a+b")
        try:
            self.handle.seek(0, os.SEEK_END)
            if self.handle.tell() == 0:
                self.handle.write(b"\0")
                self.handle.flush()
            self.handle.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BaseException:
            self.handle.close()
            raise RuntimeError("An RBX01 bridge writer already owns this private database") from None

    def close(self):
        if self.handle.closed:
            return
        self.handle.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
        self.handle.close()


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False)


def strict_object(value: Any, keys: set | frozenset, optional=frozenset()) -> dict:
    if not isinstance(value, dict) or not keys <= value.keys() or value.keys() - keys - optional:
        raise BridgeError(400, "SCHEMA_KEYS")
    return value


def integer(value: Any, low: int, high: int) -> int:
    if type(value) is not int or not low <= value <= high:
        raise BridgeError(400, "SCHEMA_INTEGER")
    return value


def boolean(value: Any) -> bool:
    if type(value) is not bool:
        raise BridgeError(400, "SCHEMA_BOOLEAN")
    return value


def identifier(value: Any) -> str:
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        raise BridgeError(400, "SCHEMA_ID")
    return value


def enum(value: Any, allowed) -> str:
    if not isinstance(value, str) or value not in allowed:
        raise BridgeError(400, "SCHEMA_ENUM")
    return value


def now_ms() -> int:
    return time.time_ns() // 1_000_000


def _no_duplicate_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def decode_body(raw: bytes) -> dict:
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_no_duplicate_pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite")))
        if not isinstance(value, dict):
            raise ValueError("object required")
        return value
    except (UnicodeError, ValueError, RecursionError):
        raise BridgeError(400, "INVALID_JSON") from None


class Bridge:
    """One durable actor session and one serial writer, including across restarts.

    Session ownership stays latched after stop. A fresh experimental owner must
    use a fresh private database deliberately prepared by the local operator.
    There is no remote reset, resume, life selector, filesystem or shell API.
    """

    def __init__(self, db_path: pathlib.Path | str, token: str, owner_user_id: int,
                 adapter: Adapter | None = None, *, world_id="RBX01_R05_C02_V1",
                 session_seconds=3600, rate_limit=60, allow_control=False,
                 max_db_bytes=64 * 1024 * 1024, start_worker=True, resume_allowed=False):
        if not isinstance(token, str) or len(token) < 32:
            raise ValueError("A private cryptographically generated token is required")
        integer(owner_user_id, 1, 2**53 - 1)
        integer(session_seconds, 30, MAX_SESSION_SECONDS)
        integer(rate_limit, 1, 60)
        self.token, self.owner_user_id, self.world_id = token, owner_user_id, world_id
        self.adapter = adapter or UnavailableAdapter()
        self.allow_control, self.session_seconds, self.rate_limit = allow_control, session_seconds, rate_limit
        self.resume_allowed = boolean(resume_allowed)
        self.lock = threading.RLock()
        self.wake, self.closing = threading.Event(), threading.Event()
        self.rates = collections.defaultdict(collections.deque)
        self.process_lease = ProcessLease(db_path)
        self.db = sqlite3.connect(str(db_path), check_same_thread=False, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        existing_tables = {r[0] for r in self.db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if existing_tables:
            existing_schema = self.db.execute("SELECT value FROM bridge_meta WHERE key='schema'").fetchone() if 'bridge_meta' in existing_tables else None
            if existing_schema is None or existing_schema[0] != DATABASE_SCHEMA:
                self.db.close(); self.process_lease.close()
                raise ValueError('Fresh C02 database required; never migrate/reuse R04 SQLite')
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("PRAGMA busy_timeout=3000")
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA journal_size_limit=1048576")
        self.db.execute(f"PRAGMA max_page_count={max_db_bytes // 4096}")
        self.db.executescript("""
          CREATE TABLE IF NOT EXISTS bridge_meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS session(
            singleton INTEGER PRIMARY KEY CHECK(singleton=1), id TEXT UNIQUE NOT NULL,
            server_id TEXT NOT NULL, mode TEXT NOT NULL, level TEXT NOT NULL,
            status TEXT NOT NULL, phase TEXT NOT NULL, created INTEGER NOT NULL,
            expires INTEGER NOT NULL, sequence INTEGER NOT NULL DEFAULT 0,
            observation_id TEXT, last_action_id TEXT, decisions INTEGER NOT NULL DEFAULT 0,
            selections INTEGER NOT NULL DEFAULT 0, ticks INTEGER NOT NULL DEFAULT 0,
            stop_reason TEXT);
          CREATE TABLE IF NOT EXISTS request(
            id TEXT PRIMARY KEY, route TEXT NOT NULL, digest TEXT NOT NULL,
            status_code INTEGER NOT NULL, response TEXT NOT NULL, created INTEGER NOT NULL);
          CREATE TABLE IF NOT EXISTS observation(
            id TEXT PRIMARY KEY, sequence INTEGER UNIQUE NOT NULL, body TEXT NOT NULL,
            created INTEGER NOT NULL);
          CREATE TABLE IF NOT EXISTS operation(
            id TEXT PRIMARY KEY, request_id TEXT UNIQUE NOT NULL, kind TEXT NOT NULL,
            status TEXT NOT NULL, payload TEXT NOT NULL, context TEXT NOT NULL,
            admitted INTEGER NOT NULL, started INTEGER, completed INTEGER,
            result TEXT, error TEXT);
          CREATE TABLE IF NOT EXISTS action(
            id TEXT PRIMARY KEY, operation_id TEXT UNIQUE NOT NULL, name TEXT NOT NULL,
            acknowledged INTEGER NOT NULL DEFAULT 0, execution_status TEXT,
            acknowledged_at INTEGER, world_time INTEGER);
          CREATE TABLE IF NOT EXISTS tool_call(
            operation_id TEXT PRIMARY KEY REFERENCES operation(id), route_action_id TEXT NOT NULL,
            observation_id TEXT NOT NULL, sequence INTEGER NOT NULL,
            acknowledged INTEGER NOT NULL DEFAULT 0, execution_status TEXT,
            acknowledged_at INTEGER, world_time INTEGER);
          CREATE TABLE IF NOT EXISTS boundary(
            singleton INTEGER PRIMARY KEY CHECK(singleton=1), session_id TEXT NOT NULL,
            completed_cycles INTEGER NOT NULL, next_opportunity INTEGER NOT NULL,
            last_action_id TEXT NOT NULL, feedback_operation_id TEXT NOT NULL,
            reason TEXT NOT NULL, suspended_at INTEGER NOT NULL);
          CREATE TABLE IF NOT EXISTS checkpoint_binding(
            singleton INTEGER PRIMARY KEY CHECK(singleton=1), checkpoint_id TEXT NOT NULL,
            checkpoint_sha256 TEXT NOT NULL, pair_manifest_sha256 TEXT,
            database_before_binding_sha256 TEXT NOT NULL, bound_at INTEGER NOT NULL);
          CREATE TABLE IF NOT EXISTS audit(
            id INTEGER PRIMARY KEY AUTOINCREMENT, at INTEGER NOT NULL,
            event TEXT NOT NULL, detail TEXT NOT NULL);
        """)
        self.db.execute("INSERT OR IGNORE INTO bridge_meta(key,value)VALUES('schema',?)", (DATABASE_SCHEMA,))
        # Even QUEUED work is not replayed after a restart. Admission may have
        # reached another system immediately before a crash. Preserve uncertainty.
        with self.lock:
            pending = self.db.execute("SELECT count(*) FROM operation WHERE status IN ('QUEUED','RUNNING')").fetchone()[0]
            if pending:
                self.db.execute("UPDATE operation SET status='UNCERTAIN',error='BRIDGE_RESTART_RECONCILIATION_REQUIRED' WHERE status IN ('QUEUED','RUNNING')")
                self.db.execute("UPDATE session SET status='PAUSED',stop_reason='UNCERTAIN_NATIVE_COMMIT'")
                self._audit("RESTART_PAUSED", {"pending": pending})
        self.worker = None
        if start_worker:
            self.worker = threading.Thread(target=self._worker, name="RBX01-single-owner", daemon=False)
            self.worker.start()

    def authenticate(self, authorization: str | None):
        expected = "Bearer " + self.token
        if not isinstance(authorization, str) or not hmac.compare_digest(authorization, expected):
            raise BridgeError(401, "UNAUTHORIZED")

    def rate_check(self):
        with self.lock:
            q, stamp = self.rates["token"], time.monotonic()
            while q and q[0] <= stamp - 60:
                q.popleft()
            if len(q) >= self.rate_limit:
                raise BridgeError(429, "RATE_LIMIT")
            q.append(stamp)

    def _audit(self, event, detail):
        # Never accept arbitrary log strings from clients, nor put bearer data here.
        self.db.execute("INSERT INTO audit(at,event,detail) VALUES(?,?,?)", (now_ms(), event, canonical(detail)))

    def _session(self):
        row = self.db.execute("SELECT * FROM session WHERE singleton=1").fetchone()
        if row is None:
            raise BridgeError(409, "NO_SESSION")
        if row["status"] in {"ACTIVE", "PAUSING", "PAUSED"} and row["expires"] <= now_ms():
            self.db.execute("UPDATE session SET status='EXPIRED',stop_reason='SESSION_EXPIRED'")
            row = self.db.execute("SELECT * FROM session WHERE singleton=1").fetchone()
        return row

    def _active(self, session):
        if session["status"] != "ACTIVE":
            raise BridgeError(409, "SESSION_" + session["status"])

    def _quiescent_boundary(self, session):
        if session['phase'] != 'READY_QUERY':
            raise BridgeError(409, 'BOUNDARY_PHASE_NOT_QUIESCENT')
        if self.db.execute("SELECT 1 FROM operation WHERE status IN ('QUEUED','RUNNING','UNCERTAIN')").fetchone():
            raise BridgeError(409, 'BOUNDARY_HAS_PENDING_OR_UNCERTAIN')
        if self.db.execute("SELECT 1 FROM action WHERE acknowledged!=1 OR execution_status!='EXECUTED'").fetchone():
            raise BridgeError(409, 'BOUNDARY_HAS_UNACKED_ACTION')
        if self.db.execute('SELECT 1 FROM tool_call WHERE acknowledged!=1').fetchone():
            raise BridgeError(409, 'BOUNDARY_HAS_UNACKED_TOOL')

    def _validate(self, route, body):
        common = {"apiVersion", "requestId", "sessionId", "serverInstanceId"}
        extras = {
            "observation": {"observationId", "seq", "phase", "worldTimeMs", "sampleTimeMs", "previousActionId", "sensors"},
            "decision": {"observationId", "seq"},
            "query_sensor": {"observationId", "seq"},
            "function": {"actionId", "observationId", "seq", "worldTimeMs", "tool"},
            "tool_ack": {"operationId", "worldTimeMs", "executionStatus"},
            "feedback": {"actionId", "seq", "observationId", "worldTimeMs", "durationMs", "outcome", "collision", "resourceCollected", "resourceDelivered", "permissionSpent", "materialConsequence"},
            "ack": {"actionId", "worldTimeMs", "executionStatus"},
            "state": set(),
            "pause": {"reason"},
            "resume": {"checkpointId", "checkpointSha256"},
            "suspend": {"completedCycles", "nextOpportunity", "lastActionId", "feedbackOperationId", "reason"},
            "stop": {"reason"},
        }
        if route == "session/start":
            strict_object(body, {"apiVersion", "requestId", "ownerUserId", "worldId", "serverInstanceId", "mode", "level"})
            integer(body["ownerUserId"], 1, 2**53 - 1)
            identifier(body["worldId"])
            enum(body["mode"], MODES)
            enum(body["level"], {"L4", "L3", "L2", "L1"})
        else:
            required = common | extras[route]
            optional = {"operationId"} if route == "state" else set()
            if route == 'stop':
                optional |= {'completedCycles', 'nextOpportunity', 'lastActionId', 'feedbackOperationId'}
            if route == "observation":
                required = required - {"previousActionId"}
                optional.add("previousActionId")
            strict_object(body, required, optional)
            identifier(body["sessionId"])
        enum(body["apiVersion"], {API_VERSION})
        identifier(body["requestId"])
        identifier(body["serverInstanceId"])
        if route in {"observation", "decision", "query_sensor", "function", "feedback"}:
            identifier(body["observationId"])
            integer(body["seq"], 1, 128)
        if route == "observation":
            enum(body["phase"], {"QUERY_CHOICE", "ROUTE_CHOICE"})
            integer(body["worldTimeMs"], 0, 86_400_000)
            integer(body["sampleTimeMs"], 0, 2**53 - 1)
            if body.get("previousActionId") is not None:
                identifier(body["previousActionId"])
            sensors = strict_object(body["sensors"], SENSOR_KEYS)
            for key, bounds in {"station": (0, 5), "stage": (0, 3), "contact": (0, 4),
                                "stationSignal": (-1, 2), "permissionStock": (0, 200), "publicContactCode": (0, 5)}.items():
                integer(sensors[key], *bounds)
            for key in ("inventoryKey", "inventoryResource", "queryAvailable", "lastFailure"):
                boolean(sensors[key])
            if body["phase"] == "QUERY_CHOICE" and sensors["stationSignal"] != -1:
                raise BridgeError(400, "QUERY_SIGNAL_NOT_PERMITTED")
        if route in {"feedback", "ack", "function"}:
            identifier(body["actionId"])
            integer(body["worldTimeMs"], 0, 86_400_000)
        if route == 'function':
            tool = body['tool']
            if not isinstance(tool, dict):
                raise BridgeError(400, 'SCHEMA_TOOL')
            enum(tool.get('kind'), {'LESSON', 'CALCULATE'})
            if tool['kind'] == 'LESSON':
                strict_object(tool, {'kind', 'items'})
                if not isinstance(tool['items'], list) or not 1 <= len(tool['items']) <= 2:
                    raise BridgeError(400, 'SCHEMA_LESSON')
                forms = []
                for item in tool['items']:
                    strict_object(item, {'form', 'observedSign'})
                    enum(item['form'], {'luma', 'nara'})
                    integer(item['observedSign'], -1, 1)
                    if item['observedSign'] == 0:
                        raise BridgeError(400, 'TEACHER_ZERO_NOT_ALLOWED')
                    forms.append(item['form'])
                if len(set(forms)) != len(forms):
                    raise BridgeError(400, 'DUPLICATE_LESSON_FORM')
            else:
                strict_object(tool, {'kind', 'slot', 'form', 'left', 'right'})
                enum(tool['slot'], {'A', 'B'}); enum(tool['form'], {'luma', 'nara'})
                integer(tool['left'], 0, 32); integer(tool['right'], 0, 32)
        if route == 'tool_ack':
            identifier(body['operationId']); integer(body['worldTimeMs'], 0, 86_400_000)
            enum(body['executionStatus'], {'APPLIED', 'NO_RESULT'})
        if route == "feedback":
            integer(body["durationMs"], 0, 600_000)
            integer(body["permissionSpent"], 0, 3)
            enum(body["outcome"], {"MOVED", "BLOCKED", "KEY_COLLECTED", "RESOURCE_COLLECTED", "DELIVERED", "WAITED", "NUMERIC_INPUT_MISSING", "NUMERIC_OUT_OF_DOMAIN", "CODE_REJECTED", "TOOL_NO_RESULT"})
            for key in ("collision", "resourceCollected", "resourceDelivered", "materialConsequence"):
                boolean(body[key])
        if route == "ack":
            enum(body["executionStatus"], {"EXECUTED", "FAILED"})
        if route == "state" and "operationId" in body:
            identifier(body["operationId"])
        if route in {"stop", "pause"}:
            enum(body["reason"], {"OWNER_REQUEST", "INFRASTRUCTURE", "HOST_SAFETY_STOP", "HORIZON_COMPLETE"})
        if route == 'suspend':
            integer(body['completedCycles'], 0, MAX_DECISIONS)
            integer(body['nextOpportunity'], 1, MAX_DECISIONS + 1)
            identifier(body['lastActionId']); identifier(body['feedbackOperationId'])
            enum(body['reason'], {'CHECKPOINT_BOUNDARY', 'BOUNDARY_CHECKPOINT', 'OWNER_REQUEST', 'PROSPECTIVE_BOUNDARY'})
        if route == 'resume':
            identifier(body['checkpointId'])
            if not isinstance(body['checkpointSha256'], str) or not re.fullmatch(r'[0-9a-f]{64}', body['checkpointSha256']):
                raise BridgeError(400, 'SCHEMA_CHECKPOINT_HASH')

    def handle(self, route: str, body: dict, authorization: str | None, *, rate=True):
        self.authenticate(authorization)  # before validation, persistence or queues
        if rate:
            self.rate_check()
        if route not in ROUTES:
            raise BridgeError(404, "NOT_FOUND")
        self._validate(route, body)
        digest = hashlib.sha256(canonical(body).encode("ascii")).hexdigest()
        with self.lock:
            if self.closing.is_set():
                raise BridgeError(503, "BRIDGE_CLOSING")
            # Persist expiration even if the following mutation is rejected.
            if route != "session/start":
                self._session()
            self.db.execute("BEGIN IMMEDIATE")
            try:
                old = self.db.execute("SELECT * FROM request WHERE id=?", (body["requestId"],)).fetchone()
                if old:
                    if old["route"] != route or old["digest"] != digest:
                        raise BridgeError(409, "IDEMPOTENCY_CONFLICT")
                    # Admission returns the original response; state reconciles it.
                    result = (old["status_code"], json.loads(old["response"]))
                else:
                    if self.db.execute("SELECT count(*) FROM request").fetchone()[0] >= MAX_REQUESTS:
                        raise BridgeError(507, "REQUEST_BUDGET_EXHAUSTED")
                    result = self._dispatch(route, body)
                    self.db.execute("INSERT INTO request VALUES(?,?,?,?,?,?)",
                                    (body["requestId"], route, digest, result[0], canonical(result[1]), now_ms()))
                self.db.execute("COMMIT")
            except BaseException:
                self.db.execute("ROLLBACK")
                raise
        self.wake.set()
        return result

    def _dispatch(self, route, body):
        if route == "session/start":
            if body["ownerUserId"] != self.owner_user_id or body["worldId"] != self.world_id:
                raise BridgeError(403, "OWNER_OR_WORLD_DENIED")
            if self.db.execute("SELECT 1 FROM session").fetchone():
                raise BridgeError(409, "OWNER_SESSION_ALREADY_LATCHED")
            if body["mode"] != self.adapter.identity:
                raise BridgeError(503, "ADAPTER_MODE_UNAVAILABLE")
            if body["mode"] != "LIVE_NATIVE" and not self.allow_control:
                raise BridgeError(403, "CONTROL_DISABLED")
            sid, stamp = uuid.uuid4().hex, now_ms()
            self.db.execute("INSERT INTO session(singleton,id,server_id,mode,level,status,phase,created,expires) VALUES(1,?,?,?,?,'ACTIVE','READY_QUERY',?,?)",
                            (sid, body["serverInstanceId"], body["mode"], body["level"], stamp, stamp + self.session_seconds * 1000))
            self._audit("SESSION_STARTED", {"sessionId": sid, "mode": body["mode"], "level": body["level"]})
            return 201, {"apiVersion": API_VERSION, "sessionId": sid, "status": "ACTIVE", "lifeId": getattr(self.adapter, "public_life_id", None), "maxDecisions": MAX_DECISIONS, "expiresAtMs": stamp + self.session_seconds * 1000}
        session = self._session()
        if body["sessionId"] != session["id"] or body["serverInstanceId"] != session["server_id"]:
            raise BridgeError(403, "SESSION_OWNER_MISMATCH")
        if route == "state":
            result = self._public_session(session)
            if "operationId" in body:
                op = self.db.execute("SELECT * FROM operation WHERE id=?", (body["operationId"],)).fetchone()
                if not op:
                    raise BridgeError(404, "OPERATION_NOT_FOUND")
                result["operation"] = self._public_operation(op)
            return 200, result
        if route == "stop":
            pending = self.db.execute("SELECT 1 FROM operation WHERE status IN ('QUEUED','RUNNING')").fetchone()
            status = "STOPPING" if pending else "STOPPED"
            self.db.execute("UPDATE session SET status=?,stop_reason=?", (status, body["reason"]))
            self._audit("SESSION_STOP_REQUESTED", {"reason": body["reason"], "pending": bool(pending)})
            return 200, {"apiVersion": API_VERSION, "status": status, "preserved": True}
        if route == "pause":
            self._active(session)
            pending = self.db.execute("SELECT 1 FROM operation WHERE status IN ('QUEUED','RUNNING')").fetchone()
            status = "PAUSING" if pending else "PAUSED"
            self.db.execute("UPDATE session SET status=?,stop_reason=?", (status, body["reason"]))
            self._audit("SESSION_PAUSE_REQUESTED", {"reason": body["reason"], "pending": bool(pending)})
            return 200, {"apiVersion": API_VERSION, "status": status, "preserved": True}
        if route == "resume":
            if not self.resume_allowed or session["status"] != "SUSPENDED_BOUNDARY":
                raise BridgeError(409, "RESUME_NOT_SAFE")
            self._quiescent_boundary(session)
            binding = self.db.execute('SELECT * FROM checkpoint_binding WHERE singleton=1').fetchone()
            if binding is None or binding['checkpoint_id'] != body['checkpointId'] or binding['checkpoint_sha256'] != body['checkpointSha256']:
                raise BridgeError(409, 'CHECKPOINT_BINDING_MISMATCH')
            self.db.execute("UPDATE session SET status='ACTIVE',stop_reason=NULL")
            self._audit("SESSION_RESUMED", {'checkpointId': body['checkpointId'], 'checkpointSha256': body['checkpointSha256']})
            return 200, {"apiVersion": API_VERSION, "status": "ACTIVE", "preserved": True}
        if route == 'suspend':
            self._active(session)
            self._quiescent_boundary(session)
            feedback = self.db.execute("SELECT * FROM operation WHERE kind='feedback' AND status='COMPLETED' ORDER BY completed DESC LIMIT 1").fetchone()
            completed = self.db.execute("SELECT count(*) FROM operation WHERE kind='feedback' AND status='COMPLETED'").fetchone()[0]
            if (feedback is None or body['feedbackOperationId'] != feedback['id'] or
                    body['lastActionId'] != session['last_action_id'] or
                    body['completedCycles'] != completed or body['nextOpportunity'] != completed + 1):
                raise BridgeError(409, 'BOUNDARY_CURSOR_MISMATCH')
            self.db.execute('DELETE FROM checkpoint_binding')
            self.db.execute('INSERT OR REPLACE INTO boundary VALUES(1,?,?,?,?,?,?,?)',
                (session['id'], completed, body['nextOpportunity'], body['lastActionId'],
                 body['feedbackOperationId'], body['reason'], now_ms()))
            self.db.execute("UPDATE session SET status='SUSPENDED_BOUNDARY',stop_reason='BOUNDARY_CHECKPOINT'")
            self._audit('SESSION_SUSPENDED_BOUNDARY', {'completedCycles': completed, 'nextOpportunity': body['nextOpportunity']})
            return 200, {'apiVersion': API_VERSION, 'status': 'SUSPENDED_BOUNDARY',
                         'preserved': True, 'completedCycles': completed, 'nextOpportunity': body['nextOpportunity']}
        if route == "ack":
            action = self.db.execute("SELECT * FROM action WHERE id=?", (body["actionId"],)).fetchone()
            if not action or body["actionId"] != session["last_action_id"]:
                raise BridgeError(409, "ACTION_MISMATCH")
            if action["acknowledged"]:
                raise BridgeError(409, "ACTION_ALREADY_ACKNOWLEDGED")
            self.db.execute("UPDATE action SET acknowledged=1,execution_status=?,acknowledged_at=?,world_time=? WHERE id=?",
                            (body["executionStatus"], now_ms(), body["worldTimeMs"], body["actionId"]))
            if body["executionStatus"] == "FAILED":
                self.db.execute("UPDATE session SET status='PAUSED',stop_reason='ACTUATION_FAILED'")
            elif session["phase"] in {"WAIT_ACK_QUERY", "WAIT_ACK_ROUTE"}:
                phase = "READY_ROUTE" if session["phase"] == "WAIT_ACK_QUERY" and action["name"] != "SAFE_WAIT" else "AWAIT_FEEDBACK"
                self.db.execute("UPDATE session SET phase=?", (phase,))
            self._audit("ACTION_ACKNOWLEDGED", {"actionId": body["actionId"], "executionStatus": body["executionStatus"]})
            return 200, {"apiVersion": API_VERSION, "acknowledged": True, "actionId": body["actionId"]}
        if route == 'tool_ack':
            self._active(session)
            call = self.db.execute('SELECT t.*,o.status FROM tool_call t JOIN operation o ON o.id=t.operation_id WHERE t.operation_id=?', (body['operationId'],)).fetchone()
            if (session['phase'] != 'AWAIT_TOOL_ACK' or call is None or call['status'] != 'COMPLETED' or
                    call['route_action_id'] != session['last_action_id'] or call['observation_id'] != session['observation_id'] or
                    call['sequence'] != session['sequence'] or call['acknowledged']):
                raise BridgeError(409, 'TOOL_ACK_MISMATCH')
            self.db.execute('UPDATE tool_call SET acknowledged=1,execution_status=?,acknowledged_at=?,world_time=? WHERE operation_id=?',
                            (body['executionStatus'], now_ms(), body['worldTimeMs'], body['operationId']))
            self.db.execute("UPDATE session SET phase='AWAIT_FEEDBACK'")
            self._audit('TOOL_ACKNOWLEDGED', {'operationId': body['operationId'], 'executionStatus': body['executionStatus']})
            return 200, {'apiVersion': API_VERSION, 'acknowledged': True, 'operationId': body['operationId']}
        self._active(session)
        if route == "observation":
            expected = {"READY_QUERY": "QUERY_CHOICE", "READY_ROUTE": "ROUTE_CHOICE"}.get(session["phase"])
            if expected != body["phase"]:
                raise BridgeError(409, "OBSERVATION_PHASE_MISMATCH")
            if body["seq"] != session["sequence"] + 1 or body.get("previousActionId") != session["last_action_id"]:
                raise BridgeError(409, "OBSERVATION_SEQUENCE_MISMATCH")
            if self.db.execute("SELECT 1 FROM observation WHERE id=?", (body["observationId"],)).fetchone():
                raise BridgeError(409, "OBSERVATION_ID_REUSED")
            if body["phase"] == "ROUTE_CHOICE":
                prior = self.db.execute("SELECT name FROM action WHERE id=?", (session["last_action_id"],)).fetchone()
                if prior["name"] != "ASK_STATION" and body["sensors"]["stationSignal"] != -1:
                    raise BridgeError(400, "UNQUERIED_SIGNAL_NOT_PERMITTED")
                if prior["name"] == "ASK_STATION" and body["sensors"]["stationSignal"] == -1:
                    raise BridgeError(400, "QUERIED_SIGNAL_REQUIRED")
            actor = {k: v for k, v in body.items() if k not in {"apiVersion", "requestId", "sessionId", "serverInstanceId"}}
            actor.setdefault("previousActionId", None)
            self.db.execute("INSERT INTO observation VALUES(?,?,?,?)", (body["observationId"], body["seq"], canonical(actor), now_ms()))
            self.db.execute("UPDATE session SET sequence=?,observation_id=?,phase=?", (body["seq"], body["observationId"], "OBSERVED_QUERY" if expected == "QUERY_CHOICE" else "OBSERVED_ROUTE"))
            return 201, {"apiVersion": API_VERSION, "accepted": True, "observationId": body["observationId"], "seq": body["seq"]}
        if route in {"decision", "query_sensor", "function", "feedback"}:
            required = {"decision": "OBSERVED_QUERY", "query_sensor": "OBSERVED_ROUTE", "function": "AWAIT_FEEDBACK", "feedback": "AWAIT_FEEDBACK"}[route]
            if session["phase"] != required:
                raise BridgeError(409, "OPERATION_PHASE_MISMATCH")
            if body["observationId"] != session["observation_id"] or body["seq"] != session["sequence"]:
                raise BridgeError(409, "STALE_OBSERVATION")
            if route == "decision" and session["decisions"] >= MAX_DECISIONS:
                raise BridgeError(409, "DECISION_BUDGET_EXHAUSTED")
            if self.db.execute("SELECT 1 FROM operation WHERE status IN ('QUEUED','RUNNING')").fetchone():
                raise BridgeError(409, "QUEUE_FULL")
            obs = json.loads(self.db.execute("SELECT body FROM observation WHERE id=?", (session["observation_id"],)).fetchone()[0])
            if route in {'feedback', 'function'}:
                if body["actionId"] != session["last_action_id"]:
                    raise BridgeError(409, "FEEDBACK_ACTION_MISMATCH")
                actual = self.db.execute("SELECT acknowledged,execution_status FROM action WHERE id=?", (body["actionId"],)).fetchone()
                if not actual or actual["acknowledged"] != 1 or actual["execution_status"] != "EXECUTED":
                    raise BridgeError(409, "FEEDBACK_REQUIRES_ACTUAL_EXECUTED_ACK")
                if route == 'function':
                    route_op = self.db.execute('SELECT o.kind FROM action a JOIN operation o ON o.id=a.operation_id WHERE a.id=?', (body['actionId'],)).fetchone()
                    if route_op is None or route_op['kind'] != 'query_sensor':
                        raise BridgeError(409, 'FUNCTION_REQUIRES_ROUTE_ACK')
                    if self.db.execute('SELECT 1 FROM tool_call WHERE route_action_id=?', (body['actionId'],)).fetchone():
                        raise BridgeError(409, 'FUNCTION_ALREADY_USED')
                    payload = {'tool': body['tool']}
                else:
                    if self.db.execute('SELECT 1 FROM tool_call WHERE route_action_id=? AND acknowledged!=1', (body['actionId'],)).fetchone():
                        raise BridgeError(409, 'FEEDBACK_REQUIRES_TOOL_ACK')
                    payload = {k: v for k, v in body.items() if k not in {"apiVersion", "requestId", "sessionId", "serverInstanceId"}}
                    payload["lastObservation"] = obs
            else:
                payload = {"observation": obs}
            operation_id = uuid.uuid4().hex
            context = {"session_id": session["id"], "sequence": session["sequence"], "observation_id": session["observation_id"], "operation_id": operation_id, "mode": session["mode"]}
            self.db.execute("INSERT INTO operation(id,request_id,kind,status,payload,context,admitted) VALUES(?,?,?,'QUEUED',?,?,?)", (operation_id, body["requestId"], route, canonical(payload), canonical(context), now_ms()))
            if route == 'function':
                self.db.execute('INSERT INTO tool_call(operation_id,route_action_id,observation_id,sequence)VALUES(?,?,?,?)',
                                (operation_id, body['actionId'], body['observationId'], body['seq']))
            self.db.execute("UPDATE session SET phase=?,decisions=decisions+?", ("PROCESSING_" + route.upper(), int(route == "decision")))
            self._audit("OPERATION_ADMITTED", {"operationId": operation_id, "kind": route, "observationId": session["observation_id"]})
            return 202, {"apiVersion": API_VERSION, "operationId": operation_id, "status": "QUEUED"}
        raise BridgeError(404, "NOT_FOUND")

    def _public_session(self, row):
        result = {"apiVersion": API_VERSION, "sessionId": row["id"], "lifeId": getattr(self.adapter, "public_life_id", None), "mode": row["mode"], "level": row["level"], "status": row["status"], "phase": row["phase"], "seq": row["sequence"], "observationId": row["observation_id"], "lastActionId": row["last_action_id"], "decisions": row["decisions"], "selections": row["selections"], "nativeTicks": row["ticks"], "remainingDecisions": MAX_DECISIONS - row["decisions"], "expiresAtMs": row["expires"], "stopReason": row["stop_reason"]}
        rows = self.db.execute("SELECT completed-admitted AS latency,started-admitted AS queued FROM operation WHERE status='COMPLETED' ORDER BY completed").fetchall()
        def percentiles(values):
            values = sorted(values)
            if not values:
                return {"samples": 0, "p50": None, "p95": None}
            return {"samples": len(values), "p50": values[math.ceil(len(values) * 0.50) - 1], "p95": values[math.ceil(len(values) * 0.95) - 1]}
        result["latencyMs"] = percentiles([r["latency"] for r in rows])
        result["queueMs"] = percentiles([r["queued"] for r in rows])
        result["queueDepth"] = self.db.execute("SELECT count(*) FROM operation WHERE status IN ('QUEUED','RUNNING')").fetchone()[0]
        return result

    def _public_operation(self, row):
        result = {"operationId": row["id"], "kind": row["kind"], "status": row["status"], "admittedAtMs": row["admitted"], "startedAtMs": row["started"], "completedAtMs": row["completed"]}
        if row["error"]:
            result["error"] = row["error"]
        if row["result"]:
            private = json.loads(row["result"])
            result["result"] = {k: private[k] for k in ("action", "nativeTick", "nativeTicks", "null", "accepted", "toolResult") if k in private}
        return result

    def _worker(self):
        while not self.closing.is_set():
            self.wake.wait(0.5)
            self.wake.clear()
            if self.closing.is_set():
                break
            self.run_one()

    def run_one(self):
        """Single serialized work item; test harness can invoke it synchronously."""
        with self.lock:
            op = self.db.execute("SELECT * FROM operation WHERE status='QUEUED' ORDER BY admitted LIMIT 1").fetchone()
            if not op:
                return False
            session = self._session()
            if session["status"] not in {"ACTIVE", "PAUSING"}:
                self.db.execute("UPDATE operation SET status='CANCELLED',error='SESSION_NOT_ACTIVE',completed=? WHERE id=?", (now_ms(), op["id"]))
                if session["status"] == "STOPPING":
                    self.db.execute("UPDATE session SET status='STOPPED'")
                return True
            self.db.execute("UPDATE operation SET status='RUNNING',started=? WHERE id=?", (now_ms(), op["id"]))
        try:
            # The only external call. HTTP timeout never cancels or retries this.
            output = self.adapter.execute(op["kind"], json.loads(op["payload"]), json.loads(op["context"]))
            output = self._validate_output(op["kind"], output)
        except BaseException as error:
            # Adapter may have applied Native before raising: uncertainty, no retry.
            code = "NATIVE_UNAVAILABLE" if isinstance(error, NativeUnavailable) else "ADAPTER_UNCERTAIN"
            with self.lock:
                self.db.execute("BEGIN IMMEDIATE")
                self.db.execute("UPDATE operation SET status='UNCERTAIN',completed=?,error=? WHERE id=?", (now_ms(), code, op["id"]))
                self.db.execute("UPDATE session SET status='PAUSED',stop_reason=?", (code,))
                self._audit("OPERATION_UNCERTAIN", {"operationId": op["id"], "code": code})
                self.db.execute("COMMIT")
            return True
        with self.lock:
            self.db.execute("BEGIN IMMEDIATE")
            try:
                session = self._session()
                if session["ticks"] + output["nativeTicks"] > MAX_TICKS:
                    raise BridgeError(409, "NATIVE_TICK_BUDGET_EXCEEDED")
                if op['kind'] == 'function':
                    self.db.execute("UPDATE session SET phase='AWAIT_TOOL_ACK',ticks=ticks+?", (output['nativeTicks'],))
                elif op["kind"] != "feedback":
                    action_id = op["id"]  # Native opportunity correlation, never a client-chosen action.
                    name = output.pop("action")
                    self.db.execute("INSERT INTO action(id,operation_id,name) VALUES(?,?,?)", (action_id, op["id"], name))
                    output["action"] = {"actionId": action_id, "name": name, "nativeTick": output["nativeTick"], "nativeTicks": output["nativeTicks"], "null": output["null"]}
                    phase = "WAIT_ACK_QUERY" if op["kind"] == "decision" else "WAIT_ACK_ROUTE"
                    self.db.execute("UPDATE session SET phase=?,last_action_id=?,selections=selections+1,ticks=ticks+?", (phase, action_id, output["nativeTicks"]))
                else:
                    self.db.execute("UPDATE session SET phase='READY_QUERY',ticks=ticks+?", (output["nativeTicks"],))
                self.db.execute("UPDATE operation SET status='COMPLETED',completed=?,result=? WHERE id=?", (now_ms(), canonical(output), op["id"]))
                if session["status"] == "STOPPING":
                    self.db.execute("UPDATE session SET status='STOPPED'")
                elif session["status"] == "PAUSING":
                    self.db.execute("UPDATE session SET status='PAUSED'")
                self._audit("OPERATION_COMPLETED", {"operationId": op["id"], "nativeTicks": output["nativeTicks"]})
                self.db.execute("COMMIT")
            except BaseException:
                self.db.execute("ROLLBACK")
                self.db.execute("UPDATE operation SET status='UNCERTAIN',completed=?,error='COMPLETION_PERSISTENCE_UNCERTAIN' WHERE id=?", (now_ms(), op["id"]))
                self.db.execute("UPDATE session SET status='PAUSED',stop_reason='COMPLETION_PERSISTENCE_UNCERTAIN'")
        return True

    def _validate_output(self, kind, value):
        if not isinstance(value, dict):
            raise ValueError("Adapter output must be dictionary")
        result = dict(value)
        result.setdefault("nativeTick", None)
        integer(result.get("nativeTicks"), 0, 4096)
        if result.get("nativeTick") is not None:
            integer(result["nativeTick"], 0, 2**53 - 1)
        if kind == 'function':
            if result.get('accepted') is not True or not isinstance(result.get('toolResult'), dict):
                raise ValueError('Function must return actual admitted tool evidence')
            tool = result['toolResult']
            allowed_tool = {'kind', 'slot', 'form', 'memory_value', 'operation', 'numeric_result',
                            'updates', 'reason', 'formed', 'capability_execution_admitted', 'inputs'}
            if set(tool) - allowed_tool or not {'kind', 'memory_value', 'operation', 'numeric_result'} <= set(tool):
                raise ValueError('Closed public tool result')
            enum(tool['kind'], {'LESSON', 'CALCULATE'})
            if tool['memory_value'] is not None:
                integer(tool['memory_value'], -1, 1)
                if tool['memory_value'] == 0:
                    raise ValueError('Lexical0 is not a signed answer')
            if tool['operation'] is not None:
                enum(tool['operation'], {'suma', 'diferencia'})
            if tool['numeric_result'] is not None:
                # Carry the actual uint16-derived result even if interference
                # puts it outside the expected arithmetic domain. The world
                # evaluates that result; transport never repairs/suppresses it.
                integer(tool['numeric_result'], -32, 65535)
            if 'slot' in tool:
                enum(tool['slot'], {'A', 'B'})
            if 'form' in tool:
                enum(tool['form'], {'luma', 'nara'})
            if 'reason' in tool and (not isinstance(tool['reason'], str) or len(tool['reason']) > 96):
                raise ValueError('Bounded public tool reason')
            for flag in ('formed', 'capability_execution_admitted'):
                if flag in tool:
                    boolean(tool[flag])
            if 'inputs' in tool:
                if not isinstance(tool['inputs'], list) or len(tool['inputs']) != 2:
                    raise ValueError('Two public independent operands only')
                for operand in tool['inputs']:
                    if operand is not None:
                        integer(operand, 0, 32)
            if 'updates' in tool:
                if not isinstance(tool['updates'], list) or len(tool['updates']) > 2:
                    raise ValueError('Bounded visible lesson updates')
                for update in tool['updates']:
                    strict_object(update, {'form', 'observedSign'})
                    enum(update['form'], {'luma', 'nara'})
                    integer(update['observedSign'], -1, 1)
                    if update['observedSign'] == 0:
                        raise ValueError('No zero teacher update')
            result.pop('action', None)
            boolean(result.get('null'))
        elif kind == "feedback":
            if result.get("accepted") is not True:
                raise ValueError("Feedback must return admitted evidence")
        else:
            allowed = {"ASK_STATION", "SKIP_STATION", "SAFE_WAIT"} if kind == "decision" else {"EXIT_0", "EXIT_1", "SAFE_WAIT"}
            enum(result.get("action"), allowed)
            boolean(result.get("null"))
            if result["action"] == "SAFE_WAIT" and not result["null"]:
                raise ValueError("SAFE_WAIT must be explicitly NULL")
            if result["null"] and result["action"] != "SAFE_WAIT":
                raise ValueError("NULL cannot produce a material action")
        # Private evidence is JSON only and bounded independently of HTTP inputs.
        if len(canonical(result).encode("ascii")) > MAX_PAYLOAD:
            raise ValueError("Adapter evidence exceeds budget")
        return result

    def close(self, wait_seconds=5):
        self.closing.set()
        self.wake.set()
        if self.worker:
            self.worker.join(wait_seconds)
            if self.worker.is_alive():
                # Do not close DB under an active Native commit or kill its owner.
                return False
        with self.lock:
            self.db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            self.db.close()
            self.process_lease.close()
        return True

    def preserve_shutdown_timeout(self):
        with self.lock:
            self.db.execute("UPDATE session SET status='PAUSED',stop_reason='HOST_SHUTDOWN_DRAIN_TIMEOUT'")
            self._audit("HOST_SHUTDOWN_DRAIN_TIMEOUT", {"ownerMustRemainOpen": True,
                                                       "noAutomaticRetry": True})


def drain_bridge(bridge, wait_seconds=DRAIN_SECONDS):
    """Never silently return to an owner's context manager with an active writer."""
    if not 0 <= wait_seconds <= DRAIN_SECONDS:
        raise ValueError("Drain wait must be bounded by400 seconds")
    try:
        closed = bridge.close(wait_seconds=wait_seconds)
    except BaseException as error:
        # A second Ctrl+C must not unwind into the owner's __exit__ while its
        # writer is still applying material. Preserve instead of guessing.
        try:
            bridge.preserve_shutdown_timeout()
        except BaseException:
            pass
        raise BridgeDrainTimeout(bridge) from error
    if not closed:
        bridge.preserve_shutdown_timeout()
        raise BridgeDrainTimeout(bridge)


class BridgeHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    request_queue_size = 8
    allow_reuse_address = False

    def __init__(self, address, bridge):
        if address[0] != "127.0.0.1":
            raise ValueError("RBX01 binds only to loopback; HTTPS tunnel terminates separately")
        self.bridge, self.slots = bridge, threading.BoundedSemaphore(8)
        super().__init__(address, BridgeHandler)

    def process_request(self, request, client_address):
        if not self.slots.acquire(blocking=False):
            self.shutdown_request(request)
            return
        try:
            super().process_request(request, client_address)
        except BaseException:
            self.slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self.slots.release()


class BridgeHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"
    server_version = "RBX01"
    sys_version = ""

    def setup(self):
        super().setup()
        self.connection.settimeout(5)

    def log_message(self, fmt, *args):
        pass  # no request bodies, headers, credential or path logging

    def _send(self, code, body):
        encoded = canonical(body).encode("ascii")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "close")
        self.send_header("X-Content-Type-Options", "nosniff")
        if code == 429:
            self.send_header("Retry-After", "2")
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"apiVersion": API_VERSION, "status": "ok"})
        else:
            self._send(404, {"apiVersion": API_VERSION, "error": "NOT_FOUND"})

    def do_POST(self):
        try:
            # Fail closed before reading or parsing any unauthenticated payload.
            self.server.bridge.authenticate(self.headers.get("Authorization"))
            self.server.bridge.rate_check()
            if not self.path.startswith("/v1/") or self.path[4:] not in ROUTES:
                raise BridgeError(404, "NOT_FOUND")
            if self.headers.get("Transfer-Encoding") is not None:
                raise BridgeError(400, "TRANSFER_ENCODING_NOT_SUPPORTED")
            lengths = self.headers.get_all("Content-Length", [])
            if len(lengths) != 1 or not lengths[0].isascii() or not lengths[0].isdigit():
                raise BridgeError(411, "CONTENT_LENGTH_REQUIRED")
            length = int(lengths[0])
            if not 1 <= length <= MAX_PAYLOAD:
                raise BridgeError(413, "PAYLOAD_TOO_LARGE")
            if self.headers.get_content_type() != "application/json":
                raise BridgeError(415, "CONTENT_TYPE_REQUIRED")
            raw = self.rfile.read(length)
            if len(raw) != length:
                raise BridgeError(400, "INCOMPLETE_BODY")
            code, result = self.server.bridge.handle(self.path[4:], decode_body(raw), self.headers.get("Authorization"), rate=False)
            self._send(code, result)
        except BridgeError as error:
            self._send(error.status, {"apiVersion": API_VERSION, "error": error.code})
        except (TimeoutError, ConnectionError, BrokenPipeError):
            self.close_connection = True
        except (sqlite3.Error, ValueError, OverflowError):
            self._send(503, {"apiVersion": API_VERSION, "error": "PERSISTENCE_OR_CONTRACT_FAILURE"})


def init_private(owner_user_id=0):
    PRIVATE.mkdir(exist_ok=True)
    config_path, token_path = PRIVATE / "bridge.json", PRIVATE / "bridge-token.txt"
    if config_path.exists() or token_path.exists():
        raise RuntimeError("Private configuration already exists; never overwrite its token")
    token_path.write_text(secrets.token_urlsafe(48), encoding="ascii")
    config = {"apiVersion": API_VERSION, "bind": "127.0.0.1", "port": 8894,
              "ownerUserId": owner_user_id, "worldId": "RBX01_R05_C02_V1", "sessionSeconds": MAX_SESSION_SECONDS,
              "requestsPerMinute": 60, "allowControl": False, "tokenFile": "bridge-token.txt",
              "databaseFile": "bridge-state.sqlite3", "resumeAllowed": False}
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    return config_path  # Never return or print bearer contents.


def load_private_config(path=None):
    path = pathlib.Path(path or PRIVATE / "bridge.json").resolve()
    if path.parent != PRIVATE.resolve():
        raise ValueError("Configuration must be inside configuracion_privada")
    config = json.loads(path.read_text(encoding="utf-8"))
    strict_object(config, {"apiVersion", "bind", "port", "ownerUserId", "worldId", "sessionSeconds", "requestsPerMinute", "allowControl", "tokenFile", "databaseFile"}, {'resumeAllowed'})
    if config["bind"] != "127.0.0.1" or config["apiVersion"] != API_VERSION:
        raise ValueError("Only RBX01 loopback is supported")
    integer(config["port"], 1024, 65535)
    integer(config["sessionSeconds"], 30, MAX_SESSION_SECONDS)
    boolean(config["allowControl"])
    config.setdefault('resumeAllowed', False)
    boolean(config['resumeAllowed'])
    for key in ("tokenFile", "databaseFile"):
        candidate = (PRIVATE / config[key]).resolve()
        if candidate.parent != PRIVATE.resolve() or not isinstance(config[key], str):
            raise ValueError("Private data path escaped private directory")
        config[key] = candidate
    token = config["tokenFile"].read_text(encoding="ascii").strip()
    return config, token


def bootstrap_idle_window(session_seconds):
    """Finite host startup allowance, clamped to the configured session horizon."""
    integer(session_seconds, 30, MAX_SESSION_SECONDS)
    return min(BOOTSTRAP_IDLE_SECONDS, session_seconds)


def bind_checkpoint(database_path, checkpoint_id, checkpoint_sha256, *, pair_manifest_sha256=None):
    """Offline binding after coherent save and bridge close, never a world call.

    The checkpoint hash identifies an EXTERNAL closed-world manifest; it must
    not include this post-binding database hash in its own hashed contents.
    Return the database before/after hashes as a separate receipt to avoid a
    self-referential hash cycle. IDs, session, sequences and receipts persist.
    """
    identifier(checkpoint_id)
    for name, value in (('checkpoint', checkpoint_sha256), ('pair', pair_manifest_sha256)):
        if value is not None and (not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{64}', value)):
            raise ValueError('Exact SHA256 required: ' + name)
    if checkpoint_sha256 is None:
        raise ValueError('External checkpoint SHA256 required')
    path = pathlib.Path(database_path).resolve(strict=True)
    if not path.is_file() or path.is_symlink():
        raise ValueError('Existing regular C02 database required')
    lease = ProcessLease(path)
    db = None
    try:
        wal = pathlib.Path(str(path) + '-wal')
        if wal.exists() and wal.stat().st_size:
            raise ValueError('Uncheckpointed WAL: close the bridge coherently first')
        before = hashlib.sha256(path.read_bytes()).hexdigest()
        db = sqlite3.connect(str(path), isolation_level=None)
        db.row_factory = sqlite3.Row
        schema = db.execute("SELECT value FROM bridge_meta WHERE key='schema'").fetchone()
        if schema is None or schema[0] != DATABASE_SCHEMA:
            raise ValueError('Only exact C02 bridge schema can be bound')
        session = db.execute('SELECT * FROM session WHERE singleton=1').fetchone()
        boundary = db.execute('SELECT * FROM boundary WHERE singleton=1').fetchone()
        if (session is None or session['status'] != 'SUSPENDED_BOUNDARY' or
                session['phase'] != 'READY_QUERY' or boundary is None or
                boundary['session_id'] != session['id'] or
                boundary['last_action_id'] != session['last_action_id']):
            raise ValueError('Exact suspended boundary required for binding')
        if db.execute("SELECT 1 FROM operation WHERE status IN('QUEUED','RUNNING','UNCERTAIN')").fetchone():
            raise ValueError('Cannot bind pending/uncertain Native transport')
        if db.execute("SELECT 1 FROM action WHERE acknowledged!=1 OR execution_status!='EXECUTED'").fetchone():
            raise ValueError('Cannot bind unacknowledged action')
        if db.execute('SELECT 1 FROM tool_call WHERE acknowledged!=1').fetchone():
            raise ValueError('Cannot bind unacknowledged tool')
        if db.execute('SELECT 1 FROM checkpoint_binding').fetchone():
            raise ValueError('Checkpoint already bound; no overwrite or favorable rebind')
        db.execute('BEGIN IMMEDIATE')
        db.execute('INSERT INTO checkpoint_binding VALUES(1,?,?,?,?,?)',
                   (checkpoint_id, checkpoint_sha256, pair_manifest_sha256, before, now_ms()))
        db.execute('INSERT INTO audit(at,event,detail)VALUES(?,?,?)',
                   (now_ms(), 'OFFLINE_CHECKPOINT_BOUND', canonical({'checkpointId': checkpoint_id,
                    'checkpointSha256': checkpoint_sha256, 'pairManifestSha256': pair_manifest_sha256,
                    'databaseBeforeBindingSha256': before})))
        db.execute('COMMIT')
        db.execute('PRAGMA wal_checkpoint(TRUNCATE)')
        db.close(); db = None
        after = hashlib.sha256(path.read_bytes()).hexdigest()
        return {'schema': 'DEE.RBX01.C02.offline_checkpoint_binding.R01',
                'database': str(path), 'database_before_sha256': before, 'database_after_sha256': after,
                'checkpoint_id': checkpoint_id, 'checkpoint_sha256': checkpoint_sha256,
                'pair_manifest_sha256': pair_manifest_sha256, 'session_id': session['id'],
                'sequence': session['sequence'], 'last_action_id': session['last_action_id'],
                'new_Native_ticks': 0, 'session_recreated': False}
    finally:
        if db is not None:
            db.close()
        lease.close()


class ResumeBootstrapGate:
    """Transport-only startup latch; only a new successful /resume releases it.

    Never changes session/counter state or marks an old suspension as resumed.
    The bounded wait permits health/passive owner checks before the first RPC.
    """
    def __init__(self, resume_allowed, initial_status, audit_floor, bootstrap_seconds, *, now=None):
        self.awaiting = resume_allowed is True and initial_status == 'SUSPENDED_BOUNDARY'
        self.audit_floor = int(audit_floor or 0)
        self.deadline = (time.monotonic() if now is None else now) + bootstrap_seconds

    def observe(self, newest_successful_resume_id, *, now=None):
        if not self.awaiting:
            return 'NORMAL'
        if int(newest_successful_resume_id or 0) > self.audit_floor:
            self.awaiting = False
            return 'NORMAL'
        if (time.monotonic() if now is None else now) >= self.deadline:
            return 'RESUME_BOOTSTRAP_TIMEOUT'
        return 'AWAIT_EXPLICIT_RESUME'


def serve(adapter=None, config_path=None):
    """Root runner attaches the existing one-owner adapter and calls this.

    This function never imports an owner, begins a DEE life, or loads a policy.
    An unattached CLI server may answer health but rejects session/start.
    """
    config, token = load_private_config(config_path)
    bridge = Bridge(config["databaseFile"], token, config["ownerUserId"], adapter,
                    world_id=config["worldId"], session_seconds=config["sessionSeconds"],
                    rate_limit=config["requestsPerMinute"], allow_control=config["allowControl"],
                    resume_allowed=config['resumeAllowed'])
    try:
        server = BridgeHTTPServer((config["bind"], config["port"]), bridge)
    except BaseException:
        drain_bridge(bridge)
        raise
    monitor_done = threading.Event()
    with bridge.lock:
        startup_row = bridge.db.execute('SELECT status FROM session WHERE singleton=1').fetchone()
        audit_floor = bridge.db.execute('SELECT COALESCE(MAX(id),0) FROM audit').fetchone()[0]
    resume_gate = ResumeBootstrapGate(config['resumeAllowed'], startup_row[0] if startup_row else None,
                                      audit_floor, bootstrap_idle_window(config['sessionSeconds']))

    def finite_service():
        deadline = time.monotonic() + config["sessionSeconds"] + 30
        idle_deadline = time.monotonic() + bootstrap_idle_window(config["sessionSeconds"])
        while not monitor_done.wait(0.5):
            with bridge.lock:
                row = bridge.db.execute("SELECT * FROM session WHERE singleton=1").fetchone()
                if row:
                    row = bridge._session()
                pending = bridge.db.execute("SELECT 1 FROM operation WHERE status IN ('QUEUED','RUNNING')").fetchone()
                should_close = (row is None and time.monotonic() >= idle_deadline) or (
                    row is not None and row["status"] in {"STOPPED", "EXPIRED", "SUSPENDED_BOUNDARY"} and not pending)
                latest_resume = bridge.db.execute("SELECT COALESCE(MAX(id),0) FROM audit WHERE event='SESSION_RESUMED'").fetchone()[0]
                resume_wait = resume_gate.observe(latest_resume)
                if resume_wait == 'AWAIT_EXPLICIT_RESUME':
                    should_close = False
                elif resume_wait == 'RESUME_BOOTSTRAP_TIMEOUT' and not pending:
                    should_close = True
                if time.monotonic() >= deadline and not pending:
                    should_close = True
            if should_close:
                server.shutdown()
                return

    monitor = threading.Thread(target=finite_service, name="RBX01-finite-service", daemon=True)
    monitor.start()
    try:
        server.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        pass
    finally:
        monitor_done.set()
        server.server_close()
        drain_bridge(bridge)


def local_admin(command):
    """Local operator status/stop; credentials remain in private memory/header."""
    config, token = load_private_config()
    path = config["databaseFile"]
    if not path.is_file():
        raise RuntimeError("No bridge database exists")
    db = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    try:
        row = db.execute("SELECT id,server_id FROM session WHERE singleton=1").fetchone()
    finally:
        db.close()
    if row is None:
        raise RuntimeError("No session has been started")
    body = {"apiVersion": API_VERSION, "requestId": uuid.uuid4().hex,
            "sessionId": row[0], "serverInstanceId": row[1]}
    route = "state" if command == "status" else "stop"
    if command == "stop":
        body["reason"] = "OWNER_REQUEST"
    request = urllib.request.Request(f"http://127.0.0.1:{config['port']}/v1/{route}",
                                     data=canonical(body).encode("ascii"), method="POST",
                                     headers={"Authorization": "Bearer " + token,
                                              "Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=5) as response:
        return json.load(response)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RBX01 restricted loopback bridge (no Native owner is opened)")
    parser.add_argument("command", choices=("init-private", "serve", "status", "stop"))
    parser.add_argument("--owner-user-id", type=int, default=0)
    args = parser.parse_args()
    if args.command == "init-private":
        print("Private configuration created:", init_private(args.owner_user_id))
    elif args.command == "serve":
        serve()
    else:
        print(canonical(local_admin(args.command)))
