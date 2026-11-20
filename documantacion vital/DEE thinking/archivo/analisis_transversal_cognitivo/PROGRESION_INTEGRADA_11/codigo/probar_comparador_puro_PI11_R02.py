"""Synthetic parser/canonicalization tests, not a Native reproduction."""
from pathlib import Path
import hashlib,importlib.util,json,struct,tempfile,unittest
H=Path(__file__).resolve().parent
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
c=module('PI11_pure_comparison',H/'comparar_reproduccion_PI11_R02.py')
PARSER=H.parents[3]/'DEE Cognitive 2.0/reproducibilidad/observador_pasivo.py'
p=module('PI11_pure_parser',PARSER)

def binary(raw=17,clock=21,phase='declared',tick=9):
    text=phase.encode('utf8')
    prefix=b'DEETSNP1'+struct.pack('<IIQ',2,1,tick)+bytes(17)+struct.pack('<I',len(text))+text+struct.pack('<Q',1)
    prefix+=struct.pack('<QQIII',raw,clock,0,0,0)+bytes(9)
    return prefix+struct.pack('<I',0)+bytes(8),hashlib.sha256(prefix).hexdigest()

class Comparison(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory(prefix='pure_compare_PI11_',dir=H.parent/'control');self.home=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def test_exact_native_prefix_coverage(self):
        data,digest=binary();path=self.home/'state.deetsnap';path.write_bytes(data)
        v,got=c.structure(path,p);self.assertEqual(got,digest);self.assertEqual(p.snapshot_view(path)['causal_prefix_sha256'],digest)
        self.assertEqual(v['N'],1);self.assertEqual(v['interfaces'],[]);self.assertEqual(v['receipts'],[])
    def test_RAW_clock_phase_are_never_normalized(self):
        src=self.home/'a';src.write_bytes(binary()[0]);s,sd=c.structure(src,p)
        for key,value in(('raw',18),('clock',22),('phase','other')):
            dst=self.home/('b_'+key);dst.write_bytes(binary(**{key:value})[0]);t,td=c.structure(dst,p)
            self.assertNotEqual(sd,td);self.assertTrue(c.diff(s,t))
    def test_numeric_zero_and_NULL_preserved(self):
        self.assertEqual(c.canonical({'choice':0},'LIFE'),{'choice':0})
        self.assertNotEqual(c.canonical({'choice':0},'LIFE'),c.canonical({'choice':None},'LIFE'))
    def test_only_current_worker_identity_path(self):
        value={'life_id':'LIFE','file':'D:/root/estado/servicios_locales/LIFE/folder/file.json','historical_life':'OLD'}
        v=c.canonical(value,'LIFE');self.assertEqual(v['life_id'],'__CURRENT_LIFE_ID__');self.assertEqual(v['historical_life'],'OLD')
        self.assertEqual(v['file'],'__CURRENT_WORKER_HOME__/folder/file.json')
    def test_Native_receipts_frames_remain_literal_even_identity_string(self):
        value={'requests':[{'receipt':{'detail':'LIFE'}}],'trace_observations':[{'tag':'LIFE'}],'physical_anchor':{'phase':'LIFE'}}
        self.assertEqual(c.canonical(value,'LIFE'),value)
    def test_verified_journal_chain_and_corruption(self):
        home=self.home/'journal';home.mkdir();line=b'{"kind":"synthetic","tick":7}\n';(home/'eventos.jsonl').write_bytes(line)
        chain=hashlib.sha256(bytes(32)+line).hexdigest();meta={'log_count':1,'log_chain_sha256':chain}
        self.assertEqual(c.journal(home,meta)[0],[{'kind':'synthetic','tick':7}])
        with self.assertRaises(ValueError):c.journal(home,{**meta,'log_chain_sha256':'0'*64})
    def test_ancestor_difference_visible(self):
        a={'paused_intervals':[[1,2]],'resources':7};b={'paused_intervals':[[1,1],[1,2]],'resources':8}
        self.assertIn('/resources',c.diff(a,b));a.pop('paused_intervals');b.pop('paused_intervals');self.assertNotEqual(a,b)

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Comparison))
    print(json.dumps({'pure':True,'Native_imported':False,'Native_ticks':0,'tests':result.testsRun,'errors':len(result.errors),'failures':len(result.failures)}))
    raise SystemExit(0 if result.wasSuccessful()else 1)
