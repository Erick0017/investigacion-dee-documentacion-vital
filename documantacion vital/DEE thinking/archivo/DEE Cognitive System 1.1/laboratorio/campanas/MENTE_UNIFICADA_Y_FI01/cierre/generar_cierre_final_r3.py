"""Build the final scientific continuity receipt from CLOSED R17 only.

Read-only stdlib verification: no DEE import, Runtime, service start, queue
mutation, epoch finalization, promotion, Word edit or packaging certification.
Root must review this source and wait for Delivery's closed R17 receipt first.
"""
from __future__ import annotations
import argparse,ctypes,gzip,hashlib,importlib.util,json,os,re,shutil,sqlite3,time
from datetime import datetime,timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent;LAB=HERE.parent;ROOT=LAB.parents[2]
S=ROOT/'sistema';EV=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01'
R17_DEFAULT=EV/'servicio/SERVICIO_60MIN_FASE_R17'
LIFE_KEY='DEE.Cognitive.System.1.1.life.v1'
MU_KEY='DEE.Cognitive.System.1.1.MENTE_UNIFICADA_01.v1'
SERVICE_KEY='DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1'

def read(p):
    p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def signature(p):
    p=Path(p);return {'path':str(p.resolve(strict=True)),'bytes':p.stat().st_size,'sha256':sha(p)}
def require(ok,message):
    if not ok:raise ValueError(message)
def physical(q):return {k:q[k]for k in('N','tick','RAW_sha256','clocks_sha256')}
def inside(base,relative):
    p=Path(relative)
    require(not p.is_absolute(),'Expected a relative operational member, not an external dependency path')
    q=(base/p).resolve(strict=True);require(q.is_relative_to(base.resolve()),'Operational path leaves its declared package');return q
def no_issues(q,label):
    require(not q.get('issues'),label+' has unresolved archived recalculation issues')
def memory_status():
    if os.name!='nt':return {'available':None,'scope':'No Windows memory status on this host; no native performance inference.'}
    class M(ctypes.Structure):
        _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong),*[(k,ctypes.c_ulonglong)for k in('total_phys','avail_phys','total_page','avail_page','total_virtual','avail_virtual','extended')]]
    m=M();m.length=ctypes.sizeof(M)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):return {'available':None,'scope':'GlobalMemoryStatusEx unavailable'}
    return {'available_bytes':int(m.avail_phys),'total_bytes':int(m.total_phys),'scope':'Host RAM at receipt creation, not DEE internal energy or functional capacity.'}

def read_closed_queue(db):
    """Immutable SQLite read of an already stopped/checkpointed transport."""
    wal=Path(str(db)+'-wal')
    require(not wal.exists()or wal.stat().st_size==0,'Closed source still has nonempty WAL; use its consistent postSTOP checkpoint/backup. This generator never checkpoints or writes the source queue.')
    before=sha(db)
    con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True,timeout=5)
    try:
        meta={row[0]:json.loads(row[1])for row in con.execute("SELECT key,value FROM meta WHERE key IN('owner','latest_checkpoint','protocol_admission_closed','epoch_closed')")}
        pending=[{'id':row[0],'status':row[1]}for row in con.execute("SELECT id,status FROM requests WHERE status IN('queued','processing','uncertain') ORDER BY seq")]
        outcomes={row[0]:int(row[1])for row in con.execute('SELECT status,count(*) FROM requests GROUP BY status')}
    finally:con.close()
    require(sha(db)==before,'Read-only queue source changed while creating the receipt; no close is declared from a racing source')
    return {'source':signature(db),'meta':meta,'outstanding':pending,'all_journal_outcomes_including_inherited':outcomes,
      'count_scope':'Lifetime journal counts are continuity witnesses only; R17 experimental denominators are copied solely from R17 recalculations.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--r17',type=Path,default=R17_DEFAULT);p.add_argument('--salida',type=Path,required=True);a=p.parse_args()
    require(not a.salida.exists(),'Refuse overwrite: preserve the previous continuity receipt and select an explicitly new output')
    require(a.salida.resolve().is_relative_to(LAB.resolve()),'Continuity output belongs to this campaign, not the operational system or an external directory')
    r17=a.r17.resolve(strict=True);require(r17.is_relative_to(EV.resolve()),'R17 evidence must be local to this campaign')
    paths={k:r17/v for k,v in {'cut':'CORTE_PARA_MANUAL.json','result':'RESULTADO.json','recalc':'RECALCULO_FASE_R3.json','time':'RECALCULO_TIEMPO_FASE_R3.json','functions':'PANELES_Y_FUNCIONES.json','protocol':'PROTOCOLO.json'}.items()}
    # CORTE is Delivery's terminal barrier. Never poll a running owner here.
    for q in paths.values():require(q.is_file(),'R17 not closed/exported yet: missing '+q.name)
    c=read(paths['cut']);r=read(paths['result']);rec=read(paths['recalc']);tim=read(paths['time']);fun=read(paths['functions']);pro=read(paths['protocol'])
    budget_path=LAB/'PRESUPUESTO.json';A_path=LAB/'CIERRE_INTERNO_A.json';old_path=LAB/'CONTINUIDAD_R11_PRESERVADA.json'
    budget=read(budget_path);A=read(A_path);old=read(old_path)
    require(A.get('block_A_closed')is True and old['status']=='CLOSED_SCIENTIFIC_CUT','Original block-A and R11 history must already be closed')
    require(sha(budget_path)==A['original_budget_file_sha256'],'Original budget bytes changed; never reset the campaign clock')
    main_cut=c['main'];service=c['persistent_service']
    for k in('life_id','tick','N','snapshot','snapshot_sha256','physical','parent','world_id'):require(k in main_cut,'Missing exact main cut field '+k)
    for k in('world_evolving_wall_seconds','completed_operations','idle_ticks','manual_results_text'):require(k in service,'Missing manual/service field '+k)
    require(main_cut['life_id']==pro['life_id']=='MU_MAIN_FASE_R3','Wrong R17 life; never replace it with a historical or favorable branch')
    require(type(main_cut['N'])is int and main_cut['N']==67 and type(main_cut['tick'])is int,'Exact N67/tick required')
    require(physical(main_cut['physical'])['tick']==main_cut['tick']and main_cut['physical']['N']==main_cut['N'],'Cut physical identity disagrees with its header')
    no_issues(rec,'R17 physical/function recalc');no_issues(tim,'R17 wall accounting')
    require(not fun.get('underlying_recalculation_issues'),'Functional tables have unresolved underlying issues')
    require(not r.get('error')and not r['remaining_before_close'],'R17 has a host error or unresolved transport; do not silently complete it')
    require(r['final_owner']['running']is False and r['final_owner']['uncertain_external_result']is False,'R17 owner has not stopped unambiguously')
    require(pro['request_prefix']=='fi60r3_'and pro['seconds']==3720,'The new R3 service has its own frozen R04 horizon/prefix')
    require(all(row['id'].startswith('fi60r3_')for row in rec['all_request_outcomes']),'R17 metrics include inherited R11 request IDs')
    require(service['completed_operations']==rec['material_request_outcomes']['completed'],'Completed operations do not match the R17-only recalc')
    require(service['world_evolving_wall_seconds']==tim['unpaused_operational_seconds_lower_estimate'],'Operational seconds differ from the independent R17 time accounting')
    require(type(service['idle_ticks'])is int and service['idle_ticks']>=0,'Idle ticks must be an exact nonnegative R17 delta, not a cumulative inherited count')
    require(service['world_evolving_wall_seconds']>=3600,'This new protocol did not accumulate sixty unpaused operational minutes')
    require(service.get('pending_or_uncertain',False)is False and service.get('owner_stopped',True)is True,'Manual cut has unresolved operational state')
    # Required protected originals: hashes only, not repeated scientific trials.
    originals={}
    require(len(budget['protected'])==8,'Original protected set is not the eight registered lives')
    for name,v in budget['protected'].items():
        rr=Path(v['record']);ss=Path(v['snapshot']);good_r=sha(rr)==v['record_sha256'];good_s=sha(ss)==v['snapshot_sha256']
        require(good_r and good_s,'Protected original changed: '+name)
        originals[name]={'record':signature(rr),'snapshot':signature(ss),'record_unchanged':good_r,'snapshot_unchanged':good_s}
    active_path=S/'estado/ACTIVO.json';require(sha(active_path)==budget['active_record_sha256'],'Global ACTIVO changed; this closure does not authorize promotion')
    active=read(active_path);require(active==old['active_record'],'Global active identity differs from the protected R11 receipt')
    # Preserve the adverse R11 future and its logical life record exactly.
    old_snapshot=inside(S,old['main']['snapshot']);old_record=Path(old['main']['current_VIDA'])
    require(sha(old_snapshot)==old['main']['snapshot_sha256'],'R11 adverse snapshot is no longer the preserved original')
    require(sha(old_record)==old['main']['current_VIDA_sha256'],'R11 life was modified after the declared preserved cut')
    life=main_cut['life_id'];require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,90}',life)is not None,'Invalid life identifier')
    record_path=S/'estado/vidas'/life/'VIDA.json';record=read(record_path);snapshot=inside(S,main_cut['snapshot'])
    require(sha(snapshot)==main_cut['snapshot_sha256']==record['snapshot_sha256'],'Current candidate snapshot hash is not the delivered cut')
    require(record['life_id']==life and record['world_id']==main_cut['world_id']and record['snapshot']==main_cut['snapshot'],'Candidate VIDA pointer does not identify the delivered cut')
    require(record['profile']=='fisica_directa'and physical(record['physical'])==physical(main_cut['physical'])and record['parent']==main_cut['parent'],'Candidate profile/physical/genealogy differs from closed evidence')
    require(record['parent'].get('encoded_sha256')==old['main']['snapshot_sha256']and record['parent'].get('source_tick')==68924,'R3 is not the explicit full fork of the preserved R11 future')
    require(physical(r['final']['physical'])==physical(main_cut['physical']),'Delivered cut is not the real final R17 physical state')
    world_id=record['world_id'];require(not(S/'estado/locks'/(world_id+'.lock')).exists(),'Candidate still has a writer lock; do not close or interrupt it here')
    require(not(record_path.parent/'FUTURO_INTERRUMPIDO.json').exists(),'Candidate has a possibly uncommitted future; never rewind it to the last snapshot')
    hist=record_path.parent/'HISTORIA.jsonl';last_line=None
    with hist.open(encoding='utf8')as f:
        for line in f:
            if line.strip():last_line=line
    require(last_line is not None and json.loads(last_line)['snapshot_sha256']==record['snapshot_sha256'],'Life journal and VIDA disagree')
    # Parse the full saved state without importing any participant or engine.
    observer_path=S/'capacidades/observador_causal_retrospectivo_01.py';spec=importlib.util.spec_from_file_location('pure_final_R3_observer',observer_path)
    ob=importlib.util.module_from_spec(spec);spec.loader.exec_module(ob);snap=ob.Snapshot(snapshot);org=ob.organization(snap);summary=snap.summary()
    require(snap.N==main_cut['N']and snap.tick==main_cut['tick']and summary['RAW_sha256']==main_cut['physical']['RAW_sha256']and summary['clocks_sha256']==main_cut['physical']['clocks_sha256'],'Complete snapshot fields do not match the authoritative cut')
    require(not snap.pending and not org['protocols'],'Complete native world has pending entries or unfinished owner protocols')
    identity=json.loads(snap.metadata[LIFE_KEY]);operational=json.loads(snap.metadata[MU_KEY]);protocol=json.loads(snap.metadata[SERVICE_KEY])
    require(identity['life_id']==life and identity['world_id']==world_id and identity['tick']==main_cut['tick'],'Native identity metadata differs from VIDA')
    require(not any(operational.get(k)for k in('external_pending','cascade_pending','external_uncertain')),'A worker artifact/progress or uncertain external effect remains pending')
    require(protocol['native_tick_at_checkpoint']==main_cut['tick']and not protocol['uncertain_external_result'],'Persistent protocol is out of sync or uncertain')
    for j in range(16):require(json.loads(snap.metadata[SERVICE_KEY+'.queue.'+str(j)])=={'empty':True},'Nonempty saved transport slot '+str(j))
    sidecar=inside(S/'estado',record['persistent_service']['sidecar_directory']);worker=inside(S/'estado',record['persistent_service']['worker_directory'])
    queue=read_closed_queue(sidecar/'cola.sqlite3');owner=queue['meta']['owner']
    require(owner['life_id']==life and owner['running']is False and owner['uncertain_external_result']is False and not queue['outstanding'],'Actual current transport is running, pending or uncertain')
    require(owner['tick']==main_cut['tick']and physical(owner['physical'])==physical(main_cut['physical']),'Cached stopped owner physical state differs from the saved cut')
    latest=queue['meta']['latest_checkpoint'];require(latest['snapshot_sha256']==main_cut['snapshot_sha256'],'Current transport points to a different complete checkpoint')
    if 'epoch_closed'in service:require(bool(service['epoch_closed'])==bool(protocol.get('closed_epoch')),'Manual epoch-closure flag differs from actual saved protocol')
    # Delivery supplies the exact postSTOP pair locator; never substitute an old export.
    paired=c.get('paired_export')or service.get('paired_export')
    require(isinstance(paired,dict),'Delivery must identify its exact postSTOP paired export')
    manifest_path=Path(paired['manifest']);manifest_resolved=manifest_path.resolve(strict=True)
    require(manifest_resolved.is_relative_to(S.resolve())or manifest_resolved.is_relative_to(r17),'PostSTOP paired export must be in the system or this exact closed R17 evidence directory')
    require(sha(manifest_path)==paired['manifest_sha256'],'PostSTOP paired manifest hash differs')
    manifest=read(manifest_path);require(manifest['life_id']==life and manifest['snapshot_sha256']==main_cut['snapshot_sha256'],'Paired export is stale or identifies another life')
    exported_native=inside(manifest_path.parent,manifest['native_snapshot']);require(sha(exported_native)==main_cut['snapshot_sha256'],'PostSTOP paired native member differs from the current cut')
    require((manifest_path.parent/'cola.sqlite3').is_file()and manifest.get('queue_journal_required')is True,'Native snapshot alone is not a complete persistent continuation')
    epoch_closed=bool(protocol.get('closed_epoch'))
    continuation=('The epoch is explicitly closed; ordinary declared continuation is allowed, and the next persistent owner opens a new epoch while retaining transport deduplication.'if epoch_closed else'The stopped epoch remains OPEN and bound to its complete paired transport. Continue with the existing persistent-owner start from the exact paired package. Before ordinary material CLI mutations, explicitly close this stopped epoch through the existing protocol; never silently drop the journal or desynchronize it.')
    verified={name:signature(path)for name,path in paths.items()}
    verified.update({'generator':signature(Path(__file__)),'budget':signature(budget_path),'block_A':signature(A_path),'R11_preserved_receipt':signature(old_path),'ACTIVO':signature(active_path),'candidate_VIDA':signature(record_path),'candidate_snapshot':signature(snapshot),'pure_snapshot_observer':signature(observer_path),'paired_manifest':signature(manifest_path)})
    started=budget['block_A_deadline_monotonic']-budget['maximum_A_seconds'];now_m=time.monotonic()
    output={'schema':'MUFI01.continuity.R3.final.v1','status':'CLOSED_SCIENTIFIC_CUT','created_utc':datetime.now(timezone.utc).isoformat(),
      'main':main_cut,'persistent_service':service,
      'budget':{'original_start_utc':budget['start_utc'],'original_total_limit_utc':budget['total_limit_utc'],'block_A_closed_utc':A['closed_utc'],'block_B_deadline_utc':A['block_B_limit_utc'],'original_total_deadline_monotonic':budget['total_deadline_monotonic'],'original_block_B_deadline_monotonic':A['block_B_deadline_monotonic'],'elapsed_monotonic_seconds':now_m-started,'remaining_B_monotonic_seconds':A['block_B_deadline_monotonic']-now_m,'clock_not_reset':True},
      'protected_original_checks':originals,'active_pointer_unchanged':True,'active_record':active,
      'genealogy':{'preserved_R11':{'life_id':old['main']['life_id'],'tick':old['main']['tick'],'snapshot':old['main']['snapshot'],'snapshot_sha256':old['main']['snapshot_sha256'],'receipt':signature(old_path),'current_VIDA_preserved':signature(old_record)},'R3_parent':record['parent'],'R3_preparation':'One explicitly taught B0 revised Dminus21 to Dminus20; P0 phase flag then changed no native RAW/clocks or tick. R16 favorable fields were never transplanted.','same_R3_life_through_preflight_and_R17':True,'R11_results_are_not_R17_denominators':True},
      'current_operational_verification':{'complete_snapshot':summary,'identity_metadata':identity,'native_pending':snap.pending,'owner_protocols':org['protocols'],'sixteen_transport_slots_empty':True,'actual_stopped_queue':queue,'closed_epoch':epoch_closed,'worker_or_cascade_pending':False,'continuation':continuation},
      'assistant_contract':{'designed':'P0 anatomy, supports, generic routes, typed context addressing, fixed six/twelve-class readers, operator-requested tasks, phase scheduling and external file transduction.','acquired':'Only the contents and native functional changes supported by this lineage and the recorded experience/return contrasts; B0 and beta revision are explicit teaching, not spontaneous recovery.','operator_selected':'Tasks, old-memory contexts, stages and enablement of prepared P0 protection. No claimed general learned planner or initiative.','not_claimed':'General R2/P2, NSM65 meanings,128concepts, unlimited stability, learned phase protection or global promotion.'},
      'global_promotion':{'performed':False,'scope':'Explicit selectable continuation option only; protected ACTIVO and eight originals remain unchanged.'},
      'resources':{'original_declared_limits':{k:budget[k]for k in('native_workers_max','OMP_NUM_THREADS','one_writer_per_world','memory_status','disk_free_bytes')},'closing_host_memory':memory_status(),'closing_disk_free_bytes':shutil.disk_usage(ROOT).free,'scope':'Host resources and declared limits, not DEE metabolism or a cognitive score.'},
      'local_dependencies':{'system':str(S),'CPython':'3.13 x64 compatible with the existing frozen official4.5.0/v27 runtime; do not reinstall a working original.','complete_checkpoint':str(snapshot),'life_record':str(record_path),'service_directory':str(sidecar),'queue_journal':queue['source'],'worker_directory':str(worker),'exact_postSTOP_paired_manifest':signature(manifest_path),'exact_postSTOP_paired_directory':str(manifest_path.parent),'audit_evidence':str(EV),'analysis_zip_is_not_operational_backup':True},
      'next_operation':continuation+' Use an explicit personal paired copy; one writer per Runtime. An uncertain external action is never automatically retried. Do not replay inherited R11 or already committed R3 IDs.',
      'source_verification':verified,'new_native_ticks_for_this_receipt':0,
      'packaging_verification':'NOT_YET_CERTIFIED_BY_THIS_RECEIPT. Exact final operational/scientific ZIP hashes, extraction and verification belong to separate external records after sealing. No self-referential output hash is included.'}
    # Exactly preserve Delivery's two manual-consumed dictionaries, without
    # importing an ID, score or duration from the preserved R11 receipt.
    require(output['main']==c['main']and output['persistent_service']==c['persistent_service'],'Manual dictionaries were unexpectedly rewritten')
    a.salida.parent.mkdir(parents=True,exist_ok=True)
    with a.salida.open('x',encoding='utf8')as f:json.dump(output,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps({'status':output['status'],'life':life,'tick':main_cut['tick'],'native_ticks':0,'protected_originals':len(originals),'owner_stopped':True,'epoch_closed':epoch_closed,'output':str(a.salida),'output_sha256':sha(a.salida)},ensure_ascii=False))

if __name__=='__main__':main()
