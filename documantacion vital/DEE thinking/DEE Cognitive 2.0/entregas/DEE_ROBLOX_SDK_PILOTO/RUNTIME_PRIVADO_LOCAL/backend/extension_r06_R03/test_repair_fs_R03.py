"""Synthetic FS-only repair transaction. No Native/SQL or real instance reads."""
from pathlib import Path
import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import reparar_boot_access_R03 as repair
CORE=Path(__file__).resolve().parents[1]/'r06/sdk_common.py'
spec=importlib.util.spec_from_file_location('repair_common_fake_files',CORE);common=importlib.util.module_from_spec(spec);spec.loader.exec_module(common)

class RepairTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.i='SDK_DEMO_0123456789ABCDEF';self.life=common.LIFE_PREFIX+self.i
        self.home=self.root/'estado_demo/instancias'/self.i;self.cap=self.home/'sistema/capacidades';self.cap.mkdir(parents=True)
        cfg={'instanceId':self.i,'lifeId':self.life,'sessionId':'sid','runtimeVersion':'0.1.1','validationRevision':'R06','nativeTick':994315}
        common.atomic(self.home/'INSTANCE.json',cfg)
        self.native={'lifeId':self.life,'nativeTick':994315,'dimension':67,'writerClosed':True,'pending':0,
                     'snapshotSha256':'a'*64,'databaseSha256':'b'*64,'cardSha256':'c'*64}
        for name in repair.FILES:(self.cap/name).write_text('old participant '+name,encoding='utf8')
        self.scope={'lifeId':self.life,'allowedLifeIds':[self.life],'instanceId':self.i,'sessionId':'sid',
                    'preCapNative':self.native,'maxEvents':10,'lastNewUtcEpoch':1234,'native_cutoff_utc_epoch':2345,
                    'sourceHashes':{name:common.sha(self.cap/name) for name in repair.FILES}}
        scopefile=self.cap/'SDK_CAPABILITIES_SCOPE_R06.json';common.atomic(scopefile,self.scope)
        self.registry={'plugins':['old_plugin','sdk_capabilities_R06'],
            'files_sha256':{**self.scope['sourceHashes'],scopefile.name:common.sha(scopefile)}}
        common.atomic(self.cap/'PI10_PLUGINS_R01.json',self.registry)
        self.oldstate={'instanceId':self.i,'sessionId':'sid','nativeTick':994315,'capabilitySequence':0,
            'status':'FAILED_PRESERVED','lastError':{'code':'OWNER_START_OR_CLOSE_FAILED','message':'denied INSTANCE'},
            'preCapDescriptor':{'nativeTick':994315}}
        common.atomic(self.home/'CAPABILITIES_STATE_R06.json',self.oldstate)
        (self.home/'ensayos').mkdir();(self.home/'ensayos/failure.txt').write_text('app/access_guard.py denied INSTANCE.json',encoding='utf8')
        ledger=self.root/'estado_demo/LEDGER_SDK_R06.json'
        common.atomic(ledger,{'intents':{},'worlds':{self.life:{'reserved':0,'capability_events':0}}})
        self.patches=[patch.object(repair,'common',return_value=common),patch.object(common,'closed_native',return_value=copy.deepcopy(self.native))]
        for p in self.patches:p.start()
    def tearDown(self):
        for p in reversed(self.patches):p.stop()
        self.tmp.cleanup()
    def test_repair_preserves_old_flags_and_physics_and_changes_only_declared_scope(self):
        state_before=(self.home/'CAPABILITIES_STATE_R06.json').read_bytes();ledger_before=(self.root/'estado_demo/LEDGER_SDK_R06.json').read_bytes()
        result=repair.apply(self.root,self.i,'ensayos/failure.txt')
        self.assertEqual(result['newNativeTicks'],0);self.assertEqual(result['nativeBefore'],result['nativeAfter'])
        self.assertEqual((self.home/'CAPABILITIES_STATE_R06.json').read_bytes(),state_before)
        self.assertEqual((self.root/'estado_demo/LEDGER_SDK_R06.json').read_bytes(),ledger_before)
        new=common.read(self.cap/'SDK_CAPABILITIES_SCOPE_R06.json')
        for k,v in self.scope.items():
            if k!='sourceHashes':self.assertEqual(new[k],v)
        self.assertEqual(new['hostProfile'],{'runtimeVersion':'0.1.1','validationRevision':'R06'})
        fresh=common.read(self.home/'CAPABILITIES_STATE_R06_R03.json')
        self.assertEqual(fresh['capabilitySequence'],0);self.assertEqual(fresh['previousFailedBoot']['errorPreserved'],self.oldstate['lastError'])
        with self.assertRaises(ValueError):repair.apply(self.root,self.i,'ensayos/failure.txt')
    def test_any_event_or_intent_prevents_changes(self):
        state=self.home/'CAPABILITIES_STATE_R06.json';v=common.read(state);v['capabilitySequence']=1;common.atomic(state,v)
        with self.assertRaises(ValueError):repair.plan(self.root,self.i,'ensayos/failure.txt')
        v['capabilitySequence']=0;common.atomic(state,v)
        ledger=self.root/'estado_demo/LEDGER_SDK_R06.json';v=common.read(ledger);v['intents']={self.life:{'id':'uncertain'}};common.atomic(ledger,v)
        with self.assertRaises(ValueError):repair.plan(self.root,self.i,'ensayos/failure.txt')
        self.assertFalse((self.home/'CAPABILITIES_REPAIR_ACCESS_R03').exists())
    def test_native_mismatch_prevents_changes(self):
        different={**self.native,'snapshotSha256':'d'*64}
        with patch.object(common,'closed_native',return_value=different):
            with self.assertRaises(ValueError):repair.plan(self.root,self.i,'ensayos/failure.txt')
        self.assertFalse((self.home/'CAPABILITIES_REPAIR_ACCESS_R03').exists())

if __name__=='__main__':unittest.main()
