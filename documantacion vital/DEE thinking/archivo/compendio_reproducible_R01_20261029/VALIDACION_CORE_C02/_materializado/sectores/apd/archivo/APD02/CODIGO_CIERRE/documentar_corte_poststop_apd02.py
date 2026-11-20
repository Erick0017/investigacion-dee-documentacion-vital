"""Seal exact stopped APD02 operational bytes. No Runtime, solver or new ticks.

The final paired snapshot and journal are copied AFTER STOP. A pre-STOP
export is never renamed as this exact cut. Scientific conclusions are supplied
separately by archived recalculations and the root's reviewed scope.
"""
import argparse,gzip,hashlib,importlib.util,json,shutil,sqlite3
from pathlib import Path

def read(p):return json.loads(Path(p).read_bytes())
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def write(p,value):
    with Path(p).open('x',encoding='utf8',newline='\n')as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--sistema',type=Path,required=True);ap.add_argument('--ventana',type=Path,required=True)
    ap.add_argument('--presupuesto',type=Path,required=True);ap.add_argument('--salida',type=Path,required=True);ap.add_argument('--alcance',required=True)
    a=ap.parse_args();s=a.sistema.resolve();trial=a.ventana.resolve();primary=json.loads(gzip.decompress((trial/'REGISTROS_VENTANA.json.gz').read_bytes()))
    if primary.get('error')or primary.get('forced_own_job_close')or not primary['sources_unchanged']or primary['pending']:raise ValueError('Do not relabel a failed, moving or pending future as a clean selected cut')
    if primary['owner_returncode']!=0 or primary['job_final'].get('job_active_processes')!=0:raise ValueError('Own supervised world owner did not close cleanly')
    final=primary['final'];life=final['life_id'];card=s/'estado/vidas'/life/'VIDA.json';record=read(card);card_sha=sha(card)
    if any(record[k]!=final[k]for k in('life_id','world_id','parent','snapshot','snapshot_sha256','physical')):raise ValueError('Actual life moved after the closed trial')
    if(s/'estado/locks'/(record['world_id']+'.lock')).exists():raise ValueError('Existing world lock; no attempt to steal/terminate another owner')
    side=s/'estado/servicios_persistentes'/record['world_id'];db=side/'cola.sqlite3';wal=db.with_name(db.name+'-wal')
    if wal.exists()and wal.stat().st_size:raise ValueError('WAL contains operational data; never discard/checkpoint it silently')
    with sqlite3.connect(db.as_uri()+'?mode=ro&immutable=1',uri=True)as con:
        if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Operational journal integrity failed')
        owner=json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0])
        outstanding=[dict(zip(('id','status'),row))for row in con.execute("SELECT id,status FROM requests WHERE status IN('queued','processing','uncertain')")]
    if owner.get('running')is not False or outstanding or owner.get('uncertain_external_result'):raise ValueError('Stopped complete owner/journal required')
    ob=module('APD02_readonly_frozen_snapshot',s/'capacidades/observador_causal_retrospectivo_01.py');snap=s/record['snapshot'];world=ob.Snapshot(snap)
    physical={'N':world.N,'tick':world.tick,'RAW_sha256':ob.sha(ob.pbytes(world.raw)),'clocks_sha256':ob.sha(ob.pbytes(world.clocks))}
    if not world.checksum_valid or world.encoded_sha256!=record['snapshot_sha256']or any(record['physical'][k]!=v for k,v in physical.items()):raise ValueError('Complete current world differs from the durable pointer')
    def meta(key):return json.loads(world.metadata[key])if key in world.metadata else{}
    protocol=meta('DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1');unified=meta('DEE.Cognitive.System.1.1.MENTE_UNIFICADA_01.v1')
    assistant=meta('DEE.Cognitive.System.1.1.APD02.assistant.R01');route=meta('DEE.Cognitive.System.1.1.APD02.delayed_action_trace.R04')
    pending={k:unified.get(k)for k in('external_pending','cascade_pending','external_uncertain')}
    pending.update(APD02_uncertain=assistant.get('external_uncertain'),route_action_window=route.get('pending_window'))
    goal=assistant.get('goal_pending');goal_unfinished=bool(goal and not goal['progress']['verified_file_goal_completed']and goal['progress']['opportunities_used']<4)
    pending['goal_unfinished']=goal_unfinished
    if world.pending or any(pending.values())or protocol.get('closed_epoch'):raise ValueError('Keep all operational work; this selected clean cut requires no unresolved native/goal work and the original open epoch')
    if protocol.get('epoch')!=6:raise ValueError('Unexpected protocol genealogy; do not close/recreate an epoch')
    out=a.salida.resolve();out.mkdir(parents=True,exist_ok=False);package=out/'PAQUETE_FINAL_POSTSTOP';package.mkdir()
    sources=[(snap,'VIDA.deetsnap.gz'),(db,'cola.sqlite3')]
    for base,prefix in((side/'resultados','resultados'),(s/'estado/servicios_locales'/life,'artefactos_trabajador')):
        for f in sorted(base.rglob('*')):
            if f.is_file():
                if f.is_symlink()or not f.resolve().is_relative_to(base.resolve()):raise ValueError('External operational file link is not silently followed')
                sources.append((f,prefix+'/'+f.relative_to(base).as_posix()))
    members=[]
    for source,name in sources:
        before=sha(source);target=package/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        if sha(source)!=before or sha(target)!=before:raise ValueError('A supposedly stopped operational member changed')
        members.append({'file':name,'source_system_relative':source.relative_to(s).as_posix(),'bytes':source.stat().st_size,'sha256':before})
    manifest={'schema':'DEE.persistent_service.paired_export.v1','life_id':life,'world_id':record['world_id'],'profile':record['profile'],'backend':'mente_unificada',
      'native_snapshot':'VIDA.deetsnap.gz','snapshot_sha256':record['snapshot_sha256'],'physical':record['physical'],'members':members,'queue_journal_required':True,
      'source_record':{'life_id':life,'world_id':record['world_id'],'parent':record.get('parent')},'no_engine_or_WHL':True,'not_a_new_cognitive_acquisition':True,
      'scope':'Exact postSTOP snapshot, complete transport journal/outbox, worker artifacts and serialized external-goal facts. No reexecution, empty queue, clock edit or learned-content transplant. Analysis is not this operational backup.'}
    write(package/'EXPORTACION_SERVICIO.json',manifest)
    validator=module('APD02_exact_existing_pair_validator',s/'app/importacion_emparejada.py');_,_,proof=validator.verify_export(package)
    if sha(card)!=card_sha or sha(db)!=members[1]['sha256']:raise ValueError('Durable source changed during read-only sealing')
    budget=read(a.presupuesto);protected=[];parent=budget['parent']
    original=[('parent_record',Path(parent['record']),parent['record_sha256']),('parent_snapshot',Path(parent['snapshot']),parent['snapshot_sha256']),('parent_paired_manifest',Path(parent['pair_manifest']),parent['pair_manifest_sha256']),('protected_active_snapshot',s/budget['protected_active']['snapshot'],budget['protected_active']['snapshot_sha256'])]
    for label,path,expected in original:
        digest=sha(path);protected.append({'name':label,'file':str(path),'expected_sha256':expected,'actual_sha256':digest,'unchanged':digest==expected})
    active=s/'estado/ACTIVO.json'
    protected.append({'name':'global_active_record','file':str(active),'expected_sha256':'5af64dc7211c6d12255dbb172e5f19c34bdda27b487d2d418838a6607f21c819','actual_sha256':sha(active),'unchanged':read(active)==budget['protected_active']and sha(active)=='5af64dc7211c6d12255dbb172e5f19c34bdda27b487d2d418838a6607f21c819'})
    if not all(x['unchanged']for x in protected):raise ValueError('Protected parent or global active changed; never conceal it')
    cut={'schema':'APD02.actual_postSTOP_operational_cut.v1','new_native_ticks':0,'main':{**final,'life_id':life,'tick':world.tick,'N':world.N,'record':card.relative_to(s).as_posix(),'record_sha256':card_sha},
      'persistent_service':{'owner_stopped':True,'pending_or_uncertain':False,'epoch':protocol['epoch'],'epoch_closed':False,'native_pending':len(world.pending),'pending':pending,'owner':owner,'journal':str(db),'journal_sha256':sha(db),
        'operational_goal_state':goal,'manual_results_text':a.alcance,'paired_manifest':str(package/'EXPORTACION_SERVICIO.json'),'paired_manifest_sha256':sha(package/'EXPORTACION_SERVICIO.json'),
        'world_evolving_wall_seconds':primary['enabled_seconds'],'one_owner_window_observation':'Requires separate exact monotonic/sampling audit; no cognitive competence inferred from duration'},
      'paired_export':{'manifest':str(package/'EXPORTACION_SERVICIO.json'),'manifest_sha256':sha(package/'EXPORTACION_SERVICIO.json'),'verification':proof,'same_cut_after_STOP':True},
      'protected_sources':protected,'issues':[],'scientific_scope':'Root-reviewed functional evidence is separate from byte/protocol integrity; a clean snapshot is not a global PASS or certification.'}
    write(out/'CORTE_OPERATIVO_APD02.json',cut)
    print(json.dumps({'cut':str(out/'CORTE_OPERATIVO_APD02.json'),'sha256':sha(out/'CORTE_OPERATIVO_APD02.json'),'tick':world.tick,'snapshot_sha256':record['snapshot_sha256'],'members':len(members),'bytes':sum(x['bytes']for x in members),'new_ticks':0}))
if __name__=='__main__':main()
