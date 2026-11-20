"""Pure failure/continuation/guard fixtures; no Native or filesystem mutation."""
import copy,importlib.util,json
from pathlib import Path
import unittest
s=importlib.util.spec_from_file_location('recovery6pure',Path(__file__).with_name('recuperacion_tecnica_core_R06.py'));c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
class RecoveryTests(unittest.TestCase):
    def m(self):return dict(code_scope={'old':'scope'},phase='AWAIT_ROUTE_SENSOR',uncertain=True,cycles=0,last_sequence=56,
      failure={'type':'ValueError','tick':991543,'no_automatic_retry':True},pending={'question_released':True,'initial_observation':{'sensors':{'permissionStock':164}},'requests':[1,2]},policy={'unchanged':[1,-1]},log_count=3)
    def test_only_uncertainty_bit_changes(self):
        original=self.m();m=copy.deepcopy(original);m['code_scope']={'new':'scope'};entries={c.KEY:c.canonical(m),c.CODE:c.canonical(m['code_scope']),'ancestor':'exact'}
        after,w=c.repaired_entries(entries,original,m['code_scope']);actual=json.loads(after[c.KEY])
        self.assertFalse(actual['uncertain']);self.assertEqual(actual['pending'],m['pending']);self.assertEqual(actual['failure'],m['failure']);self.assertEqual(after['ancestor'],'exact')
    def test_wrong_tick_or_pending_rejected(self):
        original=self.m();m=copy.deepcopy(original);m['cycles']=1;entries={c.KEY:c.canonical(m),c.CODE:c.canonical(m['code_scope'])}
        with self.assertRaises(ValueError):c.repaired_entries(entries,original,m['code_scope'])
    def proof(self,number):
        ctx={'session_id':'s','operation_id':'Q1','sequence':57};obs={'sensors':{'permissionStock':164,'stationSignal':1},'seq':58}
        return dict(life='LOAD'+str(number),profile='LOAD'+str(number),q1={'kind':'decision','context':ctx,'result':{'action':'ASK_STATION','null':False,'nativeTick':991543}},
          failed_q2_intent={'kind':'query_sensor','context':{'session_id':'s','operation_id':'Q2_'+str(number)},'payload':{'observation':obs}},
          failed_q2_id='Q2_'+str(number),failed_official_sha256='a'*64,own_metadata_preserved_from_failed_snapshot=self.m())
    def test_environment_corrects_only_real_spent_permit(self):
        proof=self.proof(1);before=copy.deepcopy(proof);env=c.environment(proof)
        self.assertEqual(proof,before);self.assertEqual(env['permission_stock'],163);self.assertEqual(env['corrected_Q2_observation']['sensors']['stationSignal'],1)
        self.assertTrue(env['no_Q1_replay']);self.assertNotEqual(env['corrected_Q2_id'],env['failed_Q2_id'])
    def test_no_ASK_cannot_consume_a_permit(self):
        proof=self.proof(1);proof['q1']['result']['action']='SKIP_STATION'
        with self.assertRaises(ValueError):c.environment(proof)
    def test_ledger_archives_zero_without_releasing_reservation(self):
        proofs=[self.proof(i)for i in(1,2,3)];old=dict(limit=160000,consumed=10452,worlds={p['life']:{'consumed':356,'reserved':3740,'cycles':0}for p in proofs},
          intents={p['life']:{'id':p['failed_q2_id']}for p in proofs},last_completed={'id':'real_Q1'},cutoff_epoch=1794906420)
        before=copy.deepcopy(old);new,records=c.archive_ledger(old,proofs,'test')
        self.assertEqual(old,before);self.assertEqual(new['intents'],{});self.assertEqual(new['worlds'],old['worlds']);self.assertEqual(len(records),3);self.assertEqual(new['consumed'],10452)
    def test_unknown_intent_blocks_reconciliation(self):
        proofs=[self.proof(i)for i in(1,2,3)];old=dict(limit=160000,consumed=10452,intents={'unknown':{'id':'unknown'}})
        with self.assertRaises(ValueError):c.archive_ledger(old,proofs,'test')
if __name__=='__main__':unittest.main()
