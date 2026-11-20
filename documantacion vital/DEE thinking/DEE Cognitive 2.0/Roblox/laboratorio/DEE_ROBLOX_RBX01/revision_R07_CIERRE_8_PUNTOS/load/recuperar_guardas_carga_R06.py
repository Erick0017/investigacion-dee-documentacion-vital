"""Explicit reviewed zero-tick recovery of three known unadmitted Q2 calls.

No actor request, Native advance, phase edit, pending edit, replay or deletion.
Prepare is files/closed SQLite only. Apply requires the already-applied R06
lease, the exact closed receipts, a fresh transaction and Root's explicit flag.
"""
from pathlib import Path
import argparse,copy,ctypes,hashlib,importlib.util,json,os,shutil,sys,time
ROOT=Path(__file__).resolve().parents[1];PRODUCT=ROOT.parents[2];LIMIT=536870912
def need(v,m):
    if not v:raise ValueError(m)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def load(p,name):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
BASE=load(ROOT/'native/migrar_lease_cerrada_v3_R06.py','_recovery_closed_tools_R06')
CORE=load(ROOT/'load/recuperacion_tecnica_core_R06.py','_recovery_pure_core_R06')
def new(p,v):return BASE.new(p,v)
def proof_rows():
    path=ROOT/'load/evidencia/CARGA3_R01/CONCILIACION_PASIVA_R06.json';proof=read(path)
    need(proof['status']=='THREE_Q1_REAL_ZERO_COMPLETE_EPISODES_KNOWN_Q2_HOST_REJECTION','ONE_REAL_PRESERVED_LOAD_BATCH')
    need(len(proof['lives'])==3,'THREE_DECLARED_LIVES')
    return path,proof['lives']
def host_available():
    fields=[('length',ctypes.c_ulong),('load',ctypes.c_ulong)]+[(n,ctypes.c_ulonglong)for n in('total','available','totalPage','availablePage','totalVirtual','availableVirtual','extended')]
    typ=type('MEMORYSTATUSEX',(ctypes.Structure,),{'_fields_':fields});value=typ();value.length=ctypes.sizeof(value)
    need(os.name=='nt'and ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(value)),'REAL_HOST_MEMORY_MEASUREMENT')
    return value.available
def prepare(a):
    lease_path=ROOT/'control/LEASE_R06_TX/RESULTADO.json';lease=read(lease_path)
    need(lease['status']=='CLOSED_LEASE_RENEWAL_COMPLETE'and lease['new_native_ticks']==0,'R06_LEASE_MUST_HAVE_CLOSED_FIRST')
    original_path,proofs=proof_rows();ledger_path=BASE.safe(a.ledger);ledger=read(ledger_path)
    need(ledger['last_new_episode_epoch']==1794902400 and ledger['cutoff_epoch']==1794906420,'UNCHANGED_18H_GLOBAL_WINDOW')
    after,_=CORE.archive_ledger(ledger,proofs,BASE.utc())
    output=a.output.resolve();need(output.is_relative_to(ROOT/'control')and not output.exists(),'FRESH_RECOVERY_TRANSACTION')
    rows=[]
    for proof in proofs:
        root=ROOT/'native'/proof['profile'];closed=BASE._closed_base(root)
        need(closed['physical']==proof['physical']and closed['physical']['tick']==991543,'NO_PHYSICAL_CHANGE_SINCE_Q1')
        migrated=next(x for x in lease['results']if x['role']==proof['profile'])
        need(migrated['snapshot_after_sha256']==closed['snapshot_sha256']and migrated['new_native_ticks']==0,'EXACT_POST_LEASE_SNAPSHOT')
        official=BASE.safe(proof['failed_official_receipt']);need(sha(official)==proof['failed_official_sha256'],'KNOWN_REJECTED_Q2_BYTES_UNCHANGED')
        record=read(official);error=record['error'];error=json.loads(error)if isinstance(error,str)else error
        need(record['status']=='failed_preserved'and error['external_execution_may_be_uncertain']is False and error['native_tick_after_attempt']==991543,'ONE_UNAMBIGUOUS_NO_ADMISSION_RECEIPT')
        need(error['detail']=='Real station query consumes exactly one environmental permit','EXACT_HOST_BUG_ONLY')
        need(error['failed_native_future_preserved']['operational_dependencies']['RBX01']['progress']==proof['own_metadata_preserved_from_failed_snapshot'],'EXACT_ORIGINAL_FAILURE_METADATA')
        scope=read(BASE.files(root)['scope']);code=BASE.CORE.code_scope(scope,sha(BASE.files(root)['scope']))
        expected=copy.deepcopy(proof['own_metadata_preserved_from_failed_snapshot']);expected['code_scope']=code
        # Pure dry-run of the sole permitted technical-field transition.
        entries={CORE.KEY:CORE.canonical(expected),CORE.CODE:CORE.canonical(code)}
        CORE.repaired_entries(entries,proof['own_metadata_preserved_from_failed_snapshot'],code)
        rows.append({'role':proof['profile'],'root':str(root),'life':proof['life'],'closed_proof':closed,
          'original_proof':proof,'current_code_scope':code,'expected_current_own_metadata_sha256':CORE.digest(expected),
          'environment':CORE.environment(proof),'scope_sha256':sha(BASE.files(root)['scope']),'actor_sha256':sha(BASE.files(root)['actor'])})
    output.mkdir(parents=True);new(output/'LEDGER_ANTES.json',ledger)
    for row in rows:
        folder=output/row['role'];folder.mkdir();new(folder/'ENVIRONMENT_PLANNED.json',row['environment'])
        new(folder/'META_ORIGINAL_FAILED_RECEIPT.json',row['original_proof']['own_metadata_preserved_from_failed_snapshot'])
        shutil.copyfile(row['original_proof']['failed_official_receipt'],folder/'FAILED_Q2_ORIGINAL.json')
        shutil.copyfile(Path(row['root'])/'sistema/estado/vidas'/row['life']/'VIDA.json',folder/'VIDA_ANTES.json')
    plan={'schema':'DEE.R07.LOAD.technical_zero_admission_recovery.R06','created_utc':BASE.utc(),
      'source_reconciliation':str(original_path),'source_reconciliation_sha256':sha(original_path),
      'lease_result':str(lease_path),'lease_result_sha256':sha(lease_path),'ledger':str(ledger_path),'ledger_before_sha256':sha(ledger_path),
      'rows':rows,'source_sha256':sha(Path(__file__)),'core_sha256':sha(ROOT/'load/recuperacion_tecnica_core_R06.py'),
      'closed_tools_sha256':sha(ROOT/'native/migrar_lease_cerrada_v3_R06.py'),
      'new_native_ticks':0,'not_applied':True,'allowed_own_field_change':['uncertain True -> False'],
      'failure_must_stay_literal':True,'phase_pending_cachedreceipts_sequence_cycles_policy_not_editable':True,
      'ledger_reconciliation':'Archive only exact failed Q2 receipts as zero-tick admissions. Keep consumed10452/reserved3740each/cycles0 and last real Q1 completion.',
      'environment_correction':'Record omitted actual ASK cost164->163 outside Native; corrected Q2 gets a distinct declared ID. No Q1 replay.'}
    new(output/'PLAN.json',plan);return {'plan':str(output/'PLAN.json'),'sha256':sha(output/'PLAN.json'),'not_applied':True,'Native_calls':0}
def child(tx,role):
    plan=read(tx/'PLAN.json');row=next(x for x in plan['rows']if x['role']==role);root=Path(row['root']);folder=tx/role;system=root/'sistema'
    proof=BASE._closed_base(root);need(proof==row['closed_proof'],'CURRENT_CLOSED_ROLE_UNCHANGED')
    shutil.copyfile(proof['snapshot'],folder/'SNAPSHOT_ANTES_RECUPERACION.deetsnap.gz')
    sys.path[:0]=[str(system),str(system/'app')]
    from app.lives import Store
    store=Store(system);card=store.record(row['life']);physical=copy.deepcopy(card['physical'])
    with store.writer(card['world_id']):
        card,adapter=store.load(row['life']);BASE.reject_preloaded_actor(BASE.files(root)['actor'])
        before=dict(adapter.world.runtime.snapshot_metadata_entries)
        need(CORE.digest(json.loads(before[CORE.KEY]))==row['expected_current_own_metadata_sha256'],'NO_INTERVENING_NATIVE_METADATA_ACTIVITY')
        new(folder/'META_OWN_ANTES_EXACTO.json',{'KEY':before[CORE.KEY],'CODE_SCOPE_KEY':before[CORE.CODE]})
        after,witness=CORE.repaired_entries(before,row['original_proof']['own_metadata_preserved_from_failed_snapshot'],row['current_code_scope'])
        need(int(adapter.tick)==991543 and physical==row['closed_proof']['physical'],'EXACT_CLOSED_Q1_PHYSICAL_CUT')
        adapter.world.runtime.set_snapshot_metadata(CORE.KEY,after[CORE.KEY])
        card=store.commit(card,adapter,{'kind':'R07_TECHNICAL_KNOWN_ZERO_ADMISSION_GUARD_RECOVERY_R06','new_native_ticks':0,
          'failed_original_Q2':row['environment']['failed_Q2_id'],'failure_preserved':True,'autonomous_repair_or_learning':False},activate=False)
        actual=dict(adapter.world.runtime.snapshot_metadata_entries)
        need({k:v for k,v in actual.items()if k!=CORE.SYSTEM}=={k:v for k,v in after.items()if k!=CORE.SYSTEM},'ONLY_UNCERTAINTY_AND_OFFICIAL_SYSTEM_BOOKKEEPING_CHANGED')
        need(card['physical']==physical and int(adapter.tick)==991543,'NO_RAW_CLOCKS_GEOMETRY_OR_TICK_CHANGE')
    need(sha(folder/'SNAPSHOT_ANTES_RECUPERACION.deetsnap.gz')==proof['snapshot_sha256'],'ORIGINAL_SNAPSHOT_PRESERVED')
    result={'status':'TECHNICAL_UNCERTAINTY_ONLY_CLOSED','role':role,'life':row['life'],'new_native_ticks':0,
      'physical_before':physical,'physical_after':card['physical'],'snapshot_before_sha256':proof['snapshot_sha256'],'snapshot_after_sha256':card['snapshot_sha256'],
      'witness':witness,'failure_preserved':True,'Native_requests_submitted':0}
    new(folder/'NATIVE_RESULT.json',result);return result
def apply(tx):
    tx=BASE.safe(tx);plan=read(tx/'PLAN.json');need(not(tx/'APPLY_INTENT.json').exists(),'NO_AUTOMATIC_RECOVERY_RETRY')
    need(plan['source_sha256']==sha(Path(__file__))and plan['core_sha256']==sha(ROOT/'load/recuperacion_tecnica_core_R06.py'),'EXACT_REVIEWED_RECOVERY_SOURCES')
    need(plan['closed_tools_sha256']==sha(ROOT/'native/migrar_lease_cerrada_v3_R06.py'),'REVIEWED_CLOSED_TOOLS_UNCHANGED')
    available=host_available();need(available>=3758096384,'3_5GiB_HOST_MEMORY_BEFORE_ZERO_TICK_JOB')
    new(tx/'MEMORIA_PRE_APPLY.json',{'utc':BASE.utc(),'available_bytes':available,'minimum':3758096384,'Native_requests':0})
    need(sha(plan['source_reconciliation'])==plan['source_reconciliation_sha256']and sha(plan['lease_result'])==plan['lease_result_sha256'],'PRESERVED_RECONCILIATION_AND_LEASE')
    ledger=Path(plan['ledger']);need(sha(ledger)==plan['ledger_before_sha256'],'GLOBAL_LEDGER_CHANGED')
    for row in plan['rows']:
        root=Path(row['root']);need(BASE._closed_base(root)==row['closed_proof'],'NO_NEW_OWNER_OR_NATIVE_ACTIVITY')
        need(sha(BASE.files(root)['scope'])==row['scope_sha256']and sha(BASE.files(root)['actor'])==row['actor_sha256'],'NO_SOURCE_OR_SCOPE_CHANGE')
        need(sha(row['original_proof']['failed_official_receipt'])==row['original_proof']['failed_official_sha256'],'FAILED_RECEIPT_CHANGED')
    with BASE.ledger_lock(ledger):
        before=read(ledger);new(tx/'APPLY_INTENT.json',{'utc':BASE.utc(),'plan_sha256':sha(tx/'PLAN.json'),'Native_advance_allowed':False})
        for row in plan['rows']:new(Path(row['root'])/'LEASE_MIGRATION_IN_PROGRESS.json',{'transaction':str(tx),'kind':'KNOWN_ZERO_ADMISSION_RECOVERY_ONLY'})
        results=[]
        try:
            for row in plan['rows']:
                folder=tx/row['role'];root=Path(row['root']);pc=load(root/'sistema/app/process_control.py','_recovery_job_'+row['role'])
                command=[str(PRODUCT/'motor/python313/python.exe'),'-I','-B','-X','utf8',str(Path(__file__).resolve()),'--native-child-root-only','--transaction',str(tx),'--role',row['role']]
                job=None
                with(folder/'native.stdout.txt').open('x',encoding='utf8')as so,(folder/'native.stderr.txt').open('x',encoding='utf8')as se:
                    try:
                        process,job,name=pc.spawn_owned(command,cwd=ROOT,stdout=so,stderr=se,memory_limit=LIMIT);start=time.monotonic();samples=[]
                        while True:
                            resources=pc.job_resources(job);code=process.poll();samples.append({'elapsed_seconds':time.monotonic()-start,**resources})
                            if code is not None and resources.get('job_active_processes',0)==0:break
                            need(time.monotonic()-start<1200 and time.time()<1794906420,'BOUNDED_ADMINISTRATIVE_RECOVERY')
                            time.sleep(.5)
                        need(code==0 and(folder/'NATIVE_RESULT.json').is_file(),'RECOVERY_CHILD_FAILURE_PRESERVED_NO_RETRY')
                        results.append(read(folder/'NATIVE_RESULT.json'));new(folder/'JOB.json',{'pid':process.pid,'job':name,'exit_code':code,'memory_limit':LIMIT,'samples':samples})
                    finally:
                        if job is not None:pc.close_job(job)
            need(read(ledger)==before,'LEDGER_CHANGED_DURING_EXCLUSIVE_ADMINISTRATIVE_TRANSACTION')
            after,archived=CORE.archive_ledger(before,[r['original_proof']for r in plan['rows']],BASE.utc())
            BASE.atomic_bytes(ledger,BASE.json_bytes(after));new(tx/'ARCHIVED_FAILED_ADMISSIONS.json',archived)
            for row,result in zip(plan['rows'],results):
                environment=dict(row['environment'],technical_recovery_result=result,ledger_after_sha256=sha(ledger),transaction=str(tx),validated_not_learning=True)
                new(tx/row['role']/'ENVIRONMENT_VALIDATED.json',environment)
                new(Path(row['root'])/'TECHNICAL_RECOVERY_APPLIED_R06.json',{'transaction':str(tx),'plan_sha256':sha(tx/'PLAN.json'),'new_native_ticks':0,'snapshot_after_sha256':result['snapshot_after_sha256']})
            for row in plan['rows']:
                marker=Path(row['root'])/'LEASE_MIGRATION_IN_PROGRESS.json';need(read(marker)['transaction']==str(tx),'ONLY_OWN_ADMIN_MARKER');marker.unlink()
            result={'status':'THREE_KNOWN_ZERO_ADMISSION_GUARDS_RECOVERED','results':results,'ledger_before_sha256':plan['ledger_before_sha256'],
              'ledger_after_sha256':sha(ledger),'consumed_unchanged':10452,'reserved_each_unchanged':3740,'remaining_intents':after['intents'],
              'archived_failed_admissions':archived,'new_native_ticks':0,'Native_requests_submitted':0,'no_learning_or_autonomous_repair_claim':True}
            new(tx/'RESULTADO.json',result);return result
        except BaseException as error:
            new(tx/'INCOMPLETE_PRESERVED.json',{'error':type(error).__name__+': '+str(error),'automatic_retry':False,'markers_preserved':True});raise
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--prepare-root-only',action='store_true');g.add_argument('--apply-root-only',action='store_true');g.add_argument('--native-child-root-only',action='store_true')
    p.add_argument('--ledger',type=Path);p.add_argument('--output',type=Path);p.add_argument('--transaction',type=Path);p.add_argument('--role',choices=('LOAD1','LOAD2','LOAD3'));a=p.parse_args()
    if a.prepare_root_only:need(a.ledger and a.output,'EXPLICIT_PREPARATION_FIELDS');value=prepare(a)
    elif a.apply_root_only:value=apply(a.transaction)
    else:value=child(a.transaction.resolve(strict=True),a.role)
    print(json.dumps(value,ensure_ascii=False,indent=2))
