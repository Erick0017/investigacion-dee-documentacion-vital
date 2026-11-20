"""AST-only proposed launcher/menu fixtures, no preparation/import/Native."""
import argparse,ast,difflib,hashlib,io,json
from contextlib import redirect_stdout,redirect_stderr
from pathlib import Path
from types import SimpleNamespace
import unittest
HERE=Path(__file__).resolve().parent
BASE=HERE/'ARRANCAR_APD02_BASE_EXACTO.py';CANDIDATE=HERE/'ARRANCAR_APD03_R02_PROPUESTO.py'

class LauncherR02Fixtures(unittest.TestCase):
    def setUp(self):
        self.calls=[];self.root=Path('D:/MOCK_EXTRACTED_FULL/cognitive sistem');self.python=self.root/'motor/python313/python.exe'
        def run(args,**kw):self.calls.append(('run',args,kw));return SimpleNamespace(returncode=0,stdout='{"MOCK":true}',stderr='')
        def call(args,**kw):self.calls.append(('call',args,kw));return 7
        self.glob={'Path':Path,'ROOT':self.root,'SYSTEM':self.root/'sistema','PYTHON':self.python,'json':json,'argparse':argparse,'subprocess':SimpleNamespace(run=run,call=call)}
        tree=ast.parse(CANDIDATE.read_text(encoding='utf8'));functions=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in('call','service_usar','menu','main')]
        exec(compile(ast.Module(body=functions,type_ignores=[]),'PROPOSED_APD03_LAUNCHER_R02_AST_N0','exec'),self.glob)
    def cli(self,*args):
        self.glob.update(sys=SimpleNamespace(argv=['arrancar.py',*args],stdout=SimpleNamespace(reconfigure=lambda **kw:None)),prepare=lambda:None)
        return self.glob['main']()
    def menu(self,answers):
        values=iter(answers);self.glob['input']=lambda prompt:next(values)
        output=io.StringIO()
        with redirect_stdout(output):result=self.glob['menu']()
        return result,output.getvalue()
    def test_cli_new_exact_ui_absolute_argv_short_cwd(self):
        self.assertEqual(self.cli('usar','--nueva','PERSONAL_1'),7)
        _,args,kw=self.calls[-1];self.assertEqual(args,[str(self.python),'-I','-B','-X','utf8',str(self.root/'sistema/app/usar_dee.py'),'--raiz',str(self.root),'--nueva','PERSONAL_1']);self.assertEqual(kw['cwd'],self.python.parent)
    def test_cli_existing_no_import_or_selection(self):
        self.assertEqual(self.cli('usar','--vida','PERSONAL_1'),7);self.assertEqual(self.calls[-1][1][-2:],['--vida','PERSONAL_1'])
    def test_explicit_mode_required_before_process(self):
        with redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):self.cli('usar')
        self.assertEqual(self.calls,[])
    def test_mutually_exclusive_identity_required(self):
        with redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):self.cli('usar','--nueva','A','--vida','B')
        self.assertEqual(self.calls,[])
    def test_invalid_identity_no_process_no_fallback(self):
        for name in('','../escape','has space','a'*92):
            with self.assertRaises(ValueError):self.glob['service_usar'](['--vida',name])
        self.assertEqual(self.calls,[])
    def test_no_root_override_via_cli(self):
        with redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):self.cli('usar','--vida','COPY','--raiz','OTHER')
        self.assertEqual(self.calls,[])
    def test_relative_operator_script_resolved_to_distribution_not_python_cwd(self):
        self.cli('usar','--vida','COPY','--sin-iniciar','--guion','trabajo_personal/test.json')
        args=self.calls[-1][1];self.assertIn('--sin-iniciar',args);self.assertEqual(args[-2:],['--guion',str((self.root/'trabajo_personal/test.json').resolve())])
    def test_menu_new_goes_through_same_service_and_preserves_error(self):
        result,text=self.menu(['1','nueva','COPY','0']);self.assertEqual(result,0);self.assertEqual(self.calls[-1][1][-2:],['--nueva','COPY']);self.assertIn('código 7',text);self.assertIn('no se reinicia',text)
    def test_menu_continue_is_explicit_no_auto_import(self):
        _,text=self.menu(['1','continuar','COPY','0']);self.assertEqual(self.calls[-1][1][-2:],['--vida','COPY']);self.assertIn('APD03',text)
    def test_menu_cancel_does_not_start_process(self):
        self.menu(['1','cancelar','0']);self.assertEqual(self.calls,[])
    def test_menu_bad_mode_or_empty_identity_no_process(self):
        _,text=self.menu(['1','auto','1','continuar','','0']);self.assertEqual(self.calls,[]);self.assertIn('ValueError',text)
    def test_old_research_and_asistente2_are_not_retargeted(self):
        got=[];self.glob['research_apd02']=lambda args:got.append(('APD02_research',args))or 11;self.glob['service_asistente2']=lambda args:got.append(('APD02_assistant',args))or 12
        self.assertEqual(self.cli('investigacion','HISTORICAL'),11);self.assertEqual(self.cli('asistente2','HISTORICAL','estado'),12);self.assertEqual(got,[('APD02_research',['HISTORICAL']),('APD02_assistant',['HISTORICAL','estado'])]);self.assertEqual(self.calls,[])
    def test_manager_capture_and_noncapture_short_cwd(self):
        self.assertEqual(self.glob['call'](['version'],True),{'MOCK':True});self.assertEqual(self.calls[-1][2]['cwd'],self.python.parent);self.assertEqual(self.glob['call'](['version']),7);self.assertEqual(self.calls[-1][2]['cwd'],self.python.parent)
    def test_only_four_functions_changed_no_policy_or_importer_rewrite(self):
        def functions(path):return{n.name:ast.dump(n,include_attributes=False)for n in ast.parse(path.read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef)}
        before,after=functions(BASE),functions(CANDIDATE);self.assertEqual(set(after)-set(before),{'service_usar'});self.assertEqual(set(before)-set(after),set())
        self.assertEqual({name for name in before if before[name]!=after[name]},{'call','menu','main'})
        self.assertIn("if args[0] == 'usar': return service_usar(args[1:])",CANDIDATE.read_text(encoding='utf8'))

def main():
    p=argparse.ArgumentParser();p.add_argument('--salida',required=True,type=Path);p.add_argument('--diff',required=True,type=Path);a=p.parse_args();suite=unittest.defaultTestLoader.loadTestsFromTestCase(LauncherR02Fixtures);r=unittest.TextTestRunner(verbosity=2).run(suite)
    diff=''.join(difflib.unified_diff(BASE.read_text(encoding='utf8').splitlines(keepends=True),CANDIDATE.read_text(encoding='utf8').splitlines(keepends=True),fromfile='a/actualizaciones/arrancar.py',tofile='b/actualizaciones/arrancar.py'))
    with a.diff.open('x',encoding='utf8',newline='\n')as f:f.write(diff)
    report={'schema':'APD03.launcher_menu_R02.N0_fixtures','tests':r.testsRun,'failures':len(r.failures),'errors':len(r.errors),'new_native_ticks':0,'Native_owners_started':0,'Full_or_S_changed':False,'sources':{path.name:{'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}for path in(BASE,CANDIDATE,Path(__file__))},'diff_sha256':hashlib.sha256(a.diff.read_bytes()).hexdigest(),'scope':'AST functions with mocked subprocess/input only; not a Full launch, GUI use or Native experiment.'}
    with a.salida.open('x',encoding='utf8',newline='\n')as f:json.dump(report,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
    return not r.wasSuccessful()
if __name__=='__main__':raise SystemExit(main())
