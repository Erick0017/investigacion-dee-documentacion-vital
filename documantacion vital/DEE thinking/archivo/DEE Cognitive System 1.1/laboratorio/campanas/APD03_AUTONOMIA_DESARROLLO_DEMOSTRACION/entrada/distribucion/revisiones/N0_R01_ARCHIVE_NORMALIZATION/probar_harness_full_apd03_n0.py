"""Pure fixtures for proposed Full proof. No archive Native execution."""
import argparse
import ast
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

HERE=Path(__file__).resolve().parent
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
INNER=load('full_inner_N0',HERE/'probar_full_apd03_entrada.py');OUTER=load('full_outer_N0',HERE/'verificar_full_apd03_exacto.py')
PROTOCOL=json.loads((HERE/'PROTOCOLO_FULL_APD03_R01_CANDIDATO.json').read_text(encoding='utf8'))

class HarnessN0(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='apd03-full-mocks-');self.root=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def test_script_fixed_before_full(self):
        s=INNER.goal_script(PROTOCOL)
        self.assertEqual([r for r in s['teach_goal']if r[0]=='ensenar-nueva'],[['ensenar-nueva','luma','-1','--revision','--retorno','omit']])
        self.assertIn(['objetivo','suma','24','5','--oculto','--contexto-ambiente','1','--retorno','real'],s['teach_goal'])
        self.assertEqual([r for r in s['teach_goal']if r[0]=='paso'],[['paso','4','--retorno','real']])
    def test_baseline_uses_new_luma_before_distinct_teacher(self):
        s=INNER.goal_script(PROTOCOL)
        self.assertIn(['lenguaje-nuevo','luma','24','gamma','--retorno','omit'],s['baseline'])
        self.assertFalse(any(r[0]=='ensenar-nueva'for r in s['baseline']))
        self.assertIn(['lenguaje-nuevo','luma','17','delta','--retorno','omit'],s['reopen'])
    def test_three_sessions_finish_and_same_life_reuses(self):
        s=INNER.goal_script(PROTOCOL)
        for rows in s.values():self.assertEqual(rows[-3:],[['guardar'],['detener'],['salir']])
        commands=[INNER.session_argv(self.root,'APD03_FULL_R01',self.root/'s.json',i==0)for i in range(3)]
        self.assertIn('--nueva',commands[0]);self.assertTrue(all('--vida'in x and'--nueva'not in x for x in commands[1:]))
    def test_no_retarged_teacher_from_baseline(self):
        bad=dict(PROTOCOL,new_luma_teacher=1)
        with self.assertRaises(ValueError):INNER.goal_script(bad)
    def test_candidate_refuses_any_native_calls(self):
        with patch.object(INNER,'load')as loader,patch.object(INNER.subprocess,'run')as run:
            with self.assertRaises(ValueError):INNER.run(self.root,PROTOCOL,self.root/'trabajo_personal/resultados/X')
        loader.assert_not_called();run.assert_not_called()
    def test_argv_paths_inside_extraction_absolute(self):
        args=OUTER.inner_argv(self.root,self.root/'trabajo_personal/p.json',self.root/'trabajo_personal/resultados/X')
        for i in(0,5,7,9,11):self.assertTrue(Path(args[i]).is_absolute()and Path(args[i]).is_relative_to(self.root))
        ui=INNER.session_argv(self.root,'X',self.root/'task.json',False)
        for i in(0,5,7,11):self.assertTrue(Path(ui[i]).is_absolute()and Path(ui[i]).is_relative_to(self.root))
    def test_native_sources_not_imported_by_harness(self):
        for name in('probar_full_apd03_entrada.py','verificar_full_apd03_exacto.py'):
            tree=ast.parse((HERE/name).read_text(encoding='utf8'));imports=[]
            for node in ast.walk(tree):
                if isinstance(node,ast.Import):imports.extend(n.name for n in node.names)
                elif isinstance(node,ast.ImportFrom):imports.append(node.module or'')
            self.assertFalse(any(x.split('.')[0]in('dee_thinking','numpy','app','capacidades')for x in imports))
    def test_archive_plain_valid(self):
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w')as z:z.writestr('cognitive sistem/a.txt','A')
        with zipfile.ZipFile(io.BytesIO(b.getvalue()))as z:self.assertEqual(OUTER.archive_inventory(z),['cognitive sistem/a.txt'])
    def test_archive_traversal_and_wrong_roots_rejected(self):
        for name in('../escape','cognitive sistem/../escape','D:/other','other/a','cognitive sistem\\bad'):
            b=io.BytesIO()
            with zipfile.ZipFile(b,'w')as z:z.writestr(name,'A')
            with zipfile.ZipFile(io.BytesIO(b.getvalue()))as z:
                with self.assertRaises(ValueError,msg=name):OUTER.archive_inventory(z)
    def test_archive_windows_case_collision_rejected(self):
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w')as z:z.writestr('cognitive sistem/a.txt','A');z.writestr('cognitive sistem/A.TXT','B')
        with zipfile.ZipFile(io.BytesIO(b.getvalue()))as z:
            with self.assertRaises(ValueError):OUTER.archive_inventory(z)
    def test_archive_symlink_rejected(self):
        b=io.BytesIO();info=zipfile.ZipInfo('cognitive sistem/symlink');info.external_attr=0o120777<<16
        with zipfile.ZipFile(b,'w')as z:z.writestr(info,'target')
        with zipfile.ZipFile(io.BytesIO(b.getvalue()))as z:
            with self.assertRaises(ValueError):OUTER.archive_inventory(z)
    def test_manifest_checks_exact_bytes(self):
        (self.root/'actualizaciones').mkdir();(self.root/'sample.txt').write_bytes(b'actual')
        m={'members':{'sample.txt':{'bytes':6,'sha256':hashlib.sha256(b'actual').hexdigest()}},'release':'MOCK','source_campaign':'MOCK'}
        (self.root/'actualizaciones/ARCHIVOS_GESTIONADOS.json').write_text(json.dumps(m),encoding='utf8')
        self.assertEqual(OUTER.validate_manifest(self.root)['members_verified'],1)
        (self.root/'sample.txt').write_bytes(b'other!')
        with self.assertRaises(ValueError):OUTER.validate_manifest(self.root)
    def test_decodes_common32_native_gate_without_truth_label(self):
        expected={INNER.pos(o,v,4,s):s for o,v in INNER.CODEC.values()for s in(-1,1)}
        selected=INNER.pos(INNER.K,(-1,0,0),4,-1)
        panel=[]
        for site,s in expected.items():
            raw=(1|(1<<60)|(7<<32)|((s&15)<<56))if site==selected else 0
            panel.append({'site':list(site),'raw':str(raw)})
        self.assertEqual(INNER.sign({'panel':panel}),-1)
        for o in panel:o['raw']='0'
        self.assertIsNone(INNER.sign({'panel':panel}))
    def test_action_zero_is_active_query_not_silence(self):
        obs=[]
        for x in(-1,0,1):
            raw=(1|(1<<60)|(5<<32)|(1<<52))if x==0 else 0
            obs.append({'site':[25+2*x,15,53],'raw':str(raw)})
        self.assertEqual(INNER.action_sign({'observations':obs}),0)
        for o in obs:o['raw']='0'
        self.assertIsNone(INNER.action_sign({'observations':obs}))
    def test_windows_short_cwd_is_explicit_in_both_helpers(self):
        for name in('probar_full_apd03_entrada.py','verificar_full_apd03_exacto.py'):
            code=(HERE/name).read_text(encoding='utf8')
            self.assertIn('cwd=python.parent',code)
            self.assertNotIn('cwd=root',code)

def main():
    p=argparse.ArgumentParser();p.add_argument('--salida',type=Path,required=True);a=p.parse_args();suite=unittest.defaultTestLoader.loadTestsFromTestCase(HarnessN0);r=unittest.TextTestRunner(verbosity=2).run(suite)
    report={'schema':'APD03.Full.proof_harness.N0_fixtures.v1','new_native_ticks':0,'native_jobs_started':0,'tests':r.testsRun,'failures':len(r.failures),'errors':len(r.errors),'scope':'Pure mocked transport/decoding/archive fixtures, not an exact Full Native proof.','sources':{n:{'bytes':(HERE/n).stat().st_size,'sha256':hashlib.sha256((HERE/n).read_bytes()).hexdigest()}for n in('probar_full_apd03_entrada.py','verificar_full_apd03_exacto.py','probar_harness_full_apd03_n0.py','PROTOCOLO_FULL_APD03_R01_CANDIDATO.json')}}
    with a.salida.open('x',encoding='utf8',newline='\n')as f:json.dump(report,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    raise SystemExit(0 if r.wasSuccessful()else 1)
if __name__=='__main__':main()
