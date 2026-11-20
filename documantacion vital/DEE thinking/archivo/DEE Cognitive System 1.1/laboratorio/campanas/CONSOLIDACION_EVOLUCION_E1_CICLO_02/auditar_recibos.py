"""Exact input ledger from saved snapshots and commit journals.
Only one passive restored world is used to name serializer status codes.
No native tick/input, no life commit, no simulator step and no answer policy.
"""
from pathlib import Path
from collections import Counter
import gzip,hashlib,importlib.util,json,sys
L=Path(__file__).resolve().parent;R=L.parents[2];S=R/'sistema';E=R/'evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02'
sys.path.insert(0,str(S))
from app.lives import Store
from app.native_tools import physical
sp=importlib.util.spec_from_file_location('snapshot_only',S/'capacidades/observador_causal_retrospectivo_01.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canon(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')
def walk(v):
    yield v
    if isinstance(v,dict):
        for q in v.values():yield from walk(q)
    elif isinstance(v,list):
        for q in v:yield from walk(q)
files=[json.loads(gzip.decompress(p.read_bytes()))for p in sorted((E/'EXPORTACION/EVIDENCIA_CAUSAL/PRIMARIOS').glob('*.json.gz'))]
cache={};journal_cache={};digest_cache={}
def digest(p):
    key=str(p)
    if key not in digest_cache:digest_cache[key]=sha(p)
    return digest_cache[key]
def snap(path,expected=None):
    p=Path(path);p=p if p.is_absolute()else S/p
    key=str(p)
    if key not in cache:
        x=m.Snapshot(p)
        cache[key]={'path':str(p.relative_to(R)),'sha256':x.encoded_sha256,'tick':x.tick,'next_event_id':x.next_event_id,
                    'pending_count':len(x.pending),'receipts':{q['id']:q for q in x.receipts},'checksum_valid':x.checksum_valid}
    q=cache[key]
    if expected:assert q['sha256']==expected
    return q
def locate(life,tick,h):
    for p in(S/'estado/checkpoints').glob(life+'.T'+str(tick)+'.*'):
        if digest(p)==h:return p
    raise FileNotFoundError('Scoped snapshot not found '+life+' T'+str(tick)+' '+h)
def journal(life):
    if life not in journal_cache:
        p=S/'estado/vidas'/life/'HISTORIA.jsonl';index={}
        if p.exists():
            with p.open(encoding='utf8')as f:
                for line in f:
                    v=json.loads(line);op=v['operation'];index[v['snapshot_sha256']]={'before_hash':v.get('previous_snapshot_sha256'),'after_hash':v['snapshot_sha256'],
                        'before_tick':op.get('before',{}).get('tick'),'after_tick':op.get('after',{}).get('tick',v.get('tick')),'kind':op['kind']}
        journal_cache[life]=index
    return journal_cache[life]
# Read, do not mutate, the exact current MAIN. The status-name authority is the
# official receipt object itself, matched to the serializer's integer code.
store=Store();record,adapter=store.load('E1_CICLO02_MAIN');before=physical(adapter.world);saved=snap(store.snapshot(record),record['snapshot_sha256']);status_names={};authority=[]
for raw_code in sorted({q['status']for q in saved['receipts'].values()}):
    example=next(q for q in saved['receipts'].values()if q['status']==raw_code);receipt=adapter.world.runtime.receipt(example['id']);name=str(receipt.status)
    assert int(receipt.id)==example['id']and int(receipt.requested_tick)==example['requested_tick']
    status_names[raw_code]=name;authority.append({'raw_status_code':raw_code,'official_status_name':name,'example_id':example['id'],'source_snapshot_sha256':record['snapshot_sha256']})
after=physical(adapter.world);assert before==after and digest(store.snapshot(record))==record['snapshot_sha256'];del adapter
results={};unresolved=[]
for d in files:
    id=d['id'];life=d.get('life');a=None;b=None;kind=None
    if d.get('initial_life')and d.get('final_life'):
        aa=d['initial_life'];bb=d['final_life'];life=bb['life_id'];a=snap(aa['snapshot'],aa['snapshot_sha256']);b=snap(bb['snapshot'],bb['snapshot_sha256']);kind='NATIVE_RECORDED_CALLBACK'
    elif d.get('instrument_context',{}).get('snapshot_sha256')and life:
        i=d['instrument_context'];h=i['snapshot_sha256'];j=journal(life).get(h)
        if j and j['before_tick']is not None and j['kind']not in('CANDIDATE','EXACT_FORK','DIAGNOSTIC_COPY','IMPORT_FULL_STATE'):
            a=snap(locate(life,j['before_tick'],j['before_hash']),j['before_hash']);b=snap(locate(life,j['after_tick'],h),h);kind=j['kind']
    if a is None or b is None:
        results[id]={'life':life,'new_requests':0 if d.get('argv')and any(w in d['argv']for w in('integrado-estado','guardar','bifurcar'))else None,
                     'scope':'No mutation envelope (passive query, identity fork or no completed operation); do not equate historical request references with new inputs.'}
        continue
    # Extend a status code only from an exact terminal official receipt in this
    # very post-state; never guess a name for an unobserved enum value.
    for v in walk(d['payload']):
        if not isinstance(v,dict)or'id'not in v or'status'not in v or type(v['id'])is not int:continue
        if v['status']in('scheduled','pending','MISSING_RECEIPT'):continue
        q=b['receipts'].get(v['id'])
        if q:
            old=status_names.get(q['status'])
            if old is not None:assert old==v['status'],('receipt status conflict',id,v['id'],old,v['status'])
            else:status_names[q['status']]=v['status'];authority.append({'raw_status_code':q['status'],'official_status_name':v['status'],'example_id':v['id'],'source_primary':d['original']})
    start=a['next_event_id'];stop=b['next_event_id'];assert stop>=start
    new_ids=list(range(start,stop));new_receipts=[b['receipts'].get(i)for i in new_ids]
    applied=[];rejected=[];events=[]
    for q in b['receipts'].values():
        previous=a['receipts'].get(q['id']);name=status_names.get(q['status'],'UNRESOLVED_ENUM_'+str(q['status']));old=status_names.get(previous['status'])if previous else None
        changed=previous is None or q['status']!=previous['status']
        if changed:
            events.append({**q,'status_name':name,'before_status_name':old,'new_request_in_this_operation':q['id']in range(start,stop)})
            if name=='applied':applied.append(q['id'])
            elif name.startswith('rejected'):rejected.append(q['id'])
    c=Counter(status_names.get(q['status'],'UNRESOLVED_ENUM_'+str(q['status']))if q else'MISSING_RECEIPT'for q in new_receipts)
    if any(k.startswith('UNRESOLVED')or k=='MISSING_RECEIPT'for k in c):unresolved.append(id)
    results[id]={'life':life,'kind':kind,'before':{k:a[k]for k in('path','sha256','tick','next_event_id','pending_count')},
        'after':{k:b[k]for k in('path','sha256','tick','next_event_id','pending_count')},
        'new_requests':len(new_ids),'new_id_range_half_open':[start,stop],'new_request_status_at_operation_end':dict(c),
        'applied_during_operation':len(applied),'rejected_during_operation':len(rejected),'pending_inputs_at_operation_end':b['pending_count'],
        'transitions':events,'scope':'New requests use monotonic input-ID difference; applied/rejected window includes previously queued requests. These denominators must not be divided blindly or counted as independent learners.'}
out={'schema':'DCS.C02.input-ledger.v1','native_ticks':0,'passive_restore_only':'E1_CICLO02_MAIN','official_status_authority':authority,
 'passive_observation_before':before,'passive_observation_after':after,'source_file_unchanged':True,
 'scope':'Zero-tick archival envelope/header/receipt calculation. Runtime was only restored once to name status codes, never stepped or committed. Forked prefixes remain distinct worlds, not independent acquisitions.',
 'operations':results,'unresolved_operations':unresolved,'unique_complete_snapshots_read':len(cache)}
path=E/'RECIBOS_OPERACIONES_EXACTOS.json.gz';path.write_bytes(gzip.compress(canon(out),9,mtime=0))
print(json.dumps({'operations':len(results),'resolved_mutation_envelopes':sum('before'in r for r in results.values()),'snapshots_read':len(cache),'unresolved':unresolved,'enum_authority':authority,'native_ticks':0,'bytes':path.stat().st_size},ensure_ascii=False))
