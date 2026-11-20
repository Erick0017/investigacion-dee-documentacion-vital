"""Only AST-executed launcher transport mocks; never install or start DEE."""
import argparse,ast,hashlib,json
from pathlib import Path
from types import SimpleNamespace
import unittest

HERE=Path(__file__).resolve().parent
SOURCE=(HERE/'ARRANCAR_APD02_BASE_EXACTO.py').read_text(encoding='utf8')

def proposed(source):
    changes=[("p = subprocess.run(command, cwd=ROOT, text=True, encoding='utf8', capture_output=True)","p = subprocess.run(command, cwd=PYTHON.parent, text=True, encoding='utf8', capture_output=True)"),
             ("return subprocess.call(command, cwd=ROOT)","return subprocess.call(command, cwd=PYTHON.parent)"),
             ("    if args[0] == 'catalogo': show_catalog(); return 0","    if args[0] == 'catalogo': show_catalog(); return 0\n    if args[0] == 'usar':\n        return subprocess.call([str(PYTHON), '-I', '-B', '-X', 'utf8', str(SYSTEM / 'app/usar_dee.py'), '--raiz', str(ROOT), *args[1:]], cwd=PYTHON.parent)")]
    for old,new in changes:
        if source.count(old)!=1:raise ValueError('The selected launcher changed; no broad rewrite or silent merge')
        source=source.replace(old,new)
    return source

class LauncherN0(unittest.TestCase):
    def setUp(self):
        self.calls=[];self.root=Path('D:/MOCK_EXTRACTED_FULL/cognitive sistem');self.python=self.root/'motor/python313/python.exe'
        def run(args,**kw):self.calls.append(('run',args,kw));return SimpleNamespace(returncode=0,stdout='{"MOCK":true}',stderr='')
        def call(args,**kw):self.calls.append(('call',args,kw));return 7
        self.glob={'Path':Path,'ROOT':self.root,'SYSTEM':self.root/'sistema','PYTHON':self.python,'json':json,'subprocess':SimpleNamespace(run=run,call=call)}
        tree=ast.parse(proposed(SOURCE));functions=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))and n.name in('call','main')]
        exec(compile(ast.Module(body=functions,type_ignores=[]),'PROPOSED_LAUNCHER_AST_N0','exec'),self.glob)
    def test_capture_same_absolute_manager_arguments_short_cwd(self):
        result=self.glob['call'](['mente-unificada-estado','--vida','COPY'],capture=True)
        self.assertEqual(result,{'MOCK':True});kind,args,kw=self.calls[-1]
        self.assertEqual(kind,'run');self.assertEqual(kw['cwd'],self.python.parent)
        self.assertEqual(args,[str(self.python),'-I','-B','-X','utf8',str(self.root/'sistema/gestionar.py'),'mente-unificada-estado','--vida','COPY'])
    def test_noncapture_preserves_return_code(self):
        self.assertEqual(self.glob['call'](['version']),7)
        self.assertEqual(self.calls[-1][2]['cwd'],self.python.parent)
    def test_using_action_only_delegates_to_UI(self):
        prepared=[];self.glob.update(sys=SimpleNamespace(argv=['arrancar.py','usar','--vida','COPY'],stdout=SimpleNamespace(reconfigure=lambda **kw:None)),prepare=lambda:prepared.append(True))
        self.assertEqual(self.glob['main'](),7)
        _,args,kw=self.calls[-1]
        self.assertEqual(args,[str(self.python),'-I','-B','-X','utf8',str(self.root/'sistema/app/usar_dee.py'),'--raiz',str(self.root),'--vida','COPY'])
        self.assertEqual(kw['cwd'],self.python.parent);self.assertEqual(prepared,[True])
    def test_changed_base_requires_explicit_revision(self):
        with self.assertRaises(ValueError):proposed(SOURCE.replace('cwd=ROOT','cwd=OTHER'))
    def test_only_three_declared_edits(self):
        p=proposed(SOURCE)
        self.assertEqual(p.count("if args[0] == 'usar':"),1)
        self.assertIn('return service_asistente2(args[1:])',p)
        self.assertIn('return research_apd02(args[1:])',p)

def main():
    p=argparse.ArgumentParser();p.add_argument('--salida',type=Path,required=True);a=p.parse_args();suite=unittest.defaultTestLoader.loadTestsFromTestCase(LauncherN0);r=unittest.TextTestRunner(verbosity=2).run(suite)
    report={'schema':'APD03.minimal_launcher_diff.N0.v1','new_native_ticks':0,'native_processes':0,'Full_or_original_mutated':False,'tests':r.testsRun,'errors':len(r.errors),'failures':len(r.failures),'base_launcher_sha256':hashlib.sha256((HERE/'ARRANCAR_APD02_BASE_EXACTO.py').read_bytes()).hexdigest(),'proposed_launcher_text_sha256':hashlib.sha256(proposed(SOURCE).encode('utf8')).hexdigest(),'scope':'Only AST function transport mocks; no Native, update, installation or exact Full proof.'}
    with a.salida.open('x',encoding='utf8',newline='\n')as f:json.dump(report,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    raise SystemExit(0 if r.wasSuccessful()else 1)
if __name__=='__main__':main()
