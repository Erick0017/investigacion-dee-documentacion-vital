"""Preserve exact stopped APD R01 plus its real queued future; zero ticks."""
import argparse,gzip,hashlib,importlib.util,json,shutil,sqlite3
from datetime import datetime
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_bytes())
def write(p,x):
    with p.open('x',encoding='utf8')as f:json.dump(x,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sistema',type=Path,required=True);p.add_argument('--ensayo',type=Path,required=True);a=p.parse_args();system=a.sistema.resolve();trial=a.ensayo.resolve();result=load(trial/'RESULTADO.json');pro=load(trial/'PROTOCOLO.json');life=pro['life_id'];card=system/'estado/vidas'/life/'VIDA.json';record=load(card);original_result_sha=sha(trial/'RESULTADO.json');card_sha=sha(card);state=system/'estado';side=state/'servicios_persistentes'/record['world_id'];db=side/'cola.sqlite3';wal=db.with_name(db.name+'-wal')
    if not result.get('error')or pro['request_prefix']!='apd61_'or not result['technical_errors']:raise ValueError('This preservation requires the recorded R02 pending-window error and explicit stopped continuation')
    if(state/'locks'/(record['world_id']+'.lock')).exists():raise ValueError('World still has a writer')
    if wal.exists()and wal.stat().st_size:raise ValueError('Unsettled WAL cannot be omitted')
    with sqlite3.connect(db.as_uri()+'?mode=ro&immutable=1',uri=True)as c:
        c.row_factory=sqlite3.Row;integrity=c.execute('PRAGMA integrity_check').fetchone()[0];rows=[dict(r)for r in c.execute('SELECT * FROM requests ORDER BY seq')];owner=json.loads(c.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0])
    pending=[r for r in rows if r['status']in('queued','processing','uncertain')]
    if integrity!='ok'or owner.get('running')is not False or owner.get('uncertain_external_result')or record['physical']['tick']!=257480:raise ValueError('Expected real stopped interrupted cut is not current')
    if len(pending)!=8 or any(r['status']!='queued'for r in pending):raise ValueError('Actual eight-row queued future differs; no replacement or discard')
    package=trial/'CORTE_INTERRUMPIDO_POSTSTOP';package.mkdir(exist_ok=False);sources=[(system/record['snapshot'],'VIDA.deetsnap.gz'),(db,'cola.sqlite3')]
    for source,prefix in((side/'resultados','resultados'),(state/'servicios_locales'/life,'artefactos_trabajador')):
        for f in sorted(source.rglob('*')):
            if f.is_file():
                if f.is_symlink()or not f.resolve().is_relative_to(source.resolve()):raise ValueError('External dependency is not a declared operational file')
                sources.append((f,prefix+'/'+f.relative_to(source).as_posix()))
    members=[]
    for f,name in sources:
        dest=package/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,dest);digest=sha(f)
        if sha(dest)!=digest:raise ValueError('Copied pair changed during preservation')
        members.append({'file':name,'source_system_relative':f.relative_to(system).as_posix(),'bytes':f.stat().st_size,'sha256':digest})
    manifest={'schema':'DEE.persistent_service.paired_export.v1','life_id':life,'world_id':record['world_id'],'profile':record['profile'],'backend':'mente_unificada','native_snapshot':'VIDA.deetsnap.gz','snapshot_sha256':record['snapshot_sha256'],'physical':record['physical'],'members':members,'queue_journal_required':True,'source_record':{'life_id':life,'world_id':record['world_id'],'parent':record.get('parent')},'scope':'Exact stopped R02 failed-window cut. Eight genuine queued actions remain; nothing was cancelled, retried or restored. BEGIN is queued, not an already formed pending artifact. This is operational continuity, not a successful sixty-minute trial.'}
    write(package/'EXPORTACION_SERVICIO.json',manifest)
    s=importlib.util.spec_from_file_location('APD_interrupted_pair_verify',system/'app/importacion_emparejada.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);_,_,verification=m.verify_export(package)
    with gzip.GzipFile(filename=str(trial/'REGISTROS_TRANSPORTE_POSTSTOP.json.gz'),mode='wb',mtime=0)as f:f.write((json.dumps(rows,sort_keys=True,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    events=[json.loads(x)for x in(trial/'ADMISIONES_Y_EVENTOS.jsonl').read_text(encoding='utf8').splitlines()if x];begin=next(e for e in events if e['kind']=='owner_ready');stop_row=next(r for r in rows if r['id']=='apd61_explicit_abort_stop');stop=json.loads(stop_row['result']);elapsed=(datetime.fromisoformat(stop['finished_execution_utc'])-datetime.fromisoformat(begin['utc'])).total_seconds();pause_row=next(r for r in rows if r['id']=='apd61_pause_1');pause=json.loads(pause_row['result']);unfinished_pause=(datetime.fromisoformat(stop['finished_execution_utc'])-datetime.fromisoformat(pause['started_utc'])).total_seconds();discount=sum(i['discount_seconds']for i in result['pause_intervals'])+unfinished_pause;selected=[r for r in rows if r['id'].startswith(pro['request_prefix'])];attempts=[e for e in events if e['kind']in('admission','transport_validation_rejection')]
    lessons=[e for e in attempts if any(s.get('modo')=='apd-docencia'or s.get('operacion_memoria')=='revisar'for s in e['payload'].get('situaciones',[]))]
    executed_lessons=[r for r in selected if r.get('result')and any(s.get('modo')=='apd-docencia'or s.get('operacion_memoria')=='revisar'for s in json.loads(r['payload']).get('situaciones',[]))]
    if executed_lessons:raise ValueError('A lesson really executed; do not call the corresponding form untaught')
    witness={'schema':'DEE.APD01.interrupted_R02_preservation.v1','original_RESULTADO_sha256':original_result_sha,'main':{k:record.get(k)for k in('life_id','world_id','parent','snapshot','snapshot_sha256','physical')},'VIDA_sha256':card_sha,'journal_sha256':sha(db),'owner':owner,'pending_rows':pending,'paired_export':{'manifest':str(package/'EXPORTACION_SERVICIO.json'),'manifest_sha256':sha(package/'EXPORTACION_SERVICIO.json'),'verification':verification},'recorded_fixed_horizon_reached':False,'sixty_minutes_claimed':False,'actual_owner_ready_to_stop_completion_seconds':elapsed,'recorded_pause_discount_seconds':discount,'incomplete_second_pause_to_explicit_stop_seconds':unfinished_pause,'observed_mode_enabled_seconds_before_technical_stop':elapsed-discount,'total_harness_seconds':result['host_seconds_total'],'nominal_opportunities_attempted':sum(e['id']in{v['id']for v in pro['events']}for e in attempts),'selected_transport_rows':len(selected),'explicit_teaching_or_beta_revision_attempts':len(lessons),'executed_explicit_teaching_or_beta_revision_rows':len(executed_lessons),'explicit_stop_record':stop_row,'error_class':'Busy FIFO left BEGIN queued, so the prospective pause did not have a formed native cascade; technical window rejected and owner remained paused until the authorized explicit stop. Not a demonstrated worker or memory failure.','new_ticks_for_this_preservation':0,'sources_unchanged':all(r['unchanged']for r in result['final_source_integrity']),'scope':'The original missing-horizon negative estimate is preserved, not physical time. Entire unresumed second pause is discounted. No R01/R02 minute counts toward a new sixty-minute reserve; no pending queue or native field is erased.'}
    if sha(card)!=card_sha or sha(db)!=witness['journal_sha256']or sha(trial/'RESULTADO.json')!=original_result_sha:raise ValueError('Current/original bytes changed while inspected')
    write(trial/'CORTE_INTERRUMPIDO.json',witness);print(json.dumps({'cut':str(trial/'CORTE_INTERRUMPIDO.json'),'snapshot_sha256':record['snapshot_sha256'],'tick':record['physical']['tick'],'pending':len(pending),'members':len(members),'actual_mode_seconds':elapsed-discount}))
if __name__=='__main__':main()
