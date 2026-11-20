"""Synthetic first-start fixtures only. Does not start cmd, a UI or Native."""
import argparse,ast,difflib,hashlib,importlib.util,json,tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--salida',required=True,type=Path);a=p.parse_args()
    folder=Path(__file__).resolve().parents[1];old=folder/'verificar_full_apd03_exacto.py';new=folder/'verificar_full_apd03_exacto_r02.py'
    spec=importlib.util.spec_from_file_location('only_outer_N0',new);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    checks=[]
    def check(name,value):checks.append({'case':name,'ok':bool(value)})
    first={n.name:ast.dump(n)for n in ast.parse(old.read_text(encoding='utf8')).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
    second={n.name:ast.dump(n)for n in ast.parse(new.read_text(encoding='utf8')).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
    check('All original functions except explicitly changed main unchanged',all(second[k]==v for k,v in first.items()if k!='main'))
    check('Only two bootstrap helpers added',set(second)-set(first)=={'bootstrap','bootstrap_argv'})
    check('Literal first-start argv',m.bootstrap_argv()==['cmd.exe','/d','/c','INICIAR.bat','usar','--help'])
    for variant in('success','nonzero','preexisting_life','new_life','wrong_wheel','missing_help_flag'):
        with tempfile.TemporaryDirectory(prefix='full-bootstrap-N0-')as tmp:
            root=Path(tmp);personal=root/'trabajo_personal';personal.mkdir();(personal/'LEER.md').write_text('fixture',encoding='utf8')
            marker=root/'motor/python313/site-packages/INSTALACION_DEE.json';marker.parent.mkdir(parents=True)
            if variant=='preexisting_life':
                life=personal/'estado/vidas/FIXTURE/VIDA.json';life.parent.mkdir(parents=True);life.write_text('{}',encoding='utf8')
            calls=[]
            def pretend_run(argv,**kwargs):
                calls.append((argv,kwargs))
                marker.write_text(json.dumps({'wheel_sha256':'wrong'if variant=='wrong_wheel'else m.WHL_SHA}),encoding='utf8')
                if variant=='new_life':(personal/'VIDA.json').write_text('{}',encoding='utf8')
                return SimpleNamespace(returncode=1 if variant=='nonzero'else 0,stdout='--nueva --vida'if variant!='missing_help_flag'else'--nueva',stderr='')
            succeeded=False;evidence=None
            with patch.object(m.subprocess,'run',side_effect=pretend_run):
                try:evidence=m.bootstrap(root);succeeded=True
                except(ValueError,RuntimeError):pass
            check('Synthetic '+variant,succeeded==(variant=='success'))
            if variant=='success':
                check('Help does not claim Native ticks',evidence['new_native_execution']is False and evidence['no_personal_files_created_or_changed'])
                check('cmd uses exact extraction cwd and timeout',calls[0][1]['cwd']==root and calls[0][1]['timeout']==60)
            if variant=='preexisting_life':check('Existing life blocks before any cmd call',not calls)
    diff=''.join(difflib.unified_diff(old.read_text(encoding='utf8').splitlines(True),new.read_text(encoding='utf8').splitlines(True),fromfile=old.name,tofile=new.name))
    diffpath=a.salida.with_suffix('.diff');diffpath.write_text(diff,encoding='utf8',newline='\n')
    report={'schema':'APD03.Full.outer.R02.synthetic.N0','new_native_ticks':0,'new_processes':0,'synthetic_only':True,'checks':checks,'issues':[r['case']for r in checks if not r['ok']],'outer_R01_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'outer_R02_sha256':hashlib.sha256(new.read_bytes()).hexdigest(),'diff_file':str(diffpath),'diff_sha256':hashlib.sha256(diffpath.read_bytes()).hexdigest()}
    with a.salida.open('x',encoding='utf8',newline='\n')as f:json.dump(report,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps(report,ensure_ascii=False));return bool(report['issues'])
if __name__=='__main__':raise SystemExit(main())
