"""Synthetic runner/World/backend only. Never imports real transport or model."""
from pathlib import Path
import copy
import importlib.util
import json
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

class FakeWorld:
    instances=[]
    def __init__(self,studio,output,record,expected_place):
        self.calls=[];self.output=output;self.closed=False;self.record=record
        self.instances.append(self)
    def initialize(self,state,identity,source_sha):
        self.state=copy.deepcopy(state);self.state['world_id']='RBX01_CIERRE8_R07'
        self.state['S']['sessionId']=identity['session'];return {'synthetic':True}
    def observation(self):return {'seq':57,'observationId':'SYNTHETIC_OBSERVATION'}
    def call(self,identifier,kind,data):
        self.calls.append((identifier,kind,data))
        if kind=='begin':return {'observation':self.observation()}
        if kind=='action':return {'result':{'outcome':'WAITED'},'executed_name':None,'selected_name':None}
        if kind=='feedback_fields':return {'feedback':{'materialConsequence':False},'observation':self.observation()}
        if kind=='complete':
            self.state['S']['completedCycles']+=1
            self.state['boundary']['next_opportunity']=self.state['S']['completedCycles']+1
            return {'S':copy.deepcopy(self.state['S']),'boundary':copy.deepcopy(self.state['boundary'])}
        raise AssertionError(kind)
    def checkpoint(self,identifier,path):
        self.state['checkpoint_id']=identifier
        path.write_text(json.dumps(self.state),'utf-8');return self.state
    def close(self):self.closed=True

class FakeBackend:
    instances=[]
    def __init__(self,*args,**kwargs):
        self.calls=[];self.state={'pending':None};self.closed=False;self.saved=False;self.instances.append(self)
    def execute(self,kind,payload,context):
        self.calls.append(kind)
        return {'action':'SKIP_STATION','null':False}if kind=='decision'else{'accepted':True}
    def checkpoint(self):self.saved=True;return {'synthetic':True,'pending':None}
    def close(self):self.closed=True

def module():
    transport=types.ModuleType('world_comprimido_v3_R05');transport.CompressedWorld=FakeWorld
    backend=types.ModuleType('backends_v3_R05');backend.create_backend=lambda *a,**k:FakeBackend(*a,**k)
    path=Path(__file__).with_name('runner_comparador_v3_R06_RAM.py')
    spec=importlib.util.spec_from_file_location('SYNTHETIC_RAM_RUNNER',path)
    value=importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules,{'world_comprimido_v3_R05':transport,'backends_v3_R05':backend}):
        spec.loader.exec_module(value)
    return value

class RAMFixtures(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.m=module();self.m.ROOT=self.root;FakeWorld.instances=[];FakeBackend.instances=[]
        self.source=self.root/'PAR28_SYNTHETIC.json'
        self.source.write_text(json.dumps({'world_id':'RBX01_INTEGRAL_V2_R06','native_tick':991187,
            'scenario_sha256':'SYNTHETIC','S':{'completedCycles':28,'sessionId':'OLD'},
            'boundary':{'phase':'BOUNDARY','next_opportunity':29}}),'utf-8')
    def tearDown(self):self.temp.cleanup()
    def args(self):
        return types.SimpleNamespace(execute_root_only=True,world=self.source,
            destination=self.root/'comparadores/SYNTHETIC',output=self.root/'evidencia/SYNTHETIC',
            participant='CONVENTIONAL_AI',studio_id='NO_REAL_STUDIO',expected_place='SYNTHETIC_ONLY',
            stop_cycle=30,session='SYNTHETIC_SESSION',resume=False,min_start_free_bytes=3758096384)
    def execute(self,values):
        samples=iter(values)
        def mem():return {'source':'SYNTHETIC_NOT_HOST','available_physical_bytes':next(samples)}
        with patch.object(self.m,'host_memory',mem),patch.object(self.m.time,'time',return_value=1794860000):
            return self.m.execute(self.args())
    def test_zero_episodes_closes_real_cursor_without_BEGIN(self):
        result=self.execute([4*1024**3,512*1024**2])
        self.assertEqual(result['new_opportunities_completed'],0)
        self.assertEqual(result['global_completed'],28)
        self.assertEqual(result['stop_reason'],'HOST_FREE_RAM_BELOW_1GiB')
        self.assertTrue(result['owner_closed'])
        self.assertEqual(FakeWorld.instances[0].calls,[])
        self.assertEqual(FakeBackend.instances[0].calls,[])
        self.assertTrue(FakeBackend.instances[0].saved and FakeBackend.instances[0].closed)
    def test_stop_after_one_does_not_begin_second(self):
        result=self.execute([4*1024**3,2*1024**3,512*1024**2])
        self.assertEqual(result['new_opportunities_completed'],1)
        self.assertEqual(result['global_completed'],29)
        self.assertEqual(result['stop_reason'],'HOST_FREE_RAM_BELOW_1GiB')
        begins=[c for c in FakeWorld.instances[0].calls if c[1]=='begin']
        self.assertEqual([c[2]['cycle']for c in begins],[29])
        self.assertEqual(FakeBackend.instances[0].calls,['decision','feedback'])
        self.assertTrue(result['owner_closed']and FakeWorld.instances[0].closed)
    def test_start_rejection_opens_no_World_or_policy(self):
        with self.assertRaises(MemoryError):self.execute([512*1024**2])
        self.assertEqual(FakeWorld.instances,[]);self.assertEqual(FakeBackend.instances,[])
        self.assertTrue((self.args().output/'PREFLIGHT_RAM_REJECTED.json').exists())
    def test_same_requested_horizon_when_memory_sufficient(self):
        result=self.execute([4*1024**3,2*1024**3,2*1024**3])
        self.assertEqual(result['new_opportunities_completed'],2)
        self.assertEqual(result['global_completed'],30)
        self.assertEqual(result['stop_reason'],'REQUESTED_HORIZON_COMPLETED')
        self.assertEqual(self.m.CUTOFF,1794880800);self.assertEqual(self.m.HARD_CLOSE,1794884820)
        self.assertFalse(result['daemon_stop_written'])
        self.assertEqual(self.m.MIN_START_FREE_BYTES,3758096384)
    def test_no_implicit_start_margin(self):
        a=self.args();a.min_start_free_bytes=0
        with patch.object(self.m.time,'time',return_value=1794860000):
            with self.assertRaisesRegex(ValueError,'threshold'):self.m.execute(a)
        self.assertEqual(FakeWorld.instances,[]);self.assertEqual(FakeBackend.instances,[])

if __name__=='__main__':unittest.main(verbosity=2)
