"""Prepared conditional D: fixed physical contingency change, no Native on import.

Reuse literal C/R02 decisions, sensor codec, actuator and six-lap second return.
One legal stationary SEM4 birth is environmental P0. New finite12 opportunity
metadata preserves ancestor R02 ordinal12 and its six available future offers.
No first-query credit, target, bank reset, RAW edit or per-failure support.
"""
from pathlib import Path
import copy,hashlib,importlib.util,json

VERSION='DEE.PI09.persistent_environment.D.R02'
KEY='DEE.Cognitive.PI09.persistent_environment.D.R02'
FOLDER='PI09_ENTORNO_PERSISTENTE_D_R02'
SUPERSEDED_KEY='DEE.Cognitive.PI09.persistent_environment.D.R01'
PREPARE='eci01-pi09-d-preparar';EPISODE='eci01-pi09-d-episodio';STATE='eci01-pi09-d-estado';MODES={PREPARE,EPISODE,STATE}
PROTOCOL=Path(__file__).with_name('PROTOCOLO_PI09_D_R02.json')
SEAL=Path(__file__).with_name('SELLO_PI09_D_R02.json')
PARENT_SOURCE=Path(__file__).with_name('pi09_consulta_selectiva_R02.py')
PARENT_SHA='3b81573f4dc0d9401db2210f3b23694e1f1f4a4d820d7654bcbd1e1b42b2dfbf'
PARENT_KEY='DEE.Cognitive.PI09.selective_registered_consultation.R02'
GUARD=(52,48,48);GUARD_CHANNEL='PI09.D.fixed_environment.guard48.SEM4.R01'
PREFIX='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_'
LIVES={'real':PREFIX+'DISCOVERY_01','none':PREFIX+'STAGE3_NONE_01','yoked':PREFIX+'STAGE3_YOKE_01'}
REPRO_IDS=[PREFIX+'DREPRO_01']
PERMUTATION=[2,0,4,1,5,3]
_PRIVATE=None
def _require(ok,reason):
    if not ok:raise ValueError(reason)
def _sha(data):return hashlib.sha256(data).hexdigest()
def _hash(v):return isinstance(v,str)and len(v)==64 and all(c in'0123456789abcdef'for c in v)
def protocol(material=False):
    data=PROTOCOL.read_bytes();p=json.loads(data);ph=_sha(data)
    _require(p.get('schema')=='DEE.PI09.persistent_environment.D.protocol.R02'and p.get('N')==67 and p.get('origin')==[8,40,50]and p.get('delay_laps')==6,'Exact D physical/calendar protocol required')
    _require(p.get('max_ticks_per_episode')==1300 and p.get('max_ticks_per_C_opportunity')==2110 and len(p.get('schedule',[]))==12 and p.get('evaluation_horizon')==6,'Six evaluated plus six explicit future D opportunities')
    contexts=[(r.get('cue'),r.get('message_payload'))for r in p['schedule']]
    _require(contexts[:6]==[('threat',5),('none',8),('falsecue',11),('threat',8),('none',5),('threat',11)],'Prospectively fixed six evaluated material contexts required')
    _require(p.get('max_ticks_per_whole_D_opportunity')==2510 and p.get('max_ticks_per_arm')==15063,'Declared wait plus unchanged C core must fit the prospective whole bound')
    _require([r.get('wait_ticks')for r in p['schedule']]==[0,0,0,400,0,0,0,0,400,0,0,0],'Fixed external waits at evaluated3/future8 only')
    for row in p['schedule']:
        _require(type(row.get('left'))is int and type(row.get('right'))is int and 0<=row['right']<row['left']<=20,'Public positive FI operands only')
    _require(p.get('guard')=={'site':[52,48,48],'direction':[0,0,0],'state':0,'semantic':4,'payload':0,'birth_offset':2,'preparation_ticks':3},'One fixed legal support only; no repair or alternative site')
    _require(p.get('yoke_permutation')==PERMUTATION,'No permutation optimization')
    if material:
        seal=json.loads(SEAL.read_text('utf-8-sig'))
        _require(p.get('status')=='SEALED_CONDITIONAL_BEFORE_D_NATIVE'and seal.get('schema')=='DEE.PI09.persistent_environment.D.source_seal.R02'and seal.get('protocol_sha256')==ph,'Root actual conditional source seal required')
        _require(seal.get('source_parent_R02_ordinal')==12 and seal.get('arms')==LIVES and seal.get('native_reproduction_ids')==REPRO_IDS and seal.get('operational_native_id')==LIVES['real'],'Exact acquired parent and separate diagnostic/reproduction identities required')
        src=seal.get('source_prefix',{})
        _require(type(src.get('tick'))is int and src['tick']>=903603 and src.get('N')==67 and _hash(src.get('manifest_sha256'))and _hash(src.get('snapshot_sha256')),'Future actual post-panel source must be sealed, never substitute an earlier frozen cut')
        _require(set(src.get('physical',{}))=={'N','tick','RAW_sha256','clocks_sha256'}and src['physical']['N']==67 and src['physical']['tick']==src['tick']and _hash(src['physical']['RAW_sha256'])and _hash(src['physical']['clocks_sha256']),'Exact four-field physical source; keep extra metrics separately')
        _require(seal.get('first_milestone_committed')is True and _hash(seal.get('first_milestone_adoption_sha256')),'D is conditional after the first milestone; preparation is not execution authorization')
        for name,value in seal.get('files_sha256',{}).items():
            _require(Path(name).name==name and _hash(value)and _sha(Path(__file__).with_name(name).read_bytes())==value,'D frozen source changed: '+name)
        _require({Path(__file__).name,PROTOCOL.name,PARENT_SOURCE.name}<=set(seal.get('files_sha256',{})),'Explicit D and literal R02 source pins required')
    return p,ph

def _bridge():
    global _PRIVATE
    if _PRIVATE is not None:return _PRIVATE
    _require(_sha(PARENT_SOURCE.read_bytes())==PARENT_SHA,'Original R02 literal must remain unchanged')
    s=importlib.util.spec_from_file_location('capacidades._PI09_D_private_R02_literal',PARENT_SOURCE);b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
    b.VERSION,b.KEY,b.FOLDER=VERSION,KEY,FOLDER
    b.PREPARE,b.EPISODE,b.STATE,b.MODES=PREPARE,EPISODE,STATE,MODES
    b.PROTOCOL,b.SEAL=PROTOCOL,SEAL
    b._protocol,b._identity,b._old_literals=protocol,_identity,_old_literals
    b.validate,b._validate_second=validate,_validate_second
    _PRIVATE=b
    return b
def _core():
    c=_bridge()._core();c._return=_returned
    return c
def _identity(a):
    c=_core();_,_,_,decode,_=c._native();identity=decode(dict(a.world.runtime.snapshot_metadata_entries)[c.body.SYSTEM_KEY])
    life=identity.get('life_id');_require(life in [*LIVES.values(),*REPRO_IDS]and identity.get('profile')=='fisica_directa'and int(a.world.runtime.dimension)==67,'Exact D N67 diagnostic/reproduction life only')
    active=Path(__file__).resolve().parents[1]/'estado/ACTIVO.json'
    if active.is_file()and json.loads(active.read_text('utf-8-sig')).get('life_id')==life:_operational_permission(a,identity)
    _bridge()._C().LIFE=life
    return identity
def _operational_permission(a,identity):
    life=identity['life_id'];_require(life==LIVES['real']and KEY in dict(a.world.runtime.snapshot_metadata_entries),'Only actual acquired D real canonical life may become selected')
    m=_get(a);_require(m['control']['arm']=='real'and m['control']['query_policy']=='native'and m['control']['information_policy']=='real','No reference policy may become principal')
    file=Path(__file__).resolve().parents[1]/'contratos/PI09_D_USO_OPERATIVO_R02.json';contract=json.loads(file.read_text('utf-8-sig'));_,ph=protocol(False)
    _require(contract.get('schema')=='DEE.PI09.D.exact_operational_permission.v2'and contract.get('status')=='COMMITTED'and contract.get('life_id')==life and contract.get('profile')=='fisica_directa'and contract.get('protocol_sha256')==ph and contract.get('allowed_modes')==[EPISODE,STATE]and contract.get('all_adoption_gates_met')is True and _hash(contract.get('adoption_decision_sha256')),'Actual exact D COMMITTED contract required before selected use')
    return contract
def _old_literals(a):
    c=_core();entries=dict(a.world.runtime.snapshot_metadata_entries)
    keys=[c.body.KEY,c.previous.KEY,'DEE.Cognitive.PI07.regulation.environment.R03',_bridge().OLD_C_KEY,PARENT_KEY]
    if _bridge()._C().OLD_B_KEY in entries:keys.append(_bridge()._C().OLD_B_KEY)
    return {k:entries[k]for k in keys}
def _get(a):return _bridge()._get(a)
def validate_yoke(value):
    _require(isinstance(value,str)and len(value.encode('utf8'))<=2048,'Bounded JSON return plan only')
    plan=json.loads(value)
    _require(set(plan)=={'schema','permutation','source_failed','values','source_evidence_sha256'}and plan['schema']=='DEE.PI09.D.yoked_return.fixed_permutation.v1'and plan['permutation']==PERMUTATION and _hash(plan['source_evidence_sha256']),'Fixed actual D real return source only')
    _require(len(plan['source_failed'])==len(plan['values'])==6 and all(type(x)is bool for x in plan['source_failed']+plan['values']),'Six actual failure booleans required')
    _require(plan['values']==[plan['source_failed'][i]for i in PERMUTATION],'Yoke values must be the prefixed actual-source permutation')
    return plan
def _returned(m,failed):
    arm=m['control']['arm']
    if arm=='real':return bool(failed)
    if arm=='none':return False
    _require(arm=='yoked','Known D arm required');return m['control']['return_plan']['values'][m['ordinal']]
def validate_literal(row):
    _require(isinstance(row,dict)and row.get('modo')in MODES,'Fixed D modes only')
    if row['modo']!=PREPARE:
        _require(set(row)=={'modo'},'No action/expected/cue/bank/coordinate override');return
    arm=row.get('brazo');_require(arm in LIVES,'Root explicit D control arm only')
    _require(set(row)==({'modo','brazo','plan'}if arm=='yoked'else{'modo','brazo'}),'Exact D preparation fields')
    if arm=='yoked':validate_yoke(row['plan'])
def validate(a,row):
    validate_literal(row);identity=_identity(a)
    if row['modo']==STATE:return
    p,ph=protocol(True);entries=dict(a.world.runtime.snapshot_metadata_entries)
    if row['modo']==PREPARE:
        exact=LIVES[row['brazo']]==identity['life_id'];repro=row['brazo']=='real'and identity['life_id']in REPRO_IDS
        _require(KEY not in entries and SUPERSEDED_KEY not in entries and(exact or repro),'No D reinstallation, R01future reinterpretation, reference/reproduction role override or counter reset')
        seal=json.loads(SEAL.read_text('utf-8-sig'));_require(_core()._physical(a)==seal['source_prefix']['physical'],'Only the actual sealed post-panel source may prepare D')
        _,_,_,decode,_=_core()._native();parent=decode(entries[PARENT_KEY])
        _require(parent.get('ordinal')==12 and len(parent.get('rows',[]))==12 and parent.get('ready')and not parent.get('pending')and not parent.get('uncertain')and parent['control']['arm']=='native_real','Coherent acquired Native R02_12 ancestor required; no resetting stock or pending state')
        _require(parent['control']['query_policy']=='native'and parent['control']['information_policy']=='real','Preserve actual acquired policy')
        return
    m=_get(a);_require(m['protocol_sha256']==ph and m['ready']and not m['pending']and not m['uncertain']and m['ordinal']<12 and(m['control']['arm']=='real'or m['ordinal']<6),'Closed finite D progress; controls are evaluation-only6')
def _validate_second(a,row):
    validate_literal(row);_identity(a);_,ph=protocol(True);m=_get(a)
    _require(row['modo']==EPISODE and m['protocol_sha256']==ph and m['ready']and m['ordinal']<12 and(m['control']['arm']=='real'or m['ordinal']<6)and m.get('pending',{}).get('phase')=='C_SECOND_STAGE_PENDING'and m.get('sample_register'),'Only actual pending D second stage, no replay or invented sample')

def prepare(a,row,directory):
    validate(a,row);c=_core();p,ph=protocol(True);identity=_identity(a);start=int(a.tick);old=_old_literals(a)
    _require(not c._home(directory,identity['life_id']).exists()and GUARD_CHANNEL not in set(a.world.runtime.channel_names),'Fresh D namespace and home only')
    preflight=c._observe(a,GUARD);_require(int(preflight['raw'])==0,'Guard48 must be whole RAW0 now; refuse without clearing, moving or searching an alternative')
    _,_,_,decode,_=c._native();parent=decode(old[PARENT_KEY]);control={'arm':row['brazo'],'query_policy':'native','information_policy':'real','from_ordinal':0,'max_ordinal':12,'evaluation_horizon':6}
    if row['brazo']=='yoked':control['return_plan']=validate_yoke(row['plan'])
    m={'version':VERSION,'life_id':identity['life_id'],'protocol_sha256':ph,'ordinal':0,'rows':[],'role':'evaluation','control':control,'instrumentation':{'global_enabled':False},'ready':False,'admitted':True,'pending':{'phase':'D_FIXED_ENVIRONMENT_PREPARATION'},'uncertain':True,'log_count':0,'log_chain_sha256':'00'*32,'old_metadata_sha256':{k:_sha(v.encode('utf8'))for k,v in old.items()},'body_P0':copy.deepcopy(parent['body_P0']),'sample_register':None,'first_stage_rows':[],'source_parent_life_id':parent['life_id'],'source_parent_PI09_ordinal':12,'environmental_supply':{'new_D_opportunities':12,'evaluation_horizon':6,'future_stock':6,'old_R02_ordinal_preserved':12,'old_R02_stock6_preserved':True,'physical_bank_reset':False},'P0_guard':{'site':list(GUARD),'state':0,'semantic':4,'payload':0,'direction':[0,0,0],'preflight':preflight,'new_support_after_each_failure':False}}
    c._record(a,m,directory,{'kind':'D_FIXED_ENVIRONMENT_PREPARATION_INTENT','preflight':preflight,'control':control,'physical_bank_or_clock_edit':False,'namespace12_is_explicit_environmental_supply':True,'evaluation_horizon':6,'future_stock':6})
    c.body._declare(a.world,GUARD_CHANNEL,GUARD,(0,0,0),0,4);requests=[];c._submit(a,GUARD_CHANNEL,0,start+2,requests,site=GUARD,direction=(0,0,0))
    c.body.SafeAdapter(a).run_until(start+3);requests=c._receipts(a,requests);summary=c._summary(requests,start,int(a.tick));after=c._observe(a,GUARD)
    ready=summary['all_terminal']and summary['applied']==1 and int(after['raw'])==(4<<60)
    m['P0_guard'].update(requests=requests,actual_after=after,Native_inputs=summary)
    m.update(ready=ready,uncertain=not summary['all_terminal'],pending=None if ready else{'phase':'unknown_D_guard_receipt'if not summary['all_terminal']else'D_guard_terminal_not_installed'})
    _require(_old_literals(a)==old,'Ancestor C/B/R03/R02 metadata changed')
    c._record(a,m,directory,{'kind':'D_FIXED_ENVIRONMENT_PREPARED','ready':ready,'requests':requests,'Native_inputs':summary,'guard_observation':after,'P0_not_learned_regulation':True,'old_metadata_literal_unchanged':True})
    return {'version':VERSION,'life_id':identity['life_id'],'before_tick':start,'after_tick':int(a.tick),'new_native_ticks':int(a.tick)-start,'ready':ready,'requests':requests,'Native_inputs':summary,'P0_guard':m['P0_guard'],'old_metadata_literal_unchanged':True,'old_R02_ordinal_preserved':12,'new_D_opportunities':12,'evaluation_horizon':6,'future_stock':6,'scope':'One legal fixed environment support; no reinjection, repair, reset or query-specific credit. Terminal installation failure is preserved.'}
def episode(a,directory):
    validate(a,{'modo':EPISODE});c=_core();old=_old_literals(a);m=_get(a);p,_=protocol(True);initial=int(a.tick);wait=p['schedule'][m['ordinal']]['wait_ticks']
    if wait:
        m['pending']={'phase':'D_DECLARED_EXTERNAL_WAIT','ordinal':m['ordinal'],'target_tick':initial+wait};m['uncertain']=True
        c._record(a,m,directory,{'kind':'D_DECLARED_EXTERNAL_WAIT_INTENT','before_tick':initial,'wait_ticks':wait,'not_selected_from_response':True})
        try:c.body.SafeAdapter(a).run_until(initial+wait)
        except BaseException:
            c._save(a,m);raise
        m['pending']=None;m['uncertain']=False
        c._record(a,m,directory,{'kind':'D_DECLARED_EXTERNAL_WAIT_COMPLETED','after_tick':int(a.tick),'wait_ticks':wait,'new_birth_or_repair':False})
    row=_bridge()._C().episode(a,directory)
    _require(_old_literals(a)==old,'Ancestor history changed')
    return {**row,'prepared_wait_ticks':wait,'before_prepared_wait':initial,'whole_new_native_ticks':int(a.tick)-initial,'D_environment_fixed_guard':list(GUARD),'D_feedback_arm':_get(a)['control']['arm'],'old_R02_ordinal_preserved':12,'timing_scope':'External fixed400-tick wait at indices3/8; actual q1/q2/refclocks decide effective window/phase. No invariant391/782phase claim.','scope':'New environmental contingency with inherited Native decisions and shared-bank second-stage return. No first-query credit, no learned guard construction, no initiative/sequence claim.'}
def state(a):
    _identity(a);present=KEY in dict(a.world.runtime.snapshot_metadata_entries)
    return {'version':VERSION,'present':present,'progress':_get(a)if present else None,'physical':_core()._physical(a),'new_native_ticks':0}
def dispatch(a,row,*,actuator='closed',directory=None):
    validate(a,row)
    if row['modo']==STATE:return state(a)
    _require(actuator=='closed'and directory is not None,'Closed actuator and owned diagnostic home required')
    return prepare(a,row,directory)if row['modo']==PREPARE else episode(a,directory)
def uncertain(a):
    return KEY in dict(a.world.runtime.snapshot_metadata_entries)and bool(_get(a).get('uncertain'))
def operational_dependencies(a,directory):
    if KEY not in dict(a.world.runtime.snapshot_metadata_entries):return {'version':VERSION,'present':False,'new_native_ticks':0}
    identity=_identity(a);c=_core();_,ph=protocol(True);m=_get(a)
    _require(m['protocol_sha256']==ph and len(m['rows'])==m['ordinal']<=12,'D actual progress/protocol mismatch')
    _require({k:_sha(v.encode('utf8'))for k,v in _old_literals(a).items()}==m['old_metadata_sha256'],'D must preserve old R02/C/B history literal')
    home=c._home(directory,identity['life_id']);file=home/'eventos.jsonl';chain='00'*32;count=0
    with file.open('rb')as lines:
        for line in lines:json.loads(line);chain=_sha(bytes.fromhex(chain)+line);count+=1
    _require(chain==m['log_chain_sha256']and count==m['log_count'],'D journal/snapshot differs')
    count_first=len(m['first_stage_rows']);_require(count_first==m['ordinal']or(count_first==m['ordinal']+1 and m.get('uncertain')and m.get('pending')),'First-stage compact references must match preserved progress')
    for ref in m['first_stage_rows']:
        item=ref['external_immediate_witness'];_require(Path(item['file']).name==item['file'],'Fixed witness basename');source=home/item['file'];_require(source.stat().st_size==item['bytes']and _sha(source.read_bytes())==item['sha256'],'D full immediate witness missing/different')
    for row in m['rows']:
        item=row.get('message_artifact')
        if item:
            _require(item['file']=='mensaje_%04d.bin'%row['ordinal'],'Fixed product ordinal');product=home/item['file'];_require(product.stat().st_size==64 and _sha(product.read_bytes())==item['sha256'],'Actual D64B product changed')
    return {'version':VERSION,'present':True,'ordinal':m['ordinal'],'remaining':12-m['ordinal'],'evaluation_remaining':max(0,6-m['ordinal']),'old_R02_ordinal_preserved':12,'pending':m['pending'],'uncertain':m['uncertain'],'new_native_ticks':0,'journal_sha256':_sha(file.read_bytes()),'P0_guard':m['P0_guard'],'shared_bank_query_credit_not_isolated':True}
def code_files():return list(dict.fromkeys([Path(__file__),PROTOCOL,SEAL,PARENT_SOURCE,*_bridge().code_files()]))
