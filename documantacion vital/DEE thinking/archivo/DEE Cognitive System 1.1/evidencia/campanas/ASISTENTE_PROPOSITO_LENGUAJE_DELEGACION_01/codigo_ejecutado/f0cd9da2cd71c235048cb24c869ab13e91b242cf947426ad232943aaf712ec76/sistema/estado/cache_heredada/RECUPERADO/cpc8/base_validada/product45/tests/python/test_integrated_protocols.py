from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import dee_thinking as dt


LAZY = dt.TickOptions(dt.Backend.LAZY, 4)


class IntegratedProtocolTests(unittest.TestCase):
    def test_h1_delay_position(self) -> None:
        config = dt.DelayPositionConfig()
        config.input_delay = 3
        result = dt.run_delay_position(config, LAZY)
        self.assertTrue(result.initial_hubs_empty)
        self.assertEqual(result.measurement, 3)
        self.assertIn(3, result.active_labels)
        for delay in range(-5, 6):
            domain_config = dt.DelayPositionConfig()
            domain_config.input_delay = delay
            domain_result = dt.run_delay_position(domain_config, LAZY)
            self.assertEqual(domain_result.measurement, delay)
            self.assertEqual(tuple(domain_result.active_labels), (delay,))
            self.assertEqual(len(domain_result.merged_events), 1)
        with tempfile.TemporaryDirectory() as temporary:
            checkpoint = Path(temporary) / "h1_mid_protocol.deetsnap"
            dt.save_delay_position_checkpoint(config, 5, str(checkpoint), LAZY)
            resumed = dt.resume_delay_position_checkpoint(str(checkpoint), LAZY)
        self.assertEqual(resumed.final_raw, result.final_raw)
        self.assertEqual(resumed.final_clock, result.final_clock)

    def test_h2_separated_and_overlap_controls(self) -> None:
        separated = dt.run_separated_repertoire(dt.SeparatedRepertoireConfig(), LAZY)
        self.assertTrue(separated.ports_empty)
        self.assertEqual(separated.exact_channels, 3)
        self.assertTrue(separated.all_exact)
        self.assertTrue(separated.load_accounting_exact)
        k7_config = dt.SeparatedRepertoireConfig()
        k7_config.channels = 7
        k7 = dt.run_separated_repertoire(k7_config, LAZY)
        self.assertEqual(k7.exact_channels, 7)
        self.assertTrue(k7.all_exact)
        self.assertTrue(k7.training_budget_exact)
        self.assertTrue(k7.read_budget_exact)
        self.assertTrue(k7.load_accounting_exact)
        with tempfile.TemporaryDirectory() as temporary:
            checkpoint = Path(temporary) / "h2_separated_mid_protocol.deetsnap"
            dt.save_separated_repertoire_checkpoint(
                dt.SeparatedRepertoireConfig(), 10, str(checkpoint), LAZY
            )
            separated_resumed = dt.resume_separated_repertoire_checkpoint(
                str(checkpoint), LAZY
            )
        self.assertEqual(separated_resumed.final_raw, separated.final_raw)
        self.assertEqual(separated_resumed.final_clock, separated.final_clock)

        overlap_config = dt.OverlapRepertoireConfig()
        overlap = dt.run_overlap_repertoire(overlap_config, LAZY)
        self.assertTrue(overlap.merge_exact)
        self.assertTrue(overlap.composed_response_exact)
        self.assertFalse(overlap.individual_identity_preserved)
        with tempfile.TemporaryDirectory() as temporary:
            checkpoint = Path(temporary) / "h2_overlap_mid_protocol.deetsnap"
            dt.save_overlap_repertoire_checkpoint(overlap_config, 15, str(checkpoint), LAZY)
            overlap_resumed = dt.resume_overlap_repertoire_checkpoint(
                str(checkpoint), LAZY
            )
        self.assertEqual(overlap_resumed.final_raw, overlap.final_raw)
        self.assertEqual(overlap_resumed.final_clock, overlap.final_clock)

        overlap_config.off_fiber = True
        off_fiber = dt.run_overlap_repertoire(overlap_config, LAZY)
        self.assertFalse(off_fiber.false_merge)

    def test_h3_repair_requires_opt_in_and_resumes_exactly(self) -> None:
        denied = dt.RepairConfig()
        with self.assertRaises(ValueError):
            dt.run_trained_redundancy_repair(denied, LAZY)

        config = dt.RepairConfig()
        config.authorize_diagnostic_damage = True
        uninterrupted = dt.run_trained_redundancy_repair(config, LAZY)
        self.assertTrue(uninterrupted.damage_applied)
        self.assertTrue(uninterrupted.function_lost_after_damage)
        self.assertTrue(uninterrupted.reconstructed_at_arrival)
        self.assertTrue(uninterrupted.fresh_function)
        with tempfile.TemporaryDirectory() as temporary:
            checkpoint = Path(temporary) / "h3_mid_protocol.deetsnap"
            dt.save_trained_redundancy_repair_checkpoint(config, 12, str(checkpoint), LAZY)
            resumed = dt.resume_trained_redundancy_repair_checkpoint(str(checkpoint), LAZY)
        self.assertEqual(resumed.final_raw, uninterrupted.final_raw)
        self.assertEqual(resumed.final_clock, uninterrupted.final_clock)

    def test_f1_panel_values_and_resume(self) -> None:
        config = dt.ReusableRevisionConfig()
        uninterrupted = dt.run_reusable_revision(config, LAZY)
        self.assertEqual(tuple(uninterrupted.response_loads), (4149, 4165, 4181))
        self.assertEqual(tuple(uninterrupted.post_revision_loads), (4160, 4178))
        self.assertTrue(uninterrupted.all_inputs_applied_at_t0)
        self.assertFalse(uninterrupted.backend_fallback)
        with tempfile.TemporaryDirectory() as temporary:
            checkpoint = Path(temporary) / "f1_mid_protocol.deetsnap"
            dt.save_reusable_revision_checkpoint(config, 40, str(checkpoint), LAZY)
            resumed = dt.resume_reusable_revision_checkpoint(str(checkpoint), LAZY)
        self.assertEqual(resumed.final_raw, uninterrupted.final_raw)
        self.assertEqual(resumed.final_clock, uninterrupted.final_clock)

    def test_f2_panel_values_and_resume(self) -> None:
        config = dt.EnvironmentalReturnConfig()
        uninterrupted = dt.run_environmental_return(config, LAZY)
        self.assertEqual(tuple(uninterrupted.downstream_loads), (24, 55, 62, 62, 67))
        self.assertEqual(uninterrupted.overflow_total, 1)
        self.assertTrue(uninterrupted.query_admitted)
        self.assertTrue(uninterrupted.all_inputs_applied_at_t0)
        self.assertFalse(uninterrupted.backend_fallback)
        with tempfile.TemporaryDirectory() as temporary:
            checkpoint = Path(temporary) / "f2_mid_protocol.deetsnap"
            dt.save_environmental_return_checkpoint(config, 40, str(checkpoint), LAZY)
            resumed = dt.resume_environmental_return_checkpoint(str(checkpoint), LAZY)
        self.assertEqual(resumed.final_raw, uninterrupted.final_raw)
        self.assertEqual(resumed.final_clock, uninterrupted.final_clock)

        panel = (
            ("ENV_INTACT", True, 15515, 17, dt.EnvironmentalQueryMode.INTACT,
             19664, 1, True, (24, 55, 62, 62, 67)),
            ("ENV_RESPONSE_CUT", False, 15515, 17, dt.EnvironmentalQueryMode.INTACT,
             15515, 0, True, (23, 54, 61, 61, 66)),
            ("ENV_NO_QUERY", True, 15515, 17, dt.EnvironmentalQueryMode.ABSENT,
             19664, 1, False, (0, 31, 7, 0, 5)),
            ("ENV_QUERY_SHAM", True, 15515, 17, dt.EnvironmentalQueryMode.SHAM,
             19664, 1, True, (0, 31, 7, 0, 5)),
            ("ENV_SUBTHRESHOLD", True, 15514, 17, dt.EnvironmentalQueryMode.INTACT,
             19663, 0, True, (23, 54, 61, 61, 66)),
            ("ENV_CONTENT_19", True, 15515, 19, dt.EnvironmentalQueryMode.INTACT,
             19664, 1, True, (24, 55, 62, 62, 67)),
        )
        for (case_id, trained, bias, marker, mode, environment, overflow,
             admitted, downstream) in panel:
            case = dt.EnvironmentalReturnConfig()
            case.id = case_id
            case.trained_response = trained
            case.bias_load = bias
            case.marker_load = marker
            case.query_mode = mode
            observed = dt.run_environmental_return(case, LAZY)
            self.assertEqual(observed.environment_load, environment)
            self.assertEqual(observed.overflow_total, overflow)
            self.assertEqual(observed.query_admitted, admitted)
            self.assertEqual(tuple(observed.downstream_loads), downstream)


if __name__ == "__main__":
    unittest.main(verbosity=2)
