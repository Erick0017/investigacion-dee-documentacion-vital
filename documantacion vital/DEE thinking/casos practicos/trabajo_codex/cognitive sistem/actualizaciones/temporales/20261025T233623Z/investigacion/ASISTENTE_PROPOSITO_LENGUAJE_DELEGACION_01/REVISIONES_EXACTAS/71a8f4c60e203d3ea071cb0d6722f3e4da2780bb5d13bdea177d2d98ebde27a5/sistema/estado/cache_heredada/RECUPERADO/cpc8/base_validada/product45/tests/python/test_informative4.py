"""DEE4 informative sessions: real evolution, no laboratory imports/answers.

Numeric references are assertions only. Every response below is observed from
the new native session, including continuation across pending event boundaries.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import dee_thinking as d


def physical(s):
    return s.tick, s.world.runtime.raw_copy(), s.world.runtime.clock_copy()


def policy(role=d.SourceRole.Q_INFORMATIVE, actual=1, origin=(30, 30, 30)):
    p = d.FinitePolicyParameters()
    p.roles = role
    p.actual_class = actual
    p.origin = d.Coordinate(*origin)
    return d.FinitePolicySession.create(p)


def information(history=d.BasalHistory.BA, actual=1, report=23, context=0, origin=(15, 15, 15), **kw):
    p = d.NativeInformationParameters()
    p.seed_path = d.reference_seed_path()
    p.origin = d.Coordinate(*origin)
    p.history = history
    p.actual_class = actual
    p.information_load = report
    p.context = context
    for k, v in kw.items():
        setattr(p, k, v)
    return d.NativeInformationSession.create(p)


class Informative4Tests(unittest.TestCase):
    def test_four_binary_role_worlds_and_translated_reserves(self):
        for roles, actual, origin in [
            (d.SourceRole.P_INFORMATIVE, 1, (30, 30, 30)),
            (d.SourceRole.Q_INFORMATIVE, 1, (30, 30, 30)),
            (d.SourceRole.P_INFORMATIVE, -1, (30, 30, 30)),
            (d.SourceRole.Q_INFORMATIVE, -1, (30, 30, 30)),
            (d.SourceRole.P_INFORMATIVE, 1, (27, 28, 29)),
            (d.SourceRole.Q_INFORMATIVE, -1, (35, 34, 33)),
        ]:
            s = policy(roles, actual, origin)
            self.assertEqual(s.tick, 0)
            first = s.run_until(1).physical_outputs['first_action']
            self.assertEqual((first.record.dx, first.record.dy, first.record.dz), (0, 0, 1))
            comp = s.compare()
            self.assertEqual(len(comp.comparisons), 1)
            self.assertEqual(comp.comparisons[0].presentation,
                             'coincidence' if roles == d.SourceRole.P_INFORMATIVE else 'directional_discrepancy')
            action = s.source()
            self.assertEqual(len(action.actions), 1)
            self.assertEqual(action.actions[0].source, 'P' if roles == d.SourceRole.P_INFORMATIVE else 'Q')
            info = s.sense()
            self.assertEqual(len(info.information), 1)
            self.assertEqual(info.information[0].value, actual)
            self.assertEqual(len(info.receipts), 2)
            self.assertTrue(all(r.status == d.EventStatus.APPLIED for r in info.receipts))
            self.assertEqual(s.source().status, 'OUTSIDE_CURRENT_SOURCE_ACTION_WINDOW')
            self.assertEqual(s.compare().status, 'OUTSIDE_CURRENT_COMPARISON_WINDOW')

    def test_pending_events_full_state_ui_and_another_process(self):
        s = policy()
        s.run_until(2)
        s.process_boundary()
        self.assertTrue(all(r.status == d.EventStatus.SCHEDULED for r in s.observe().receipts))
        s.set_interface_metadata('alias', 'fuente opaca')
        with tempfile.TemporaryDirectory(prefix='dee4-policy-') as temp:
            path = str(Path(temp) / 'pending.deetsnap')
            before = physical(s)
            s.save_snapshot(path)
            self.assertEqual(physical(s), before)
            loaded = d.FinitePolicySession.load_snapshot(path)
            self.assertEqual(physical(loaded), before)
            self.assertEqual(loaded.get_interface_metadata('alias'), 'fuente opaca')
            self.assertEqual(len(loaded.journal), len(s.journal))
            a = s.run_until(14)
            b = loaded.run_until(14)
            self.assertEqual(physical(s), physical(loaded))
            self.assertEqual(a.information[0].physical.raw, b.information[0].physical.raw)
            code = ('import dee_thinking as d,json,sys;'
                    's=d.FinitePolicySession.load_snapshot(sys.argv[1]);r=s.run_until(14);'
                    'print(json.dumps({"tick":s.tick,"value":r.information[0].value,"source":r.information[0].source}))')
            run = subprocess.run([sys.executable, '-I', '-B', '-c', code, path],
                                 cwd=temp, text=True, capture_output=True, timeout=60, check=True)
            self.assertEqual(json.loads(run.stdout), {'tick': 14, 'value': 1, 'source': 'Q'})

    def test_observation_fork_controls_and_no_actual_report(self):
        s = policy()
        s.run_until(1)
        before = physical(s)
        for _ in range(3):
            s.observe().as_dict()
        self.assertEqual(physical(s), before)
        f = s.fork()
        f.run_until(14)
        self.assertEqual(physical(s), before)
        p = d.FinitePolicyParameters()
        p.actual_enabled = False
        omitted = d.FinitePolicySession.create(p)
        self.assertEqual(omitted.sense().status, 'ACTUAL_REPORT_OMITTED')
        r = omitted.run_until(14)
        self.assertFalse(r.information)
        self.assertFalse(r.actions)
        self.assertFalse(r.receipts)
        q = d.ResearchStateEdit()
        q.coordinate = s.world.view('selection').spec.ports['first_action']
        q.raw = 0
        q.label = 'explicit late action control; not a native repair'
        cut = s.diagnostic_fork([q], True)
        # A different diagnostic world is never returned to the native MAIN.
        result = cut.run_until(14)
        self.assertFalse(result.information)
        self.assertFalse(result.actions)
        self.assertEqual(len(result.receipts), 2)
        self.assertTrue(all(r.status == d.EventStatus.APPLIED for r in result.receipts))
        self.assertEqual(cut.world.runtime.observe(q.coordinate).clock, s.tick + 13)
        self.assertEqual(physical(s), before)

    def test_native_information_and_later_use(self):
        for h, c, context, report, origin, source in [
            (d.BasalHistory.BA, 1, 0, 23, (15, 15, 15), 'P'),
            (d.BasalHistory.AB, -1, 1, 23, (15, 15, 15), 'Q'),
            (d.BasalHistory.BA, 1, 0, 41, (22, 20, 24), 'P'),
        ]:
            s = information(h, c, report, context, origin)
            self.assertEqual(s.tick, 32)
            emitted = s.run_until(37)
            self.assertEqual(emitted.delta, -1 if h == d.BasalHistory.BA else 1)
            self.assertIsNotNone(emitted.current_prediction)
            self.assertEqual(len(s.compare().comparisons), 1)
            # The route at51 is an actual native product, not source utility.
            a = s.source()
            self.assertTrue(any(x.source == source for x in a.actions))
            r = s.sense()
            self.assertTrue(any(x.source == source and x.value == report for x in r.information))
            used = s.run_until(64)
            self.assertTrue(any(x.value == report + 44 for x in used.later_responses))
            self.assertEqual(s.source().status, 'OUTSIDE_CURRENT_SOURCE_ACTION_WINDOW')

    def test_native_information_pending_resume_and_control(self):
        s = information()
        s.run_until(43)
        s.process_boundary()
        s.set_interface_metadata({'grammar': 'externa', 'last_form': 'sonda'})
        with tempfile.TemporaryDirectory(prefix='dee4-information-') as temp:
            path = str(Path(temp) / 'pending.deetsnap')
            s.save_snapshot(path)
            loaded = d.NativeInformationSession.load_snapshot(path)
            self.assertEqual(physical(s), physical(loaded))
            self.assertEqual(loaded.interface_metadata, s.interface_metadata)
            s.run_until(64)
            loaded.run_until(64)
            self.assertEqual(physical(s), physical(loaded))
            self.assertEqual(len([r for r in loaded.journal if r.operation == 'submit']), 4)
        cut = information(source_cut='P')
        r = cut.run_until(64)
        self.assertFalse(r.later_responses)
        h0 = information(history=d.BasalHistory.H0)
        h0.run_until(37)
        self.assertEqual(h0.observe().delta, 0)

    def test_validation_missing_data_no_timeout_absence_or_hidden_reset(self):
        p = d.FinitePolicyParameters()
        p.actual_class = 0
        with self.assertRaises(ValueError):
            d.FinitePolicySession.create(p)
        s = policy()
        with self.assertRaises(ValueError):
            s.submit_actual(1)
        s.run_until(2)
        with self.assertRaises(ValueError):
            s.submit_actual(0)
        s.submit_actual(-1)
        with self.assertRaises(ValueError):
            s.submit_actual(1)
        with self.assertRaises(ValueError):
            s.run_until(1)
        p = d.NativeInformationParameters()
        p.seed_path = d.reference_seed_path()
        p.distance = 11
        with self.assertRaises(ValueError):
            d.NativeInformationSession.create(p)
        with self.assertRaises(ValueError):
            s.set_interface_metadata('x', 'z' * 65537)
        s.world.runtime.pause()
        with self.assertRaises(ValueError):
            s.advance()
        s.world.runtime.resume()
        s.advance()
        with tempfile.TemporaryDirectory() as temp:
            pth = Path(temp) / 'truncated.deetsnap'
            pth.write_bytes(b'not a snapshot')
            with self.assertRaises((ValueError, RuntimeError)):
                d.FinitePolicySession.load_snapshot(str(pth))

    def test_actual_report_rejection_is_not_presented_as_applied(self):
        s = policy()
        s.run_until(2)
        ch = next(x for x in s.world.interfaces if x.name == 'actual.negative.1')
        edit = d.ResearchStateEdit()
        edit.coordinate = ch.channel.injection_site
        edit.raw = d.pack_record(1, 77, 0, 0, 0, 1)
        edit.label = 'diagnostic occupied input; no repair'
        blocked = s.diagnostic_fork([edit], True)
        r = blocked.sense()
        self.assertEqual(r.status, 'ACTUAL_REPORT_PARTIALLY_APPLIED')
        self.assertEqual([x.status for x in r.receipts].count(d.EventStatus.APPLIED), 1)
        self.assertEqual([x.status for x in r.receipts].count(d.EventStatus.REJECTED_OCCUPIED), 1)
        self.assertEqual(s.tick, 2)
        self.assertFalse(s.observe().receipts)

    def test_journal_capture_budget_never_prevents_physical_continuation(self):
        s = policy()
        before = physical(s)
        for i in range(8200):
            s.set_interface_metadata('external_alias', str(i))
        self.assertEqual(len(s.journal), 8192)
        self.assertTrue(s.observe().journal_truncated)
        self.assertEqual(physical(s), before)
        # Near the documented UI bound as well as the journal count bound.
        s.set_interface_metadata({str(i): 'x' * 60000 for i in range(8)})
        with tempfile.TemporaryDirectory(prefix='dee4-journal-') as temp:
            path = str(Path(temp) / 'bounded.deetsnap')
            s.save_snapshot(path)
            loaded = d.FinitePolicySession.load_snapshot(path)
            self.assertEqual(physical(s), physical(loaded))
            self.assertEqual(loaded.interface_metadata, s.interface_metadata)
            self.assertTrue(loaded.observe().journal_truncated)
            loaded.run_until(14)
            self.assertEqual(loaded.tick, 14)
            self.assertEqual(len(loaded.observe().information), 1)


if __name__ == '__main__':
    unittest.main()
