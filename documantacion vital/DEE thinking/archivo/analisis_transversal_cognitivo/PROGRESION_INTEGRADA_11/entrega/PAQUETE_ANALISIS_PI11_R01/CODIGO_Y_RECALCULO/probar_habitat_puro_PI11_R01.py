"""Pure tests; no DEE import, owner, process or Native tick.

Each test uses a new temporary environmental directory beneath PI11/control.
Synthetic values only verify the transducer, never count as Native evidence.
"""
from pathlib import Path
import importlib.util,json,tempfile,unittest

MODULE=Path(__file__).with_name('pi11_habitat_persistente_R01.py')
spec=importlib.util.spec_from_file_location('pi11_pure_habitat',MODULE)
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
ROOT=MODULE.parent.parent/'control'
RAW_Z=(1<<60)|(1<<56)|1
RAW_X=(1<<60)|(1<<48)|1

def protocol():return {'schema':'DEE.PI11.persistent_habitat.protocol.R01','events':[
    {'at_offset':0,'mode':'need','cue':'z'},
    {'at_offset':601,'mode':'bypass','cue':'x'},
    {'at_offset':1177,'mode':'need','cue':'none'}]}

def snapshot(home):
    return {str(p.relative_to(home)):p.read_bytes()for p in home.rglob('*')if p.is_file()}

class Habitat(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='pure_PI11_',dir=ROOT)
        self.home=Path(self.temp.name);h.init(self.home,protocol(),10000)
    def tearDown(self):self.temp.cleanup()
    def offer(self,n,tick,raw=RAW_Z):return h.prepare_offer(self.home,n,{'raw':raw,'tick':tick-1},tick)
    def access(self,n,tick,gate=1,signature=True):return h.request_access(self.home,n,gate,signature,tick)
    def test_init_finite_and_no_reset(self):
        self.assertEqual(h.status(self.home)['remaining_stock'],24)
        before=snapshot(self.home)
        with self.assertRaises(ValueError):h.init(self.home,protocol(),10000)
        self.assertEqual(snapshot(self.home),before)
    def test_whole_elapsed_clock_and_irregular_events(self):
        self.assertEqual(h.environment_at(self.home,10600)['mode'],'need')
        self.assertEqual(h.environment_at(self.home,10601)['mode'],'bypass')
        self.assertEqual(h.environment_at(self.home,11177)['mode'],'need')
        h.advance(self.home,10000+3*4687+5)
        self.assertEqual(h.status(self.home)['replenishments'],3)
    def test_status_and_verify_are_passive(self):
        before=snapshot(self.home);h.status(self.home);h.verify(self.home)
        self.assertEqual(snapshot(self.home),before)
    def test_refresh_then_reuse_consecutive_same_habitat(self):
        self.offer(0,10010);self.access(0,10018)
        result=h.execute(self.home,0,1,True,True,1,True,10100)
        self.assertTrue(result['physical_delivered']);self.assertEqual(result['remaining_stock'],23)
        self.offer(1,10400);self.access(1,10408,-1,False)
        result=h.execute(self.home,1,1,True,True,None,False,10450)
        self.assertTrue(result['physical_delivered']);self.assertEqual(result['remaining_stock'],22)
        self.assertEqual(h.status(self.home)['certificate_reuses'],1)
        self.assertTrue(h.verify(self.home)['verified'])
    def test_no_certificate_cannot_fabricate_success(self):
        self.offer(0,10010);self.access(0,10018,-1,False)
        result=h.execute(self.home,0,1,True,True,None,False,10100)
        self.assertFalse(result['physical_delivered']);self.assertEqual(result['remaining_stock'],24)
    def test_failed_refresh_not_rescued_by_old_certificate(self):
        self.offer(0,10010);self.access(0,10018)
        h.execute(self.home,0,1,True,True,1,True,10100)
        self.offer(1,10400);self.access(1,10408,-1,False)
        result=h.execute(self.home,1,1,True,True,-1,True,10450)
        self.assertFalse(result['physical_delivered']);self.assertTrue(result['certificate_valid'])
    def test_expiry_with_clock_no_reset(self):
        self.offer(0,10010);self.access(0,10018)
        h.execute(self.home,0,1,True,True,1,True,10100)
        self.offer(1,15000);self.access(1,15008,-1,False)
        result=h.execute(self.home,1,1,True,True,None,False,15050)
        self.assertFalse(result['physical_delivered']);self.assertFalse(result['certificate_valid'])
    def test_permission_busy_interval_and_replenishment(self):
        self.offer(0,10010);self.access(0,10018)
        self.assertFalse(h.can_access(self.home,10019)['allowed'])
        self.assertTrue(h.can_access(self.home,10251)['allowed'])
        self.assertEqual(h.status(self.home)['permissions'],3)
        h.advance(self.home,14687)
        self.assertEqual(h.status(self.home)['permissions'],4)
    def test_unknown_RAW_rejected_without_partial_effect(self):
        before=snapshot(self.home)
        with self.assertRaises(ValueError):self.offer(0,10010,RAW_X|(1<<56))
        self.assertEqual(snapshot(self.home),before)
    def test_bad_route_rejected_without_effect(self):
        self.offer(0,10010);self.access(0,10018)
        before=snapshot(self.home)
        with self.assertRaises(ValueError):h.execute(self.home,0,2,True,True,1,True,10100)
        self.assertEqual(snapshot(self.home),before)
    def test_fail_retains_shared_resource_then_success_consumes(self):
        first=self.offer(0,10010);self.access(0,10018)
        result=h.execute(self.home,0,0,True,True,1,True,10100)
        self.assertFalse(result['physical_delivered'])
        second=self.offer(1,10400,RAW_X);self.access(1,10408,-1,False)
        self.assertEqual(first['slot_id'],second['slot_id'])
        result=h.execute(self.home,1,0,True,True,None,False,10450)
        self.assertTrue(result['physical_delivered']);self.assertEqual(result['remaining_stock'],23)
    def test_save_reload_same_environment(self):
        self.offer(0,10010);self.access(0,10018)
        h.execute(self.home,0,1,True,True,1,True,10100)
        before=h.status(self.home)
        another=importlib.util.module_from_spec(spec);spec.loader.exec_module(another)
        self.assertEqual(another.status(self.home),before)
        self.assertTrue(another.verify(self.home)['verified'])

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Habitat)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    print(json.dumps({'pure':True,'Native_imported':False,'Native_ticks':0,
                      'tests':result.testsRun,'errors':len(result.errors),'failures':len(result.failures)},sort_keys=True))
    raise SystemExit(0 if result.wasSuccessful()else 1)
