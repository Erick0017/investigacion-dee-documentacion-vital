"""Actual installation/use from a fresh extraction. No old runtime fallback."""
import argparse,hashlib,importlib.util,json,shutil,subprocess,sys,tempfile,zipfile
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def load(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def main():
    p=argparse.ArgumentParser();p.add_argument('--archive',type=Path,required=True);p.add_argument('--work',type=Path);a=p.parse_args()
    sys.path.insert(0,str(ROOT));from supervise40 import run
    work=a.work or Path(tempfile.mkdtemp(prefix='dt40-final-clean-'));work.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(a.archive) as z:
        assert z.testzip() is None
        assert all(n.startswith('DEE_thinking_4_0_0/') and '..' not in Path(n).parts for n in z.namelist());z.extractall(work)
    package=work/'DEE_thinking_4_0_0';verifier=load('extracted_manifest_verifier',package/'tools/verify40.py');container=verifier.verify(package)
    out=ROOT/'validation/final_extraction';out.mkdir(exist_ok=True);rows=[];venv=work/'venv';cwd=work/'outside_source';cwd.mkdir(exist_ok=True)
    def execute(name,argv,timeout=180):
        r=run(ROOT,'final_extract_'+name,[str(x) for x in argv],timeout,str(cwd));rows.append(r);put(out/'COMMANDS.json',rows);assert r['exit_code']==0,r;return r
    execute('venv',[sys.executable,'-I','-m','venv',venv],180);py=venv/'Scripts/python.exe';wheel=package/'wheel/dee_thinking-4.0.0-cp313-cp313-win_amd64.whl'
    execute('install',[py,'-I','-m','pip','install','--no-index',wheel],120)
    execute('smoke',[py,'-I','-B',package/'validation/release_smoke40.py','--wheel',wheel,'--out',out/'SMOKE.json'],180)
    execute('reproduce',[py,'-I','-B',package/'tools/reproduce40.py','--root',package,'--case','online_contact_main','--output',work/'reproduced_online'],180)
    reproduction=read(work/'reproduced_online/REPRODUCTION_CHECK.json');shutil.copy2(work/'reproduced_online/REPRODUCTION_CHECK.json',out/'REPRODUCTION_CHECK.json')
    # Exercise the shipped launcher, not just a Python facade.
    execute('native_launcher',['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',package/'iniciar_mente.ps1','-Perfil','mundo_nativo','-Python',py,'-Eventos',package/'app/ejemplos/mundo_nativo_principal.txt','-Sesion',work/'native_session'],180)
    transcript=cwd/'MUNDO_DIALOGOS.jsonl';shutil.copy2(transcript,out/'NATIVE_MAIN_DIALOGOS.jsonl');transcript.unlink()
    dialogue=[json.loads(x) for x in (out/'NATIVE_MAIN_DIALOGOS.jsonl').read_text(encoding='utf-8').splitlines()]
    assert dialogue and all('error' not in x['response'] for x in dialogue)
    values=[x['response']['physical_output']['s_reg'] for x in dialogue if x['input']=='Observa respuesta'];assert values==[54,73],values
    execute('native_other_process_load',['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',package/'iniciar_mente.ps1','-Perfil','mundo_nativo','-Python',py,'-Cargar',work/'native_session/pendiente16.deetsnap','-Eventos',package/'app/ejemplos/mundo_nativo_continuar.txt','-Sesion',work/'restored_session'],180)
    shutil.copy2(cwd/'MUNDO_DIALOGOS.jsonl',out/'NATIVE_RESTORED_DIALOGOS.jsonl')
    continued=[json.loads(x) for x in (out/'NATIVE_RESTORED_DIALOGOS.jsonl').read_text(encoding='utf-8').splitlines()];assert all('error' not in x['response'] for x in continued)
    actual=[x['response']['physical_output']['s_reg'] for x in continued if x['input']=='Observa respuesta'];assert actual==[73],actual
    execute('external_cpp',['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',package/'tools/build40.ps1','-SourcePath',package/'source','-BuildRoot',work/'cpp_consumer','-ProductRoot',package,'-Stage','consumer','-ConsumerSource',package/'validation/consumer'],240)
    cache=(work/'cpp_consumer/consumer/CMakeCache.txt').read_text(encoding='utf-8');assert str(package/'install_cpp').replace('\\','/') in cache
    smoke=read(out/'SMOKE.json');assert smoke['identity']['wheel_sha256']==container['wheel_sha256']
    result={'all_commands_succeeded':True,'archive_tested_sha256':hashlib.sha256(a.archive.read_bytes()).hexdigest(),'package':str(package),'container':container,'installed_wheel_sha256':container['wheel_sha256'],'installed_module':smoke['module'],'trajectory_reproduction_equal':all(reproduction['physical_comparison'].values()),'native_app_pending_restore_continue':True,'native_main_values':values,'native_restored_values':actual,'shipped_launcher_exercised':True,'external_cpp_consumer_from_extracted_install':True,'no_hidden_lab_imports':smoke['no_hidden_lab_imports'],'new_reserved_query':smoke['new_reserved_question'],'commands':rows,'generated_utc':datetime.now(timezone.utc).isoformat(),'scope':'clean extraction of final code/payload candidate; later package metadata may add this verification record without changing code, wheel, install or data'}
    put(ROOT/'validation/FINAL_EXTRACTION_CHECK.json',result);print(json.dumps({k:result[k] for k in ('all_commands_succeeded','installed_wheel_sha256','trajectory_reproduction_equal','native_app_pending_restore_continue')},indent=2))
if __name__=='__main__':main()
