"""Synthetic bounded ZIP only; never packages the actual experiment."""
from pathlib import Path
import hashlib,importlib.util,json,sys,tempfile,unittest,zipfile
ROOT=Path(__file__).resolve().parents[1]
def module():
    s=importlib.util.spec_from_file_location('_r07_pack_fixture',ROOT/'control/expediente_compacto_v3.py');m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m
class Test(unittest.TestCase):
    def test_explicit_names_clean_extract_and_hash(self):
        m=module()
        with tempfile.TemporaryDirectory(prefix='r07_zip_fixture_')as t:
            root=Path(t)/'revision_R07_CIERRE_8_PUNTOS';root.mkdir();m.HERE=root
            (root/'control').mkdir();files=[]
            for n in range(11):
                p=root/'control'/('p'+str(n)+'.txt');p.write_text('critical fixture '+str(n),encoding='utf8');raw=p.read_bytes()
                files.append({'role':'synthetic','path':str(p),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
            (root/'control/CRITICOS_ANTES_R07.json').write_text(json.dumps({'files':files}),encoding='utf8')
            src=root/'control/code.py';src.write_text('value = 1\n',encoding='utf8')
            plan={'schema':'DEE.INTEGRAL.V3.explicit_export_plan.R01','files':[{'source':str(src),'archive':'control/code.py','role':'code'}]}
            p=root/'plan.json';p.write_text(json.dumps(plan),encoding='utf8');frozen=root/'frozen.json';m.freeze(p,frozen)
            v=json.loads(frozen.read_text('utf8'));v['finalized']=True;frozen.write_text(json.dumps(v),encoding='utf8')
            out=root/'fixture.zip';m.build(frozen,out);r=m.verify(out,root/'CLEAN_EXTRACT')
            self.assertLess(out.stat().st_size,15000000)
            with zipfile.ZipFile(out)as z:self.assertIn('CONTROL/MANIFIESTO_SHA256.json',z.namelist())
            self.assertTrue((root/'CLEAN_EXTRACT/control/code.py').is_file())
    def test_reject_path_and_secret(self):
        m=module()
        for name in('../escape.json','D:/escape.json','safe/../escape.json'):
            with self.assertRaises(ValueError):m.archive_name(name)
        with self.assertRaises(ValueError):m.secret_values({'authorization':'secret fixture'})
    def test_empty_native_or_model_file_forbidden(self):
        m=module()
        for name in('snapshot.gz','queue.sqlite3','weights.gguf','motor/code.py'):
            with self.assertRaises(ValueError):m.archive_name(name)
if __name__=='__main__':unittest.main()
