from pathlib import Path
import ast,importlib.util,json,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
def load(p,name):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
class Tests(unittest.TestCase):
    def test_one_batch_three_owners(self):
        p=json.loads((ROOT/'load/PROTOCOLO_CARGA_V3_R01.json').read_text('utf8'))
        self.assertEqual(p['stages'],[{'simultaneous_lives':['LOAD1','LOAD2','LOAD3']}])
        self.assertEqual(len({x['id']for x in p['lifes'].values()}),3)
        self.assertEqual(p['episodes_per_life'],3);self.assertEqual(p['parent_tick'],991187)
        self.assertLess(p['latest_batch_start_epoch'],p['latest_GO_epoch']);self.assertLess(p['latest_GO_epoch'],p['last_new_episode_epoch'])
    def test_frozen_base_and_no_reset(self):
        s=(ROOT/'load/worker_carga_v3.py').read_text('utf8');ast.parse(s)
        for value in('sequence=56','native_tick=991187',"scope['max_cycles']==3",'permissionStock=164','ACTUAL_NUMERIC_INPUT_UNAVAILABLE'):
            self.assertIn(value,s)
        self.assertNotIn('actual_a or 0',s)
        self.assertNotIn('953651',s)
    def test_pure_import(self):
        before=set(sys.modules)
        for n in('worker_carga_v3','ejecutar_carga3_v3','recalcular_concurrencia_v3'):load(ROOT/'load'/(n+'.py'),'_fixture_'+n)
        self.assertFalse(any(x.startswith(('dee_thinking','rbx07_native'))for x in set(sys.modules)-before))
    def test_overlap_math(self):
        m=load(ROOT/'load/recalcular_concurrencia_v3.py','_fixture_overlap')
        self.assertEqual(m.intersect([(0,4)],[(2,7)]),[(2,4)])
        self.assertEqual(m.intersect(m.intersect([(0,4)],[(2,7)]),[(3,8)]),[(3,4)])
    def test_closed_portable_fixture(self):
        m=load(ROOT/'load/recalcular_concurrencia_v3.py','_fixture_closed_overlap')
        with tempfile.TemporaryDirectory(prefix='r07_closed_fixture_')as temp:
            root=Path(temp);paths=[]
            for n in range(3):
                d=root/str(n);d.mkdir();paths.append(d)
                result={'closed':True,'pending_global_intent':None,'life':'L'+str(n),'profile':'LOAD'+str(n+1),'owner_pid':10+n,
                  'results':[{'tool':None,'public_tool_result':None}for _ in range(3)]}
                (d/'RESULTADO.json').write_text(json.dumps(result),encoding='utf8')
                ctx={'operation_id':'OP'+str(n)}
                rows=[{'event':'INTENT','context':ctx,'utc':'2026-11-16T17:00:00Z'},
                  {'event':'COMPLETED','context':ctx,'utc':'2026-11-16T17:00:02Z','kind':'decision','elapsed_seconds':2,'result':{'action':'SAFE_WAIT','null':True}}]
                (d/'FASES.jsonl').write_text(''.join(json.dumps(x)+'\n'for x in rows),encoding='utf8')
            got=m.run(paths,root/'OUT.json');self.assertEqual(got['common_material_call_overlap_seconds'],2)
            self.assertTrue(got['three_complete_episodes_each']);self.assertEqual(got['Native_calls'],0)
if __name__=='__main__':unittest.main()
