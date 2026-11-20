"""Synthetic administrative lease/RAM tests; no real SDK/model/OS measurement."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
from test_runner_RAM_R06_sintetico import FakeWorld,FakeBackend
ROOT=Path(__file__).resolve().parents[1]

def load_synthetic():
    transport=types.ModuleType('world_comprimido_v3_R06');transport.CompressedWorld=FakeWorld
    backends=types.ModuleType('backends_v3_R06');backends.create_backend=lambda *a,**k:FakeBackend(*a,**k)
    spec=importlib.util.spec_from_file_location('_SYNTHETIC_NEW_LEASE',ROOT/'control/runner_comparador_v3_R07_RAM.py')
    module=importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules,{'world_comprimido_v3_R06':transport,'backends_v3_R06':backends}):spec.loader.exec_module(module)
    return module

class LeaseFixtures(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.module=load_synthetic()
        self.module.ROOT=self.root;FakeWorld.instances=[];FakeBackend.instances=[]
        self.source=self.root/'SYNTHETIC_PAR28.json'
        self.source.write_text(json.dumps({'world_id':'RBX01_INTEGRAL_V2_R06','native_tick':991187,
            'scenario_sha256':'SYNTHETIC','S':{'completedCycles':28,'sessionId':'OLD'},
            'boundary':{'phase':'BOUNDARY','next_opportunity':29}}),'utf-8')
        self.args=types.SimpleNamespace(execute_root_only=True,world=self.source,
            destination=self.root/'comparadores/SYNTHETIC',output=self.root/'evidencia/SYNTHETIC',
            participant='CONVENTIONAL_AI',studio_id='NO_REAL_STUDIO',expected_place='SYNTHETIC',
            stop_cycle=29,session='SYNTHETIC_SESSION',resume=False,min_start_free_bytes=3758096384)
    def tearDown(self):self.tmp.cleanup()
    def call(self,mem):
        elapsed=[0.0]
        def sleep(seconds):elapsed[0]+=seconds
        with patch.object(self.module,'host_memory',mem),patch.object(self.module.time,'monotonic',side_effect=lambda:elapsed[0]),\
            patch.object(self.module.time,'sleep',side_effect=sleep),patch.object(self.module.time,'time',return_value=1794885000):
            result=self.module.execute(self.args)
        return result,elapsed[0]
    def test_wait_before_any_World_policy_then_guarded_zero_episode_close(self):
        values=iter([3*1024**3,4*1024**3,512*1024**2]);n=[0]
        def mem():
            if n[0]<2:self.assertEqual(FakeWorld.instances,[]);self.assertEqual(FakeBackend.instances,[])
            n[0]+=1;return {'source':'SYNTHETIC','available_physical_bytes':next(values)}
        result,seconds=self.call(mem)
        self.assertEqual(seconds,5.0);self.assertEqual(result['new_opportunities_completed'],0)
        self.assertEqual(result['global_completed'],28);self.assertEqual(result['stop_reason'],'HOST_FREE_RAM_BELOW_1GiB')
        self.assertTrue(result['owner_closed']);self.assertEqual(FakeBackend.instances[0].calls,[])
    def test_wait_is_max120_and_timeout_opens_no_World_or_policy(self):
        elapsed=[0.0]
        def sleep(seconds):elapsed[0]+=seconds
        mem=lambda:{'source':'SYNTHETIC','available_physical_bytes':3*1024**3}
        with patch.object(self.module,'host_memory',mem),patch.object(self.module.time,'monotonic',side_effect=lambda:elapsed[0]),\
            patch.object(self.module.time,'sleep',side_effect=sleep),patch.object(self.module.time,'time',return_value=1794885000):
            with self.assertRaises(MemoryError):self.module.execute(self.args)
        self.assertEqual(elapsed[0],120.0);self.assertEqual(FakeWorld.instances,[]);self.assertEqual(FakeBackend.instances,[])
        rejected=json.loads((self.args.output/'PREFLIGHT_RAM_REJECTED.json').read_text())
        self.assertEqual(rejected['model_calls'],0);self.assertEqual(rejected['minimum_start_free_bytes'],3758096384)
    def test_fixed_lease_and_policy_AST_source_invariance(self):
        self.assertEqual(self.module.CUTOFF,1794902400);self.assertEqual(self.module.HARD_CLOSE,1794906420)
        self.assertEqual(self.module.MIN_START_FREE_BYTES,3758096384);self.assertEqual(self.module.STOP_FREE_BYTES,1073741824)
        metadata=json.loads((ROOT/'control/E5_LEASE_R06_PREPARADO.json').read_text())
        for row in metadata['records']:
            self.assertEqual(hashlib.sha256((ROOT/row['source']).read_bytes()).hexdigest(),row['original_sha256'])
            self.assertEqual(hashlib.sha256((ROOT/row['new']).read_bytes()).hexdigest(),row['new_sha256'])
        self.assertTrue(metadata['AST_policy_functions_identical']);self.assertFalse(metadata['quota_reset'])

if __name__=='__main__':unittest.main(verbosity=2)
