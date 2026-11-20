"""Pure FOCAL6 contracts and synthetic shared accounting; no DEE/SQL/network."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
HERE=Path(__file__).resolve().parent;sys.path[:0]=[str(HERE),str(HERE.parent)]
import common_focal as c
import sdk_common as demo
import lease_focal_R02 as lease_module
import ledger_focal as f
import ledger_sdk as base

def lease(cfg, extra=6):
    w=c.budget(now=0);start=int(time.time())
    return {'schema':'DEE.Roblox.SDK.operational_lease.0.1.0','leaseId':'SDK_LEASE_0123456789ABCDEF',
        'instanceId':cfg['instanceId'],'lifeId':cfg['lifeId'],'sessionId':cfg['sessionId'],
        'startUtcEpoch':start,'lastNewUtcEpoch':w['lastNewUtcEpoch'],'hardFinishUtcEpoch':w['hardFinishUtcEpoch'],
        'additionalCycles':extra,'startingCompletedCycles':0,'startingConsumedTicks':0,'cumulativeCycleCap':extra,
        'validationCampaign':True,'validationCampaignSha256':c.sha(c.RUNTIME/'configuracion/VENTANA_CONGELADA.json')}

class Profile(unittest.TestCase):
    def cfg(self):
        iid='SDK_DEMO_0123456789ABCDEF';return {'instanceId':iid,'lifeId':base.PREFIX+iid,'sessionId':'SDK_SESSION_'+'a'*32,'profile':'FOCAL'}
    def test_local12_and_lua_nil_without_changing_demo6(self):
        observation={'observationId':'obs12','seq':12,'phase':'ROUTE_CHOICE','worldTimeMs':0,'sampleTimeMs':0,'sensors':{}}
        p,n,_=c.native_payload('query_sensor',{'observation':observation},56)
        self.assertEqual((p['observation']['seq'],n),(68,12));self.assertIsNone(p['observation']['previousActionId'])
        with self.assertRaises(ValueError):demo.native_payload('query_sensor',{'observation':observation},56)
        observation['seq']=13
        with self.assertRaises(ValueError):c.native_payload('query_sensor',{'observation':observation},56)
    def test_lease6_cap_and_native_identity(self):
        cfg=self.cfg();x=lease(cfg)
        w=c.budget(now=0)
        self.assertEqual(lease_module.validate_lease(x,cfg,now=x['startUtcEpoch'],campaign=w,campaign_sha=x['validationCampaignSha256']),x)
        cfg['operationalLease']=x;self.assertEqual(c.operational_window(cfg,now=x['startUtcEpoch'])['hardFinishUtcEpoch'],w['hardFinishUtcEpoch'])
        x['additionalCycles']=7;x['cumulativeCycleCap']=7
        with self.assertRaises(ValueError):lease_module.validate_lease(x,cfg,now=x['startUtcEpoch'],campaign=w,campaign_sha=x['validationCampaignSha256'])
    def test_shared_ledger_counts_focal_and_preserves_existing_demo(self):
        cfg=self.cfg();x=lease(cfg)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'configuracion').mkdir();(root/'configuracion/VENTANA_CONGELADA.json').write_bytes((c.RUNTIME/'configuracion/VENTANA_CONGELADA.json').read_bytes())
            home=root/'estado_demo/instancias'/cfg['instanceId'];home.mkdir(parents=True);(home/'INSTANCE.json').write_text(json.dumps(cfg))
            path=root/'estado_demo/LEDGER_SDK.json'
            with patch.object(base,'ROOT',root):
                base.initialize(path,c.budget(now=0));v=json.loads(path.read_text())
                # Already-completed demo dose is literal and cannot be reset by a focal role.
                v['worlds']['DEMO_PRIOR']={'cycles':1,'consumed':1564,'reserved':0,'role':'pilot','max_cycles':3,'validation_consumed':1564,'validation_cycles':1}
                v['consumed']=v['validation_consumed']=1564;base.write(path,v)
                old=json.loads(path.read_text());ledger=f.TickLedger(path,cfg['lifeId'],6,role='focal')
                ledger.register_lease(x,expected_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
                for mode,before,after in [('eci01-rbx01-decision',991187,991543),('eci01-rbx01-query-sensor',991543,991565),('eci01-rbx01-feedback',991565,992751)]:
                    oid='SYNTHETIC_'+mode.replace('-','_');ledger.begin(cfg['lifeId'],oid,mode);ledger.finish(cfg['lifeId'],oid,before,after,mode)
                result=ledger.read();self.assertEqual(result['worlds']['DEMO_PRIOR'],old['worlds']['DEMO_PRIOR'])
                self.assertEqual(result['consumed'],3128);self.assertEqual(result['worlds'][cfg['lifeId']]['cycles'],1)
                self.assertEqual(result['intents'],{});self.assertEqual(result['worlds'][cfg['lifeId']]['max_cycles'],6)
    def test_all_new_sources_parse(self):
        for p in HERE.glob('*.py'):ast.parse(p.read_text('utf8'),filename=str(p))
    def test_demo_profile_cannot_enter_focal_closed_guard(self):
        with self.assertRaises(ValueError):
            lease_module._closed(None,None,Path('never_opened'),{'profile':'DEMO'},{})

if __name__=='__main__':unittest.main(verbosity=2)
