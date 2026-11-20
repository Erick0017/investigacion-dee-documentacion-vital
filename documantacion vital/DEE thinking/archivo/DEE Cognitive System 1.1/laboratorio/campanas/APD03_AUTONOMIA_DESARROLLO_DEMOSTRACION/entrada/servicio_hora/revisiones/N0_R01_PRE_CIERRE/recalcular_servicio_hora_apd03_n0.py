"""Read-only APD03 service-hour audit, NOT a native/cognitive experiment.

Reads only already-closed JSON/GZip members. Never imports DEE, opens a live
journal, creates a Runtime, starts an owner or advances a tick. A partial run
is reported as partial; absence of closing evidence is not fabricated success.
Scientific action/learning/RAW claims are deliberately left to the actor audit.
"""
import argparse
from collections import Counter
from datetime import datetime
import gzip
import hashlib
import json
from pathlib import Path
import shutil


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1048576),b''):h.update(block)
    return h.hexdigest()
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def read(path):
    data=Path(path).read_bytes()
    return json.loads(gzip.decompress(data) if Path(path).suffix=='.gz' else data)
def utc(value):return datetime.fromisoformat(value.replace('Z','+00:00')).timestamp()
def unwrap(value):return value.get('request') or value
def physical_equal(a,b):return all(a[k]==b[k] for k in('N','tick','RAW_sha256','clocks_sha256'))
def request_pair(row):
    payload=json.loads(row['payload']);result=json.loads(row['result']) if row.get('result') else None
    actual=hashlib.sha256(canonical(payload).encode('utf8')).hexdigest()
    if row['payload_sha']!=actual:raise ValueError('Payload SHA is not the canonical literal request:'+str(row['id']))
    if result is not None and result['id']!=row['id']:raise ValueError('Result ID changed:'+str(row['id']))
    return payload,result
def same_queued_row(old,new):
    fields=('id','payload','payload_sha','arrived_utc','arrived_ns','seq','is_control')
    if any(old[k]!=new[k] for k in fields):raise ValueError('Queued row identity/payload/arrival changed across owners')
    if old['status']!='queued' or new['status']!='completed':raise ValueError('Not the recorded queued-to-completed transition')
    request_pair(old);request_pair(new)
    return fields


class Audit:
    def __init__(self,root,require_closed=False):
        self.root=Path(root).resolve(strict=True);self.require_closed=require_closed;self.checks=0;self.issues=[];self.pending=[];self.inputs=[]
    def check(self,condition,message):
        self.checks+=1
        if not condition:self.issues.append(message)
        return bool(condition)
    def data(self,name,required=True):
        path=self.root/name
        if not path.is_file():
            if required:self.issues.append('Required recorded evidence absent:'+name)
            else:self.pending.append(name)
            return None
        value=read(path);self.inputs.append({'file':name,'bytes':path.stat().st_size,'sha256':sha(path)})
        return value
    def rows(self,directory):
        answer=[]
        for path in sorted((self.root/directory).glob('*.json*')):
            answer.append(self.data(path.relative_to(self.root).as_posix()))
        return answer
    def audit_request(self,row,life):
        payload,result=request_pair(row)
        self.check(row['status']=='completed','A logged control/material request is not completed:'+row['id'])
        if result is not None:
            self.check(result['before_tick']<=result['after_tick'],'Native ticks reversed in result:'+row['id'])
            if 'committed_snapshot'in result:
                cut=result['committed_snapshot'];self.check(cut['life_id']==life,'Committed result belongs to another life:'+row['id'])
                self.check(cut['physical']['tick']==result['after_tick'],'Committed snapshot/result tick differs:'+row['id'])
        return payload,result
    def run(self):
        before=self.data('ANTES_DEL_PRIMER_TICK.json')
        if before is None:return self.finish({'phase':'missing_start'})
        plan=before['plan'];life=plan['life'];initial=before['initial_record'];self.life=life
        self.check(before['native_not_started']is True,'Initial record does not predate the owner')
        self.check(initial['life_id']==life and initial['world_id']==life,'Initial life/world mismatch')
        self.check(initial['physical']['tick']==plan['initial_tick'],'Initial tick differs from predeclared current import')
        self.check(initial['snapshot_sha256']==plan['initial_imported_snapshot_sha256'],'Initial physical import changed')
        self.check(initial['parent']['encoded_sha256']==plan['parent_snapshot_sha256'],'Initial parent differs')
        self.check(before['ui_protocol']['world_id']==life and before['ui_protocol']['source_snapshot_sha256']==plan['parent_snapshot_sha256'],'Initial UI does not refer to the recorded paired parent')
        self.check(before['ui_protocol']['uncertain_preserved']is False,'Initial uncertainty was not resolved/preserved as declared')
        self.check(before['config']['memory_limit_bytes']==536870912,'Native owner memory contract is not512MiB')
        source_coverage=[]
        for row in before['sources']:
            path=self.root/row['file']
            present=path.is_file();source_coverage.append({'file':row['file'],'included':present})
            if present:
                self.check(path.stat().st_size==row['bytes']and sha(path)==row['sha256'],'Frozen copied source mismatch:'+row['file'])
        events=self.rows('EVENTOS');heartbeats=self.rows('HEARTBEATS');blocks=self.rows('BLOQUES')
        self.check([e['index']for e in events]==list(range(len(events))),'Incremental events are not a contiguous recorded prefix')
        starts=[e for e in events if e['kind']=='start_paused']
        self.check(len(starts)==1,'Recorded MAIN prefix must contain exactly one initial owner start')
        if not starts:return self.finish({'phase':'missing_owner_start','life':life})
        start=starts[0]['start'];owner=start['observation'];pid=owner['pid'];epoch=owner['epoch']
        self.check(start['started_paused']and owner['paused']and owner['running'],'Initial owner not recorded started paused')
        self.check(owner['life_id']==life and physical_equal(owner['physical'],initial['physical']),'First owner did not load exact selected physical state')
        self.check(owner['runtime_loads_in_this_process']==1,'Owner did not report exactly one Runtime load')
        ids={};counts=Counter();control_operations=Counter();paused_records=[];last_elapsed=-1;last_before_tick=initial['physical']['tick'];material_tags=[]
        for event in events:
            self.check(event['driver_elapsed_seconds']>=last_elapsed,'Driver event monotonic timestamps regress')
            last_elapsed=event['driver_elapsed_seconds']
            if event['kind']in('control','material'):
                row=unwrap(event['result'] if event['kind']=='control' else event['transport_result'])
                self.check(row['id']not in ids,'A logged new submission duplicated an ID:'+row['id']);ids[row['id']]=row
                payload,result=self.audit_request(row,life);counts[(event['kind'],row['status'])]+=1
                if result is not None:
                    self.check(result['before_tick']>=last_before_tick,'Sequential completed requests reverse their before_tick')
                    last_before_tick=result['after_tick'];self.check(result['owner_epoch']==epoch,'MAIN request changed owner epoch inside first service window')
                if event['kind']=='control':
                    operation=event['operation'];control_operations[operation]+=1
                    self.check(row['is_control']==1 and payload=={'operacion':operation},'Control payload differs from literal operation')
                    if operation=='pausar':paused_records.append(event)
                else:
                    material_tags.append(event['tag'])
                    expected={'operacion':'sesion','situaciones':event['literal_situations'],'retorno':event['feedback'],'actuador':'closed'}
                    self.check(row['is_control']==0 and payload==expected,'Material payload is not the declared literal request:'+event['id'])
                    self.check(row['id']==event['id'],'Event/queue material ID differs')
                    self.check(result==event['decoded_result'],'Recorded decoded material is not the queue result')
                    self.check(all(p['id']==row['id']for p in event['read_only_same_ID_polls']),'A wait polled another material ID')
            elif event['kind']=='checkpoint':
                record=event['record'];self.check(record['life_id']==life and record['world_id']==life,'Checkpoint changed life/world')
                self.check(record['snapshot_sha256']==event['copied_snapshot_sha256'],'Checkpoint copy digest mismatch')
                self.check(record['parent']==initial['parent'],'Checkpoint genealogy changed')
        begin=self.data('INICIO_VENTANA_CONGELADA.json',required=False)
        end=self.data('FIN_VENTANA_CONGELADA.json',required=False)
        window={'closed':end is not None,'minimum_seconds':plan['evolving_window_minimum_seconds'],'not_CPU_time':True,'not_cached_tick_speed':True}
        if begin is not None:
            self.check(begin['minimum_seconds']==plan['evolving_window_minimum_seconds'],'Window minimum differs from predeclared program')
            self.check(begin['owner']==start,'Reserved window changed initial owner identity')
            self.check(begin['no_more_engineering_during_window']is True,'Source freeze not declared')
        if begin is not None and end is not None:
            delta=end['monotonic']-begin['monotonic'];window['monotonic_seconds']=delta
            self.check(abs(delta-end['actual_enabled_seconds'])<0.000001,'Window seconds are not the recorded monotonic difference')
            self.check(delta>=plan['evolving_window_minimum_seconds'],'Recorded evolving window did not reach its predeclared minimum')
            self.check(end['owner']==start,'Closing window changed owner')
            self.check(end['sources_unchanged']is True,'Frozen source attestation failed at window end')
            in_window=[e for e in paused_records if utc(begin['wall_utc'])<=utc(e['wall_utc'])<=utc(end['wall_utc'])]
            window['recorded_pause_controls_inside_window']=len(in_window)
            self.check(not in_window,'A pause control occurred inside the claimed continuously enabled window')
        observed_ticks=[];observed_enabled=[];cache_ages=[]
        for h in heartbeats:
            status=h['cached_status'];published=status['ESTADO_PUBLICADO'];obs=published['observation'];instrument=status['INSTRUMENTO']
            self.check(published['no_material_probe']and instrument['no_material_probe'],'Heartbeat added a material query')
            self.check(obs['life_id']==life and instrument['world_id']==life,'Heartbeat life/world changed')
            self.check(obs['pid']==pid and obs['epoch']==epoch and obs['runtime_loads_in_this_process']==1,'Heartbeat owner/epoch/Runtime load changed')
            self.check(obs['running']and obs['paused']is False,'Heartbeat does not confirm enabled owner')
            self.check(obs['tick']==obs['physical']['tick'],'Published native/physical tick differs')
            self.check(instrument['uncertain_preserved']is False,'Supervisor preserved uncertainty during window')
            self.check(h['job']['job_memory_limit']==536870912,'Heartbeat Native owner resource scope changed')
            observed_ticks.append(obs['tick']);observed_enabled.append(h['enabled_elapsed_seconds']);cache_ages.append(published['cache_age_seconds'])
        self.check(observed_ticks==sorted(observed_ticks),'Passive sampled Native ticks regress')
        self.check(observed_enabled==sorted(observed_enabled),'Heartbeat enabled monotonic elapsed regresses')
        gaps=[b-a for a,b in zip(observed_enabled,observed_enabled[1:])]
        window['passive_observation']={'samples':len(heartbeats),'first_tick':observed_ticks[0]if observed_ticks else None,'last_tick':observed_ticks[-1]if observed_ticks else None,'last_enabled_seconds_observed':observed_enabled[-1]if observed_enabled else None,'max_gap_seconds':max(gaps,default=None),'max_cache_age_seconds':max(cache_ages,default=None),'negative_cache_ages':sum(v<0 for v in cache_ages),'coverage':'Sampled cached status plus exact command/event log; not a per-tick trace or instantaneous wall/tick synchrony.'}
        for block in blocks:
            expected=next((r for r in plan['blocks']if r['id']==block['id']),None)
            self.check(expected is not None,'Unknown reserved block appeared')
            if expected is not None:
                self.check(block['scheduled_seconds']==expected['at_seconds'],'Reserved block schedule changed')
                self.check(block['actual_start_enabled_seconds']>=expected['at_seconds'],'Reserved block began before its declared offset')
                lo,hi=block['events'];self.check(0<=lo<=hi<=len(events),'Block event slice absent from recorded prefix')
                actual=[e['tag']for e in events[lo:hi]if e['kind']=='material'];planned=[]
                for row in expected['events']:planned.extend([row['id']+'_init',row['id']+'_offered']if row['kind']=='goal'else[row['id']])
                self.check(actual==planned,'Reserved block material order differs:'+block['id'])
        final=self.data('REGISTROS_VENTANA.json.gz',required=False)
        continuity={'closed':False,'same_queued_ID_checked':False,'new_native_ticks_in_this_audit':0}
        if final is not None:
            self.check(final['life']==life and final['initial_record']==initial,'Final summary changed initial identity')
            self.check(final['events']==events,'Final summary/events do not match incremental primary bytes after JSON decode')
            self.check(final['error']is None,'Main run recorded an error; this audit preserves it')
            self.check(final['sources_unchanged']and final['protected_originals_unchanged'],'Frozen/protected source attestation failed')
            self.check(not final['native_engine_imported_in_driver'],'The driver imported the engine unexpectedly')
            self.check(final['energy']=='NO MEDIDA','Unmeasured energy was relabeled')
            self.check(final['forced_child_cleanup']is None,'A host-forced stop occurred; no clean ordinary-stop claim')
            for row in final['sources']:self.check(row['actual_sha256']==row['sha256']and row['unchanged'],'Final source receipt mismatch:'+row['file'])
            for row in final['protected_originals']:self.check(row['actual_sha256']==row['sha256']and row['unchanged'],'Protected source receipt mismatch:'+row['path'])
            if begin is not None and end is not None:self.check(abs(final['enabled_seconds']-(end['monotonic']-begin['monotonic']))<0.000001,'Final enabled seconds differ')
            pending=self.data('CORTE_PENDIENTE_POSTSTOP.json',required=False);continued=self.data('CONTINUACION_OTRO_PROCESO.json.gz',required=False);last=self.data('CORTE_FINAL_POSTSTOP.json',required=False)
            if pending is not None and continued is not None and last is not None:
                self.check(final['first_stopped_pending_cut']==pending and final['continuation']==continued and final['final_stopped_cut']==last,'Final summary changed exact closing primaries')
                outstanding=pending['outstanding'];self.check(len(outstanding)==1,'Pending cut does not contain exactly one queued row')
                if len(outstanding)==1:
                    old=outstanding[0];new=unwrap(continued['same_queued_ID_result']);fields=same_queued_row(old,new)
                    self.check(old['id']==plan['after_window']['queued_request_id'],'Queued pending ID differs from prospective program')
                    self.check(json.loads(old['payload'])['situaciones']==plan['after_window']['queued_situations'],'Queued situations were changed')
                    continuity.update(same_queued_ID_checked=True,preserved_queue_fields=list(fields),queued_id=old['id'],queued_seq=old['seq'],queued_arrived_utc=old['arrived_utc'])
                self.check(pending['owner']['running']is False and last['owner']['running']is False,'A paired cut still records a running owner')
                self.check(not last['outstanding'],'Final stopped cut still contains pending/uncertain requests')
                ready=continued['ready_before_new_input'];self.check(ready['life_id']==life,'Reopen changed life')
                self.check(physical_equal(ready['physical'],pending['record']['physical']),'Reopen did not load the stopped physical state before input')
                self.check(ready['pid']!=pid,'Second ordinary Native owner does not have a new process identity')
                self.check(continued['returncode']==0,'Second ordinary UI returned an error')
                self.check(continued['source_Main_not_reimported']and continued['same_original_queue_row_fields_preserved'],'Continuation reports a reimport or changed pending row')
                self.check(continued['native_job_after']['job_active_processes']==0,'Second owned Native job did not close')
                self.check(last['record']['parent']==initial['parent']and last['record']['life_id']==life,'Final biography differs')
                continuity.update(closed=True,first_native_PID=pid,reopened_native_PID=ready['pid'],first_stop_tick=pending['record']['physical']['tick'],final_tick=last['record']['physical']['tick'])
            journal=self.root/'SESIONES_UI_NUEVAS.jsonl.gz'
            if journal.is_file():
                lines=[json.loads(s)for s in gzip.decompress(journal.read_bytes()).splitlines()if s];self.inputs.append({'file':journal.name,'bytes':journal.stat().st_size,'sha256':sha(journal)})
                submissions=[r for r in lines if r['event']=='literal_material_submission'];hist=Counter(r['id']for r in submissions)
                self.check(all(count==1 for count in hist.values()),'UI submitted a material ID more than once')
                self.check(all(r['life_id']==life for r in lines),'UI journal mixes lives')
                self.check(not any(r['event']=='explicit_complete_paired_import'for r in lines),'Hour/reopening unexpectedly imported a fresh life')
                starts_ui=[r for r in lines if r['event']=='owned_start_paused'];stops_ui=[r for r in lines if r['event']=='owned_stop']
                self.check(len(starts_ui)==2 and len(stops_ui)==2,'Expected two sequential owners with confirmed STOP, not a restart inside the hour')
                pending_id=plan['after_window']['queued_request_id'];self.check(hist[pending_id]==1,'Pending goal was not submitted exactly once')
                self.check(any(r['event']=='same_id_read_only_result'and r['id']==pending_id and r['no_requeue']for r in lines),'Reopening same-ID reconciliation is not recorded')
                continuity['UI_material_submissions']=len(submissions);continuity['UI_recorded_owner_starts']=len(starts_ui);continuity['UI_recorded_owner_stops']=len(stops_ui)
            else:self.pending.append(journal.name)
        closed=bool(end is not None and final is not None and continuity['closed'])
        if self.require_closed:self.check(closed,'A complete recorded closure is required but absent')
        return self.finish({'phase':'closed'if closed else'incremental_not_closed','life':life,'parent':initial['parent'],'initial_tick':initial['physical']['tick'],'first_owner_PID':pid,'epoch':epoch,'window':window,'continuity':continuity,'transport_logged_new_submission_denominators':[{'kind':kind,'status':status,'count':n}for(kind,status),n in sorted(counts.items())],'control_operations':dict(control_operations),'reserved_blocks_recorded':[r['id']for r in blocks],'source_copies':{'listed':len(source_coverage),'included_and_hash_checked':sum(r['included']for r in source_coverage),'omitted':[r['file']for r in source_coverage if not r['included']]},'interpretation':'This is service/identity/transport/continuation evidence only, not proof of useful decisions, learning, energy, human use, Full independence or general intelligence.'})
    def finish(self,results):
        return {'schema':'APD03.service_hour.read_only_recalculation.R01','new_native_ticks':0,'new_processes':0,'checks':self.checks,'issues':self.issues,'pending_closing_evidence':sorted(set(self.pending)),'results':results,'inputs':self.inputs}


def extract_existing(source,destination):
    source=Path(source).resolve(strict=True);destination=Path(destination).resolve()
    if destination.exists():raise FileExistsError('Existing extraction preserved; choose a new empty destination')
    paths=[]
    for name in('ANTES_DEL_PRIMER_TICK.json','INICIO_VENTANA_CONGELADA.json','FIN_VENTANA_CONGELADA.json','REGISTROS_VENTANA.json.gz','CORTE_PENDIENTE_POSTSTOP.json','CONTINUACION_OTRO_PROCESO.json.gz','CORTE_FINAL_POSTSTOP.json','SESIONES_UI_NUEVAS.jsonl.gz','ERROR_PRESERVADO.json'):
        if(source/name).is_file():paths.append(source/name)
    for folder in('EVENTOS','HEARTBEATS','BLOQUES','FUENTES_ANTES_DE_NATIVE'):
        paths.extend(p for p in(source/folder).rglob('*')if p.is_file())
    for folder in('PAR_POSTSTOP_PENDIENTE','PAR_POSTSTOP_FINAL'):
        if(source/folder/'EXPORTACION_SERVICIO.json').is_file():paths.append(source/folder/'EXPORTACION_SERVICIO.json')
    destination.mkdir(parents=True,exist_ok=False);members=[]
    for path in sorted(paths):
        relative=path.relative_to(source);target=destination/relative;target.parent.mkdir(parents=True,exist_ok=True)
        before=sha(path);shutil.copyfile(path,target)
        if sha(path)!=before or sha(target)!=before:raise ValueError('Recorded source changed during read-only extraction:'+relative.as_posix())
        members.append({'file':relative.as_posix(),'bytes':path.stat().st_size,'sha256':before})
    omitted=[]
    for folder in('CHECKPOINTS','PAR_POSTSTOP_PENDIENTE','PAR_POSTSTOP_FINAL'):
        for path in sorted((source/folder).rglob('*')):
            if path.is_file()and path not in paths:omitted.append({'source_local':str(path),'bytes':path.stat().st_size,'sha256':sha(path),'reason':'Full snapshots/journals/artifacts are operational state retained locally; not needed for this service-only JSON recalculation.'})
    manifest={'schema':'APD03.service_hour.essential_exact_export.R01','members':members,'omitted':omitted,'source':str(source),'new_native_ticks':0,'not_an_operational_backup':True}
    with(destination/'MANIFIESTO_EXTRACCION.json').open('x',encoding='utf8',newline='\n')as stream:json.dump(manifest,stream,ensure_ascii=False,sort_keys=True,indent=2);stream.write('\n')
    return destination


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);p.add_argument('--requiere-cierre',action='store_true');p.add_argument('--extraer',type=Path);a=p.parse_args()
    root=extract_existing(a.evidencia,a.extraer)if a.extraer else a.evidencia
    result=Audit(root,require_closed=a.requiere_cierre).run()
    with a.salida.open('x',encoding='utf8',newline='\n')as stream:json.dump(result,stream,ensure_ascii=False,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps({'new_native_ticks':0,'phase':result['results']['phase'],'checks':result['checks'],'issues':result['issues'],'closing_evidence_pending':result['pending_closing_evidence']},ensure_ascii=False))
    return bool(result['issues'])
if __name__=='__main__':raise SystemExit(main())
