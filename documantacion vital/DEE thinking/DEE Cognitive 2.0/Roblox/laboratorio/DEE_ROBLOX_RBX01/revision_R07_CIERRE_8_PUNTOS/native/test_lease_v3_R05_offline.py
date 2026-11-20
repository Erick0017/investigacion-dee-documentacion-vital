"""Synthetic metadata/ledger only; no Native, process, DB or owner."""
from pathlib import Path
import ast,copy,importlib.util,json,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
def load(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
C=load(ROOT/'native/lease_core_v3_R05.py','_fixture_lease_core')
class Tests(unittest.TestCase):
    def scope(self):
        return {'life_id':'X','native_cutoff_utc_epoch':C.OLD_END,'last_new_cycle_utc_epoch':C.OLD_LAST,
          'code_scope_manifest_sha256':'a'*64,'sources_sha256':{'rbx07_native_v3.py':'b'*64},'feedback_arm':'real','teacher_mode':'paired',
          'input_codec':{'original':'unchanged'},'max_raw_support':10000,'sensor_codec':'products_v1','q2_sensor_codec':'price_tag_v1','q2_sensor_arm':'local_tag',
          'source_tick':991187,'source_snapshot_sha256':'c'*64,'max_cycles':24,'native_start_utc_epoch':1794841620}
    def entries(self,c):
        code=C.code_scope(c,'d'*64)
        m={'version':'DEE.RBX01.async_native.INTEGRAL.V3.R01','code_scope':code,'phase':'IDLE','pending':None,'uncertain':False,'cycles':6,
          'last_sequence':68,'session_id':'SAME_SID','log_count':40,'log_chain_sha256':'e'*64,'policy_fixture':{'actual':0,'missing':None}}
        return {C.KEY:C.canonical(m),C.CODE:C.canonical(code),'ANCESTOR_KEY':'literal acquired history'}
    def test_only_own_witness_changes(self):
        old=self.scope();new=C.renew_scope(old,'f'*64,'0'*64);entries=self.entries(old)
        got,w=C.metadata_after(entries,old,'d'*64,new,'1'*64,6)
        a=json.loads(entries[C.KEY]);b=json.loads(got[C.KEY]);a.pop('code_scope');b.pop('code_scope')
        self.assertEqual(a,b);self.assertEqual(got['ANCESTOR_KEY'],entries['ANCESTOR_KEY']);self.assertEqual(w['session_id'],'SAME_SID')
        self.assertEqual(new['max_cycles'],old['max_cycles']);self.assertEqual(new['native_start_utc_epoch'],1794841620)
    def test_pending_and_wrong_count_rejected(self):
        old=self.scope();new=C.renew_scope(old,'f'*64,'0'*64)
        for pending in(True,False):
            entries=self.entries(old)
            if pending:
                m=json.loads(entries[C.KEY]);m['pending']={'actual':'unresolved'};entries[C.KEY]=C.canonical(m)
            with self.assertRaises(ValueError):C.metadata_after(entries,old,'d'*64,new,'1'*64,5 if not pending else 6)
    def test_untouched_key_not_invented(self):
        old=self.scope();new=C.renew_scope(old,'f'*64,'0'*64);entries={'ANCESTOR_KEY':'unchanged'}
        got,w=C.metadata_after(entries,old,'d'*64,new,'1'*64,0);self.assertEqual(got,entries);self.assertFalse(w['Native_metadata_changed'])
    def test_ledger_accounting_exact(self):
        old={'schema':'x','limit':160000,'max_worlds':6,'consumed':9384,'worlds':{'M':{'consumed':9384,'reserved':0,'cycles':6,'max_cycles':24}},'intents':{},
          'last_new_episode_epoch':C.OLD_LAST,'cutoff_epoch':C.OLD_END,'last_completed':{'id':'REAL_ID'}}
        got=C.renew_ledger(old,'test');self.assertEqual(got['consumed'],9384);self.assertEqual(got['worlds'],old['worlds']);self.assertEqual(got['last_completed'],old['last_completed'])
        old['worlds']['M']['reserved']=1
        with self.assertRaises(ValueError):C.renew_ledger(old,'test')
    def test_actor_only_dates_and_labels(self):
        old=(ROOT/'native/bundle/rbx07_native_v3.py').read_text('utf8');new=(ROOT/'native/lease_R05_bundle/rbx07_native_v3.py').read_text('utf8')
        new=new.replace(str(C.NEW_LAST),str(C.OLD_LAST)).replace(str(C.NEW_END),str(C.OLD_END)).replace('cutoff03:07UTCNov17','cutoff04:13UTCNov16').replace('Q1 after02:00UTCNov17','Q1 after03:10UTCNov16')
        self.assertEqual(ast.dump(ast.parse(old)),ast.dump(ast.parse(new)))
        for name in('rbx07_identity_v3.py','rbx07_funciones_v3.py'):
            self.assertEqual((ROOT/'native/bundle'/name).read_bytes(),(ROOT/'native/lease_R05_bundle'/name).read_bytes())
    def test_pure_import_new_support(self):
        before=set(sys.modules)
        for name in('owner_support_v3_R05','ledger_v3_R05','migrar_lease_cerrada_v3_R05'):load(ROOT/'native'/(name+'.py'),'_fixture_'+name)
        self.assertFalse(any(n.startswith(('dee_thinking','app.mundo','app.lives'))for n in set(sys.modules)-before))
    def test_no_material_calls_in_native_child(self):
        t=ast.parse((ROOT/'native/migrar_lease_cerrada_v3_R05.py').read_text('utf8'))
        f=next(n for n in t.body if isinstance(n,ast.FunctionDef)and n.name=='native_child')
        names=[n.func.attr for n in ast.walk(f)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)]
        self.assertFalse(set(names)&{'run_until','advance','step','request','execute','control'})
        self.assertIn('commit',names)
if __name__=='__main__':unittest.main()
