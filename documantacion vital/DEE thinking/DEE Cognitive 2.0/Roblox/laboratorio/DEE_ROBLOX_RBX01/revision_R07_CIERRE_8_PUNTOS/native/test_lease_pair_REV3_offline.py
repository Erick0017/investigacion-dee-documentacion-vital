"""Synthetic current-pair binding fixtures. No Native/MCP/database calls."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('lease_pair_rev3_fixture',HERE/'migrar_lease_cerrada_v3_R05_REV3.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class PairTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.previous_root=module.ROOT;self.addCleanup(setattr,module,'ROOT',self.previous_root)
        module.ROOT=Path(self.temp.name);self.directory=module.ROOT/'evidencia/PAIR';self.directory.mkdir(parents=True)
        self.root=module.ROOT/'native/MAIN';self.root.mkdir(parents=True)
        self.main={'root':str(self.root),'life':'SYNTHETIC_MAIN','snapshot_sha256':'a'*64,'physical':{'tick':42}}
        values={'WORLD_CHECKPOINT.json':{'native_life_id':'SYNTHETIC_MAIN','native_tick':42},
          'CIERRE_BLOQUE_ORIGINAL.json':{'owner_closed':True,'final_tick':42,'identity':{'life':'SYNTHETIC_MAIN'}},
          'LEDGER_AL_CORTE.json':{'intents':{},'worlds':{'SYNTHETIC_MAIN':{'reserved':0}}}}
        self.members=[]
        for name,value in values.items():
            file=self.directory/name;raw=json.dumps(value).encode();file.write_bytes(raw)
            self.members.append({'file':name,'locator':str(file),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'storage_kind':'UNIQUE_PRESERVED_ANCHOR'})
        self.pair={'schema':'DEE.RBX07.ClosedPointOverlay.R05','native_source_root':str(self.root),
          'boundary':{'native_tick':42,'native_snapshot_sha256':'a'*64,'life_id':'SYNTHETIC_MAIN'},
          'storage_mode':'COMPLETE_FILE_LEVEL_CONTENT_OVERLAY','immutable_all_members':True,'members':self.members}
        self.write_pair()
    def write_pair(self):
        (self.directory/'PAREJA_INTEGRAL_V3.json').write_text(json.dumps(self.pair),encoding='utf8')
    def plan(self):
        return {'roots':[{'role':'MAIN','proof':self.main}],'main_pair_witness':module.main_pair_witness(self.directory,self.main)}
    def test_current_complete_pair_is_bound_without_rollback_claim(self):
        plan=self.plan();module.recheck_main_pair(plan)
        self.assertTrue(plan['main_pair_witness']['only_current_boundary_required_by_lease'])
        self.assertFalse(plan['main_pair_witness']['material_rollback_tested'])
    def test_manifest_changed_after_plan_rejected(self):
        plan=self.plan();self.pair['additional_note']='mutation';self.write_pair()
        with self.assertRaisesRegex(ValueError,'CHANGED_SINCE_PLAN'):module.recheck_main_pair(plan)
    def test_copied_anchor_corruption_rejected(self):
        plan=self.plan();(self.directory/'WORLD_CHECKPOINT.json').write_bytes(b'corrupt')
        with self.assertRaisesRegex(ValueError,'ANCHOR_BYTES'):module.recheck_main_pair(plan)
    def test_descriptor_only_is_explicitly_not_frozen_rollback(self):
        self.pair['storage_mode']='COMPLETE_CURRENT_ROOT_DESCRIPTOR_WITH_CRITICAL_MUTABLE_COPIES_ONLY';self.pair['immutable_all_members']=False;self.write_pair()
        value=module.main_pair_witness(self.directory,self.main)
        self.assertFalse(value['immutable_all_members_as_declared']);self.assertFalse(value['material_rollback_tested'])
    def test_false_immutable_claim_rejected(self):
        self.pair['immutable_all_members']=False;self.write_pair()
        with self.assertRaisesRegex(ValueError,'HONEST_PAIR_STORAGE_MODE'):self.plan()
    def test_wrong_native_cut_rejected(self):
        self.pair['boundary']['native_tick']=43;self.write_pair()
        with self.assertRaisesRegex(ValueError,'PRE_LEASE_MAIN_PAIR'):self.plan()

if __name__=='__main__':unittest.main()
