from __future__ import annotations

import sys
import tempfile
import unittest
import gc
from pathlib import Path

import dee_thinking as dt


class WheelApiTests(unittest.TestCase):
    def test_native_identity_and_platform(self) -> None:
        self.assertEqual(dt.__version__, "2.2.0")
        self.assertEqual(dt.KERNEL_MODULUS, 19665)
        self.assertEqual(dt.REDUCER_CAP, 19664)
        info = dt.build_info()
        self.assertTrue(info["native_module"])
        self.assertFalse(info["delegates_to_dee_universe_v27"])
        self.assertFalse(info["gil_released_during_runtime_evolution"])
        self.assertNotIn("dee_universe_v27", sys.modules)
        self.assertEqual(sys.version_info[:2], (3, 13))

    def test_runtime_receipt_observe_snapshot_and_fork(self) -> None:
        world = dt.Runtime(11)
        channel = dt.ChannelSpec()
        channel.name = "input"
        channel.injection_site = dt.Coordinate(3, 4, 5)
        channel.state = 101
        channel.direction = dt.Direction(1, 0, 0)
        channel.semantic = 1
        channel.allow_experience = True
        channel.allow_probe = True
        world.register_channel(channel)
        scheduled = world.experience("input", 0, 17)
        self.assertEqual(scheduled.status, dt.EventStatus.SCHEDULED)

        before_raw = world.raw_copy()
        before_clock = world.clock_copy()
        world.observe(dt.Coordinate(3, 4, 5))
        self.assertEqual(before_raw, world.raw_copy())
        self.assertEqual(before_clock, world.clock_copy())
        self.assertEqual(world.advance(0).total, 0)

        info = world.advance(1)
        self.assertFalse(info.fallback)
        applied = world.receipt(scheduled.id)
        self.assertEqual(applied.status, dt.EventStatus.APPLIED)
        self.assertEqual(applied.effective_tick, 0)
        self.assertEqual(world.current_tick, 1)

        fork = world.fork()
        self.assertEqual(world.raw_copy(), fork.raw_copy())
        fork.advance(1)
        self.assertEqual(world.current_tick, 1)
        self.assertEqual(fork.current_tick, 2)

        independent = dt.Runtime(11)
        self.assertEqual(independent.metrics().raw_support, 0)
        self.assertNotEqual(world.raw_copy(), independent.raw_copy())

        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "python_runtime.deetsnap"
            world.set_snapshot_metadata("python.test", "wheel_api")
            world.save_snapshot(str(path))
            restored = dt.Runtime.load_snapshot(str(path))
            self.assertEqual(restored.raw_copy(), world.raw_copy())
            self.assertEqual(restored.clock_copy(), world.clock_copy())
            self.assertEqual(restored.snapshot_metadata("python.test"), "wheel_api")

    def test_pause_and_explicit_errors(self) -> None:
        world = dt.Runtime(5)
        world.pause()
        with self.assertRaises(RuntimeError):
            world.advance(1)
        world.resume()
        world.advance(1)
        with self.assertRaises(ValueError):
            world.run_until(0)

    def test_catalog_and_protocol_registry(self) -> None:
        catalog = dt.OrganizationCatalog()
        self.assertGreater(len(catalog.descriptors), 0)
        descriptors = dt.integrated_protocol_descriptors()
        self.assertEqual(
            {item.id for item in descriptors},
            {dt.H1_ID, dt.H2_ID, dt.H3_ID, dt.H4_ID, dt.F1_ID, dt.F2_ID},
        )
        self.assertIsNotNone(dt.find_integrated_protocol(dt.F2_ID))
        self.assertIsNone(dt.find_integrated_protocol("not.a.protocol"))
        for _ in range(32):
            descriptor = dt.find_integrated_protocol(dt.F1_ID)
            self.assertEqual(descriptor.id, dt.F1_ID)
            del descriptor
            gc.collect()
        self.assertEqual(dt.find_integrated_protocol(dt.F1_ID).id, dt.F1_ID)

    def test_composition_world_experience_probe_and_snapshot(self) -> None:
        catalog = dt.OrganizationCatalog()

        learner_request = dt.OrganizationRequest()
        learner_request.catalog_id = "relation_learning.c6h01.v1"
        learner_request.instance_id = "learner"
        learner_request.anchor = dt.Coordinate(10, 18, 14)
        learner = catalog.instantiate(learner_request)

        reader_request = dt.OrganizationRequest()
        reader_request.catalog_id = "relation_query.c6h01.v1"
        reader_request.instance_id = "reader"
        reader_request.anchor = dt.Coordinate(10, 26, 14)
        reader = catalog.instantiate(reader_request)

        connection = dt.ConnectionRequest()
        connection.source = dt.Endpoint()
        connection.source.instance = "learner"
        connection.source.port = "learned_relation"
        connection.target = dt.Endpoint()
        connection.target.instance = "reader"
        connection.target.port = "relation_input"
        connection.purpose = "later query"

        planner = dt.CompositionPlanner(34)
        planner.add(learner)
        planner.add(reader)
        planner.connect(connection)
        diagnostics = planner.analyze()
        self.assertFalse(any(item.severity == dt.DiagnosticSeverity.ERROR for item in diagnostics))
        world = planner.build()
        world.runtime.execution_options = dt.TickOptions(dt.Backend.LAZY, 2)

        cue = dt.PortInputRequest()
        cue.instance, cue.port, cue.s_reg = "learner", "cue", 5
        teacher = dt.PortInputRequest()
        teacher.instance, teacher.port, teacher.s_reg = "learner", "teacher", 7
        training = world.experience_batch([cue, teacher], 0)
        self.assertEqual(training.status, dt.EventStatus.SCHEDULED)
        world.runtime.run_until(6)
        query = world.probe("reader", "query", 6, 13)
        self.assertEqual(query.status, dt.EventStatus.SCHEDULED)
        world.runtime.run_until(11)
        response_site = world.landmarks["reader.response"]
        response = world.runtime.observe(response_site)
        self.assertEqual(response.record.s_reg, 25)

        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "composed_world.deetsnap"
            world.save_snapshot(str(path))
            restored = dt.ComposedWorld.load_snapshot(str(path))
            self.assertEqual(restored.runtime.raw_copy(), world.runtime.raw_copy())
            self.assertEqual(restored.runtime.clock_copy(), world.runtime.clock_copy())
            self.assertEqual(
                restored.runtime.observe(restored.landmarks["reader.response"]).record.s_reg,
                25,
            )

    def test_h4_finite_diagnostic(self) -> None:
        q = dt.Coordinate(1, 2, 3)
        raw_10 = dt.pack_record(1, 10, 1, 0, 0, 1)
        raw_12 = dt.pack_record(1, 12, 1, 0, 0, 1)
        raw_17 = dt.pack_record(1, 17, 1, 0, 0, 1)

        def reading(raw: int) -> dt.AccessibilityReading:
            value = dt.AccessibilityReading()
            value.site = q
            value.raw = raw
            value.clock = 41
            return value

        case_a = dt.AccessibilityCase()
        case_a.history_id = "history_a"
        case_a.baseline_tick = case_a.challenged_tick = 41
        case_a.baseline = [reading(raw_10)]
        case_a.challenged = [reading(raw_12)]
        case_a.history_status = dt.AccessibilityStatus.REACHED
        case_a.history_reached_natively = True

        case_b = dt.AccessibilityCase()
        case_b.history_id = "history_b"
        case_b.baseline_tick = case_b.challenged_tick = 41
        case_b.baseline = [reading(raw_10)]
        case_b.challenged = [reading(raw_17)]
        case_b.history_status = dt.AccessibilityStatus.ACQUIRED
        case_b.history_reached_natively = True

        request = dt.AccessibilityRequest()
        request.observer_id = "declared_observer"
        request.challenge_id = "frozen_challenge"
        request.cases = [case_a, case_b]
        result = dt.analyze_accessibility(request)
        self.assertTrue(result.comparable)
        self.assertTrue(result.history_conditioned_response)
        self.assertEqual(result.effects[0].s_reg_deltas, [2])
        self.assertEqual(result.effects[1].s_reg_deltas, [7])


if __name__ == "__main__":
    unittest.main(verbosity=2)
