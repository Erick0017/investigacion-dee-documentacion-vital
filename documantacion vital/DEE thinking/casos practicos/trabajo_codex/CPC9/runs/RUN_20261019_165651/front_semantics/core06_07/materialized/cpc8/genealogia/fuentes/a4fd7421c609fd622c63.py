"""Native4 sessions: expected results evaluate Runtime, never supply answers."""
import gc
import tempfile
import unittest
from pathlib import Path
import dee_thinking as d

def physical(world):
    return (world.runtime.current_tick,world.runtime.raw_copy(),world.runtime.clock_copy())

def parameters(profile="continuity",initial=False,change=80):
    p=d.CognitiveParameters();p.seed_path=d.reference_seed_path();p.profile=profile
    p.initial_open=initial;p.change_tick=change
    return p

class CognitiveApiTests(unittest.TestCase):
    def test_online_main_reader_and_resume(self):
        e=d.CognitiveSession.create(parameters());before=physical(e.world)
        for _ in range(5):e.observe()
        self.assertEqual(before,physical(e.world))
        got=e.sense();self.assertEqual([r['status'] for r in got['receipts']],['applied','applied'])
        self.assertEqual(e.tick,34);self.assertEqual(e.observe()['delta'],-1)
        p=e.predict();self.assertEqual(p['prediction_set'],[False]);self.assertEqual(p['emission_tick'],37)
        self.assertEqual(p['target_tick'],67)
        diagnostic=e.fork();self.assertEqual(physical(e.world),physical(diagnostic.world));diagnostic.sense()
        self.assertEqual(e.tick,37);self.assertEqual(diagnostic.tick,164)
        diagnostic.set_interface_metadata('branch','only branch')
        self.assertNotIn('branch',e.interface_metadata)
        e.set_interface_metadata('forms','{"pulso":"A"}')
        with tempfile.TemporaryDirectory() as folder:
            path=str(Path(folder)/'pending.deetsnap');e.save_snapshot(path)
            other=d.CognitiveSession.load_snapshot(path);self.assertEqual(physical(e.world),physical(other.world))
            self.assertEqual(other.interface_metadata,e.interface_metadata)
            e.sense();other.sense();self.assertEqual(e.tick,164);self.assertEqual(physical(e.world),physical(other.world))
        self.assertTrue(any(c['operation']=='submit' for c in e.journal))
        self.assertFalse(any(c['operation']=='fork' for c in e.journal))
        self.assertEqual(e.compare()['status'],'COMPARISON_PROFILE_NOT_PREPARED')
        self.assertRaises(ValueError,e.experience,'unknown')

    def test_native_actual_comparison_and_no_false_reuse(self):
        for initial in (False,True):
            for change in (None,80):
                e=d.CognitiveSession.create(parameters('comparison',initial,change));e.sense();p=e.predict()
                self.assertEqual(p['target_tick'],83);self.assertEqual(p['prediction_set'],[initial])
                self.assertEqual(e.predict()['status'],'ONE_PENDING_EXPECTATION_ALREADY_REGISTERED')
                with tempfile.TemporaryDirectory() as folder:
                    path=str(Path(folder)/'pending.deetsnap');e.save_snapshot(path)
                    copy=d.CognitiveSession.load_snapshot(path)
                    a=e.compare();b=copy.compare()
                    self.assertEqual(physical(e.world),physical(copy.world));self.assertEqual(e.tick,84)
                    self.assertEqual(a['comparison_decoder'],b['comparison_decoder'])
                self.assertEqual(a['input_receipt']['status'],'applied')
                self.assertEqual(a['comparison_decoder']['presentation'],
                                 'coincidencia_direccional' if change is None else 'discrepancia_direccional')
                self.assertEqual(e.predict()['status'],'OUTSIDE_FORECAST_DOMAIN')
                self.assertEqual(e.observe()['prediction_set'],[False,True])
                e.advance();self.assertIsNone(e.observe()['comparison_live']['presentation'])

    def test_interface_limits_and_invalidation(self):
        e=d.CognitiveSession.create(parameters('comparison'));e.sense();e.predict()
        e.experience('A');self.assertEqual(e.compare()['status'],'EXPECTATION_INVALIDATED_BY_EXPERIENCE')
        p=parameters();p.profile='unknown';self.assertRaises(ValueError,d.CognitiveSession.create,p)
        p=parameters();p.journal_limit=1;self.assertRaises(ValueError,d.CognitiveSession.create,p)
        self.assertRaises(ValueError,e.set_interface_metadata,'x','x'*(1024*1024+1))
        self.assertRaises(ValueError,d.CognitiveSession.load_snapshot,d.reference_seed_path())
        rt=d.CognitiveSession.load_legacy_physical_snapshot(d.reference_seed_path());self.assertEqual(rt.current_tick,32)

    def test_lifetime_native_association_and_reserved_loads(self):
        for teachers in ([7,11],[4,8]):
            a=d.NativeAssociationSession.create();r=a.train(teachers,5)
            self.assertEqual(len(r['receipts']),4)
            branch=a.fork();branch.query_panel(13);self.assertEqual(a.tick,6)
            with tempfile.TemporaryDirectory() as folder:
                path=str(Path(folder)/'association.deetsnap');a.save_snapshot(path)
                b=d.NativeAssociationSession.load_snapshot(path)
                x=a.query_panel(13);y=b.query_panel(13)
                self.assertEqual(x['decoded'],{'q0':teachers[0]+18,'q1':teachers[1]+18})
                self.assertEqual(x['outputs'],y['outputs']);self.assertEqual(physical(a.world),physical(b.world))
        view=a.world.view('q0');del a;gc.collect();self.assertEqual(view.runtime.dimension,34)

    def test_online_composition_and_intermediate_save(self):
        w=d.create_learnable_cascade(2);rs=d.experience_composition(w,[(3,9),(3,11)])
        self.assertTrue(all(r['status']=='applied' for r in rs))
        with tempfile.TemporaryDirectory() as folder:
            p=str(Path(folder)/'cascade.deetsnap');w.save_snapshot(p);copy=d.OrganizationalWorld.load_snapshot(p)
            a=d.query_composition(w,13);b=d.query_composition(copy,13)
            self.assertEqual(a['decoded'],{'stage0':25,'stage1':39});self.assertEqual(a,b)
            self.assertEqual(physical(w),physical(copy))

if __name__=='__main__':unittest.main()
