"""Isolated installed-wheel unittest modules, each with owned timeout."""
import argparse,hashlib,json,os,re,subprocess,sys,time
from pathlib import Path
def child(path,out):
    import importlib.util,unittest,dee_thinking as dt
    assert dt.__version__=='4.0.0' and 'site-packages' in dt.__file__
    before=set(sys.modules)
    spec=importlib.util.spec_from_file_location('test_installed_dee4',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(m))
    row={'module':str(path),'run':result.testsRun,'failures':[(str(t),s) for t,s in result.failures],'errors':[(str(t),s) for t,s in result.errors],'skipped':[(str(t),s) for t,s in result.skipped],'success':result.wasSuccessful(),'installed_module':dt.__file__,'version':dt.__version__,'hidden_lab_imports':[x for x in set(sys.modules)-before if x.startswith(('src.core','src.habitat','src.lenguaje','dee_universe_v27'))]}
    Path(out).write_text(json.dumps(row,indent=2),encoding='utf-8');return 0 if result.wasSuccessful() and not row['hidden_lab_imports'] else 1
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path);p.add_argument('--python');p.add_argument('--child',type=Path);p.add_argument('--out',type=Path);p.add_argument('--attempt',default='01');p.add_argument('--only',nargs='*');a=p.parse_args()
    if a.child:return child(a.child,a.out)
    sys.path.insert(0,str(a.root));from supervise40 import run,put
    target=a.root/('validation/python_'+a.attempt);target.mkdir(exist_ok=True)
    names=['test_cognitive_api.py','test_informative4.py','test_cognition_facilitators.py','test_wheel_api.py','test_basal_api.py','test_integrated_protocols.py','test_organizational_api.py','test_mbp4_regressions.py']
    if a.only:names=a.only
    rows=[]
    for name in names:
        dest=target/(Path(name).stem+'.json');job=run(a.root,'python_'+a.attempt+'_'+Path(name).stem,[a.python,'-I',__file__,'--child',str(a.root/'source/tests/python'/name),'--out',str(dest)],1200 if name=='test_integrated_protocols.py' else 600,cwd=str(target))
        rows.append({'name':name,'job':job,'result':json.loads(dest.read_text()) if dest.exists() else None});put(target/'SUITE.json',rows)
    return int(any(x['job']['exit_code']!=0 for x in rows))
if __name__=='__main__':raise SystemExit(main())
