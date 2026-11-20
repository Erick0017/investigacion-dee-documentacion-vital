"""Bounded version of the existing paused-owner export; PLAN by default.

Only the exact product system or PI04 candidate system is admitted. --ejecutar
opens the existing complete life paused, exports at zero ticks, closes its exact
owned process/job, verifies the whole pair and moves it into stable RP once.
No experiment, resource reset, replacement, selection or promotion is performed.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,os,sqlite3,sys
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0'
CANDIDATE=P/'estados/candidato_R02/sistema';PRODUCT=C/'sistema';RP=C/'reproducibilidad'
LIFE='ECI02_PI03_REPRO_PI04_MAIN_02'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def load(f):return json.loads(f.read_text(encoding='utf-8-sig'))
def write_new(path,data):
    with path.open('x',encoding='utf-8')as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def bounded_system(value):
    path=Path(value).absolute()
    for part in(path,*path.parents):
        if part.is_symlink()or(part.exists()and getattr(part.lstat(),'st_file_attributes',0)&0x400):raise ValueError('Linked system path rejected')
        if part==P.parents[2]:break
    path=path.resolve(strict=True)
    if path not in(PRODUCT.resolve(strict=True),CANDIDATE.resolve(strict=True)):raise ValueError('Only literal existing product/sistema or PI04 candidato_R02/sistema is admitted')
    return path
def selection(system):
    file=system/'estado/ACTIVO.json'
    return load(file)if file.is_file()else None
def preflight(system,life,tick):
    if not life.startswith('ECI02_PI03_REPRO_PI04_')or life=='ECI02_PI03_REPRO_PI04_':raise ValueError('Named existing PI04 continuation only')
    if system==PRODUCT.resolve()and life!=LIFE:raise ValueError('Product export is bounded to the exact adopted PI04 life')
    cardfile=system/'estado/vidas'/life/'VIDA.json';card=load(cardfile)
    if card.get('life_id')!=life or card['physical']['N']!=67 or card['physical']['tick']!=tick:raise ValueError('Actual complete life card must match the exact requested cut')
    if sha(system/card['snapshot'])!=card['snapshot_sha256']:raise ValueError('Current Native snapshot identity differs')
    for marker in(system/'estado/locks'/(card['world_id']+'.lock'),cardfile.parent/'FUTURO_INTERRUMPIDO.json',system/'estado/servicios_persistentes'/life/'IMPORTACION_EN_CURSO.json'):
        if marker.exists():raise ValueError('Current writer/interruption preserved:'+str(marker))
    db=system/'estado/servicios_persistentes'/life/'cola.sqlite3'
    if not db.is_file():raise FileNotFoundError('Existing complete transport is required; no bootstrap/new world')
    wal=db.with_name(db.name+'-wal')
    if wal.exists()and wal.stat().st_size:raise ValueError('Nonempty operational WAL requires consistency diagnosis')
    con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
    try:
        pending=con.execute("SELECT id,status FROM requests WHERE status IN('queued','processing','uncertain')").fetchall();row=con.execute("SELECT value FROM meta WHERE key='owner'").fetchone();owner=None if row is None else json.loads(row[0])
    finally:con.close()
    if pending or(owner and owner.get('running')is True):raise ValueError('Existing operational queue/owner is not closed; never launch another writer')
    return cardfile,card,owner
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--system-root',type=Path,required=True)
    ap.add_argument('--vida',required=True);ap.add_argument('--alias',required=True);ap.add_argument('--tick',required=True,type=int);ap.add_argument('--ejecutar',action='store_true');a=ap.parse_args()
    system=bounded_system(a.system_root)
    if not a.alias or len(a.alias)>90 or any(c not in'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-'for c in a.alias):raise ValueError('Bounded new RP alias required')
    destination=RP/'materiales'/a.alias;proof=P/'control'/('EXPORTACION_ESTABLE_'+a.alias+'.json')
    if destination.exists()or proof.exists():raise FileExistsError('Existing pair/proof protected; do not repeat export')
    try:cardfile,card,cached_owner=preflight(system,a.vida,a.tick)
    except Exception as error:
        if a.ejecutar:raise
        print(json.dumps({'mode':'PLAN_NO_NATIVE_NO_WRITES','status':'BLOCKED','source_system':str(system),'reason':type(error).__name__+': '+str(error)},ensure_ascii=False));return
    selected_before=selection(system)
    if not a.ejecutar:
        print(json.dumps({'mode':'PLAN_NO_NATIVE_NO_WRITES','source_system':str(system),'system_role':'product'if system==PRODUCT.resolve()else'candidate','life_id':a.vida,'cut':card['physical'],'destination':str(destination),'requires':'--ejecutar for the existing paused-owner zero-tick export','currently_selected':None if selected_before is None else selected_before.get('life_id')},ensure_ascii=False));return
    if Path(sys.executable).resolve()!=(C/'motor/python313/python.exe').resolve()or sys.version_info[:2]!=(3,13):raise ValueError('Use the official existing CPython3.13 runtime for the explicit export')
    if system==PRODUCT.resolve():
        for name in('app/cola_local.py','app/process_control.py'):
            if sha(system/name)!=sha(CANDIDATE/name):raise ValueError('Existing shared owner transport source differs between product and candidate:'+name)
    # These imports are deliberately after all bounds/guards and explicit mode.
    sys.path.insert(0,str(P/'codigo'));from servicio_ensayo_R02 import Owner
    sys.path.insert(0,str(RP));from preservar_revision_pi03 import pair_check
    from observador_pasivo import snapshot_view,compare_native
    before=snapshot_view(system/card['snapshot'])
    with Owner(a.vida,'PI04_EXPORT_'+a.alias,system=system)as owner:
        if not owner.initial['paused']or owner.initial['tick']!=a.tick:raise ValueError('Only the exact existing paused cut may be exported')
        row=owner.control('exportar');value=json.loads(row['result'])if isinstance(row['result'],str)else row['result']
        if value['before_tick']!=a.tick or value['after_tick']!=a.tick:raise ValueError('Unexpected Native advancement during technical export')
    if owner.proc.poll()!=0 or owner.job is not None:raise ValueError('Actual owned process/job did not close cleanly')
    after_card=load(cardfile);current=snapshot_view(system/after_card['snapshot']);comparison=compare_native(before,current,allow_service=True)
    pair=value['paired_export'];source=Path(pair['directory']).resolve(strict=True);expected=(system/'estado/servicios_persistentes'/a.vida/'exportaciones').resolve(strict=True)
    if source.parent!=expected or not source.is_dir()or source.is_symlink():raise ValueError('Export source escaped its exact existing life')
    if not destination.resolve(strict=False).is_relative_to((RP/'materiales').resolve())or source.drive.casefold()!=destination.drive.casefold():raise ValueError('Only bounded same-volume atomic export relocation allowed')
    for base,dirs,files in os.walk(source,followlinks=False):
        for name in[*dirs,*files]:
            f=Path(base)/name
            if f.is_symlink()or(getattr(f.lstat(),'st_file_attributes',0)&0x400):raise ValueError('Linked export member rejected')
    entry={'source':str(source),'manifest_sha256':pair['manifest_sha256'],'life_id':a.vida,'N':67,'tick':a.tick};_,manifest,checked=pair_check(entry)
    exported=snapshot_view(source/'VIDA.deetsnap.gz');exported_comparison=compare_native(exported,current,allow_service=True)
    selected_after=selection(system)
    before_id=None if selected_before is None else selected_before.get('life_id');after_id=None if selected_after is None else selected_after.get('life_id')
    if before_id!=after_id:raise ValueError('Selection identity changed concurrently; preserve export without RP move')
    cfgfile=RP/'RECURSOS.json';cfgbytes=cfgfile.read_bytes();cfg=json.loads(cfgbytes)
    if a.alias in cfg['pairs']:raise ValueError('Existing RP alias protected')
    stage=proof.with_name(proof.stem+'_EN_CURSO.json')
    record={'schema':'DEE.PI04.stable_closed_full_pair.v1','helper_revision':'R02_BOUNDED_TWO_SYSTEMS','local_cut':datetime.datetime.now().astimezone().isoformat(),'source_system':str(system),'system_role':'product'if system==PRODUCT.resolve()else'candidate','life_id':a.vida,'tick':a.tick,'source':str(source),'destination':str(destination),'alias':a.alias,'manifest_sha256':pair['manifest_sha256'],'source_physical':after_card['physical'],'zero_tick_export_comparison':comparison,'export_source_comparison':exported_comparison,'actual_owned_process_handle_exit_code':owner.proc.poll(),'actual_owned_job_closed':owner.job is None,'paired_export_transport':row,'new_native_ticks':0,'copied_full_pair':False,
       'no_principal_selected':True,'selection_semantics':'No select/promote was called by this helper. An already-selected product life remains selected; ordinary zero-tick save may refresh its snapshot pointer. This flag does not mean the source was unselected.',
       'principal_already_selected_at_entry':before_id==a.vida,'selected_life_before':before_id,'selected_life_after':after_id,'historical_paths_rewritten':False,'completed':False}
    write_new(stage,record)
    # Targets have been verified as absolute descendants before any move.
    source.rename(destination);_,_,after=pair_check(dict(entry,source=str(destination)))
    if after!=checked or source.exists():raise ValueError('Moved complete pair verification failed; preserve stage')
    if cfgfile.read_bytes()!=cfgbytes:raise ValueError('Concurrent RP edit; preserve moved pair/stage without blind retry')
    backup=P/'control'/('RECURSOS_ANTES_'+a.alias+'.json')
    with backup.open('xb')as f:f.write(cfgbytes)
    cfg['pairs'][a.alias]={'product_relative':destination.relative_to(C).as_posix(),'manifest_sha256':pair['manifest_sha256'],'life_id':a.vida,'N':67,'tick':a.tick,'role':'operational_continuation_checkpoint'if system==PRODUCT.resolve()else'scientific_prefix','source_system':str(system),'source':str(source),'source_relocation':{'proof':str(proof),'origin':str(source),'current':str(destination),'manifest_sha256':pair['manifest_sha256']}}
    tmp=cfgfile.with_name('RECURSOS.'+a.alias+'.writing');write_new(tmp,cfg)
    if cfgfile.read_bytes()!=cfgbytes:raise ValueError('Concurrent RP edit before atomic registry replacement')
    os.replace(tmp,cfgfile)
    record.update(completed=True,members=len(manifest['members']),bytes=sum(x['bytes']for x in manifest['members']),registered_resources_sha256=sha(cfgfile),after_pair_check=after)
    write_new(proof,record)
    print(json.dumps({'proof':str(proof),'pair':str(destination),'source_system':str(system),'tick':a.tick,'members':record['members'],'bytes':record['bytes'],'manifest_sha256':pair['manifest_sha256'],'new_Native_ticks':0,'selection_changed_by_this_helper':False},ensure_ascii=False))
if __name__=='__main__':main()
