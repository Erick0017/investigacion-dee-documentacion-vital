"""Build-independent extraction, offline installation and live public checks.

Coordinator only: it does not implement actor physics or read a response table
to answer a participant. Each subprocess has an owned Windows Job and timeout.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,shutil,sys,time,zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from campaign import put,sha
from supervision import run,remaining

def execute(name,argv,cwd,timeout):
    result=run(ROOT,name,[str(x) for x in argv],timeout,cwd=str(cwd))
    if result['exit_code']!=0:raise RuntimeError('Clean check failed: '+name+'; inspect jobs/'+name)
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--directory',type=Path,required=True);p.add_argument('--resume',action='store_true');a=p.parse_args()
    start=time.monotonic();work=a.directory.resolve();work.mkdir(parents=True,exist_ok=a.resume)
    candidate=a.candidate.resolve();digest=sha(candidate);extracted=work/'extracted'
    prior=None;section='CPC4/ampliaciones/'+ROOT.name+'/'
    if a.resume:
        previous=extracted/section
        prior_manifest=json.loads((previous/'MANIFEST.json').read_text(encoding='utf-8'))
        with zipfile.ZipFile(candidate) as z:new_manifest=json.loads(z.read(section+'MANIFEST.json'))
        def code_rows(manifest):
            return {r['path']:r['sha256'] for r in manifest['files'] if Path(r['path']).suffix in ('.py','.ps1') or Path(r['path']).parent.name=='configuraciones'}
        old_code,new_code=code_rows(prior_manifest),code_rows(new_manifest)
        for name,h in old_code.items():
            if sha(previous/name)!=h:raise RuntimeError('Previous extracted code/config was changed: '+name)
        changed={name for name in set(old_code)|set(new_code) if old_code.get(name)!=new_code.get(name)}
        allowed={'iniciar_cpc4.ps1','src/clean_reproduction.py'}
        if not changed<=allowed:raise RuntimeError('Cannot reuse native prechecks after actor/test/config change: '+repr(sorted(changed)))
        prior={'changed_code':sorted(changed),'native_precheck_reused_only_after_byte_identity':True,
               'prior_candidate':json.loads((ROOT/'jobs/publication_candidate01/stdout.log').read_text(encoding='utf-8')),
               'native_report':json.loads((work/'evidence/native/CLEAN_REPRODUCTION.json').read_text(encoding='utf-8'))}
        attempt=ROOT/'resultados/reproduccion_intentos/INTENTO01';attempt.mkdir(parents=True,exist_ok=True)
        for name in allowed:
            shutil.copyfile(previous/name,attempt/(name.replace('/','__')+'.txt'))
        shutil.copyfile(previous/'MANIFEST.json',attempt/'EXTRACTED_MANIFEST_01.json')
        put(attempt/'REUSE_DECISION.json',prior)
    with zipfile.ZipFile(candidate) as z:
        for info in z.infolist():
            dest=(extracted/info.filename).resolve()
            if not dest.is_relative_to(extracted):raise ValueError('Unsafe ZIP path')
        z.extractall(extracted)
    ext=extracted/'CPC4/ampliaciones'/ROOT.name
    (work/'evidence').mkdir(exist_ok=a.resume);commands=[]
    venv=work/'clean_env'
    if not a.resume:commands.append(execute('clean_create_env01',[sys.executable,'-I','-m','venv',venv],work,180))
    python=venv/'Scripts/python.exe';wheel=extracted/'CPC4/runtime/dee_thinking-4.0.0-cp313-cp313-win_amd64.whl'
    if not a.resume:
        commands.append(execute('clean_install01',[python,'-I','-m','pip','install','--no-index','--no-deps','--disable-pip-version-check',wheel],work,180))
        commands.append(execute('clean_native_reference01',[python,'-I','-B',ext/'src/clean_worker.py','--output',work/'evidence/native'],work,240))
    else:
        commands += [json.loads((ROOT/'jobs'/name/'job.json').read_text(encoding='utf-8')) for name in ('clean_create_env01','clean_install01','clean_native_reference01')]
        assert all(c['exit_code']==0 for c in commands)
    # Exercise the shipped PowerShell launcher itself using this fresh offline
    # venv, not the development install. The launcher uses its local environment.
    commands.append(execute('clean_public_launcher02' if a.resume else 'clean_public_launcher01',['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',ext/'iniciar_cpc4.ps1',
                  '-Python',sys._base_executable,'-Eventos',ext/'configuraciones/DEMO_CENTRAL_V3.eventos','-Salida',work/'evidence/CENTRAL_V3_01'],work,300))
    # A second process restores1501 and physically asks the unasked word. No
    # results are copied into MAIN; its output is compared only afterwards.
    continuation=work/'continue.eventos';continuation.write_text('cargar "'+str(work/'evidence/CENTRAL_V3_01/RED_LENGUAJE_T1501.deetsnap')+'"\nconsultar MALO\nguardar RED_LENGUAJE_T1529.deetsnap\nsalir\n',encoding='utf-8')
    commands.append(execute('clean_public_continue01',[python,'-I','-B',ext/'demostracion.py','--eventos',continuation,'--salida',work/'evidence/CONTINUAR_V3_02'],work,180))
    commands.append(execute('clean_public_regulated01',[python,'-I','-B',ext/'demostracion.py','--eventos',ext/'configuraciones/DEMO_REGULADA.eventos','--salida',work/'evidence/REGULATED_FINAL01'],work,240))
    commands.append(execute('clean_public_regulated_restore01',[python,'-I','-B',ext/'demostracion.py','--eventos',ext/'configuraciones/DEMO_REGULADA_CONTINUAR.eventos','--salida',work/'evidence/REGULATED_RESTORE02'],work,180))
    commands.append(execute('clean_compare_actual_demos01',[python,'-I','-B',ext/'src/check_clean_demos.py','--evidence',work/'evidence'],work,180))
    commands.append(execute('clean_hashes01',[python,'-I','-B',ext/'ejecutar.py','verificar'],work,300))
    report=json.loads((work/'evidence/native/CLEAN_REPRODUCTION.json').read_text(encoding='utf-8'))
    dialogue=[json.loads(x) for x in (work/'evidence/CONTINUAR_V3_02/DIALOGOS.jsonl').read_text(encoding='utf-8').splitlines()]
    assert not any('error' in x['result'] for x in dialogue)
    assert any(x['command']=='consultar MALO' for x in dialogue)
    # Retain source-byte identities of the exact extracted execution. The final
    # ZIP adds these reports only, then verifies the same code/config bytes.
    executed=[p for p in ext.rglob('*') if p.is_file() and (p.suffix in ('.py','.ps1') or p.parent.name=='configuraciones') and '.venv' not in p.parts]
    record={'schema':'CPC4.A02.clean_reproduction.v1','tested_candidate_sha256':digest,
       'extraction_directory':str(extracted),'clean_python':str(python),'commands':commands,
       'reused_unchanged_native_prechecks':prior,
       'native_reference':report,'new_post_restore_dialogue':dialogue,
       'executed_payload_identity':[{'path':str(p.relative_to(ext)).replace('\\','/'),'sha256':sha(p)} for p in executed],
       'elapsed_seconds':time.monotonic()-start,'completed_utc':datetime.now(timezone.utc).isoformat(),
       'remaining_original_campaign_seconds':remaining(),
       'scope':'Actual extraction, offline official wheel, source-independent site-packages, inherited step, fresh native trajectory, full pending queue and future, public launcher, second-process new query. Candidate hash is not a self-hash of the later evidence append.'}
    destination=ROOT/'resultados/reproduccion_limpia';destination.mkdir(parents=True,exist_ok=False)
    put(destination/'CLEAN_REPRODUCTION.json',record)
    # Compact useful logs and the emitted evidence, no clean venv/corpus copy.
    shutil.copyfile(work/'evidence/DEMO_STATE_COMPARISONS.json',destination/'DEMO_STATE_COMPARISONS.json')
    for sub in ('native','CENTRAL_V3_01','CONTINUAR_V3_02','REGULATED_FINAL01','REGULATED_RESTORE02'):
        target=destination/sub;target.mkdir()
        for item in (work/'evidence'/sub).rglob('*'):
            if item.is_file() and item.suffix not in ('.deetsnap','.pyd','.pyc'):
                relative=item.relative_to(work/'evidence'/sub);(target/relative).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(item,target/relative)
    print(json.dumps({'clean_reproduction':'completed','seconds':record['elapsed_seconds'],'candidate':digest,'fresh_query_after_restore':True}))

if __name__=='__main__':main()
