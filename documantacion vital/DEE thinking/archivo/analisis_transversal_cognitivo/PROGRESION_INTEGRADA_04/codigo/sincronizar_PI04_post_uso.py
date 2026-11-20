"""Plan by default; synchronize metadata only after a REAL post-commit use.

No DEE imports, ticks, owner, GUI, promotion, memory edits or new experiments.
--aplicar requires actual closed-use/export/process evidence at the current cut.
The historical GUI seed and all historical validated_lives remain unchanged.
"""
from pathlib import Path,PurePosixPath
import argparse,copy,datetime,hashlib,json,os,runpy,shutil,sqlite3

P4=Path(__file__).resolve().parents[1];R=P4.parents[2]
C=R/'DEE Cognitive 2.0';S=C/'sistema';CONTROL=P4/'control'
LIFE='ECI02_PI03_REPRO_PI04_MAIN_02';PARENT='ECI02_PI03_MAIN';PARENT_T=775355
PARENT_SHA='5581d3785bf7d7194b5bdb545827aab55f0659d8b3f2c00301425d89616cf07b'
C2C_KEY='DEE.Cognitive.PI04.C2C.coordination.R01'
PARSER=P4/'codigo/contrastar_finales_E3_pasivo.py'

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def info(p):p=Path(p);return {'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p)}
def checked(path,root,must_exist=True):
    raw=Path(path).absolute();root=Path(root).absolute()
    if not raw.is_relative_to(root):raise ValueError('Lexical path outside allowed root')
    for part in(raw,*raw.parents):
        if part==root.parent:break
        if part.is_symlink()or(part.exists()and getattr(part.lstat(),'st_file_attributes',0)&1024):raise ValueError('No symlink/junction:'+str(part))
    target=raw.resolve(strict=must_exist)
    if not target.is_relative_to(root.resolve(strict=True)):raise ValueError('Resolved path outside allowed root')
    return target
def relative(value):
    if not isinstance(value,str)or '\\'in value or ':'in value:raise ValueError('Portable relative path required')
    p=PurePosixPath(value)
    if not value or p.is_absolute()or any(k in('..','.')for k in p.parts):raise ValueError('Unsafe relative path')
    return p
_ANY=object()
def atomic(path,value,expected=_ANY):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+'.pi04_post_uso.tmp')
    if expected is not _ANY and(sha(path)if path.exists()else None)!=expected:raise ValueError('Concurrent change before temporary write:'+str(path))
    with tmp.open('x',encoding='utf-8',newline='\n')as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
    if expected is not _ANY and(sha(path)if path.exists()else None)!=expected:raise ValueError('Concurrent change before atomic replace:'+str(path))
    os.replace(tmp,path)
def primary(path):
    d=read(path);return json.loads(d['result'])if isinstance(d.get('result'),str)else d
def existing_entry_protocol(card,adoption_witness):
    if card.get('life_id')!=LIFE or not card.get('world_id'):raise ValueError('Exact already-existing adopted identity/world required')
    return {'schema':'DEE.simple_entry.protocol.v1','life_id':LIFE,'world_id':card['world_id'],
        'source_snapshot_sha256':(card.get('parent')or{}).get('encoded_sha256'),'source_life':PARENT,
        'pending_material':None,'uncertain_preserved':False,'history_is_transport_not_native_memory':True,
        'never_automatic_material_retry':True,'genesis_explicit_existing_life':True,
        'existing_life_registered_utc':now(),'registration_evidence':adoption_witness,
        'scope':'Administrative registration of the already existing committed world; no import, experience, memory, work record or T0 created.'}
def actual_input_summary(row):
    groups={'outer':row['requests'],'FI':row['native_arithmetic']['native_operation']['native_trial']['requests'],'MU':row['second_native_use']['requests']}
    receipts={}
    for name,items in groups.items():
        for item in items:
            r=item['receipt'];identifier=int(item['id'])
            if identifier!=r['id']or not row['before_tick']<=r['requested_tick']<=row['after_tick']:raise ValueError('Receipt outside actual current-use window')
            if identifier in receipts and receipts[identifier]!=r:raise ValueError('Conflicting Native receipt aliases')
            receipts[identifier]=r
    if len(receipts)!=186 or any(r['status']!='applied'for r in receipts.values()):raise ValueError('Post-commit C2C use requires all186 actual direct Native inputs applied')
    return {'unique_requested':len(receipts),'applied':len(receipts),'rejected':0,'group_raw_counts':{k:len(v)for k,v in groups.items()},'IDs':sorted(receipts)}
def fresh_closed_processes(path):
    p=checked(path,P4);v=read(p);stamp=v.get('recorded_utc')
    stamp=datetime.datetime.fromisoformat(stamp.replace('Z','+00:00'))if isinstance(stamp,str)else None
    age=None if stamp is None or stamp.tzinfo is None else(datetime.datetime.now(datetime.timezone.utc)-stamp.astimezone(datetime.timezone.utc)).total_seconds()
    if age is None or not 0<=age<=600 or v.get('no_live_affected_writers')is not True or LIFE not in v.get('affected_life_ids',[])or not v.get('scope')or not v.get('evidence'):raise ValueError('Fresh zoned no-live-affected-writer proof required')
    return {'proof':info(p),'age_seconds':age,'scope':v['scope']}
def actual_closed_queue(card):
    for lock in(S/'estado/locks'/(card['world_id']+'.lock'),S/'estado/entrada_sencilla/vidas'/LIFE/'SUPERVISOR.lock',S/'estado/vidas'/LIFE/'FUTURO_INTERRUMPIDO.json',S/'estado/servicios_persistentes'/LIFE/'IMPORTACION_EN_CURSO.json'):
        if lock.exists():raise ValueError('Unresolved lock/interrupted operation:'+str(lock))
    db=checked(S/'estado/servicios_persistentes'/LIFE/'cola.sqlite3',S)
    wal=db.with_name(db.name+'-wal')
    if wal.exists()and wal.stat().st_size:raise ValueError('Nonempty operational WAL; do not assume a closed SQLite cut')
    con=sqlite3.connect(db.as_uri()+'?mode=ro&immutable=1',uri=True)
    try:
        if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Operational SQLite integrity failure')
        pending=con.execute("SELECT id,status FROM requests WHERE status IN('queued','processing','uncertain')").fetchall()
        row=con.execute("SELECT value FROM meta WHERE key='owner'").fetchone();owner=None if row is None else json.loads(row[0])
    finally:con.close()
    if pending or(owner and owner.get('running')is True):raise ValueError('Current operational owner/requests not closed and reconciled')
    return {'database':info(db),'pending':pending,'owner_cache':owner,'scope':'Cache corroborated by fresh process proof; not an instantaneous Native observation.'}
def latest_pair(path,card):
    proof_path=checked(path,P4);v=read(proof_path)
    if v.get('schema')!='DEE.PI04.stable_closed_full_pair.v1'or v.get('completed')is not True or v.get('actual_owned_job_closed')is not True or v.get('actual_owned_process_handle_exit_code')!=0 or v.get('new_native_ticks')!=0 or v.get('life_id')!=LIFE:raise ValueError('Actual closed zero-tick full-export witness required')
    if v.get('tick')!=card['physical']['tick']:raise ValueError('Latest pair is a different cut')
    for k in('N','tick','RAW_sha256','clocks_sha256'):
        if v['source_physical'][k]!=card['physical'][k]:raise ValueError('Latest pair/source current physical cut differs')
    for key in('zero_tick_export_comparison','export_source_comparison'):
        q=v.get(key,{})
        if q.get('physical_equal')is not True or q.get('causal_prefix_equal')is not True or q.get('new_ticks')!=0:raise ValueError('Exact zero-tick export comparison missing')
    folder=checked(v['destination'],C/'reproducibilidad');manifest=folder/'EXPORTACION_SERVICIO.json';m=read(manifest)
    if sha(manifest)!=v['manifest_sha256']or m.get('life_id')!=LIFE or m.get('queue_journal_required')is not True:raise ValueError('Full-pair manifest identity mismatch')
    origin=Path(v['source']).absolute();expected_origin=S/'estado/servicios_persistentes'/LIFE/'exportaciones'
    if origin.parent!=expected_origin or origin.exists():raise ValueError('Only the actual closed product export moved to the stable store is accepted')
    checked(origin,expected_origin,must_exist=False)
    for k in('N','tick','RAW_sha256','clocks_sha256'):
        if m['physical'][k]!=card['physical'][k]:raise ValueError('Latest pair manifest does not contain the actual current physical cut')
    seen=set();total=0
    for item in m['members']:
        name=relative(item['file']).as_posix()
        if name in seen:raise ValueError('Duplicate full-pair member')
        seen.add(name);member=checked(folder/name,folder)
        if member.stat().st_size!=item['bytes']or sha(member)!=item['sha256']:raise ValueError('Full-pair member changed:'+name)
        total+=item['bytes']
    actual={p.relative_to(folder).as_posix()for p in folder.rglob('*')if p.is_file()and p!=manifest}
    if actual!=seen or len(seen)!=v['members']or total!=v['bytes']:raise ValueError('Full pair has missing/unindexed members or different totals')
    registry_path=C/'reproducibilidad/RECURSOS.json';registry=read(registry_path);alias=v['alias']
    registered=registry.get('pairs',{}).get(alias,{})
    if registered.get('manifest_sha256')!=v['manifest_sha256']or registered.get('tick')!=card['physical']['tick']or checked(C/relative(registered['product_relative']),C)!=folder:raise ValueError('Actual latest full pair is not registered in Cognitive reproducibility')
    return {'alias':alias,'manifest':info(manifest),'path_relative_to_product':folder.relative_to(C).as_posix(),'tick':card['physical']['tick'],'members_verified':len(seen),'member_bytes':total,'witness':info(proof_path),'registry':info(registry_path),'scope':'Latest closed continuation export, distinct from historical GUI import seed; not new learning.'}
def plan(args):
    adoption_path=checked(args.adopcion,P4);decision_path=checked(args.decision,P4)
    adoption=read(adoption_path);decision=read(decision_path)
    if adoption.get('phase')!='COMMITTED'or adoption.get('life_id')!=LIFE or decision.get('approved_for_adoption')is not True or decision.get('life_id')!=LIFE:raise ValueError('Actual PI04 COMMITTED adoption and reasoned approval required')
    adoption_record=adoption['record'];adoption_tick=adoption_record['physical']['tick']
    card_path=checked(S/'estado/vidas'/LIFE/'VIDA.json',S);card=read(card_path)
    if card['life_id']!=LIFE or card['physical']['N']!=67 or card['physical']['tick']<adoption_tick:raise ValueError('Exact same current N67 life at or after adoption required')
    parent=card.get('PI04_migration',{}).get('physical_parent',{})
    if parent.get('life_id')!=PARENT or parent.get('tick')!=PARENT_T or parent.get('snapshot_sha256')!=PARENT_SHA:raise ValueError('Actual physical-parent migration provenance differs')
    active_path=S/'estado/ACTIVO.json';active=read(active_path);project_path=C/'PROYECTO.json';project=read(project_path);personal_path=S/'estado/genesis/SELECCION_PERSONAL.json';personal=read(personal_path)
    if active.get('life_id')!=LIFE or project.get('selected_life')!=LIFE or personal.get('life_id')!=LIFE:raise ValueError('All three current selectors must already identify this committed life; no new promotion')
    if active.get('tick')!=card['physical']['tick']or active.get('snapshot_sha256')!=card['snapshot_sha256']:raise ValueError('ACTIVO does not identify the latest current checkpoint')
    process=fresh_closed_processes(args.procesos);queue=actual_closed_queue(card)
    snapshot=checked(S/relative(card['snapshot']),S)
    parser=runpy.run_path(str(PARSER),run_name='post_use_frozen_stdlib_parser')['parse'];v=parser(snapshot,card['snapshot_sha256'])
    if v[0]['physical']!={k:card['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')}or v[4]:raise ValueError('Frozen current Native snapshot differs or has pending agenda')
    state=json.loads(v[6][C2C_KEY])
    if not state.get('ready')or not state.get('admitted')or state.get('arm')!='real'or any(state.get(k)for k in('pending','uncertain','halted_reason')):raise ValueError('Current Native C2C is not admitted real and coherently closed')
    usage_path=checked(args.uso,P4);d=primary(usage_path);row=d['result']['rows'][0]
    if d['committed_snapshot']['life_id']!=LIFE or row['arm']!='real'or row['before_tick']<adoption_tick or row['after_tick']!=card['physical']['tick']or row['after_tick']<=row['before_tick']:raise ValueError('A real post-commit use ending at the actual current cut is required')
    if type(row['useful_product'])is not bool or row['first_NULL_preserved']or row.get('first_rejected_preserved'):raise ValueError('Post-commit use has unresolved/invalid Native output or admission; preserve the failed future for diagnosis')
    inputs=actual_input_summary(row)
    native_receipts={x['id']:x for x in v[5]}
    direct_requests=[*row['requests'],*row['native_arithmetic']['native_operation']['native_trial']['requests'],*row['second_native_use']['requests']]
    for request in direct_requests:
        actual=native_receipts.get(int(request['id']),{})
        if actual.get('status')!=2 or actual.get('requested_tick')!=request['receipt']['requested_tick']or actual.get('channels')!=request['receipt']['channels']:raise ValueError('Recorded current-use input is not confirmed by the full Native receipt history')
    inputs['all_direct_receipts_confirmed_in_current_Native_snapshot']=True
    for k in('N','tick','RAW_sha256','clocks_sha256'):
        if d['committed_snapshot']['physical'][k]!=card['physical'][k]:raise ValueError('Use witness and latest Native physical state differ')
    product=row['actual_effect']['product'];product_file=None
    if row['useful_product']:
        if not isinstance(product,dict):raise ValueError('Claimed useful external product is absent')
        product_path=checked(S/'estado/servicios_locales'/LIFE/'PI04_C2C_COORDINACION_R01/dispositivo'/relative(product['path']),S)
        if product_path.stat().st_size!=product['bytes']or sha(product_path)!=product['sha256']or product['actual_native_integer']!=row['actual_numeric_result']:raise ValueError('Actual external product or transported Native value mismatch')
        product_file=info(product_path)
    elif product is not None:raise ValueError('Negative use must not be reported with a fabricated product')
    pair=latest_pair(args.exportacion,card)
    cut={'life_id':LIFE,'world_id':card['world_id'],'physical':card['physical'],'snapshot_sha256':card['snapshot_sha256'],'snapshot_relative_to_product':'sistema/'+card['snapshot']}
    use={'evidence':info(usage_path),'before_tick':row['before_tick'],'after_tick':row['after_tick'],'new_native_ticks':row['after_tick']-row['before_tick'],'ordinal':row['ordinal'],'operation':row['selected_operation'],'actual_numeric_result':row['actual_numeric_result'],'first_choice':row['first_reader']['choice'],'second_choice':row['second_native_use']['reader']['choice'],'Native_inputs':inputs,'useful_product':row['useful_product'],'product_file':product_file,'actual_failed':row['actual_failed'],'returned_failed':row['returned_failed'],'assistance':row['scope'],'scope':'One actual post-adoption C2C use, positive or adverse as recorded; not another full historical panel or a new promotion.'}
    adoption_cut={'life_id':LIFE,'physical':adoption_record['physical'],'snapshot_sha256':adoption_record['snapshot_sha256'],'witness':info(adoption_path)}
    cont_path=C/'CONTINUIDAD_DEE_COGNITIVE_2_0.json';cont=read(cont_path);catalog_path=S/'capacidades/CATALOGO_CAPACIDADES.json';catalog=read(catalog_path);config_path=C/'aplicacion/GENESIS/SELECCION_CANDIDATA.json';config=read(config_path)
    contract_path=checked(S/relative(decision['new_contract']['file']),S);contract=read(contract_path)
    if not contract_path.is_relative_to(S/'contratos')or contract_path.suffix!='.json':raise ValueError('Only actual PI04 JSON contract may be synchronized')
    entry_id=decision['catalog_entry']['id'];entries=[e for e in catalog['entries']if e.get('id')==entry_id]
    if len(entries)!=1:raise ValueError('Exact adopted PI04 capability entry required')
    if any(x.get('evidence',{}).get('sha256')==use['evidence']['sha256']for x in entries[0].get('post_adoption_native_uses',[])):raise FileExistsError('This actual post-commit use is already registered; reuse prior synchronization proof')
    project['latest_saved_tick']=card['physical']['tick'];project['current_operational_cut']=cut;project['post_adoption_use_PI04']=use;project['current_complete_pair_PI04']=pair
    personal['latest_confirmed_tick']=card['physical']['tick'];personal['latest_confirmed_snapshot_sha256']=card['snapshot_sha256']
    # source_* fields remain the literal historical import seed. Consumers use
    # Supervisor.backend.record(life) on reopening an existing registered life.
    old_seed={k:config.get(k)for k in('source_alias','source_life','source_tick','source_snapshot_sha256','source_paired_export_manifest','paired_export_manifest_sha256')}
    config.update(current_operational_tick=card['physical']['tick'],current_operational_snapshot_sha256=card['snapshot_sha256'],current_operational_snapshot_relative_to_product='sistema/'+card['snapshot'],current_complete_pair_PI04=pair,seed_scope='source_* remains the historical complete import seed; existing registered life reopens its latest VIDA without import or rewind.')
    cont.update(updated_utc=now(),physical_cut=card['physical'],latest_snapshot={'path_relative_to_product':'sistema/'+card['snapshot'],'sha256':card['snapshot_sha256']},identity_card={'path_relative_to_product':card_path.relative_to(C).as_posix(),'sha256':sha(card_path)},personal_selection=personal,selected_seed=config)
    cont['PI04_adoption_cut_preserved']=adoption_cut;cont['PI04_current_scope']=dict(cont.get('PI04_current_scope',{}),life_id=LIFE,physical_cut=card['physical'],snapshot_sha256=card['snapshot_sha256'],post_adoption_use=use);cont['PI04_latest_complete_pair']=pair
    cont['operational_directories']=list(dict.fromkeys([*cont.get('operational_directories',[]),pair['path_relative_to_product']]))
    historical_current=catalog.get('current_principal');catalog.setdefault('PI04_adoption_principal_preserved',copy.deepcopy(historical_current))
    current=dict(historical_current or {});current.update(life_id=LIFE,N=67,tick=card['physical']['tick'],snapshot_sha256=card['snapshot_sha256'],selection='COMMITTED',updated_utc=now(),post_adoption_use=use,adoption_cut=adoption_cut,current_complete_pair=pair)
    catalog['current_principal']=current;catalog['PI04_current_principal']=copy.deepcopy(current)
    entry=entries[0];entry.setdefault('post_adoption_native_uses',[]).append(use);entry['current_operational_life']=cut;entry['latest_complete_pair']=pair
    contract.setdefault('PI04_adoption_cut_preserved',adoption_cut);contract['PI04_current_operational_cut']=cut;contract.setdefault('post_adoption_native_uses',[]).append(use);contract['PI04_latest_complete_pair']=pair
    docs={project_path:project,personal_path:personal,config_path:config,cont_path:cont,catalog_path:catalog,contract_path:contract}
    protocol_path=checked(S/'estado/entrada_sencilla/vidas'/LIFE/'PROTOCOLO.json',S,must_exist=False)
    gui_created=not protocol_path.exists()
    if gui_created:
        docs[protocol_path]=existing_entry_protocol(card,info(adoption_path))
    else:
        protocol=read(protocol_path)
        if protocol.get('life_id')!=LIFE or protocol.get('world_id')!=card['world_id']or protocol.get('pending_material')or protocol.get('uncertain_preserved'):raise ValueError('Existing GUI protocol is incompatible or unresolved; preserve it')
    seed_after={k:config.get(k)for k in old_seed}
    if old_seed!=seed_after:raise AssertionError('Historical GUI seed was altered')
    originals={str(path):sha(path)if path.exists()else None for path in docs}
    critical={str(path):sha(path)for path in(card_path,snapshot,active_path,C/'reproducibilidad/RECURSOS.json',Path(pair['manifest']['path']),Path(queue['database']['path']),S/'estado/vidas'/PARENT/'VIDA.json')}
    parent_card=read(S/'estado/vidas'/PARENT/'VIDA.json')
    if parent_card['physical']['tick']!=PARENT_T or parent_card['snapshot_sha256']!=PARENT_SHA or sha(S/relative(parent_card['snapshot']))!=PARENT_SHA:raise ValueError('Protected physical parent changed')
    evidence={'adoption':info(adoption_path),'decision':info(decision_path),'current_cut':cut,'adoption_cut_preserved':adoption_cut,'actual_post_commit_use':use,'latest_complete_pair':pair,'process':process,'queue':queue,'Native_snapshot_pending':len(v[4]),'Native_C2C_closed':True,'GUI_protocol_creation_needed':gui_created,'GUI_seed_preserved':old_seed,'documents':[{'path':p.relative_to(C).as_posix(),'before_sha256':originals[str(p)]}for p in docs],'CAS_critical_hashes':critical,'scope':'Metadata synchronization only; no ACTIVO write, promotion, Native change, reimport or historical panel claim.'}
    return docs,originals,critical,evidence
def apply_plan(args,docs,originals,critical,evidence):
    token='T'+str(evidence['current_cut']['physical']['tick'])+'_'+evidence['actual_post_commit_use']['evidence']['sha256'][:12]
    backup=checked(CONTROL/('POST_USO_PI04_'+token),P4,must_exist=False)
    if backup.exists():raise FileExistsError('Prior post-use synchronization preserved; inspect its stage')
    for path,h in {**originals,**critical}.items():
        p=Path(path)
        if (sha(p)if p.exists()else None)!=h:raise ValueError('Concurrent change before synchronization:'+path)
    # Refresh the writer check immediately before the first output/product edit.
    fresh_closed_processes(args.procesos)
    backup.mkdir(parents=True);stage=backup/'SINCRONIZACION.json'
    for path in docs:
        if path.exists():
            target=backup/'originales'/path.relative_to(C);target.parent.mkdir(parents=True,exist_ok=True)
            with path.open('rb')as a,target.open('xb')as b:shutil.copyfileobj(a,b)
            if sha(target)!=originals[str(path)]:raise ValueError('Backup byte identity mismatch')
    status={'schema':'PI04.metadata.post_commit_use_sync.v1','phase':'PREPARED','at':now(),'evidence':evidence,'steps':[],'new_Native_ticks_by_sync':0,'new_promotion':False}
    atomic(stage,status)
    try:
        for path,value in docs.items():
            if (sha(path)if path.exists()else None)!=originals[str(path)]:raise ValueError('Concurrent metadata change; preserve partial stage:'+str(path))
            atomic(path,value,expected=originals[str(path)]);status['steps'].append(info(path));atomic(stage,status)
        for path,h in critical.items():
            if sha(Path(path))!=h:raise ValueError('A Native/selection/registry source changed during metadata synchronization:'+path)
        status.update(phase='COMMITTED_METADATA_ONLY',completed_utc=now(),all_document_hashes=[info(p)for p in docs],Native_and_ACTIVO_unchanged=True)
        atomic(stage,status);return {'proof':info(stage),'phase':status['phase'],'new_Native_ticks':0,'promotion':False}
    except BaseException as error:
        status.update(phase='FAILED_PARTIAL_PRESERVED',error={'type':type(error).__name__,'message':str(error)})
        atomic(stage,status);raise
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--aplicar',action='store_true')
    ap.add_argument('--uso',type=Path);ap.add_argument('--exportacion',type=Path);ap.add_argument('--procesos',type=Path)
    ap.add_argument('--adopcion',type=Path,default=CONTROL/'ADOPCION_PRODUCTO_PI04.json');ap.add_argument('--decision',type=Path,default=CONTROL/'DECISION_FINAL_PI04.json');args=ap.parse_args()
    if not all((args.uso,args.exportacion,args.procesos)):
        if args.aplicar:ap.error('--aplicar requires actual --uso --exportacion --procesos')
        print(json.dumps({'mode':'PLAN_NO_NATIVE_NO_WRITES','status':'BLOCKED_UNTIL_REAL_EVIDENCE','required':['actual COMMITTED adoption','actual post-commit C2C use ending at current Native cut','registered exact closed latest full pair','fresh no-live-writer proof'],'adoption_available':args.adopcion.is_file(),'decision_available':args.decision.is_file(),'no_future_tick_or_result_assumed':True},ensure_ascii=False,indent=2));return
    try:docs,originals,critical,evidence=plan(args)
    except Exception as error:
        if args.aplicar:raise
        print(json.dumps({'mode':'PLAN_NO_NATIVE_NO_WRITES','status':'BLOCKED','reason':type(error).__name__+': '+str(error)},ensure_ascii=False,indent=2));return
    result=apply_plan(args,docs,originals,critical,evidence)if args.aplicar else{'mode':'PLAN_NO_NATIVE_NO_WRITES','status':'READY_ONLY_FOR_METADATA_SYNC','evidence':evidence}
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
