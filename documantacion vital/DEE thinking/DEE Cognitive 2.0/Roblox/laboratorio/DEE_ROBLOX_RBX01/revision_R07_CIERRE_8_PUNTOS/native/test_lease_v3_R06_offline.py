"""Pure fixtures: pending Q1 stays pending; budget and history never reset."""
from pathlib import Path
import copy,hashlib,importlib.util,json,unittest
P=Path(__file__).with_name('lease_core_v3_R06.py');s=importlib.util.spec_from_file_location('lease6pure',P);c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
class LeaseTests(unittest.TestCase):
    def scope(self):return dict(native_cutoff_utc_epoch=c.OLD_END,last_new_cycle_utc_epoch=c.OLD_LAST,life_id='TEST',code_scope_manifest_sha256='a'*64,
      sources_sha256={'rbx07_native_v3.py':'b'*64},feedback_arm='real',teacher_mode='paired',input_codec={'Q1':'products'},max_raw_support=10000,
      sensor_codec='products_v1',q2_sensor_codec='price_tag_v1',q2_sensor_arm='local_tag',source_tick=991187,source_snapshot_sha256='c'*64,max_cycles=3)
    def fixture(self,pending=True):
        old=self.scope();new=c.renew_scope(old,'d'*64,'e'*64);m=dict(code_scope=c.code_scope(old,'f'*64),cycles=0,last_sequence=56,session_id='s',
          phase='AWAIT_ROUTE_SENSOR'if pending else'IDLE',pending={'exact_Q1':'not edited','permissionStock':164}if pending else None,
          uncertain=pending,log_count=3,log_chain_sha256='1'*64,failure={'type':'ValueError','tick':991543},policy={'actual_history':[1,0,-1]})
        entries={c.KEY:c.canonical(m),c.CODE:c.canonical(m['code_scope']),'ancestor':'literal'}
        return old,new,m,entries
    def test_pending_all_fields_preserved_except_code(self):
        old,new,m,entries=self.fixture();proof=hashlib.sha256(c.canonical(m).encode()).hexdigest()
        actual,w=c.metadata_after(entries,old,'f'*64,new,'2'*64,0,known_pending_sha256=proof);after=json.loads(actual[c.KEY])
        self.assertEqual({k:v for k,v in after.items()if k!='code_scope'},{k:v for k,v in m.items()if k!='code_scope'})
        self.assertTrue(after['uncertain']);self.assertEqual(after['phase'],'AWAIT_ROUTE_SENSOR');self.assertTrue(w['technical_recovery_NOT_applied'])
    def test_pending_without_exact_witness_rejected(self):
        old,new,m,entries=self.fixture()
        with self.assertRaises(ValueError):c.metadata_after(entries,old,'f'*64,new,'2'*64,0)
    def test_wrong_pending_hash_rejected(self):
        old,new,m,entries=self.fixture()
        with self.assertRaises(ValueError):c.metadata_after(entries,old,'f'*64,new,'2'*64,0,known_pending_sha256='0'*64)
    def test_idle_preserves_actual_cycles(self):
        old,new,m,entries=self.fixture(False);m['cycles']=6;entries[c.KEY]=c.canonical(m)
        actual,_=c.metadata_after(entries,old,'f'*64,new,'2'*64,6)
        self.assertEqual(json.loads(actual[c.KEY])['cycles'],6)
    def test_ledger_preserves_intents_reservations_and_consumed(self):
        old=dict(limit=160000,max_worlds=6,last_new_episode_epoch=c.OLD_LAST,cutoff_epoch=c.OLD_END,consumed=10452,
          worlds={'load':{'reserved':3740,'consumed':356,'cycles':0}},intents={'load':{'id':'failed_Q2'}},last_completed={'id':'Q1'})
        before=copy.deepcopy(old);new=c.renew_ledger(old,'test')
        self.assertEqual(old,before)
        for key in('worlds','intents','consumed','last_completed','limit','max_worlds'):self.assertEqual(old[key],new[key])
        self.assertEqual(new['last_new_episode_epoch'],1794902400);self.assertEqual(new['cutoff_epoch'],1794906420)
    def test_absent_key_is_not_created(self):
        old=self.scope();new=c.renew_scope(old,'d'*64,'e'*64)
        actual,_=c.metadata_after({'ancestor':'literal'},old,'f'*64,new,'2'*64,0)
        self.assertEqual(actual,{'ancestor':'literal'})
if __name__=='__main__':unittest.main()
