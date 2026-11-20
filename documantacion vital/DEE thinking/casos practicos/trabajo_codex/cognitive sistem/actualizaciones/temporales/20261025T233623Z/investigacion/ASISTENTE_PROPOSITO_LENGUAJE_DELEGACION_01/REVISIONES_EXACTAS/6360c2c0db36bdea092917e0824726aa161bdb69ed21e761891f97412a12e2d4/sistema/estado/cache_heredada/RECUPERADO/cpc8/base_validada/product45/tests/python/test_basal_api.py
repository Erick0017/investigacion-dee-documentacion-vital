from __future__ import annotations

import tempfile
import unittest
import gc
from pathlib import Path

import dee_thinking as dt


class BasalApiTests(unittest.TestCase):
    @staticmethod
    def _port_signature(ports):
        coord = lambda q: None if q is None else (q.x, q.y, q.z)
        return {
            "origin": coord(ports.origin),
            "a": coord(ports.a),
            "b": coord(ports.b),
            "comparator": coord(ports.comparator),
            "reader_source": coord(ports.reader_source),
            "event_sources": [coord(q) for q in ports.event_sources],
            "supports": [coord(q) for q in ports.supports],
            "environmental_sources": [coord(q) for q in ports.environmental_sources],
            "action_site": coord(ports.action_site),
            "return_site": coord(ports.return_site),
            "bend_site": coord(ports.bend_site),
            "bend2_site": coord(ports.bend2_site),
        }

    def test_relational_histories_and_validated_translations(self) -> None:
        expected = {
            dt.BasalHistory.AB: 1,
            dt.BasalHistory.BA: -1,
            dt.BasalHistory.H0: 0,
        }
        for history, delta in expected.items():
            with self.subTest(history=str(history)):
                world = dt.create_relational_world(history)
                before = world.observe()
                self.assertEqual(before.absolute_tick, 32)
                self.assertEqual(before.relative_tick, 0)
                self.assertEqual(before.delta, 0)
                self.assertEqual(before.a.record.s_reg, 100)
                self.assertEqual(before.b.record.s_reg, 100)
                world.advance(1)
                self.assertEqual(world.observe().delta, delta)

        for origin in ((22, 20, 24), (28, 26, 18)):
            with self.subTest(origin=origin):
                world = dt.create_relational_world(origin=origin)
                world.advance(1)
                observed = world.observe()
                self.assertEqual(observed.delta, 1)
                self.assertEqual(observed.a.record.s_reg, 101)
                self.assertEqual(observed.b.record.s_reg, 100)

    def test_contextual_write_gate_and_retention(self) -> None:
        world = dt.create_contextual_world()
        world.advance(131)
        before = world.observe()
        self.assertEqual(before.absolute_tick, 163)
        self.assertEqual(before.relative_tick, 131)
        self.assertEqual(before.a.record.s_reg, 101)
        self.assertEqual(before.b.record.s_reg, 100)
        self.assertEqual(before.delta, 1)

        raw = world.runtime.raw_copy()
        clocks = world.runtime.clock_copy()
        gate = dt.inspect_write_gate(world.runtime, world.ports.b, True)
        self.assertEqual(gate.local_clock, 391)
        self.assertEqual(gate.n_active, 6)
        self.assertEqual(gate.period, 391)
        self.assertEqual(gate.phase_remainder, 0)
        self.assertTrue(gate.ordinary_increment_condition)
        self.assertEqual(len(gate.neighbors), 26)
        self.assertEqual(gate.demux_status, "UNRESOLVED_FROM_PASSIVE_PRESTATE")
        self.assertEqual(raw, world.runtime.raw_copy())
        self.assertEqual(clocks, world.runtime.clock_copy())

        before_write = world.fork()
        world.advance(1)
        after = world.observe()
        self.assertEqual(after.relative_tick, 132)
        self.assertEqual(after.b.record.s_reg, 101)
        self.assertEqual(after.delta, 0)
        transition = dt.compare_site_transition(
            before_write.runtime, world.runtime, world.ports.b
        )
        self.assertEqual(transition.classification, "OBSERVED_CHANGE")
        self.assertIn("s_reg", transition.changed_fields)

        world.advance(38)
        retained = world.observe()
        self.assertEqual(retained.relative_tick, 170)
        self.assertEqual(retained.delta, 0)

    def test_passive_tracker_and_fork_isolation(self) -> None:
        tracked = dt.create_relational_world()
        reference = tracked.fork()
        a = dt.TrackedSite()
        a.id, a.site = "A", tracked.ports.a
        b = dt.TrackedSite()
        b.id, b.site = "B", tracked.ports.b
        tracker = dt.PassiveTracker([a, b], 8)
        tracker.capture(tracked.runtime)
        for _ in range(3):
            tracked.advance(1)
            tracker.capture(tracked.runtime)
            reference.advance(1)
        self.assertEqual(tracked.runtime.raw_copy(), reference.runtime.raw_copy())
        self.assertEqual(tracked.runtime.clock_copy(), reference.runtime.clock_copy())
        self.assertEqual(len(tracker.frames), 4)
        self.assertEqual(len(tracker.transitions), 3)

        parent = dt.create_contextual_world()
        parent.advance(131)
        parent_raw = parent.runtime.raw_copy()
        parent_clock = parent.runtime.clock_copy()
        edit = dt.ResearchStateEdit()
        edit.coordinate = parent.ports.b
        edit.clock = 392
        edit.label = "diagnostic.phase_miss_at_b"
        with self.assertRaises(ValueError):
            parent.diagnostic_fork([edit], False)
        result = dt.compare_diagnostic_fork(parent, [edit], 1, True)
        self.assertTrue(result.parent_unchanged)
        self.assertEqual(result.reference_observation.delta, 0)
        self.assertEqual(result.diagnostic_observation.delta, 1)
        self.assertGreater(result.raw_different_sites, 0)
        self.assertEqual(parent.runtime.raw_copy(), parent_raw)
        self.assertEqual(parent.runtime.clock_copy(), parent_clock)

    def test_attach_is_live_view_and_keeps_python_owner_alive(self) -> None:
        prepared = dt.create_relational_world()
        owner = prepared.runtime.fork()
        owner.execution_options = dt.TickOptions(dt.Backend.DENSE_SEQUENTIAL, 1)
        config = dt.BasalConfig.relational_reference(dt.reference_seed_path())
        config.execution = dt.TickOptions(dt.Backend.LAZY, 1)
        view = dt.BasalWorld.attach(owner, config, prepared.ports, prepared.t0_tick)
        self.assertEqual(owner.execution_options.backend, dt.Backend.DENSE_SEQUENTIAL)
        view.advance(1)
        self.assertEqual(owner.current_tick, 33)
        self.assertEqual(view.observe().delta, 1)

        # py::keep_alive<0,1> ties the non-owning C++ view to the Python owner.
        del owner
        gc.collect()
        view.advance(1)
        self.assertEqual(view.runtime.current_tick, 34)

    def test_snapshot_round_trip_resumes_same_future(self) -> None:
        world = dt.create_relational_world()
        world.advance(1)
        with tempfile.TemporaryDirectory() as temporary:
            snapshot = Path(temporary) / "basal_world.deetsnap"
            world.save_snapshot(str(snapshot))
            restored = dt.BasalWorld.load_snapshot(str(snapshot))
            self.assertEqual(restored.t0_tick, world.t0_tick)
            self.assertEqual(
                self._port_signature(restored.ports),
                self._port_signature(world.ports),
            )
            self.assertEqual(restored.observe().delta, world.observe().delta)
            self.assertEqual(restored.runtime.raw_copy(), world.runtime.raw_copy())
            self.assertEqual(restored.runtime.clock_copy(), world.runtime.clock_copy())

            with self.assertRaises(RuntimeError):
                dt.BasalWorld.load_snapshot(dt.reference_seed_path())

            for key, value in (
                ("dee_thinking.basal.recipe", "unsupported.recipe"),
                ("dee_thinking.basal.seed_id", "unknown-seed"),
                ("dee_thinking.basal.t0", "999999"),
            ):
                with self.subTest(metadata_key=key):
                    invalid = dt.Runtime.load_snapshot(str(snapshot))
                    invalid.set_snapshot_metadata(key, value)
                    invalid_path = Path(temporary) / f"invalid-{key.rsplit('.', 1)[-1]}.deetsnap"
                    invalid.save_snapshot(str(invalid_path))
                    with self.assertRaises(RuntimeError):
                        dt.BasalWorld.load_snapshot(str(invalid_path))

            world.advance(8)
            restored.advance(8)
            self.assertEqual(restored.runtime.raw_copy(), world.runtime.raw_copy())
            self.assertEqual(restored.runtime.clock_copy(), world.runtime.clock_copy())


if __name__ == "__main__":
    unittest.main(verbosity=2)
