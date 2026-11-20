"""Non-editable clean installation and byte identity. No scientific evolution."""
import argparse,hashlib,json,os,sys,zipfile
from pathlib import Path
def child(wheel,out):
    import dee_thinking as d
    import dee_thinking._native as native
    wheel=Path(wheel);package=Path(d.__file__).parent
    assert d.__version__=='4.0.0' and d.build_info()['kernel_version']==27
    assert package.is_relative_to(Path(sys.prefix)) and 'site-packages' in str(package)
    matched=[]
    with zipfile.ZipFile(wheel) as z:
        assert z.testzip() is None
        for name in z.namelist():
            if name.startswith('dee_thinking/') and not name.endswith('/'):
                rel=Path(name).relative_to('dee_thinking');p=package/rel
                assert p.is_file() and p.read_bytes()==z.read(name),name
                matched.append(name)
    forbidden=[x for x in sys.modules if x.startswith(('dee_universe_v27','core.entity','core.central_comparison','core.comparison_entity','core.revisable_selection','core.policy_session','habitat.','lenguaje.','src.core','src.habitat','src.lenguaje'))]
    assert not forbidden,forbidden
    report={'version':d.__version__,'kernel':27,'python_executable':sys.executable,'module_path':d.__file__,'native_path':native.__file__,'wheel_sha256':hashlib.sha256(wheel.read_bytes()).hexdigest(),'native_sha256':hashlib.sha256(Path(native.__file__).read_bytes()).hexdigest(),'wheel_package_files_identical':matched,'no_hidden_lab_imports':True,'build_info':d.build_info()}
    Path(out).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False));return 0
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path);p.add_argument('--venv',type=Path);p.add_argument('--child',action='store_true');p.add_argument('--wheel');p.add_argument('--out');a=p.parse_args()
    if a.child:return child(a.wheel,a.out)
    sys.path.insert(0,str(a.root));from supervise40 import run,put
    rows=[];out=a.root/'validation/resumption_install';out.mkdir(exist_ok=True)
    if not a.venv.exists():rows.append(run(a.root,'resume_create_clean_venv',[sys.executable,'-I','-m','venv',str(a.venv)],180,str(a.venv.parent)))
    py=a.venv/'Scripts/python.exe';wheel=a.root/'wheel/dee_thinking-4.0.0-cp313-cp313-win_amd64.whl'
    rows.append(run(a.root,'resume_install_wheel',[str(py),'-I','-m','pip','install','--no-index',str(wheel)],120,str(a.venv.parent)))
    rows.append(run(a.root,'resume_install_identity',[str(py),'-I',__file__,'--child','--wheel',str(wheel),'--out',str(out/'IDENTITY.json')],120,str(a.venv.parent)))
    put(out/'COMMANDS.json',rows);return int(any(r['exit_code'] for r in rows))
if __name__=='__main__':raise SystemExit(main())
