"""Technical K4 contract using temporary JSON and no Native owner."""
from pathlib import Path
import copy
import queue
import sys
import tempfile
import threading
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from restoration_contract import expected_view,compare
from sdk_common import atomic,digest,sha
from servicio_sdk import Service,Conflict

class RestoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.home=Path(self.tmp.name)
        self.state={'sessionId':'sid','lifeId':'life','sequence':2,'nativeTick':992751,
                    'completedOpportunities':1,'phase':'BOUNDARY','closeRequested':True,
                    'lastFeedbackOperationId':'feedback_old'}
        self.snapshot={'schema':'DEE.RBX.AgentWorldCheckpoint.R01','namespace':'ns',
            'scenarioFingerprint':'f'*64,'bindings':{'x':1},'state':self.state,
            'actions':{'action_old':{'exact':'receipt'}},'tools':[],
            'body':{'pose':[1,2,3],'CanCollide':True},
            'world':{'motor':{'cframe':[1,2,3]},'permissionStock':163}}
        pair={'snapshot':self.snapshot,'snapshotSha256':digest(self.snapshot)}
        atomic(self.home/'SDK_PAIR.json',pair)
        s=Service.__new__(Service);self.service=s;s.home=self.home;s.instance_id='SDK_DEMO_0123456789ABCDEF'
        s.session_id='sid';s.cfg={'lifeId':'life','completedCycles':1};s.native_tick=992751;s.local_sequence=2
        s.mode='continue';s.status='READY';s.phase='decision';s.work=queue.Queue();s.lock=threading.RLock()
        s.restoration_verified=False;s.store=self.home/'http_operations';s.store.mkdir();s.acks={'action_old':{}}
        for op in ('action_old','feedback_old'):
            atomic(s.store/(op+'.json'),{'operationId':op,'status':'COMPLETED','kind':'feedback' if op.startswith('feedback') else 'decision','value':{'nativeTick':992751}})
        expected=expected_view(self.snapshot)
        self.body={'instanceId':s.instance_id,'sessionId':'sid','operationId':'restore_original',
            'checkpointSha256':pair['snapshotSha256'],'pairSha256':sha(self.home/'SDK_PAIR.json'),
            'proof':{'schema':'DEE.RBX.RestorationProof.R06','ok':True,'differenceCount':0,
                'differences':[],'poseTolerance':1e-5,'actual':copy.deepcopy(expected),'expected':expected}}
    def tearDown(self):self.tmp.cleanup()
    def test_full_match_is_durable_idempotent_and_unlocks_gate(self):
        s=self.service;v=s.restoration_proof(self.body)
        self.assertEqual(v['status'],'RECORDED');self.assertTrue(s.restoration_verified)
        self.assertEqual(s.restoration_proof(self.body),v)
        self.assertEqual(len(list((self.home/'restoration_proofs').glob('*.json'))),1)
    def test_collision_difference_rejected_and_preserved(self):
        self.body['proof']['actual']['body']['CanCollide']=False
        with self.assertRaises(Conflict):self.service.restoration_proof(self.body)
        self.assertFalse(self.service.restoration_verified)
        self.assertTrue((self.home/'restoration_proofs/restore_original.json').exists())
    def test_numeric_tolerance_only_for_pose_paths(self):
        a=expected_view(self.snapshot);b=copy.deepcopy(a);b['body']['pose'][0]+=5e-6
        self.assertTrue(compare(a,b)['passed'])
        b['world']['permissionStock']+=5e-6;self.assertFalse(compare(a,b)['passed'])
    def test_receipt_and_bool_are_literal(self):
        a=expected_view(self.snapshot);b=copy.deepcopy(a);b['actions']['action_old']['exact']='different'
        self.assertFalse(compare(a,b)['passed']);b=copy.deepcopy(a);b['body']['CanCollide']=1
        self.assertFalse(compare(a,b)['passed'])
    def test_raw_snapshot_is_not_modified_by_allowed_close_transition(self):
        value=expected_view(self.snapshot);self.assertFalse(value['state']['closeRequested'])
        self.assertTrue(self.snapshot['state']['closeRequested'])
    def test_receipt_uuid_c0_does_not_enable_pose_tolerance(self):
        a=expected_view(self.snapshot);a['actions']['op_c0']={'nativeTick':992751}
        b=copy.deepcopy(a);b['actions']['op_c0']['nativeTick']+=5e-6
        self.assertFalse(compare(a,b)['passed'])

if __name__=='__main__':unittest.main()
