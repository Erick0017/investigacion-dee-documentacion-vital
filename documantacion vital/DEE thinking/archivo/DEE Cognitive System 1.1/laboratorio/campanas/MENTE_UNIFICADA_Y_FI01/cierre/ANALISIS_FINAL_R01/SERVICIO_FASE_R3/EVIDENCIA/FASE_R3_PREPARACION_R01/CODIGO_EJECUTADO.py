"""Exact stopped R11 package and explicit new-identity zero-tick R3 import.

No parent Runtime is opened. Import/epoch closure execute only on the named copy,
after the operator explicitly authorizes that stage and source files are stable.
"""
import argparse,hashlib,importlib.util,json,shutil,sqlite3,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone

LIFE='MU_MAIN_FASE_R3'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def protected(system):
    card=system/'estado/vidas/MU_MAIN/VIDA.json';v=json.loads(card.read_bytes());paths=[card,system/v['snapshot'],system/'estado/servicios_persistentes/MU_MAIN/cola.sqlite3',system/'estado/ACTIVO.json']
    return [{'file':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}for p in paths]
def prepare(system,folder):
    folder.mkdir(parents=True,exist_ok=False);before=protected(system);record=json.loads((system/'estado/vidas/MU_MAIN/VIDA.json').read_bytes());state=system/'estado';side=state/'servicios_persistentes/MU_MAIN';db=side/'cola.sqlite3';wal=side/'cola.sqlite3-wal'
    if record['snapshot_sha256']!='c2f5c43806de20b1009d9bea3a41503135bf7c914f2691691ecb3bbb7b47d610':raise ValueError('The explicitly selected stopped R11 final checkpoint changed; no fallback to earlier export')
    if(state/'locks/MU_MAIN.lock').exists()or(wal.exists()and wal.stat().st_size):raise ValueError('Parent writer/WAL active: never package a mid-operation state')
    with sqlite3.connect(db.as_uri()+'?mode=ro&immutable=1',uri=True)as con:
        owner=json.loads(con.execute('SELECT value FROM meta WHERE key=?',('owner',)).fetchone()[0]);pending=con.execute('SELECT id FROM requests WHERE status IN (?,?,?)',('queued','processing','uncertain')).fetchall()
        if owner.get('running')or pending or con.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Parent transport not stopped and unambiguous')
    target=folder/'PAQUETE_PADRE_FINAL_R11';target.mkdir();shutil.copyfile(system/record['snapshot'],target/'VIDA.deetsnap.gz');shutil.copyfile(db,target/'cola.sqlite3')
    for src,prefix in((side/'resultados','resultados'),(state/'servicios_locales/MU_MAIN','artefactos_trabajador')):
        for source in sorted(src.rglob('*')):
            if not source.is_file():continue
            if source.is_symlink()or not source.resolve().is_relative_to(src.resolve()):raise ValueError('Undeclared external artifact path')
            dest=target/prefix/source.relative_to(src);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
    members=[{'file':p.relative_to(target).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(target.rglob('*'))if p.is_file()]
    manifest={'schema':'DEE.persistent_service.paired_export.v1','life_id':'MU_MAIN','profile':record['profile'],'backend':'mente_unificada','native_snapshot':'VIDA.deetsnap.gz','snapshot_sha256':record['snapshot_sha256'],'physical':record['physical'],'members':members,'queue_journal_required':True,'source_record':{'life_id':'MU_MAIN','world_id':record['world_id'],'parent':record.get('parent')},'no_engine_or_WHL':True,'not_a_new_cognitive_acquisition':True,'scope':'Fresh exact-byte paired package from the current stopped post-STOP R11 cut; not the earlier fi60s_export. Parent is read only, no Runtime or tick. New identity import and technical epoch closure are separate explicit operations.'}
    write(target/'EXPORTACION_SERVICIO.json',manifest)
    spec=importlib.util.spec_from_file_location('verify_existing_paired_contract',system/'app/importacion_emparejada.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);_,_,verification=m.verify_export(target)
    after=protected(system)
    if before!=after:raise ValueError('Protected original changed while preparing copy')
    write(folder/'PREPARACION.json',{'schema':'DEE.MUFI.R3.explicit_paired_parent_preparation.v1','prepared_utc':datetime.now(timezone.utc).isoformat(),'new_native_ticks':0,'package':str(target),'manifest_sha256':sha(target/'EXPORTACION_SERVICIO.json'),'verification':verification,'protected_before':before,'protected_after':after,'originals_unchanged':True,'next_commands':[[sys.executable,'-I','-B',str(system/'gestionar.py'),'mente-unificada-importar','--paquete',str(target),'--vida',LIFE],[sys.executable,'-I','-B',str(system/'gestionar.py'),'mente-unificada-finalizar-protocolo','--vida',LIFE]],'no_teaching_no_phase_flag_no_source_main_advance':True})
    shutil.copyfile(Path(__file__),folder/'CODIGO_EJECUTADO.py');print(json.dumps({'package':str(target),'members':len(members),'manifest_sha256':sha(target/'EXPORTACION_SERVICIO.json'),'new_native_ticks':0}))
def import_and_close(system,folder):
    p=json.loads((folder/'PREPARACION.json').read_bytes());before=protected(system)
    if before!=p['protected_after']:raise ValueError('Original stopped cut or ACTIVO changed since preparation')
    if(system/'estado/vidas'/LIFE).exists():raise FileExistsError('Preserve existing candidate; no duplicate import or silent rewind')
    logs=[]
    for i,command in enumerate(p['next_commands']):
        r=subprocess.run(command,cwd=system,capture_output=True,text=True,encoding='utf8',timeout=120);entry={'command':command,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr};logs.append(entry);write(folder/('OPERACION_'+str(i+1)+'.json'),entry)
        if r.returncode:write(folder/'IMPORTACION_INTERRUMPIDA.json',{'logs':logs,'protected_current':protected(system),'no_retry':True});raise RuntimeError('Explicit copy operation failed; preserve partial state and diagnose, never retry blindly')
    candidate=json.loads((system/'estado/vidas'/LIFE/'VIDA.json').read_bytes());source=json.loads((system/'estado/vidas/MU_MAIN/VIDA.json').read_bytes());keys=('N','tick','RAW_sha256','clocks_sha256')
    checks={'same_native_physical_cut_zero_ticks':all(candidate['physical'][k]==source['physical'][k]for k in keys),'explicit_import_parent_sha':candidate['parent']['encoded_sha256']==source['snapshot_sha256'],'all_original_files_unchanged':before==protected(system),'native_tick_preserved':candidate['physical']['tick']==68924,'separate_identity':candidate['life_id']==candidate['world_id']==LIFE}
    result={'schema':'DEE.MUFI.R3.zero_tick_import_and_epoch_close.v1','new_native_ticks':0,'checks':checks,'issues':[k for k,v in checks.items()if not v],'candidate':candidate,'operations':logs,'protected_before':before,'protected_after':protected(system),'scope':'Exact whole native state plus transport imported under a new identity; only technical metadata/epoch closure changed. No B0, phase flag, teaching or other material request has been applied.'};write(folder/'IMPORTACION_Y_CIERRE_0TICKS.json',result);print(json.dumps({'issues':result['issues'],'candidate':{k:candidate[k]for k in('life_id','snapshot','snapshot_sha256','physical')}}));return bool(result['issues'])
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sistema',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);p.add_argument('--importar-y-cerrar',action='store_true');a=p.parse_args()
    if a.importar_y_cerrar:return import_and_close(a.sistema,a.salida)
    prepare(a.sistema,a.salida);return 0
if __name__=='__main__':raise SystemExit(main())
