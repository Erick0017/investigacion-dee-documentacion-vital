from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

import dee_thinking as dt


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "fixtures" / "mbp4" / "regressions"
CHECKPOINTS = FIXTURES / "checkpoints"
TELEMETRY = FIXTURES / "telemetry"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _edit(
    coordinate: dt.Coordinate,
    *,
    raw: int | None = None,
    clock: int | None = None,
    label: str,
):
    edit = dt.ResearchStateEdit()
    edit.coordinate = coordinate
    edit.raw = raw
    edit.clock = clock
    edit.label = label
    return edit


def _packed(record, *, s_reg=None, direction=None, semantic=None) -> int:
    dx, dy, dz = (
        direction if direction is not None else (record.dx, record.dy, record.dz)
    )
    return dt.pack_record(
        record.state,
        record.s_reg if s_reg is None else s_reg,
        dx,
        dy,
        dz,
        record.semantic if semantic is None else semantic,
    )


def _translated(origin: tuple[int, int, int], base: tuple[int, int, int]) -> dt.Coordinate:
    return dt.Coordinate(
        (base[0] + origin[0] - 15) % 47,
        (base[1] + origin[1] - 15) % 47,
        (base[2] + origin[2] - 15) % 47,
    )


class MBP4ProductRegressions(unittest.TestCase):
    maxDiff = None

    def assert_runtime_equal(self, actual, expected, message: str = "") -> None:
        self.assertEqual(actual.current_tick, expected.current_tick, message)
        self.assertEqual(actual.raw_copy(), expected.raw_copy(), message)
        self.assertEqual(actual.clock_copy(), expected.clock_copy(), message)

    def assert_relation(self, world, a: int, b: int, delta: int) -> None:
        observed = world.observe()
        self.assertEqual(observed.a.record.s_reg, a)
        self.assertEqual(observed.b.record.s_reg, b)
        self.assertEqual(observed.delta, delta)

    def test_fixture_manifest_integrity(self) -> None:
        manifest = _json(FIXTURES / "MANIFEST.json")
        self.assertEqual(
            manifest["source_archive"]["sha256"],
            "4d20d893d04486de047c66ce76c9f7dad067158941b553025bd946b7dc6ce086",
        )
        for item in manifest["fixtures"]:
            with self.subTest(path=item["path"]):
                path = FIXTURES / item["path"]
                self.assertTrue(path.is_file())
                self.assertEqual(path.stat().st_size, item["bytes"])
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), item["sha256"])

    def test_r1_relational_recipe_histories_against_primary_oracles(self) -> None:
        oracle = _json(TELEMETRY / "R1_MATCHED_CONTROLS.json")
        cases = {
            "AB": dt.BasalHistory.AB,
            "BA": dt.BasalHistory.BA,
            "H0": dt.BasalHistory.H0,
            "SHAM": dt.BasalHistory.SHAM,
        }
        for name, history in cases.items():
            with self.subTest(history=name):
                world = dt.create_relational_world(history)
                self.assert_relation(world, 100, 100, 0)
                world.advance(1)
                self.assertEqual(world.observe().delta, oracle[name]["observed"]["delta_tick1"])
                if name == "AB":
                    acquired = dt.Runtime.load_snapshot(
                        str(CHECKPOINTS / "R1_FIRST_HISTORY_ACQUIRED.deetsnap")
                    )
                    self.assert_runtime_equal(world.runtime, acquired, "R1 AB recipe")
                world.advance(15)
                self.assertEqual(
                    world.observe().axis_projection,
                    oracle[name]["observed"]["axis_projection"]["16"],
                )

    def test_r2_section22_checkpoint_continuation_matches_full_state(self) -> None:
        resumed = dt.Runtime.load_snapshot(
            str(CHECKPOINTS / "R2_RELATIONAL_MAIN_T0.deetsnap")
        )
        expected = dt.Runtime.load_snapshot(str(CHECKPOINTS / "R2_FIRST_RETURN.deetsnap"))
        self.assertEqual((resumed.current_tick, expected.current_tick), (32, 50))
        resumed.advance(expected.current_tick - resumed.current_tick)
        self.assert_runtime_equal(resumed, expected, "R2 T32->T50 continuation")

        chain = _json(TELEMETRY / "R1_MATCHED_CONTROLS.json")["AB"]["observed"]
        self.assertEqual(chain["event_ticks"]["action"][:4], [8, 10, 16, 18])
        self.assertEqual(chain["event_ticks"]["environment_return"][:4], [14, 16, 22, 24])
        self.assertEqual(chain["event_ticks"]["organization_return"][:4], [18, 20, 26, 28])

    def test_r3_contextual_recipe_and_checkpoint_continuation(self) -> None:
        recipe = dt.create_contextual_world()
        historical_t0 = dt.Runtime.load_snapshot(str(CHECKPOINTS / "R3_MAIN_T0.deetsnap"))
        self.assert_runtime_equal(recipe.runtime, historical_t0, "R3 physical T0")

        recipe.advance(131)
        historical_before = dt.Runtime.load_snapshot(
            str(CHECKPOINTS / "R3_BEFORE_WRITE_OPPORTUNITY.deetsnap")
        )
        self.assert_runtime_equal(recipe.runtime, historical_before, "R3 t_rel=131")
        gate = dt.inspect_write_gate(recipe.runtime, recipe.ports.b, True)
        self.assertEqual((gate.local_clock, gate.n_active, gate.period), (391, 6, 391))
        self.assertEqual(gate.phase_remainder, 0)
        self.assertTrue(gate.ordinary_increment_condition)
        self.assert_relation(recipe, 101, 100, 1)

        recipe.advance(1)
        historical_after = dt.Runtime.load_snapshot(
            str(CHECKPOINTS / "R3_AFTER_POSSIBLE_REWRITE.deetsnap")
        )
        self.assert_runtime_equal(recipe.runtime, historical_after, "R3 131->132")
        self.assert_relation(recipe, 101, 101, 0)

        recipe.advance(18)
        historical_retained = dt.Runtime.load_snapshot(
            str(CHECKPOINTS / "R3_RETENTION_READOUT.deetsnap")
        )
        self.assert_runtime_equal(recipe.runtime, historical_retained, "R3 retention t_rel=150")
        self.assert_relation(recipe, 101, 101, 0)

        recipe.advance(20)
        self.assertEqual(recipe.runtime.current_tick, 202)
        self.assert_relation(recipe, 101, 101, 0)

        checkpoint_path = CHECKPOINTS / "R3_BEFORE_WRITE_OPPORTUNITY.deetsnap"
        resumed = dt.Runtime.load_snapshot(str(checkpoint_path))
        resumed.advance(1)
        self.assert_runtime_equal(resumed, historical_after, "R3 intermediate checkpoint")

    def test_r4_selective_controls_execute_through_public_diagnostics(self) -> None:
        action_oracle = _json(TELEMETRY / "R4_ACTION_ENVIRONMENT_INTERVENTIONS.json")
        local_oracle = _json(TELEMETRY / "R4_R5_LOCAL_INTERVENTIONS_AND_RESCUE.json")[
            "local_interventions"
        ]

        at18 = dt.create_contextual_world()
        at18.advance(18)
        action_site = dt.Coordinate(31, 31, 15)
        action = at18.runtime.observe(action_site)
        self.assertEqual(action.raw, action_oracle["ACT_REMOVE"]["edit"]["before_raw"])
        action_variants = {
            "ACT_REMOVE": 0,
            "ACT_LOAD_MINUS": _packed(action.record, s_reg=17),
            "ACT_LOAD_PLUS": _packed(action.record, s_reg=19),
            "ACT_DIRECTION": _packed(action.record, direction=(1, 0, 0)),
        }
        for name, raw in action_variants.items():
            with self.subTest(control=name):
                branch = at18.diagnostic_fork(
                    [_edit(action_site, raw=raw, label=f"R4.{name}")], True
                )
                branch.advance(170 - 18)
                expected = action_oracle[name]["final_test"]
                self.assert_relation(
                    branch,
                    expected["a"]["s_reg"],
                    expected["b"]["s_reg"],
                    expected["delta"],
                )

        at65 = dt.create_contextual_world()
        at65.advance(65)
        environment_site = dt.Coordinate(42, 42, 4)
        environment = at65.runtime.observe(environment_site)
        self.assertEqual(
            environment.raw,
            action_oracle["ENV42_REMOVE"]["edit"]["before_raw"],
        )
        environment_cut = at65.diagnostic_fork(
            [_edit(environment_site, raw=0, label="R4.ENV42_REMOVE")], True
        )
        environment_cut.advance(170 - 65)
        expected_environment = action_oracle["ENV42_REMOVE"]["final_test"]
        self.assert_relation(
            environment_cut,
            expected_environment["a"]["s_reg"],
            expected_environment["b"]["s_reg"],
            expected_environment["delta"],
        )

        at131 = dt.create_contextual_world()
        at131.advance(131)
        dynamic_site = dt.Coordinate(15, 16, 15)
        dynamic = at131.runtime.observe(dynamic_site)
        local_variants = {
            "B_CLOCK_PLUS1": _edit(
                at131.ports.b, clock=392, label="R4.B_CLOCK_PLUS1"
            ),
            "LOCAL_DYNAMIC_REMOVE": _edit(
                dynamic_site, raw=0, label="R4.LOCAL_DYNAMIC_REMOVE"
            ),
            "LOCAL_DYNAMIC_SEM5": _edit(
                dynamic_site,
                raw=_packed(dynamic.record, semantic=5),
                label="R4.LOCAL_DYNAMIC_SEM5",
            ),
            "LOCAL_DYNAMIC_DIRECTION_ZERO": _edit(
                dynamic_site,
                raw=_packed(dynamic.record, direction=(0, 0, 0)),
                label="R4.LOCAL_DYNAMIC_DIRECTION_ZERO",
            ),
            "LOCAL_DYNAMIC_LOAD_ZERO": _edit(
                dynamic_site,
                raw=_packed(dynamic.record, s_reg=0),
                label="R4.LOCAL_DYNAMIC_LOAD_ZERO",
            ),
        }
        for name, edit in local_variants.items():
            with self.subTest(control=name):
                branch = at131.diagnostic_fork([edit], True)
                branch.advance(170 - 131)
                expected = local_oracle[name]["final_test"]
                self.assert_relation(
                    branch,
                    expected["a"]["s_reg"],
                    expected["b"]["s_reg"],
                    expected["delta"],
                )

    def test_r5_absolute_writes_are_not_collapsed_to_relational_delta(self) -> None:
        rescues = _json(TELEMETRY / "R4_R5_LOCAL_INTERVENTIONS_AND_RESCUE.json")[
            "rescues"
        ]
        for name in ("ENV_RAW_RESCUE", "LOCAL_RAW_RESCUE", "LOCAL_RAW_CLOCK_RESCUE"):
            with self.subTest(rescue=name):
                branch = rescues[name]
                self.assertEqual(
                    (
                        branch["final_reference"]["a"]["s_reg"],
                        branch["final_reference"]["b"]["s_reg"],
                        branch["final_reference"]["delta"],
                    ),
                    (101, 100, 1),
                )
                self.assertEqual(
                    (
                        branch["final_test"]["a"]["s_reg"],
                        branch["final_test"]["b"]["s_reg"],
                        branch["final_test"]["delta"],
                    ),
                    (102, 101, 1),
                )
        inverse = rescues["INVERSE_FULL_FROM_NO_ACTION"]
        self.assertEqual(
            (
                inverse["final_test"]["a"]["s_reg"],
                inverse["final_test"]["b"]["s_reg"],
                inverse["final_test"]["delta"],
            ),
            (101, 100, 1),
        )

    def test_r6_b12_checkpoint_continuation_and_primary_transition(self) -> None:
        resumed = dt.Runtime.load_snapshot(
            str(CHECKPOINTS / "R6_B1_B2_PRE_CONTACT.deetsnap")
        )
        expected = dt.Runtime.load_snapshot(str(CHECKPOINTS / "R6_B12_FOLLOWUP.deetsnap"))
        self.assertLess(resumed.current_tick, expected.current_tick)
        resumed.advance(expected.current_tick - resumed.current_tick)
        self.assert_runtime_equal(resumed, expected, "R6 B12 continuation")

        tracker = _json(TELEMETRY / "R6_R7_TRANSFORMATIVE_TRACKER.json")["B12"]
        interaction = next(
            row for row in tracker["trace"]["transitions"]
            if row["after_target"] is not None
            and row["after_target"]["s_reg"] == 14014
        )
        sources = {(row["s_reg"], tuple(row["direction"])) for row in interaction["incoming_sources"]}
        self.assertEqual(sources, {(12014, (1, 1, 0)), (2000, (1, -1, 0))})
        self.assertEqual(tuple(interaction["after_target"]["direction"]), (1, 0, 0))

    def test_r7_protected_source_arrival_has_no_effect_on_target(self) -> None:
        oracle = _json(TELEMETRY / "R6_R7_TRANSFORMATIVE_TRACKER.json")["NINTH_RETURN"]
        full = dt.Runtime.load_snapshot(str(CHECKPOINTS / "R7_INTEGRATED_MAIN_T0.deetsnap"))
        full.advance(409 - full.current_tick)
        source = dt.Coordinate(*oracle["source"])
        target = dt.Coordinate(*oracle["protected_target"])
        source_observation = full.observe(source)
        target_before = full.observe(target)
        self.assertEqual(source_observation.record.s_reg, 19664)
        self.assertEqual(
            (target_before.record.s_reg, target_before.record.semantic),
            (3000, 4),
        )
        cut = full.diagnostic_fork(
            [_edit(source, raw=0, label="R7.NINTH_RETURN_SOURCE_CUT")], True
        )
        full.advance(1)
        cut.advance(1)
        self.assertEqual(full.current_tick, oracle["after_tick"])
        self.assertEqual(full.raw_copy(), cut.raw_copy())
        self.assertEqual(full.clock_copy(), cut.clock_copy())
        target_after = full.observe(target)
        self.assertEqual(target_after.raw, target_before.raw)
        self.assertEqual(oracle["transition"]["branch"], "semantic4_protection")

    def test_r8_translated_replicates_and_executed_interventions(self) -> None:
        oracle = _json(TELEMETRY / "R8_REPLICATIONS.json")
        for origin in ((22, 20, 24), (28, 26, 18)):
            key = "origin_" + "_".join(str(value) for value in origin)
            with self.subTest(origin=origin):
                parent = dt.create_contextual_world(origin=origin)
                parent.advance(131)
                self.assert_relation(parent, 101, 100, 1)

                reference = parent.fork()
                reference.advance(39)
                self.assert_relation(reference, 101, 101, 0)

                clock_edit = _edit(
                    parent.ports.b,
                    clock=392,
                    label=f"R8.{key}.B_CLOCK_PLUS1",
                )
                phase_miss = parent.diagnostic_fork([clock_edit], True)
                phase_miss.advance(39)
                clock_expected = oracle[key]["B_CLOCK_PLUS1"]["final_test"]
                self.assert_relation(
                    phase_miss,
                    clock_expected["a"]["s_reg"],
                    clock_expected["b"]["s_reg"],
                    clock_expected["delta"],
                )

                dynamic_site = _translated(origin, (15, 16, 15))
                dynamic_remove = parent.diagnostic_fork(
                    [_edit(dynamic_site, raw=0, label=f"R8.{key}.LOCAL_DYNAMIC_REMOVE")],
                    True,
                )
                dynamic_remove.advance(39)
                remove_expected = oracle[key]["LOCAL_DYNAMIC_REMOVE"]["final_test"]
                self.assert_relation(
                    dynamic_remove,
                    remove_expected["a"]["s_reg"],
                    remove_expected["b"]["s_reg"],
                    remove_expected["delta"],
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
