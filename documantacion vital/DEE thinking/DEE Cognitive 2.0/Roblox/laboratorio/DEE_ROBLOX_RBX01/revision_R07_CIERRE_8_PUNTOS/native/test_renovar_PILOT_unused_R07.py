"""Pure fixture tests; no Native, filesystem state or SQLite access."""
import importlib.util,pathlib,unittest
p=pathlib.Path(__file__).with_name('renovar_PILOT_unused_R07.py');s=importlib.util.spec_from_file_location('pilot_lease_pure',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Lease(unittest.TestCase):
 def scope(self):return dict(life_id=m.LIFE,role='pilot',max_cycles=3,last_new_cycle_utc_epoch=m.OLD_LAST,native_cutoff_utc_epoch=m.OLD_END,sources_sha256={'rbx07_native_v3.py':'old','x':'same'},code_scope_manifest_sha256='old',cycles=0,seq=56,pending=None,flags={'retained':True})
 def ledger(self):return dict(limit=160000,max_worlds=6,intents={},consumed=17,last_new_episode_epoch=m.OLD_LAST,cutoff_epoch=m.OLD_END,worlds={'OLD':dict(consumed=17,cycles=18,reserved=0)},untouched={'history':['retained']})
 def test_scope_dates_only(self):
  old=self.scope();new=m.renew_scope(old,'new','freeze');self.assertEqual(old['flags'],new['flags']);self.assertEqual(new['seq'],56);self.assertEqual(new['sources_sha256']['x'],'same');self.assertEqual(old['native_cutoff_utc_epoch'],m.OLD_END)
 def test_used_role_rejected(self):
  x=self.scope();x['role']='main'
  with self.assertRaises(ValueError):m.renew_scope(x,'new','freeze')
 def test_wrong_old_lease_rejected(self):
  x=self.scope();x['last_new_cycle_utc_epoch']-=1
  with self.assertRaises(ValueError):m.renew_scope(x,'new','freeze')
 def test_accounting_literal(self):
  old=self.ledger();new=m.renew_ledger(old);self.assertEqual(old['worlds'],new['worlds']);self.assertEqual(old['untouched'],new['untouched']);self.assertEqual(old['consumed'],new['consumed']);self.assertEqual(new['last_new_episode_epoch'],m.NEW_LAST)
 def test_pending_rejected(self):
  x=self.ledger();x['intents']={'x':{'id':'old'}}
  with self.assertRaises(ValueError):m.renew_ledger(x)
 def test_used_pilot_rejected(self):
  x=self.ledger();x['worlds'][m.LIFE]={'cycles':1,'consumed':0,'reserved':0}
  with self.assertRaises(ValueError):m.renew_ledger(x)
 def test_actor_normalization(self):self.assertEqual(m.normalize('x='+str(m.OLD_END)),m.normalize('x='+str(m.NEW_END)))
if __name__=='__main__':unittest.main()
