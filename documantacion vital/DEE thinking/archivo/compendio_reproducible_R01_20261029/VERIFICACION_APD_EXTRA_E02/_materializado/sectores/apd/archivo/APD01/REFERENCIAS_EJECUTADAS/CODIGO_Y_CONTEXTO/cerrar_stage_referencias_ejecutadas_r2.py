"""Finalize a NEW executed-reference stage revision with report; zero DEE imports/ticks."""
import argparse, hashlib, json, shutil, subprocess, sys, tempfile
from pathlib import Path

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(p, value):
    if p.exists(): raise FileExistsError(str(p))
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)+'\n', encoding='utf8')
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ('source','report','out','check_root'): ap.add_argument('--'+key.replace('_','-'), type=Path, required=True)
    a=ap.parse_args()
    if a.out.exists(): raise FileExistsError('A fresh revision is required')
    manifest=json.loads((a.source/'MANIFIESTO.json').read_text(encoding='utf8'))
    expected={row['file']:row for row in manifest['members']}
    actual={p.relative_to(a.source).as_posix():p for p in a.source.rglob('*') if p.is_file() and p.name!='MANIFIESTO.json'}
    if set(actual)!=set(expected): raise ValueError('Source manifest membership differs')
    for name,p in actual.items():
        row=expected[name]
        if p.stat().st_size!=row['bytes'] or sha(p)!=row['sha256']: raise ValueError('Source bytes differ: '+name)
    shutil.copytree(a.source,a.out,ignore=shutil.ignore_patterns('MANIFIESTO.json'))
    shutil.copyfile(a.report,a.out/'INFORME_REFERENCIAS_EJECUTADAS.txt')
    shutil.copyfile(Path(__file__),a.out/'CODIGO_Y_CONTEXTO'/Path(__file__).name)
    comparison=json.loads((a.out/'REFERENCIAS/COMPARACION.json').read_text(encoding='utf8'))
    emit(a.out/'TABLA_OBSERVADA_PARA_MANUAL.json', {'schema':'APD01.observed_reference_manual_projection.v1','native_ticks_in_projection':0,'source':'REFERENCIAS/COMPARACION.json','source_sha256':sha(a.out/'REFERENCIAS/COMPARACION.json'),'rows':comparison['rows'],'limits':comparison['limits'],'coverage':comparison['coverage']})
    plan=json.loads((a.out/'PLAN_RECALCULO.json').read_text(encoding='utf8'))
    checks=[]
    with tempfile.TemporaryDirectory(prefix='_apd_actualrefs_closed_',dir=a.check_root) as directory:
        tree=Path(directory)/'extraido'; shutil.copytree(a.out,tree)
        for i,case in enumerate(plan['jobs']):
            base=tree/case.get('base','.')
            output=Path(directory)/(str(i)+'.json')
            argv=[sys.executable,'-I','-B','-X','utf8',str(base/case['script']),*[str(output) if v=='{output}' else v for v in case['args']]]
            run=subprocess.run(argv,cwd=base,capture_output=True,text=True,encoding='utf8',timeout=60)
            equal=run.returncode==0 and output.exists() and output.read_bytes()==(base/case['reference']).read_bytes()
            checks.append({'case':case['name'],'returncode':run.returncode,'exact_reference_bytes':equal,'stdout':run.stdout,'stderr':run.stderr})
            if not equal: raise ValueError(json.dumps(checks[-1],ensure_ascii=False))
    emit(a.out/'CIERRE_REVISION_R02.json',{'schema':'APD01.executed_reference_stage_closed.v2','native_ticks':0,'new_native_replay':False,'source_revision_manifest_sha256':sha(a.source/'MANIFIESTO.json'),'preserved_all_source_members_exactly':True,'added_report_and_projection_only':True,'portable_checks':checks})
    emit(a.out/'MANIFIESTO.json',{'schema':'SHA256.members.no_self_reference.v1','members':[{'file':p.relative_to(a.out).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(a.out.rglob('*')) if p.is_file()]})
    files=[p for p in a.out.rglob('*') if p.is_file()]
    print(json.dumps({'stage':str(a.out),'files':len(files),'bytes':sum(p.stat().st_size for p in files),'manifest_sha256':sha(a.out/'MANIFIESTO.json'),'portable_cases':len(checks),'native_ticks_in_closure':0}))
if __name__=='__main__': main()

