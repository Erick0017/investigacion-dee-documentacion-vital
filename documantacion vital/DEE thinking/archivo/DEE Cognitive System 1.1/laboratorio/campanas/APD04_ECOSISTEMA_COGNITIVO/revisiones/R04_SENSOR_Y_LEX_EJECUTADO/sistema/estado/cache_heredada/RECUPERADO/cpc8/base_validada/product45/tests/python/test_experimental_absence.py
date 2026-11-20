"""Finite prepared missing-report aperture, independent from integrated U0."""
from pathlib import Path
import tempfile
import unittest
from dee_thinking.experimental_absence import AbsenceSession, prepare_absence_recipe


def physics(s):
    r = s.world.runtime
    return r.current_tick, r.raw_copy(), r.clock_copy()


def prepare(*, order="AB", value=1, actual=None, mode="paired", reader=True):
    s = AbsenceSession.create()
    s.experience_order(order, reader=reader)
    s.acquire_source(value, mode=mode)
    s.prepare_use()
    s.run_until(5)
    if actual is not None:
        s.actual(actual)
    return s


def emitted(s, tick, stage):
    return next(r for r in s.readings if r["tick"] == tick)["decoded"][stage]


class AbsenceTests(unittest.TestCase):
    def test_configuration_and_batch_errors_are_inert(self):
        with self.assertRaises(ValueError):
            prepare_absence_recipe(center=(67, 25, 33))
        s = AbsenceSession.create(); before = physics(s)
        with self.assertRaises(ValueError):
            s.stimulate([{"port": "order.read", "payload": 7, "tick": 2},
                         {"port": "missing", "payload": 7, "tick": 2}])
        self.assertEqual(physics(s), before)
        self.assertEqual(s.receipts(), [])
        with self.assertRaises((TypeError, ValueError)):
            s.acquire_source(True)

    def test_missing_current_report_and_match_control(self):
        missing = prepare(); missing.run_until(29)
        for t, k in ((19, "questions"), (24, "information"), (29, "use")):
            self.assertEqual(len(emitted(missing, t, k)), 1)
        self.assertIn("missing_actual", emitted(missing, 19, "questions")[0]["route"])
        matched = prepare(actual=1); matched.run_until(29)
        self.assertEqual(emitted(matched, 19, "questions"), [])
        self.assertEqual(emitted(matched, 29, "use"), [])
        self.assertTrue(all(r["receipt"]["status"] == "applied" for r in missing.receipts()))

    def test_opposite_history_reserved_content_and_discrepancy_route(self):
        reserved = prepare(order="BA", value=-1); reserved.run_until(29)
        self.assertEqual(len(emitted(reserved, 29, "use")), 1)
        self.assertEqual(emitted(reserved, 29, "use")[0]["physical"]["direction"][1], -1)
        discrepant = prepare(actual=-1); discrepant.run_until(29)
        q = emitted(discrepant, 19, "questions")
        self.assertEqual(len(q), 1)
        self.assertIn("different", q[0]["route"])
        self.assertEqual(len(emitted(discrepant, 29, "use")), 1)

    def test_unpaired_source_is_not_an_answer(self):
        s = prepare(mode="unpaired"); s.run_until(29)
        self.assertEqual(len(emitted(s, 19, "questions")), 1)
        self.assertEqual(emitted(s, 24, "information"), [])
        self.assertEqual(emitted(s, 29, "use"), [])

    def test_passive_observation_fork_and_pending_restore(self):
        s = prepare(); s.run_until(20); before = physics(s)
        s.observe(); s.observe()
        cut = s.diagnostic_question_cut(); sham = s.diagnostic_question_cut(sham=True)
        self.assertEqual(physics(s), before)
        self.assertEqual(physics(sham), before)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/"ausencia_pendiente.deetsnap.gz"
            s.save_snapshot(path)
            restored = AbsenceSession.load_snapshot(path)
            self.assertEqual(physics(restored), physics(s))
            self.assertEqual(restored.receipts(), s.receipts())
            restored.run_until(29); s.run_until(29); cut.run_until(29); sham.run_until(29)
            self.assertEqual(physics(restored), physics(s))
            self.assertEqual(physics(sham), physics(s))
            self.assertEqual(len(emitted(s, 29, "use")), 1)
            self.assertEqual(emitted(cut, 29, "use"), [])


if __name__ == "__main__":
    unittest.main()
