from pathlib import Path
import copy,importlib.util,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('_fixture_world_motor_R02',ROOT/'control/world_comprimido_v3_R02.py');m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
class Tests(unittest.TestCase):
    def fixture(self,common=False):
        pose=[0]*12;source={'events':[{'kind':'OLD_NATIVE_EVENT','data':{'actual':11}}],'body_pose':pose}
        identity={'life':'V3_MAIN','session':'S','participant':'LIVE_NATIVE'}
        added=[{'kind':'MOTOR_PREPARED','data':{'kind':'HUMANOID_PATHFINDING','preservedPivot':pose,'semantic_destination_selected_by_motor':False}},
          {'kind':'R07_MOTOR_ENVIRONMENT_PREPARATION','data':{'native_ticks_advanced':0,'semanticPolicy':False,'floorAndObstaclesPrepared':True}},
          {'kind':'R07_TECHNICAL_IDENTITY','data':{'current':identity,'Native_memory_edited':False,'products_preserved':True}}]
        if common:added.insert(0,{'kind':'R07_COMMON_NAVIGATION_GEOMETRY','data':{'oldDecorativeCollidersDisabled':0}})
        return source,{'events':copy.deepcopy(source['events'])+added},identity
    def test_exact_preparation(self):
        for common in(False,True):
            a,b,c=self.fixture(common);self.assertEqual(len(m.verify_restore_events(a,b,c)),3+int(common))
    def test_reject_historical_edit(self):
        a,b,c=self.fixture();b['events'][0]['data']['actual']=0
        with self.assertRaises(RuntimeError):m.verify_restore_events(a,b,c)
    def test_reject_added_action(self):
        a,b,c=self.fixture();b['events'].append({'kind':'ACTION_EXECUTED'})
        with self.assertRaises(RuntimeError):m.verify_restore_events(a,b,c)
    def test_reject_semantic_motor(self):
        a,b,c=self.fixture();b['events'][1]['data']['semantic_destination_selected_by_motor']=True
        with self.assertRaises(RuntimeError):m.verify_restore_events(a,b,c)
    def test_reject_pivot_change(self):
        a,b,c=self.fixture();b['events'][1]['data']['preservedPivot']=[1]*12
        with self.assertRaises(RuntimeError):m.verify_restore_events(a,b,c)
    def test_keep_same_session_on_reopen(self):
        text=(ROOT/'control/run_integrated_v3_R02.py').read_text('utf8')
        self.assertIn("state['S']['sessionId'] if state['native_life_id']==life",text)
        self.assertEqual(m.BASE.FINISH,1794863220)
if __name__=='__main__':unittest.main()
