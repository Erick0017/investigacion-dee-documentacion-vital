"""Fresh scoped affected-writer proof, stdlib only. No DEE/CIM/WMI/stop.

Checks only protected parent, candidate source and prospective product target.
Cached statuses are corroborated with locks/closed immutable SQLite, actual
owner journals and Win32 handles. Ambiguity/access denial fails closed.
"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import argparse,ctypes,hashlib,importlib.util,json,os,sqlite3
H=Path(__file__).resolve().parent;P=H.parent;C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';CS=P/'estados/candidato/sistema'
PARENT='ECI02_PI03_MAIN';SOURCE='ECI02_PI03_REPRO_PI04_PI05_GUARD_01';TARGET='ECI02_PI03_REPRO_PI04_PI05_MAIN_01'
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):
    h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def regular(p):
    for q in(p,*p.parents):
        if q.exists()and(q.is_symlink()or getattr(q.lstat(),'st_file_attributes',0)&1024):raise ValueError('Reparse path refused: '+str(q))
def pid_probe(pid):
    if os.name!='nt':raise ValueError('This scoped process witness requires native Windows Win32')
    k=ctypes.WinDLL('kernel32',use_last_error=True)
    k.OpenProcess.argtypes=[ctypes.c_uint32,ctypes.c_int,ctypes.c_uint32];k.OpenProcess.restype=ctypes.c_void_p
    k.GetExitCodeProcess.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_uint32)];k.GetExitCodeProcess.restype=ctypes.c_int
    k.CloseHandle.argtypes=[ctypes.c_void_p];k.CloseHandle.restype=ctypes.c_int
    handle=k.OpenProcess(0x1000,False,pid)
    if not handle:
        err=ctypes.get_last_error()
        return {'pid':pid,'observation':'PID_ABSENT'if err==87 else'QUERY_DENIED_OR_UNKNOWN','windows_error':err,'confirmed_not_alive':err==87}
    try:
        code=ctypes.c_uint32()
        if not k.GetExitCodeProcess(handle,ctypes.byref(code)):return {'pid':pid,'observation':'GET_EXIT_CODE_FAILED','windows_error':ctypes.get_last_error(),'confirmed_not_alive':False}
        result={'pid':pid,'observation':'STILL_ACTIVE'if code.value==259 else'PROCESS_EXITED','exit_code':code.value,'confirmed_not_alive':code.value!=259}
        # Creation/exit timestamps identify PID reuse for manual diagnosis, but
        # never turn an active PID into an automatic absent-writer assertion.
        class FT(ctypes.Structure):_fields_=[('low',ctypes.c_uint32),('high',ctypes.c_uint32)]
        k.GetProcessTimes.argtypes=[ctypes.c_void_p,*([ctypes.POINTER(FT)]*4)];k.GetProcessTimes.restype=ctypes.c_int
        times=[FT()for _ in range(4)]
        if k.GetProcessTimes(handle,*[ctypes.byref(x)for x in times]):
            def stamp(t):
                value=(t.high<<32)|t.low
                return None if not value else(datetime(1601,1,1,tzinfo=timezone.utc)+timedelta(microseconds=value//10)).isoformat()
            result['created_utc']=stamp(times[0]);result['exit_utc']=stamp(times[1])
        k.QueryFullProcessImageNameW.argtypes=[ctypes.c_void_p,ctypes.c_uint32,ctypes.c_wchar_p,ctypes.POINTER(ctypes.c_uint32)]
        k.QueryFullProcessImageNameW.restype=ctypes.c_int
        size=ctypes.c_uint32(32768);image=ctypes.create_unicode_buffer(size.value)
        if k.QueryFullProcessImageNameW(handle,0,image,ctypes.byref(size)):
            result['process_image']=image.value
        else:result['process_image_query_error']=ctypes.get_last_error()
        return result
    finally:k.CloseHandle(handle)
def journal_evidence(path,life):
    if not path.exists():return {'path':str(path),'available':False}
    starts={};closed={};selected=[]
    with path.open('r',encoding='utf-8-sig')as f:
        for number,line in enumerate(f,1):
            if not line.strip():continue
            row=json.loads(line)
            if row.get('life')!=life or row.get('kind')not in('OWNER_STARTED','OWNER_CLOSED','OWN_CLOSE_PROBLEM'):continue
            item={'line':number,'kind':row['kind'],'run':row.get('run'),'pid':row.get('pid'),'exit_code':row.get('exit_code')}
            if row['kind']=='OWNER_STARTED':
                command=row.get('command')
                item['command_image_only']=command[0]if isinstance(command,list)and command else None
            if row['kind']=='OWNER_CLOSED':
                final=row.get('final_status')or{}
                item['closed_cache_wall_utc']=final.get('wall_utc')
                item['closed_cache_running']=final.get('running')
                item['closed_cache_pid']=final.get('pid')
            if row['kind']=='OWNER_STARTED':starts[row.get('run')]=item
            elif row['kind']=='OWNER_CLOSED':closed[row.get('run')]=item
            selected.append(item)
    for run,item in closed.items():
        item['matched_started_record']=starts.get(run)
    return {'path':str(path),'sha256':sha(path),'available':True,'matching_records':len(selected),
        'last_relevant_records':selected[-8:],'started_runs_without_closed':[r for r in starts if r not in closed],
        'last_close':next((r for r in reversed(selected)if r['kind']=='OWNER_CLOSED'),None)}

def prove_reused_other_image(observed,evidence,scope_sources):
    """One sound exception to PID liveness: a later DIFFERENT executable.

    The current process remains alive. Only absence of the historical Native
    owner is asserted, with exact successful owner-close journal provenance.
    Unknown image/time/mismatched closure still blocks; no process is stopped.
    """
    if observed.get('observation')!='STILL_ACTIVE'or any(x.startswith('explicit_')for x in scope_sources):return None
    image=observed.get('process_image');created=observed.get('created_utc')
    if not image or not created:return None
    official=str((C/'motor/python313/python.exe').resolve()).casefold()
    if str(Path(image).resolve()).casefold()==official:return None
    creation=datetime.fromisoformat(created.replace('Z','+00:00'))
    closures=[]
    for life in evidence:
        if life.get('error'):continue
        owner=life.get('cached_owner')or{}
        for journal in life.get('owner_journals',[]):
            closed=journal.get('last_close');started=(closed or{}).get('matched_started_record')or{}
            if not closed or closed.get('pid')!=observed['pid']or closed.get('exit_code')!=0:continue
            stamp=closed.get('closed_cache_wall_utc')
            if not stamp or closed.get('closed_cache_running')is not False or closed.get('closed_cache_pid')!=observed['pid']:continue
            expected_image=started.get('command_image_only')
            if started.get('pid')!=observed['pid']or not expected_image or str(Path(expected_image).resolve()).casefold()!=official:continue
            closed_cache=datetime.fromisoformat(stamp.replace('Z','+00:00'))
            if closed_cache.tzinfo is None or not closed_cache<creation:continue
            if owner.get('pid')==observed['pid']and(owner.get('running')is not False or owner.get('wall_utc')!=stamp):continue
            closures.append({'life_id':life['life_id'],'journal':journal['path'],'journal_sha256':journal['sha256'],
                'closed_line':closed['line'],'started_line':started['line'],'run':closed['run'],
                'old_owner_executable':expected_image,'old_owner_exit_code':0,'closed_cache_wall_utc':stamp,
                'new_process_created_utc':created,'new_process_image':image,
                'new_process_created_seconds_after_closed_cache':(creation-closed_cache).total_seconds()})
    if not closures:return None
    return {'classification':'PID_REUSED_OTHER_IMAGE','current_process_is_alive':True,
        'historical_affected_Native_owner_is_absent':True,'proofs':closures,
        'reason':'Exact same PID belonged to a successfully closed official-Python owner; current different executable was created later. Closed affected caches/queues and no locks are independently checked.'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--salida',type=Path,required=True);ap.add_argument('--source-tick',type=int,default=824911)
    ap.add_argument('--known-pid',action='append',type=int,default=[]);args=ap.parse_args()
    output=args.salida.resolve(strict=False);regular(output)
    if output.exists()or not output.is_relative_to((P/'control').resolve()):raise ValueError('New unique output under current PI05/control only; never overwrite a witness')
    parserpath=C/'reproducibilidad/observador_pasivo.py';spec=importlib.util.spec_from_file_location('PI05_fresh_process_snapshot_parser',parserpath)
    parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
    targets=[(S,PARENT,775355),(CS,SOURCE,args.source_tick),(S,TARGET,None)]
    evidence=[];errors=[];pids={int(p):['explicit_Root_managed_Native_PID']for p in args.known_pid};critical={}
    def remember(p):critical[str(p)]=sha(p)
    for system,life,expected_tick in targets:
        item={'system':str(system),'life_id':life,'inspection_utc':now()};evidence.append(item)
        try:
            cardfile=system/'estado/vidas'/life/'VIDA.json'
            if not cardfile.exists():
                item['exists']=False
                if life!=TARGET:raise ValueError('Required affected life card inaccessible')
                continue
            regular(cardfile);item['exists']=True;card=read(cardfile);remember(cardfile)
            if card['life_id']!=life or card['physical']['N']!=67:raise ValueError('Affected identity/dimension mismatch')
            if expected_tick is not None and card['physical']['tick']!=expected_tick:raise ValueError('Affected stable cut differs from expected: '+str(card['physical']['tick']))
            item['world_id']=card['world_id'];item['tick']=card['physical']['tick'];item['card_sha256']=sha(cardfile)
            markers=[system/'estado/locks'/(card['world_id']+'.lock'),system/'estado/locks'/(life+'.lock'),
                system/'estado/locks/promotion_registry.lock',cardfile.parent/'FUTURO_INTERRUMPIDO.json',
                system/'estado/servicios_persistentes'/life/'IMPORTACION_EN_CURSO.json']
            markers+=list(system.glob('*.lock'))+list((system/'estado').glob('*.lock'))
            item['lock_or_interruption_markers']=[str(x)for x in dict.fromkeys(markers)if x.exists()]
            if item['lock_or_interruption_markers']:raise ValueError('Affected/root lock or interrupted import present')
            snapshot=(system/card['snapshot']).resolve(strict=True);regular(snapshot)
            if not snapshot.is_relative_to((system/'estado/checkpoints').resolve())or sha(snapshot)!=card['snapshot_sha256']:raise ValueError('Current complete snapshot pointer/hash mismatch')
            remember(snapshot);view=parser.snapshot_view(snapshot);item['snapshot_sha256']=view['encoded_sha256'];item['pending_Native_inputs']=view['pending_native']
            if any(view['physical'][k]!=card['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')):raise ValueError('Snapshot/card physical cut mismatch')
            service=json.loads(view['metadata'].get(parser.SERVICE_KEY,'{}'));pid=service.get('pid_at_checkpoint')
            item['Native_service_checkpoint']={k:service.get(k)for k in('life_id','pid_at_checkpoint','native_tick_at_checkpoint','paused','uncertain_external_result','closed_epoch')}
            if type(pid)is int and pid>0:pids.setdefault(pid,[]).append(life+':Native_service_checkpoint')
            if service.get('uncertain_external_result'):raise ValueError('Affected Native service reports uncertainty')
            db=system/'estado/servicios_persistentes'/life/'cola.sqlite3'
            if db.exists():
                regular(db);aux=[Path(str(db)+s)for s in('-wal','-shm','-journal')]
                item['SQLite_auxiliaries']=[{'path':str(p),'bytes':p.stat().st_size}for p in aux if p.exists()]
                if item['SQLite_auxiliaries']:raise ValueError('SQLite auxiliaries present; no incoherent closed copy/read claim')
                remember(db);q=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
                try:
                    if q.execute('pragma integrity_check').fetchone()[0]!='ok':raise ValueError('Affected closed SQLite integrity failure')
                    row=q.execute("select value from meta where key='owner'").fetchone();owner=None if row is None else json.loads(row[0])
                    counts=dict(q.execute('select status,count(*)from requests group by status'))
                    pending=q.execute("select id,status from requests where status in('queued','processing','uncertain','failed_preserved')").fetchall()
                finally:q.close()
                item['cached_owner']=owner;item['transport_status_counts']=counts;item['unresolved_requests']=pending
                if owner:
                    if owner.get('running')is not False or owner.get('uncertain_external_result'):raise ValueError('Affected cached owner is not explicitly closed')
                    if type(owner.get('pid'))is int:pids.setdefault(owner['pid'],[]).append(life+':closed_SQLite_owner_cache')
                if pending:raise ValueError('Affected journal has unresolved/failed-preserved requests')
            journals=[P/'ENSAYOS.jsonl',P.with_name('PROGRESION_INTEGRADA_03')/'ENSAYOS.jsonl']
            item['owner_journals']=[journal_evidence(j,life)for j in journals]
            # Only the latest explicit successful closure corroborates a PID.
            for j in item['owner_journals']:
                last=j.get('last_close')
                if last and type(last.get('pid'))is int:
                    pids.setdefault(last['pid'],[]).append(life+':last_actual_OWNER_CLOSED_journal')
                    if last['exit_code']!=0:raise ValueError('Latest affected owner journal closure is not exit0')
        except Exception as e:
            item['error']={'type':type(e).__name__,'message':str(e)};errors.append({'life_id':life,**item['error']})
    handles=[]
    for pid,sources in sorted(pids.items()):
        try:observed=pid_probe(pid)
        except Exception as e:observed={'pid':pid,'confirmed_not_alive':False,'error':type(e).__name__+': '+str(e)}
        observed['scope_sources']=sources;handles.append(observed)
        reused=prove_reused_other_image(observed,evidence,sources)
        if reused:observed['reused_PID_proof']=reused
        if not observed.get('confirmed_not_alive')and reused is None:errors.append({'pid':pid,'error':'Live or unqueryable affected/cached PID; do not assume absence'})
    after={}
    for name,before in critical.items():
        try:after[name]=sha(Path(name))
        except Exception as e:errors.append({'file':name,'error':'Critical file inaccessible after inspection: '+str(e)});continue
        if after[name]!=before:errors.append({'file':name,'error':'Critical affected file changed concurrently'})
    # Recheck target locks after reads/Win32 calls to close the observation window.
    for system,life,_ in targets:
        cf=system/'estado/vidas'/life/'VIDA.json'
        if cf.exists():
            record=read(cf)
            for lock in(system/'estado/locks'/(record['world_id']+'.lock'),system/'estado/locks/promotion_registry.lock'):
                if lock.exists():errors.append({'file':str(lock),'error':'Lock appeared by end of scoped inspection'})
    proof={'schema':'DEE.PI05.fresh_affected_writer_proof.R02_PID_identity','recorded_utc':now(),'no_live_affected_writers':not errors,
        'scope':'Only exact protected product PI03 parent, final S5 GUARD source and prospective product PI05 target; no global process census, no CIM/WMI, no stopping or DEE imports. Cached status is corroborated by fresh Win32 handles, closed SQLite and actual owner logs.',
        'affected_life_ids':[PARENT,SOURCE,TARGET],'evidence':evidence,'Win32_process_handles':handles,'errors':errors,
        'critical_before_sha256':critical,'critical_after_sha256':after,'Native_executed':False,'new_ticks':0,
        'unrelated_worlds_or_processes_not_claimed_closed':True,'fresh_for_seconds_max':600}
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'output':str(output),'sha256':sha(output),'no_live_affected_writers':not errors,'errors':errors,'Native_ticks':0},ensure_ascii=False))
    return 0 if not errors else 2
if __name__=='__main__':raise SystemExit(main())
