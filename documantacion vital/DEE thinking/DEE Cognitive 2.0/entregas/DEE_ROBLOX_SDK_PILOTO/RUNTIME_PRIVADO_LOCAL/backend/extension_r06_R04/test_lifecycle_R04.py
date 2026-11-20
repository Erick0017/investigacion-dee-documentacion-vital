"""Pure R04 HTTP receipt lifecycle checks: no sockets, owners or Native imports."""
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlsplit, parse_qs
import ast
import hashlib
import hmac
import json
import unittest

SOURCE = Path(__file__).with_name("servicio_capabilities_http_R06.py")


class FakeClock:
    def __init__(self, now=100.0):
        self.now = now
    def time(self):
        return self.now


class LifecycleR04Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = SOURCE.read_bytes()
        cls.source_sha256 = hashlib.sha256(source).hexdigest()
        tree = ast.parse(source.decode("utf-8-sig"), filename=str(SOURCE))
        names = {"keep_http_open", "mark_terminal_delivery", "handler"}
        selected = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
        if {node.name for node in selected} != names:
            raise AssertionError("Exact three lifecycle functions are required")
        cls.namespace = {
            "BaseHTTPRequestHandler": object, "canonical": lambda value: json.dumps(value, sort_keys=True),
            "hmac": hmac, "urlsplit": urlsplit, "parse_qs": parse_qs, "json": json,
            "Conflict": type("FixtureConflict", (RuntimeError,), {}),
        }
        # Execute only the three selected definitions, never the service module.
        module = ast.Module(body=selected, type_ignores=[])
        exec(compile(module, str(SOURCE) + ":pure_lifecycle_only", "exec"), cls.namespace)

    @classmethod
    def tearDownClass(cls):
        if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != cls.source_sha256:
            raise AssertionError("R04 service source changed during pure tests")

    def setUp(self):
        self.clock = FakeClock()
        self.events = []
        self.service = SimpleNamespace(
            stop=True, scope={"native_cutoff_utc_epoch": 1000.0},
            close_grace_deadline=None, close_receipt_delivered=False,
            token="SYNTHETIC_AUTH_ONLY", instance="SDK_DEMO_0123456789ABCDEF",
        )
        self.operation_value = {"kind": "CLOSE", "status": "COMPLETED", "operationId": "CLOSE_FAKE"}
        self.service.operation = lambda identifier: self.operation_value
        self.service.handshake = lambda: {"kind": "CLOSE", "status": "COMPLETED"}
        self.original_marker = self.namespace["mark_terminal_delivery"]

        def mark(service, value):
            self.events.append("mark")
            return self.original_marker(service, value)

        self.namespace["mark_terminal_delivery"] = mark
        self.addCleanup(self.namespace.__setitem__, "mark_terminal_delivery", self.original_marker)

    def keep(self):
        return self.namespace["keep_http_open"](self.service, self.clock.time())

    def request(self, path=None, fail=None):
        events = self.events
        handler_type = self.namespace["handler"](self.service)
        handler = handler_type()
        handler.command = "GET"
        handler.path = path or ("/v1/capability-operations/CLOSE_FAKE?instanceId=" + self.service.instance)
        handler.headers = {"Authorization": "Bearer " + self.service.token}
        handler.send_response = lambda code: events.append(("status", code))
        handler.send_header = lambda name, value: None
        handler.end_headers = lambda: events.append("headers")

        class FakeWriter:
            def write(self, data):
                events.append("write")
                if fail == "write":
                    raise OSError("Synthetic write failure")
                self.data = data
            def flush(self):
                events.append("flush")
                if fail == "flush":
                    raise OSError("Synthetic flush failure")

        handler.wfile = FakeWriter()
        return handler

    def test_running_http_is_limited_by_hard_deadline(self):
        self.service.stop = False
        self.assertTrue(self.keep())
        self.assertIsNone(self.service.close_grace_deadline)
        self.clock.now = 1000.0
        self.assertFalse(self.keep())

    def test_stop_does_not_exit_immediately_and_grace_never_extends(self):
        self.assertTrue(self.keep())
        self.assertEqual(self.service.close_grace_deadline, 160.0)
        self.clock.now = 125.0
        self.assertTrue(self.keep())
        self.assertEqual(self.service.close_grace_deadline, 160.0)
        self.clock.now = 159.999
        self.assertTrue(self.keep())
        self.clock.now = 160.0
        self.assertFalse(self.keep())
        self.assertFalse(self.service.close_receipt_delivered)

    def test_pending_and_nonclose_operation_get_do_not_end_receipt_wait(self):
        self.assertTrue(self.keep())
        for value in (
            {"kind": "CLOSE", "status": "PENDING"},
            {"kind": "CLOSE", "status": "RUNNING"},
            {"kind": "CLOSE", "status": "FAILED_KNOWN"},
            {"kind": "NUMERIC", "status": "COMPLETED"},
        ):
            self.operation_value = value
            self.events.clear()
            with self.subTest(value=value):
                self.request().route()
                self.assertFalse(self.service.close_receipt_delivered)
                self.assertTrue(self.keep())
        # Even an accidental CLOSE-like handshake body is not a terminal operation GET.
        self.events.clear()
        self.request("/v1/capabilities/handshake").route()
        self.assertNotIn("mark", self.events)
        self.assertFalse(self.service.close_receipt_delivered)
        self.assertTrue(self.keep())

    def test_terminal_close_get_is_marked_only_after_200_write_and_flush_then_exits(self):
        self.assertTrue(self.keep())
        handler = self.request()
        handler.route()
        self.assertEqual(self.events, [("status", 200), "headers", "write", "flush", "mark"])
        self.assertTrue(self.service.close_receipt_delivered)
        body = json.loads(handler.wfile.data)
        self.assertTrue(body["ok"])
        self.assertEqual(body["result"], self.operation_value)
        self.clock.now = 101.0
        self.assertFalse(self.keep())

    def test_failed_write_or_flush_never_marks_terminal_delivery(self):
        for failure in ("write", "flush"):
            self.events.clear()
            self.service.close_receipt_delivered = False
            with self.subTest(failure=failure), self.assertRaises(OSError):
                self.request(fail=failure).route()
            self.assertNotIn("mark", self.events)
            self.assertFalse(self.service.close_receipt_delivered)
            self.assertTrue(self.keep())

    def test_grace_is_clipped_to_hard_cutoff_and_expired_hard_never_opens(self):
        self.service.scope["native_cutoff_utc_epoch"] = 130.0
        self.assertTrue(self.keep())
        self.assertEqual(self.service.close_grace_deadline, 130.0)
        self.clock.now = 129.999
        self.assertTrue(self.keep())
        self.clock.now = 130.0
        self.assertFalse(self.keep())
        self.service.close_grace_deadline = None
        self.clock.now = 140.0
        self.assertFalse(self.keep())
        self.assertEqual(self.service.close_grace_deadline, 130.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)

