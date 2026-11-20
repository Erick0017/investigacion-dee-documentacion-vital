"""Close exact before/after descriptor bytes and a portable AST-only check, zero ticks."""
import argparse, hashlib, json, shutil, subprocess, sys, tempfile
from pathlib import Path
FILES=('app/access_guard.py','app/servicio_persistente.py','gestionar.py')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(p,v):
    if p.exists():raise FileExistsError(str(p))
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
def copy(p,q):
    q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
    if sha(p)!=sha(q):raise ValueError('Copy bytes changed')
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in('before','system','checker','reference','out','check_root'):ap.add_argument('--'+key.replace('_','-'),type=Path,required=True)
    a=ap.parse_args()
    if a.out.exists():raise FileExistsError('Fresh closed stage required')
    expected=json.loads(a.reference.read_text(encoding='utf8'))
    entries={r['relative_SYSTEM']:r for r in expected['files']}
    if set(entries)!=set(FILES):raise ValueError('Unexpected reference file set')
    for name in FILES:
        old=a.before/name;new=a.system/name
        if sha(old)!=entries[name]['before_sha256']or sha(new)!=entries[name]['after_sha256']:raise ValueError('Reference source mismatch: '+name)
        copy(old,a.out/'ANTES'/name);copy(new,a.out/'DESPUES'/name)
    copy(a.checker,a.out/'RECALCULO'/a.checker.name)
    copy(a.reference,a.out/'REFERENCIA/VERIFICACION_METADATOS_PERIMETRO_N0.json')
    copy(Path(__file__),a.out/'CODIGO/preparar_stage_perimetro_metadata_r1.py')
    plan={'schema':'APD01.descriptive_metadata.closed_stdlib_plan.v1','native_ticks':0,'jobs':[{'name':'DESCRIPTORES_SIN_CAMBIO_ALGORITMO_O_PERMISOS','base':'.','script':'RECALCULO/'+a.checker.name,'args':['--system','DESPUES','--before','ANTES','--output','{output}'],'reference':'REFERENCIA/VERIFICACION_METADATOS_PERIMETRO_N0.json'}]}
    emit(a.out/'PLAN_RECALCULO.json',plan)
    with tempfile.TemporaryDirectory(prefix='_apd_metadata_',dir=a.check_root)as directory:
        tree=Path(directory)/'extraido';shutil.copytree(a.out,tree);output=Path(directory)/'recalculado.json'
        argv=[sys.executable,'-I','-B','-X','utf8',str(tree/'RECALCULO'/a.checker.name),'--system','DESPUES','--before','ANTES','--output',str(output)]
        run=subprocess.run(argv,cwd=tree,capture_output=True,text=True,encoding='utf8',timeout=30)
        exact=run.returncode==0 and output.exists() and output.read_bytes()==a.reference.read_bytes()
        proof={'native_ticks':0,'application_imported':False,'returncode':run.returncode,'exact_reference_bytes':exact,'stdout':run.stdout,'stderr':run.stderr,'scope':'AST normalization of the approved literal descriptors only. Not an OS access-control test or proof that every hidden solver is impossible.'}
        if not exact:raise ValueError(json.dumps(proof,ensure_ascii=False))
    emit(a.out/'PRUEBA_PORTABLE.json',proof)
    emit(a.out/'ALCANCE.json',{'native_ticks':0,'original_historical_FENCE_true_bytes_preserved':True,'new_description_only':True,'new_permissions':False,'new_memory_or_cognitive_capability':False,'no_OS_security_guarantee':True,'native_state_advanced_or_modified_by_this_check':False,'scope':'The old combined metadata flag overclaimed universal blocking of operational-history reads. Corrected descriptors distinguish undeclared external laboratory/evidence reads from a universal guarantee not supplied by this hook. Both exact code revisions remain in this stage. Code file bytes differ as explicitly hashed; no physical DEE state is loaded or modified.'})
    emit(a.out/'MANIFIESTO.json',{'schema':'SHA256.members.no_self_reference.v1','members':[{'file':p.relative_to(a.out).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(a.out.rglob('*'))if p.is_file()]})
    files=[p for p in a.out.rglob('*')if p.is_file()]
    print(json.dumps({'stage':str(a.out),'files':len(files),'bytes':sum(p.stat().st_size for p in files),'manifest_sha256':sha(a.out/'MANIFIESTO.json'),'native_ticks':0,'portable_byte_equal':exact}))
if __name__=='__main__':main()

