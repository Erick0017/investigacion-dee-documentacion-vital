"""Explicit Root-only closed lease migration; default preflight is stdlib.

No owner, request, query, advance, teaching or policy update. Used Native epochs
are loaded only by the internal official-python512MiB child when Root applies.
Untouched import0 roots need only filesystem lease files; their snapshot remains
byte-identical. A partial transaction stays marked and cannot auto-retry.
REV3 additionally pins and rechecks the preserved current-pair manifest and its
World/closure/ledger anchors. It does not claim a tested material rollback.
"""
from pathlib import Path
from contextlib import contextmanager
import argparse,datetime,gc,hashlib,importlib.util,json,os,shutil,sqlite3,sys,time,uuid
ROOT=Path(__file__).resolve().parents[1];PRODUCT=ROOT.parents[2]
PREFIX='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V3_'
ROLES=('MAIN','CTRL1','LOAD1','LOAD2','LOAD3','PILOT');LIMIT=536870912
def need(v,m):
    if not v:raise ValueError(m)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def load(p,name):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
CORE=load(ROOT/'native/lease_core_v3_R06.py','_r07_lease_core_R05')
def new(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def atomic_bytes(p,raw):
    p=Path(p);temp=p.with_name(p.name+'.LEASE_'+uuid.uuid4().hex)
    with temp.open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    os.replace(temp,p)
def json_bytes(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def reject_preloaded_actor(path):
    target=os.path.normcase(os.path.abspath(path))
    loaded=[]
    for name,module in list(sys.modules.items()):
        file=getattr(module,'__file__',None)
        if isinstance(file,str)and os.path.normcase(os.path.abspath(file))==target:loaded.append(name)
    need(not loaded,'UNEXPECTED_ACTOR_PRELOADED_BEFORE_METADATA_OR_FILE_MUTATION: '+','.join(loaded))
def safe(p):
    p=Path(p).resolve(strict=True)
    for q in(p,*p.parents):need(not q.is_symlink()and not getattr(q.lstat(),'st_file_attributes',0)&1024,'NO_REPARSE_OR_SYMLINK')
    return p
def _closed_base(root):
    root=safe(root);need(root.parent==ROOT/'native'and root.name in ROLES,'ONLY_SIX_EXPERIMENTAL_ROOTS')
    c=read(root/'CONTEXTO_EJECUCION.json');life=c['life'];need(life==PREFIX+root.name,'EXACT_LIFE')
    system=root/'sistema';card_file=system/'estado/vidas'/life/'VIDA.json';card=read(card_file)
    need(card['life_id']==card['world_id']==life and not(system/'estado/ACTIVO.json').exists(),'UNSELECTED_EXPERIMENTAL_WORLD')
    need(not(system/'estado/locks'/(life+'.lock')).exists()and not(card_file.parent/'FUTURO_INTERRUMPIDO.json').exists(),'NO_LIVE_OR_INTERRUPTED_WRITER')
    journal=root/'ENSAYOS.jsonl';start=None;end=None
    if journal.exists():
        for line in journal.read_text('utf8').splitlines():
            if not line.strip():continue
            r=json.loads(line)
            if r.get('kind')=='OWNER_STARTED':start=r;end=None
            elif r.get('kind')=='OWNER_CLOSED':end=r
    if start:
        need(end and start['run']==end['run']and start['pid']==end['pid']and end['exit_code']==0,'EXACT_LATEST_OWNER_CLOSED')
        cache=end['final_status'];need(cache.get('running')is False  and cache['tick']==card['physical']['tick'],'CLOSED_CACHE_MATCHES_CARD')
    imported=read(root/'IMPORTACION_DIAGNOSTICA.json')
    actor_log=system/'estado/servicios_locales'/life/'RBX07_NATIVE_INTEGRAL_V3/events.jsonl'
    untouched=(start is None and not end and(not actor_log.exists()or actor_log.stat().st_size==0)and card['snapshot_sha256']==imported['result']['snapshot_sha256'])
    need(start is not None or untouched,'NO_UNACCOUNTED_NATIVE_HISTORY')
    snapshot=safe(system/card['snapshot']);need(snapshot.is_relative_to(system)and sha(snapshot)==card['snapshot_sha256'],'EXACT_CURRENT_SNAPSHOT')
    db=system/'estado/servicios_persistentes'/life/'cola.sqlite3'
    need(all(not Path(str(db)+s).exists()or Path(str(db)+s).stat().st_size==0 for s in('-wal','-journal')),'NO_NONEMPTY_SQLITE_WAL_OR_JOURNAL')
    before=sha(db);con=sqlite3.connect(safe(db).as_uri()+'?mode=ro&immutable=1',uri=True)
    try:
        need(con.execute('PRAGMA quick_check').fetchone()[0]=='ok','CLOSED_QUEUE_INTEGRITY')
        need(con.execute("SELECT COUNT(*) FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0]==0,'NO_UNKNOWN_OR_PENDING_REQUEST')
        owner=json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0]);need(owner.get('running')is False,'CLOSED_QUEUE_OWNER')
    finally:con.close()
    need(sha(db)==before,'NO_CONCURRENT_QUEUE_CHANGE')
    return {'root':str(root),'life':life,'physical':card['physical'],'card_sha256':sha(card_file),'snapshot':str(snapshot),'snapshot_sha256':card['snapshot_sha256'],
      'queue_sha256':before,'untouched_import0_prefix':untouched,'last_owner_closed':end,'actor_log':str(actor_log)}
def known_q2(root,proof):
    if root.name not in('LOAD1','LOAD2','LOAD3'):return None
    path=ROOT/'load/evidencia/CARGA3_R01/CONCILIACION_PASIVA_R06.json';report=read(path)
    need(report['status']=='THREE_Q1_REAL_ZERO_COMPLETE_EPISODES_KNOWN_Q2_HOST_REJECTION','EXACT_CLOSED_Q2_RECONCILIATION')
    row=next(x for x in report['lives']if x['profile']==root.name)
    need(row['life']==proof['life']and row['physical']==proof['physical']and row['snapshot_sha256']==proof['snapshot_sha256'],'EXACT_CURRENT_CLOSED_FAILED_FUTURE')
    receipt=safe(row['failed_official_receipt']);need(sha(receipt)==row['failed_official_sha256'],'EXACT_NO_ADMISSION_RECEIPT_BYTES')
    request=read(receipt);error=request['error'];error=read_error(error)
    need(request['status']=='failed_preserved'and error['external_execution_may_be_uncertain']is False and error['native_tick_after_attempt']==991543,'FAILED_Q2_PROVEN_ZERO_TICKS')
    need(error['detail']=='Real station query consumes exactly one environmental permit','ONE_KNOWN_HOST_STOCK_BUG_ONLY')
    m=row['own_metadata_preserved_from_failed_snapshot']
    need(m==error['failed_native_future_preserved']['operational_dependencies']['RBX01']['progress'],'EXACT_SERIALIZED_OWN_PENDING_METADATA')
    need(m['phase']=='AWAIT_ROUTE_SENSOR'and m['uncertain']is True and m['cycles']==0 and m['last_sequence']==56,'PENDING_UNCERTAINTY_MUST_STAY_PRESERVED_BY_LEASE')
    return {'reconciliation':str(path),'reconciliation_sha256':sha(path),'failed_receipt':str(receipt),'failed_receipt_sha256':sha(receipt),
      'failed_id':row['failed_q2_id'],'metadata_sha256':hashlib.sha256(CORE.canonical(m).encode()).hexdigest(),
      'no_Q2_pulses_or_ticks':True,'repair_permitted_by_this_lease':False}
def read_error(value):return json.loads(value)if isinstance(value,str)else value
def closed(root):
    value=_closed_base(root);root=Path(value['root']);known=known_q2(root,value)
    end=value['last_owner_closed']
    if end and end['final_status'].get('uncertain_external_result',False):
        need(known is not None,'UNKNOWN_EXTERNAL_FUTURE_NOT_LEASABLE')
    if known is not None:value['known_zero_q2']=known
    actor_log=Path(value['actor_log']);value['actor_log_sha256']=sha(actor_log)if actor_log.is_file()else None
    return value

def files(root):return {'scope':root/'sistema/capacidades/RBX07_NATIVE_SCOPE_INTEGRAL_V3.json','host':root/'sistema/app/HOST_INTEGRAL_V3.json','actor':root/'sistema/capacidades/rbx07_native_v3.py'}

def pair_path(path):
    """Check lexical ancestors before resolution; never follow a reparse alias."""
    path=Path(os.path.abspath(path))
    for part in reversed((path,*path.parents)):
        need(part.exists(),'PRESERVED_PAIR_PATH_MISSING')
        stat=part.lstat()
        need(not part.is_symlink()and not getattr(stat,'st_file_attributes',0)&1024,'PAIR_PATH_NO_REPARSE_OR_SYMLINK')
    return path.resolve(strict=True)

def main_pair_witness(directory,main):
    directory=pair_path(directory)
    need(directory.is_dir()and directory.is_relative_to(ROOT/'evidencia'),'PAIR_INSIDE_EXPERIMENT_EVIDENCE')
    manifest=pair_path(directory/'PAREJA_INTEGRAL_V3.json');pair=read(manifest)
    need(pair.get('schema')=='DEE.RBX07.ClosedPointOverlay.R05','EXACT_COMPATIBLE_P04_SCHEMA')
    need(pair_path(pair['native_source_root'])==pair_path(main['root']),'PAIR_IS_CURRENT_MAIN_ROOT')
    boundary=pair['boundary']
    need(boundary['native_snapshot_sha256']==main['snapshot_sha256']and boundary['native_tick']==main['physical']['tick']and boundary['life_id']==main['life'],'PRESERVED_COMPLETE_PRE_LEASE_MAIN_PAIR')
    allowed={'COMPLETE_FILE_LEVEL_CONTENT_OVERLAY':True,'COMPLETE_CURRENT_ROOT_DESCRIPTOR_WITH_CRITICAL_MUTABLE_COPIES_ONLY':False}
    mode=pair['storage_mode'];need(mode in allowed and pair['immutable_all_members']is allowed[mode],'HONEST_PAIR_STORAGE_MODE')
    anchors=[]
    for name in('WORLD_CHECKPOINT.json','CIERRE_BLOQUE_ORIGINAL.json','LEDGER_AL_CORTE.json'):
        candidates=[row for row in pair['members']if row.get('file')==name]
        need(len(candidates)==1,'ONE_PRESERVED_PAIR_ANCHOR_'+name)
        row=candidates[0];file=pair_path(row['locator'])
        need(file==pair_path(directory/name)and row.get('storage_kind')=='UNIQUE_PRESERVED_ANCHOR','ANCHOR_LOCAL_LITERAL_COPY')
        need(file.is_file()and file.stat().st_size==row['bytes']and sha(file)==row['sha256'],'PRESERVED_PAIR_ANCHOR_BYTES_'+name)
        anchors.append({'file':name,'path':str(file),'bytes':row['bytes'],'sha256':row['sha256']})
    world=read(directory/'WORLD_CHECKPOINT.json');closure=read(directory/'CIERRE_BLOQUE_ORIGINAL.json');budget=read(directory/'LEDGER_AL_CORTE.json')
    need(world['native_life_id']==main['life']and world['native_tick']==main['physical']['tick'],'WORLD_ANCHOR_SAME_NATIVE_CUT')
    need(closure['owner_closed']is True and closure['final_tick']==main['physical']['tick']and closure['identity']['life']==main['life'],'CLOSURE_ANCHOR_SAME_NATIVE_CUT')
    need(not budget['intents']and budget['worlds'][main['life']]['reserved']==0,'PAIR_BUDGET_QUIESCENT')
    return {'manifest':str(manifest),'manifest_bytes':manifest.stat().st_size,'manifest_sha256':sha(manifest),
      'storage_mode':mode,'immutable_all_members_as_declared':pair['immutable_all_members'],'anchors':anchors,
      'native_snapshot_sha256':main['snapshot_sha256'],'native_tick':main['physical']['tick'],
      'only_current_boundary_required_by_lease':True,'material_rollback_tested':False,
      'RW_current_root_is_not_immutable_backup_after_continuation':True,
      'verification_scope':'Manifest and all three copied anchors SHA checked here. Full Native-root and BASE object hashes are P04 evidence; this is not a second full-tree audit.'}

def recheck_main_pair(plan):
    # The historical helper name is retained; R06 pins CURRENT manifests for
    # all six roles, including closed Q1 futures, not an invented frozen backup.
    for row in plan['roots']:
        path=safe(row['role_manifest']);need(sha(path)==row['role_manifest_sha256'],'CURRENT_ROLE_MANIFEST_CHANGED')
        manifest=read(path);need(manifest['closed_proof']==row['proof'],'MANIFEST_CURRENT_CLOSED_BOUNDARY')
        for name,entry in manifest['linked_anchors'].items():
            p=safe(entry['path']);need(sha(p)==entry['sha256'],'PRESERVED_ROLE_ANCHOR_CHANGED: '+name)

def stage(a):
    need(time.time()<CORE.NEW_LAST,'PROSPECTIVE_NEW_WINDOW_ONLY')
    need(set(a.roles)==set(ROLES)and len(a.roles)==6,'ONE_ADMINISTRATIVE_RENEWAL_ALL_SIX_CLOSED_ROLES')
    output=a.output.resolve();need(not output.exists()and output.is_relative_to(ROOT/'control'),'FRESH_TRANSACTION_DIRECTORY')
    freeze=safe(a.freeze);need(sha(freeze)==a.freeze_sha256,'EXACT_18H_FREEZE');f=read(freeze)
    need(f['sealed']is True and f['native_start_epoch']==1794841620 and f['last_new_episode_epoch']==CORE.NEW_LAST and f['native_cutoff_epoch']==CORE.NEW_END,'SAME_ORIGINAL_START_FINITE_18H_WINDOW')
    ledger=safe(a.ledger);old_ledger=read(ledger);CORE.renew_ledger(old_ledger,utc())
    proofs=[closed(ROOT/'native'/role)for role in a.roles]
    need(not ledger.with_name(ledger.name+'.LOCK').exists(),'GLOBAL_BUDGET_QUIESCENT')
    expected={x['life']:x['known_zero_q2']['failed_id']for x in proofs if 'known_zero_q2'in x}
    need(set(old_ledger['intents'])==set(expected),'NO_UNEXPLAINED_INTENT')
    for proof in proofs:
        life=proof['life'];world=old_ledger['worlds'].get(life)
        if life in expected:
            need(old_ledger['intents'][life]['id']==expected[life]and world['reserved']==3740 and world['consumed']==356 and world['cycles']==0,'EXACT_FAILED_Q2_RESERVATION_PRESERVED')
        elif world:need(world['reserved']==0,'NO_UNPROVEN_PARTIAL_RESERVATION')
    pair_manifest=safe(a.main_pair)/'PAREJA_INTEGRAL_V3.json';pair=read(pair_manifest)
    previous=safe(ROOT/'control/LEASE_R05_REV3_TX/RESULTADO.json');prior=read(previous)
    main=next(x for x in proofs if Path(x['root']).name=='MAIN');bridge=next(x for x in prior['results']if x['role']=='MAIN')
    need(prior['status']=='CLOSED_LEASE_RENEWAL_COMPLETE'and prior['new_native_ticks']==0 and bridge['snapshot_before_sha256']==pair['boundary']['native_snapshot_sha256']and bridge['snapshot_after_sha256']==main['snapshot_sha256'],'P04_TO_CURRENT_ADMINISTRATIVE_SNAPSHOT_CHAIN')
    need(bridge['physical_before']==bridge['physical_after']==main['physical']and pair['boundary']['native_tick']==main['physical']['tick'],'P04_AND_CURRENT_IDENTICAL_PHYSICAL_BOUNDARY')
    linked={'P04':{'path':str(pair_manifest),'sha256':sha(pair_manifest)},'prior_lease_zero_tick':{'path':str(previous),'sha256':sha(previous)}}
    output.mkdir(parents=True);new(output/'LEDGER_ANTES.json',old_ledger);rows=[]
    for proof in proofs:
        root=Path(proof['root']);folder=output/root.name;folder.mkdir();paths=files(root);old=read(paths['scope']);host=read(paths['host'])
        need(old['sources_sha256']['rbx07_native_v3.py']==sha(paths['actor']),'CURRENT_12H_ACTOR_PIN')
        updated=CORE.renew_scope(old,f['native_sources_sha256']['rbx07_native_v3.py'],a.freeze_sha256);changed=CORE.renew_host(host)
        for key,p in paths.items():shutil.copyfile(p,folder/('OLD_'+p.name))
        card=Path(proof['root'])/'sistema/estado/vidas'/proof['life']/'VIDA.json';shutil.copyfile(card,folder/'VIDA_ANTES_STAGE.json')
        history=card.parent/'HISTORIA.jsonl'
        if history.is_file():shutil.copyfile(history,folder/'HISTORIA_ANTES_STAGE.jsonl')
        (folder/'NEW_SCOPE.json').write_bytes(json_bytes(updated));(folder/'NEW_HOST.json').write_bytes(json_bytes(changed));new(folder/'CLOSED_PREFLIGHT.json',proof)
        anchors=dict(linked)if root.name=='MAIN'else{}
        if 'known_zero_q2'in proof:
            k=proof['known_zero_q2'];anchors['failed_Q2_receipt']={'path':k['failed_receipt'],'sha256':k['failed_receipt_sha256']};anchors['closed_Q2_reconciliation']={'path':k['reconciliation'],'sha256':k['reconciliation_sha256']}
        manifest={'schema':'DEE.R07.current_closed_role_lease_descriptor.R06','closed_proof':proof,'linked_anchors':anchors,
          'complete_current_native_root':str(root),'current_root_is_not_an_immutable_rollback_backup':True,'material_rollback_tested':False,
          'scope':'Current coherent closed root remains complete in place; original snapshot/card/scope preserved. This lease changes code witnesses and dates only; pending/failure/intents are NOT repaired.'}
        manifest_path=folder/'ROLE_CURRENT_MANIFEST.json';new(manifest_path,manifest)
        cycles=old_ledger['worlds'].get(proof['life'],{}).get('cycles',0)
        rows.append({'role':root.name,'root':str(root),'life':proof['life'],'expected_cycles':cycles,'proof':proof,
          'role_manifest':str(manifest_path),'role_manifest_sha256':sha(manifest_path),
          'old_files_sha256':{k:sha(p)for k,p in paths.items()},'new_scope_sha256':sha(folder/'NEW_SCOPE.json'),'new_host_sha256':sha(folder/'NEW_HOST.json')})
    plan={'schema':'DEE.R07.closed_lease_transaction.R06','created_utc':utc(),'original_start_epoch':1794841620,'old_last_new_epoch':CORE.OLD_LAST,'old_cutoff_epoch':CORE.OLD_END,
      'new_last_new_epoch':CORE.NEW_LAST,'new_cutoff_epoch':CORE.NEW_END,'ledger':str(ledger),'ledger_before_sha256':sha(ledger),
      'freeze':str(freeze),'freeze_sha256':a.freeze_sha256,'actor_source':str(ROOT/'native/lease_R06_bundle/rbx07_native_v3.py'),
      'actor_source_sha256':f['native_sources_sha256']['rbx07_native_v3.py'],'roots':rows,'Native_calls':0,'new_ticks':0,'not_applied':True,
      'pending_intents_will_remain_literal':old_ledger['intents'],'technical_uncertainty_recovery_NOT_authorized_by_this_plan':True}
    new(output/'PLAN.json',plan);return plan

def install(folder,root,plan,row):
    paths=files(root)
    for key,p in paths.items():need(sha(p)==row['old_files_sha256'][key],'OPERATIONAL_FILE_CHANGED_SINCE_PREFLIGHT')
    actor=Path(plan['actor_source']);need(sha(actor)==plan['actor_source_sha256'],'NEW_ACTOR_PIN')
    atomic_bytes(paths['actor'],actor.read_bytes());atomic_bytes(paths['scope'],(folder/'NEW_SCOPE.json').read_bytes());atomic_bytes(paths['host'],(folder/'NEW_HOST.json').read_bytes())
def native_child(tx,role):
    """Native-load0 operation, only invoked inside Root's official512MiB job."""
    plan=read(tx/'PLAN.json');row=next(x for x in plan['roots']if x['role']==role);root=Path(row['root']);folder=tx/role;system=root/'sistema'
    proof=closed(root);need(not proof['untouched_import0_prefix'],'UNTOUCHED_ROOT_NEEDS_NO_NATIVE_LOAD')
    need(proof['snapshot_sha256']==row['proof']['snapshot_sha256'],'EXACT_PREFLIGHT_SNAPSHOT')
    sys.path[:0]=[str(system),str(system/'app')]
    from app.lives import Store
    store=Store(system);card=store.record(row['life']);old_physical=json.loads(json.dumps(card['physical']));snapshot=system/card['snapshot']
    shutil.copyfile(snapshot,folder/'VIDA_ANTES_LEASE.deetsnap.gz');new(folder/'VIDA_ANTES_LEASE.json',card)
    with store.writer(card['world_id']):
        card,adapter=store.load(row['life'])
        # Store.load(fisica_directa) is a plain snapshot WorldAdapter, not the
        # Genesis service/dispatch. Reject before any mutation if that contract
        # ever changes; do not commit with an old actor module cached in memory.
        reject_preloaded_actor(system/'capacidades/rbx07_native_v3.py')
        before=dict(adapter.world.runtime.snapshot_metadata_entries)
        old_scope=read(folder/'OLD_RBX07_NATIVE_SCOPE_INTEGRAL_V3.json');new_scope=read(folder/'NEW_SCOPE.json')
        after,witness=CORE.metadata_after(before,old_scope,row['old_files_sha256']['scope'],new_scope,row['new_scope_sha256'],row['expected_cycles'],known_pending_sha256=row['proof'].get('known_zero_q2',{}).get('metadata_sha256'))
        need(int(adapter.tick)==old_physical['tick'],'LOADING_ADVANCED_NO_TICKS')
        for key in(CORE.KEY,CORE.CODE):
            if before.get(key)!=after.get(key):adapter.world.runtime.set_snapshot_metadata(key,after[key])
        install(folder,root,plan,row)
        card=store.commit(card,adapter,{'kind':'R07_ADMIN_PROSPECTIVE_LEASE_ONLY_R06','new_native_ticks':0,'old_cutoff':CORE.OLD_END,'new_cutoff':CORE.NEW_END,
          'policy_and_experience_fields_unchanged':True,'transaction':str(tx)},activate=False)
        actual=dict(adapter.world.runtime.snapshot_metadata_entries)
        need({k:v for k,v in actual.items()if k!=CORE.SYSTEM}=={k:v for k,v in after.items()if k!=CORE.SYSTEM},'ONLY_SYSTEM_AND_TWO_TECHNICAL_WITNESSES_MAY_CHANGE')
        need(card['physical']==old_physical and int(adapter.tick)==old_physical['tick'],'RAW_CLOCKS_GEOMETRY_TICK_LITERAL')
    need(sha(folder/'VIDA_ANTES_LEASE.deetsnap.gz')==proof['snapshot_sha256'],'ORIGINAL_SNAPSHOT_PRESERVED')
    result={'status':'LEASE_METADATA_ONLY_COMMITTED','role':role,'life':row['life'],'Native_runtime_loaded':True,'new_native_ticks':0,
      'physical_before':old_physical,'physical_after':card['physical'],'snapshot_before_sha256':proof['snapshot_sha256'],'snapshot_after_sha256':card['snapshot_sha256'],
      'metadata_witness':witness,'actor_journal_untouched':True,'m_policy_counters_sequence_session_and_log_chain_unchanged':True}
    new(folder/'NATIVE_RESULT.json',result);return result
@contextmanager
def ledger_lock(path):
    lock=path.with_name(path.name+'.LOCK');token=uuid.uuid4().hex
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    try:
        with os.fdopen(fd,'w',encoding='utf8')as f:json.dump({'pid':os.getpid(),'token':token,'kind':'LEASE_ONLY_NO_NATIVE'},f);f.flush();os.fsync(f.fileno())
        yield
    finally:
        if lock.exists()and read(lock).get('token')==token:lock.unlink()
def apply(tx):
    tx=safe(tx);plan=read(tx/'PLAN.json');ledger=Path(plan['ledger']);need(not(tx/'APPLY_INTENT.json').exists(),'NO_AUTOMATIC_TRANSACTION_RETRY')
    need(sha(Path(plan['freeze']))==plan['freeze_sha256']and sha(ledger)==plan['ledger_before_sha256'],'FROZEN_PLAN_OR_BUDGET_CHANGED')
    for row in plan['roots']:need(closed(Path(row['root']))==row['proof'],'NO_NEW_ACTIVITY_SINCE_PREFLIGHT')
    recheck_main_pair(plan)
    results=[]
    with ledger_lock(ledger):
        # No Native metadata, file, queue or budget mutation has happened yet.
        # Recheck after acquiring the administrative lock, before APPLY_INTENT.
        recheck_main_pair(plan)
        before=read(ledger);renewed=CORE.renew_ledger(before,utc());new(tx/'APPLY_INTENT.json',{'utc':utc(),'plan_sha256':sha(tx/'PLAN.json'),'Native_advance_permitted':False})
        for row in plan['roots']:
            root=Path(row['root']);new(root/'LEASE_MIGRATION_IN_PROGRESS.json',{'transaction':str(tx),'plan_sha256':sha(tx/'PLAN.json')})
        try:
            for row in plan['roots']:
                root=Path(row['root']);folder=tx/row['role']
                if row['proof']['untouched_import0_prefix']:
                    install(folder,root,plan,row);need(sha(row['proof']['snapshot'])==row['proof']['snapshot_sha256'],'UNTOUCHED_SNAPSHOT_LITERAL')
                    result={'status':'FILESYSTEM_LEASE_UNTOUCHED_IMPORT0','role':row['role'],'life':row['life'],'Native_runtime_loaded':False,'new_native_ticks':0,
                      'snapshot_bytes_unchanged':True,'Native_key_not_created_by_tool':True,'evidence':'Exact import0 snapshot unchanged; no owner/actor journal or consumed cycle.'}
                    new(folder/'NATIVE_RESULT.json',result)
                else:
                    pc=load(root/'sistema/app/process_control.py','_r07_lease_job_'+row['role']);stdout=(folder/'native.stdout.txt').open('x',encoding='utf8');stderr=(folder/'native.stderr.txt').open('x',encoding='utf8')
                    command=[str(PRODUCT/'motor/python313/python.exe'),'-I','-B','-X','utf8',str(Path(__file__).resolve()),'--native-child-root-only','--transaction',str(tx),'--role',row['role']]
                    job=None;started=time.monotonic();samples=[]
                    try:
                        process,job,name=pc.spawn_owned(command,cwd=ROOT,stdout=stdout,stderr=stderr,memory_limit=LIMIT)
                        while True:
                            resources=pc.job_resources(job);code=process.poll();samples.append({'elapsed_seconds':time.monotonic()-started,**resources})
                            if code is not None and resources.get('job_active_processes',0)==0:break
                            need(time.monotonic()-started<1200 and time.time()<CORE.NEW_END,'FINITE_ZERO_TICK_MIGRATION_JOB')
                            time.sleep(.5)
                        need(code==0 and(folder/'NATIVE_RESULT.json').is_file(),'NATIVE_CHILD_FAILURE_PRESERVED_NO_RETRY');result=read(folder/'NATIVE_RESULT.json')
                        new(folder/'JOB.json',{'pid':process.pid,'job':name,'exit_code':code,'memory_limit_bytes':LIMIT,'samples':samples,'new_native_ticks':0})
                    finally:
                        if job is not None:pc.close_job(job)
                        stdout.close();stderr.close()
                results.append(result)
            need(read(ledger)==before,'BUDGET_UNCHANGED_DURING_EXCLUSIVE_LEASE')
            atomic_bytes(ledger,json_bytes(renewed))
            for row in plan['roots']:
                root=Path(row['root']);new(root/'LEASE_APPLIED_R06.json',{'transaction':str(tx),'plan_sha256':sha(tx/'PLAN.json'),'new_scope_sha256':row['new_scope_sha256'],
                  'new_last_new_epoch':CORE.NEW_LAST,'new_hard_finish_epoch':CORE.NEW_END,'original_start_epoch':1794841620,'new_native_ticks':0})
            for row in plan['roots']:
                p=Path(row['root'])/'LEASE_MIGRATION_IN_PROGRESS.json';need(read(p)['transaction']==str(tx),'OWN_TRANSACTION_MARKER');p.unlink()
            result={'status':'CLOSED_LEASE_RENEWAL_COMPLETE','results':results,'ledger_before_sha256':plan['ledger_before_sha256'],'ledger_after_sha256':sha(ledger),
              'accounting_unchanged':True,'new_native_ticks':0,'no_experiences_or_policy_written':True,'original_start_epoch':1794841620,'last_new_epoch':CORE.NEW_LAST,'hard_finish_epoch':CORE.NEW_END}
            new(tx/'RESULTADO.json',result);return result
        except BaseException as e:
            new(tx/'INCOMPLETE_PRESERVED.json',{'error':type(e).__name__+': '+str(e),'automatic_retry':False,'markers_preserved':True});raise
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True);g.add_argument('--prepare-root-only',action='store_true');g.add_argument('--apply-root-only',action='store_true');g.add_argument('--native-child-root-only',action='store_true')
    p.add_argument('--roles',choices=ROLES,nargs='+');p.add_argument('--role',choices=ROLES);p.add_argument('--ledger',type=Path);p.add_argument('--main-pair',type=Path);p.add_argument('--freeze',type=Path);p.add_argument('--freeze-sha256');p.add_argument('--output',type=Path);p.add_argument('--transaction',type=Path);a=p.parse_args()
    if a.prepare_root_only:need(all((a.roles,a.ledger,a.freeze,a.freeze_sha256,a.output))and('MAIN'not in a.roles or a.main_pair),'EXPLICIT_CLOSED_PREPARATION_FIELDS');r=stage(a)
    elif a.apply_root_only:r=apply(a.transaction)
    else:r=native_child(a.transaction.resolve(strict=True),a.role)
    print(json.dumps(r,ensure_ascii=False,indent=2))
