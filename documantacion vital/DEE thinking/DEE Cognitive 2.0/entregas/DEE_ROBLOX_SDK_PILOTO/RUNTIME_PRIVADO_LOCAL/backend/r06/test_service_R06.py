"""Only fake adapters and temporary JSON. No Native/HTTP/host memory calls."""
from pathlib import Path
import json
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import servicio_sdk as service
import sdk_common as common
from resource_wait import ResourceUnavailableBeforeNative

class FakeManager:
    def __init__(self):self.closed=False
    def __enter__(self):return self
    def __exit__(self,*_):self.closed=True

class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.i='SDK_DEMO_0123456789ABCDEF';self.sid='SDK_SESSION_'+'0'*32
        self.home=self.root/'estado_demo/instancias'/self.i;self.home.mkdir(parents=True)
        now=int(time.time());self.window={'schema':common.SCHEMA,'startUtcEpoch':now-10,
            'lastNewUtcEpoch':now+1200,'hardFinishUtcEpoch':now+3600,'maxNativeTicks':40000,
            'maxSdkCycles':3,'ownerMemoryBytes':536870912,'threads':1,'maxRawSupport':10000,
            'minimumHostFreeBytes':3758096384,'sealed':True}
        (self.root/'configuracion').mkdir();common.atomic(self.root/'configuracion/VENTANA_R06.json',self.window)
        self.cfg={'instanceId':self.i,'lifeId':common.LIFE_PREFIX+self.i,'sessionId':self.sid,
            'runtimeVersion':'0.1.1','validationRevision':'R06','sequenceOffset':56,
            'localSequence':0,'nativeTick':991187,'completedCycles':0,'nextPhase':'decision',
            'initialPublicState':{},'sourceWorldSha256':'0'*64}
        self.cfg['operationalLease']={'schema':'DEE.Roblox.SDK.operational_lease.0.1.0',
            'instanceId':self.i,'lifeId':self.cfg['lifeId'],'sessionId':self.sid,
            'startUtcEpoch':now-5,'lastNewUtcEpoch':now+1200,'hardFinishUtcEpoch':now+3600,
            'additionalCycles':1,'startingCompletedCycles':0,'startingConsumedTicks':0,
            'cumulativeCycleCap':1,'validationCampaign':True,
            'validationCampaignSha256':common.sha(self.root/'configuracion/VENTANA_R06.json')}
        common.atomic(self.home/'INSTANCE.json',self.cfg);self.calls=[];self.manager=FakeManager()
    def tearDown(self):self.tmp.cleanup()
    def start(self,adapter,memory=lambda:4*1024**3):
        self.s=service.Service(self.i,runtime=self.root,mode='new',token='test-only-'+'x'*40,
            factory=lambda *_:(self.manager,adapter),memory=memory)
        until=time.monotonic()+3
        while self.s.status!='READY' and time.monotonic()<until:time.sleep(.001)
        self.assertEqual(self.s.status,'READY')
    def body(self):
        return {'instanceId':self.i,'sessionId':self.sid,'operationId':'sdk_decision_original',
            'payload':{'observation':{'observationId':'obs_original','seq':1,'phase':'QUERY_CHOICE',
                'worldTimeMs':0,'sampleTimeMs':0,'sensors':{}}}}
    def finish_thread(self):
        self.s.window['hardFinishUtcEpoch']=time.time()-.01
        self.s.thread.join(3);self.assertFalse(self.s.thread.is_alive());self.s.release()
    def test_low_ram_waits_same_id_without_adapter_replay(self):
        outer=self;enough=threading.Event()
        class Adapter:
            def execute(self,*args):
                outer.calls.append(args);return {'action':'ASK_STATION','nativeTick':991543}
        def memory():return 4*1024**3 if self.s.owner is None or enough.is_set() else 1024**3-1
        # The callback may run before assignment to self.s; startup sample is high.
        def safe_memory():return 4*1024**3 if not hasattr(self,'s') else memory()
        self.start(Adapter(),safe_memory);b=self.body();first=self.s.submit('decision',b)
        until=time.monotonic()+2
        while self.s.operation(b['operationId'])['status']!='PENDING_RESOURCE' and time.monotonic()<until:time.sleep(.001)
        self.assertEqual(self.s.operation(b['operationId'])['status'],'PENDING_RESOURCE')
        self.assertEqual(self.calls,[]);self.assertEqual(self.s.local_sequence,0)
        self.s.submit('decision',b);self.assertEqual(self.calls,[])
        enough.set();until=time.monotonic()+3
        while self.s.operation(b['operationId'])['status']!='COMPLETED' and time.monotonic()<until:time.sleep(.001)
        self.assertEqual(len(self.calls),1);self.assertEqual(self.s.local_sequence,1)
        self.s.submit('decision',b);self.assertEqual(len(self.calls),1);self.finish_thread()
    def test_generic_failure_after_execute_remains_uncertain(self):
        outer=self
        class Adapter:
            def execute(self,*args):outer.calls.append(args);raise RuntimeError('unknown after admission')
        self.start(Adapter());b=self.body();self.s.submit('decision',b)
        self.s.thread.join(3);v=self.s.operation(b['operationId'])
        self.assertEqual(v['status'],'UNCERTAIN');self.assertTrue(v['nativeAdmissionStarted'])
        self.assertEqual(len(self.calls),1);self.s.submit('decision',b)
        self.assertEqual(len(self.calls),1);self.s.release()
    def test_pair_cursor_and_hash_checked_before_continue(self):
        cfg={**self.cfg,'localSequence':2,'nativeTick':992751,'completedCycles':1}
        native={'lifeId':cfg['lifeId'],'nativeTick':992751,'snapshotSha256':'a'*64,
                'databaseSha256':'b'*64,'cardSha256':'c'*64,'writerClosed':True,'pending':0}
        state={'sessionId':self.sid,'lifeId':cfg['lifeId'],'nativeTick':992751,
               'sequence':2,'completedOpportunities':1,'phase':'BOUNDARY'}
        snapshot={'schema':'DEE.RBX.AgentWorldCheckpoint.R01','state':state,'world':{'exact':True}}
        proof={**native,'sessionId':self.sid,'localSequence':2,'backendWriterClosed':True,'bridgeQuiescent':True}
        proof['proofSha256']=common.digest(proof)
        pair={'snapshot':snapshot,'snapshotSha256':common.digest(snapshot),'native':native,
              'backendProof':proof,'instanceId':self.i,'sessionId':self.sid,'localSequence':2}
        common.atomic(self.home/'SDK_PAIR.json',pair)
        self.assertEqual(common.validate_pair(self.home,cfg,native)['snapshot'],snapshot)
        pair['snapshot']['state']['sequence']=0;common.atomic(self.home/'SDK_PAIR.json',pair)
        with self.assertRaises(ValueError):common.validate_pair(self.home,cfg,native)

if __name__=='__main__':unittest.main()
