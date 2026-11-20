"""PILOT-only prospective filesystem lease. No Native imports or runtime.

Untouched official import0 is mandatory: no actor key, owner or episode is
created by this tool. Historical used MAIN/CTRL/LOAD states remain unchanged.
An interrupted APPLY remains marked; never automatically retry it.
"""
from pathlib import Path
import argparse,ast,copy,datetime,hashlib,importlib.util,json,os,shutil,sqlite3,sys,time,uuid
ROOT=Path(__file__).resolve().parents[1]
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V3_PILOT'
OLD_LAST=1794902400;OLD_END=1794906420
NEW_LAST=1794909600;NEW_END=1794913620
def need(v,m):
    if not v:raise ValueError(m)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def raw(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def create(p,v):
    with Path(p).open('xb')as f:f.write(raw(v));f.flush();os.fsync(f.fileno())
def replace(p,b):
    temp=Path(p).with_name(Path(p).name+'.PILOT_LEASE_'+uuid.uuid4().hex)
    with temp.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
    os.replace(temp,p)
def safe(p):
    p=Path(os.path.abspath(p))
    for q in reversed((p,*p.parents)):
        if q.exists():need(not q.is_symlink()and not getattr(q.lstat(),'st_file_attributes',0)&1024,'NO_LINKED_PATH')
    return p.resolve(strict=True)
def normalize(text):
    return text.replace(str(OLD_LAST),'LAST').replace(str(NEW_LAST),'LAST').replace(str(OLD_END),'END').replace(str(NEW_END),'END')
def changed_dates(text):
    need(str(OLD_LAST)in text and str(OLD_END)in text,'BOTH_OLD_DATES_REQUIRED')
    return text.replace(str(OLD_LAST),str(NEW_LAST)).replace(str(OLD_END),str(NEW_END))
def renew_scope(old,actor_sha,freeze_sha):
    need(old['life_id']==LIFE and old['role']=='pilot'and old['max_cycles']==3,'PILOT_UNUSED_SCOPE_ONLY')
    need(old['last_new_cycle_utc_epoch']==OLD_LAST and old['native_cutoff_utc_epoch']==OLD_END,'EXACT_PREVIOUS_WINDOW')
    new=copy.deepcopy(old);new['last_new_cycle_utc_epoch']=NEW_LAST;new['native_cutoff_utc_epoch']=NEW_END
    new['sources_sha256']['rbx07_native_v3.py']=actor_sha;new['code_scope_manifest_sha256']=freeze_sha
    a=copy.deepcopy(old);b=copy.deepcopy(new)
    for x in(a,b):
        for k in('last_new_cycle_utc_epoch','native_cutoff_utc_epoch','code_scope_manifest_sha256'):x.pop(k)
        x['sources_sha256'].pop('rbx07_native_v3.py')
    need(a==b,'ONLY_DATES_AND_CODE_WITNESSES')
    return new
def renew_ledger(old):
    need(old['limit']==160000 and old['max_worlds']==6 and old['intents']=={},'QUIESCENT_ORIGINAL_GLOBAL_LEDGER')
    need(old['last_new_episode_epoch']==OLD_LAST and old['cutoff_epoch']==OLD_END,'EXACT_PREVIOUS_GLOBAL_WINDOW')
    need(old['consumed']==sum(w['consumed']for w in old['worlds'].values()),'GLOBAL_DOSE_EXACT')
    w=old['worlds'].get(LIFE)
    need(w is None or(w['cycles']==0 and w['consumed']==0 and w['reserved']==0),'PILOT_NEVER_USED')
    new=copy.deepcopy(old);new['last_new_episode_epoch']=NEW_LAST;new['cutoff_epoch']=NEW_END
    new['lease_history']=[*old.get('lease_history',[]),{'utc':utc(),'original_start_epoch':1794841620,
      'old_last_new_epoch':OLD_LAST,'old_hard_finish_epoch':OLD_END,'new_last_new_epoch':NEW_LAST,'new_hard_finish_epoch':NEW_END,
      'scope':'ONLY unused PILOT; no MAIN/CTRL/LOAD admission or state migration','old_window_expired':True,
      'prospective_no_retroactive_admission':True,'consumed_unchanged':old['consumed'],'no_clock_or_counter_reset':True}]
    need({k:v for k,v in old.items()if k not in('last_new_episode_epoch','cutoff_epoch','lease_history')}==
         {k:v for k,v in new.items()if k not in('last_new_episode_epoch','cutoff_epoch','lease_history')},'ALL_ACCOUNTING_LITERAL')
    return new
def sources():
    bundle=ROOT/'native/lease_PILOT_R07_bundle';need(not bundle.exists(),'NEW_SOURCES_ONLY');bundle.mkdir()
    original=ROOT/'native/lease_R06_bundle/rbx07_native_v3.py';old=original.read_bytes();text=old.decode('utf8')
    actor=bundle/'rbx07_native_v3.py';actor.write_bytes(changed_dates(text).encode('utf8'))
    need(ast.dump(ast.parse(normalize(text)))==ast.dump(ast.parse(normalize(actor.read_text('utf8')))),'ACTOR_AST_ONLY_DATES')
    ledger=ROOT/'native/ledger_v3_R07.py';need(not ledger.exists(),'NEW_LEDGER_SOURCE_ONLY')
    text=changed_dates((ROOT/'native/ledger_v3_R06.py').read_text('utf8'))
    anchor='self.path=Path(path).resolve();self.life=life;self.role=role_for(life);self.max_cycles=max_cycles'
    need(text.count(anchor)==1,'EXACT_LEDGER_CONSTRUCTOR')
    text=text.replace(anchor,anchor+'\n        if life!='+repr(LIFE)+':raise ValueError("R07_RENEWAL_ONLY_UNUSED_PILOT")')
    ledger.write_text(text,encoding='utf8',newline='')
    owner=ROOT/'native/owner_support_v3_R07.py';need(not owner.exists(),'NEW_OWNER_SOURCE_ONLY')
    text=changed_dates((ROOT/'native/owner_support_v3_R06.py').read_text('utf8')).replace('ledger_v3_R06.py','ledger_v3_R07.py').replace('LEASE_APPLIED_R06.json','LEASE_APPLIED_PILOT_R07.json')
    anchor='destination = Path(destination).resolve(strict=True)\n    ledger_file'
    need(text.count(anchor)==1,'EXACT_OWNER_DESTINATION_ANCHOR')
    text=text.replace(anchor,'destination = Path(destination).resolve(strict=True)\n    if destination != REVISION_ROOT / "native/PILOT":raise ValueError("PILOT_ONLY_PROSPECTIVE_OWNER")\n    ledger_file')
    owner.write_text(text,encoding='utf8',newline='')
    driver=ROOT/'prototipo/NATIVE_LIMPIO_R07/ejecutar_piloto_R07_preparado_R07.py';need(not driver.exists(),'NEW_DRIVER_ONLY')
    text=changed_dates((driver.with_name('ejecutar_piloto_R07_preparado_R06.py')).read_text('utf8')).replace('owner_support_v3_R06.py','owner_support_v3_R07.py').replace('after08:00UTCNov17','after10:00UTCNov17')
    driver.write_text(text,encoding='utf8',newline='')
    paths=[actor,ledger,owner,driver,Path(__file__).resolve(),ROOT/'native/test_renovar_PILOT_unused_R07.py']
    rows=[]
    for p in paths:
        ast.parse(p.read_bytes());rows.append({'file':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
    f={'schema':'DEE.R07.PILOT_UNUSED.prospective_lease.R07','sealed':True,'utc':utc(),'native_start_epoch':1794841620,
       'last_new_episode_epoch':NEW_LAST,'native_cutoff_epoch':NEW_END,'only_life':LIFE,'old_window_expired':True,
       'Native_ticks':0,'Native_imports':0,'MCP_calls':0,'old_actor_sha256':sha(original),'native_actor_sha256':sha(actor),
       'files':rows,'global_tick_limit':160000,'max_lives':6,'owner_job_limit_bytes':536870912,'raw_support_limit':10000,
       'threads':1,'minimum_available_host_bytes':3758096384,'PILOT_scope_max':3,'PILOT_authorized_episodes':1,
       'other_roles_migrated':False,'automatic_material_execution':False,'reason':'Root prospective decision08:14UTC; no admission happened in expired08:00 window.'}
    p=ROOT/'control/CONGELADO_PILOT_LEASE_R07.json';create(p,f);return{'freeze':str(p),'sha256':sha(p),'files':rows}
def proof(own_transaction=None):
    pilot=safe(ROOT/'native/PILOT');system=pilot/'sistema';ctx=read(pilot/'CONTEXTO_EJECUCION.json');need(ctx['life']==LIFE,'EXACT_PILOT')
    marker=pilot/'LEASE_MIGRATION_IN_PROGRESS.json'
    if marker.exists():need(own_transaction is not None and read(marker).get('transaction')==str(own_transaction),'NO_INCOMPLETE_OR_FOREIGN_MIGRATION')
    cardp=system/'estado/vidas'/LIFE/'VIDA.json';card=read(cardp);imported=read(pilot/'IMPORTACION_DIAGNOSTICA.json')
    need(card['physical']['N']==67 and card['physical']['tick']==991187 and card['snapshot_sha256']==imported['result']['snapshot_sha256'],'LITERAL_UNUSED_IMPORT0')
    need(imported['new_native_ticks']==0 and imported['comparison']['physical_equal']and imported['comparison']['causal_prefix_equal'],'OFFICIAL_COMPLETE_IMPORT0')
    need(not(system/'estado/ACTIVO.json').exists()and not(system/'estado/locks'/(LIFE+'.lock')).exists(),'UNSELECTED_NO_OWNER_LOCK')
    actorlog=system/'estado/servicios_locales'/LIFE/'RBX07_NATIVE_INTEGRAL_V3/events.jsonl'
    need(not actorlog.exists()or actorlog.stat().st_size==0,'NO_NATIVE_ACTOR_HISTORY')
    journal=pilot/'ENSAYOS.jsonl'
    if journal.exists():need(not any(json.loads(s).get('kind')=='OWNER_STARTED'for s in journal.read_text('utf8').splitlines()if s.strip()),'NO_OWNER_STARTED_EVER')
    db=safe(system/'estado/servicios_persistentes'/LIFE/'cola.sqlite3');need(all(not Path(str(db)+s).exists()or Path(str(db)+s).stat().st_size==0 for s in('-wal','-journal')),'CLOSED_DB')
    before=sha(db);con=sqlite3.connect(db.as_uri()+'?mode=ro&immutable=1',uri=True)
    try:
        need(con.execute('PRAGMA quick_check').fetchone()[0]=='ok','DB_QUICK_CHECK')
        need(con.execute("SELECT COUNT(*) FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0]==0,'NO_PENDING')
        need(json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0])['running']is False,'CLOSED_OWNER_META')
    finally:con.close()
    need(before==sha(db),'DB_UNCHANGED')
    snap=safe(system/card['snapshot']);need(snap.is_relative_to(system)and sha(snap)==card['snapshot_sha256'],'SNAPSHOT_SHA_EXACT')
    protected=[cardp,snap,db,pilot/'CONTEXTO_EJECUCION.json',pilot/'IMPORTACION_DIAGNOSTICA.json',system/'capacidades/rbx07_identity_v3.py',system/'capacidades/rbx07_funciones_v3.py']
    return{'life':LIFE,'physical':card['physical'],'snapshot':str(snap),'snapshot_sha256':sha(snap),'actor_log_present':actorlog.exists(),
      'critical_sha256':{str(p):sha(p)for p in protected},'Native_owner_ever_started':False}
def other_roles():
    result={}
    for role in('MAIN','CTRL1','LOAD1','LOAD2','LOAD3'):
        p=ROOT/'native'/role;life=read(p/'CONTEXTO_EJECUCION.json')['life']
        for q in(p/'sistema/estado/vidas'/life/'VIDA.json',p/'sistema/capacidades/RBX07_NATIVE_SCOPE_INTEGRAL_V3.json',p/'sistema/capacidades/rbx07_native_v3.py',p/'sistema/app/HOST_INTEGRAL_V3.json'):result[str(q)]=sha(q)
    return result
def stage(output):
    need(time.time()<NEW_LAST,'PROSPECTIVE_STAGE_WINDOW');output=Path(os.path.abspath(output));need(output.parent.resolve()==ROOT/'control'and not output.exists(),'NEW_CONTROL_TX_ONLY')
    freeze=safe(ROOT/'control/CONGELADO_PILOT_LEASE_R07_REV2.json');f=read(freeze);need(f['only_life']==LIFE and f['sealed']is True,'PILOT_FREEZE')
    for row in f['files']:need(sha(safe(ROOT/row['file']))==row['sha256'],'FROZEN_SOURCE_CHANGED')
    current=proof();others=other_roles();ledger=safe(ROOT/'control/LEDGER_V3.json');oldledger=read(ledger);newledger=renew_ledger(oldledger)
    need(not ledger.with_name(ledger.name+'.LOCK').exists(),'NO_LEDGER_LOCK')
    pilot=ROOT/'native/PILOT';files={'actor':pilot/'sistema/capacidades/rbx07_native_v3.py','scope':pilot/'sistema/capacidades/RBX07_NATIVE_SCOPE_INTEGRAL_V3.json','host':pilot/'sistema/app/HOST_INTEGRAL_V3.json'}
    oldscope=read(files['scope']);need(sha(files['actor'])==oldscope['sources_sha256']['rbx07_native_v3.py']==f['old_actor_sha256'],'OLD_ACTOR_BYTES')
    newScope=renew_scope(oldscope,f['native_actor_sha256'],sha(freeze));oldhost=read(files['host']);need(oldhost['native_cutoff_utc_epoch']==OLD_END,'OLD_HOST')
    newhost=copy.deepcopy(oldhost);newhost['native_cutoff_utc_epoch']=NEW_END
    output.mkdir();create(output/'PREFLIGHT.json',current);create(output/'OTHER_ROLES_UNCHANGED_BASELINE.json',others)
    for name,p in files.items():shutil.copyfile(p,output/('OLD_'+p.name))
    for pstr in current['critical_sha256']:
        p=Path(pstr)
        if p.name in('VIDA.json','cola.sqlite3')or str(p)==current['snapshot']:shutil.copyfile(p,output/('PRESERVED_'+p.name))
    shutil.copyfile(ledger,output/'LEDGER_ANTES.json');create(output/'NEW_SCOPE.json',newScope);create(output/'NEW_HOST.json',newhost);create(output/'NEW_LEDGER.json',newledger)
    plan={'schema':'DEE.R07.PILOT_UNUSED.lease_transaction.R07','utc':utc(),'only_life':LIFE,'proof':current,'others':others,
       'freeze':str(freeze),'freeze_sha256':sha(freeze),'ledger':str(ledger),'ledger_sha256':sha(ledger),
       'files':{k:{'path':str(p),'old_sha256':sha(p)}for k,p in files.items()},'new_actor':str(ROOT/'native/lease_PILOT_R07_bundle/rbx07_native_v3.py'),
       'new_sha256':{n:sha(output/('NEW_'+n+'.json'))for n in('SCOPE','HOST','LEDGER')},'new_actor_sha256':f['native_actor_sha256'],
       'Native_runtime_loaded':False,'Native_calls':0,'new_ticks':0,'old_window_expired':True,'no_retroactive_admission':True,
       'new_last_epoch':NEW_LAST,'new_hard_epoch':NEW_END,'global_consumed_unchanged':oldledger['consumed'],'episode_cap_authorized':1}
    create(output/'PLAN.json',plan);return{'plan':str(output/'PLAN.json'),'sha256':sha(output/'PLAN.json'),'consumed':oldledger['consumed'],'physical':current['physical']}
def apply(tx,expected_sha):
    tx=safe(tx);need(tx.parent==ROOT/'control'and sha(tx/'PLAN.json')==expected_sha,'EXACT_TX_PLAN')
    plan=read(tx/'PLAN.json');need(not(tx/'APPLY_INTENT.json').exists(),'NO_RETRY_PARTIAL_TRANSACTION')
    need(time.time()<NEW_LAST,'NO_ADMISSION_AFTER_NEW_WINDOW');need(proof()==plan['proof']and other_roles()==plan['others'],'NO_ACTIVITY_SINCE_STAGE')
    need(sha(plan['freeze'])==plan['freeze_sha256'],'FREEZE_CHANGED')
    for row in read(plan['freeze'])['files']:need(sha(safe(ROOT/row['file']))==row['sha256'],'FROZEN_SOURCE_CHANGED')
    for n,row in plan['files'].items():need(sha(row['path'])==row['old_sha256'],'OPERATIONAL_FILE_CHANGED')
    for n,h in plan['new_sha256'].items():need(sha(tx/('NEW_'+n+'.json'))==h,'STAGED_CONTENT_CHANGED')
    need(sha(plan['new_actor'])==plan['new_actor_sha256'],'ACTOR_CHANGED')
    ledger=Path(plan['ledger']);lock=ledger.with_name(ledger.name+'.LOCK');token=uuid.uuid4().hex
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    try:
        with os.fdopen(fd,'w')as f:json.dump({'pid':os.getpid(),'token':token,'kind':'PILOT_UNUSED_ADMIN0'},f);f.flush();os.fsync(f.fileno())
        need(sha(ledger)==plan['ledger_sha256'],'LEDGER_CHANGED');renew_ledger(read(ledger))
        marker=ROOT/'native/PILOT/LEASE_MIGRATION_IN_PROGRESS.json';create(tx/'APPLY_INTENT.json',{'utc':utc(),'plan_sha256':expected_sha,'Native_calls':0});create(marker,{'transaction':str(tx)})
        try:
            replace(plan['files']['actor']['path'],Path(plan['new_actor']).read_bytes());replace(plan['files']['scope']['path'],(tx/'NEW_SCOPE.json').read_bytes());replace(plan['files']['host']['path'],(tx/'NEW_HOST.json').read_bytes())
            need(proof(tx)==plan['proof'],'CRITICAL_NATIVE_STATE_CHANGED')
            need(other_roles()==plan['others'],'OTHER_ROLES_CHANGED');need(sha(ledger)==plan['ledger_sha256'],'LEDGER_CONCURRENT_CHANGE')
            replace(ledger,(tx/'NEW_LEDGER.json').read_bytes())
            marker2=ROOT/'native/PILOT/LEASE_APPLIED_PILOT_R07.json';create(marker2,{'transaction':str(tx),'plan_sha256':expected_sha,'new_last_epoch':NEW_LAST,'new_hard_epoch':NEW_END,'Native_ticks':0,'untouched_import0_snapshot':True})
            # No physics loader is used: same snapshot/card/queue proves literal RAW/clocks/metadata preservation.
            final_proof=proof(tx);need(final_proof==plan['proof'],'FINAL_CRITICAL_NATIVE_STATE_CHANGED')
            result={'status':'PILOT_UNUSED_PROSPECTIVE_LEASE_COMPLETE','utc':utc(),'only_life':LIFE,'plan_sha256':expected_sha,
              'snapshot_byte_identical':True,'card_byte_identical':True,'SQLite_byte_identical':True,'all_original_critical_hashes':plan['proof']['critical_sha256'],
              'physical_before':plan['proof']['physical'],'physical_after':final_proof['physical'],'other_roles_bytes_unchanged':True,
              'global_consumed':read(ledger)['consumed'],'global_intents':read(ledger)['intents'],'ledger_before_sha256':plan['ledger_sha256'],'ledger_after_sha256':sha(ledger),
              'new_scope_sha256':sha(plan['files']['scope']['path']),'new_actor_sha256':sha(plan['files']['actor']['path']),
              'Native_imports':0,'Native_calls':0,'new_ticks':0,'no_scope_flags_or_counter_reset':True,'last_new_epoch':NEW_LAST,'hard_close_epoch':NEW_END}
            create(tx/'RESULTADO.json',result)
            marker.unlink()
            return result
        except BaseException as e:
            create(tx/'INCOMPLETE_PRESERVED.json',{'utc':utc(),'error':repr(e),'automatic_retry':False});raise
    finally:
        if lock.exists()and read(lock).get('token')==token:lock.unlink()
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True);g.add_argument('--prepare-sources',action='store_true');g.add_argument('--stage',type=Path);g.add_argument('--apply',type=Path);p.add_argument('--plan-sha256');a=p.parse_args()
    print(json.dumps(sources()if a.prepare_sources else stage(a.stage)if a.stage else apply(a.apply,a.plan_sha256),ensure_ascii=False,indent=2))
