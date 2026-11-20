"""PI11 product permission and administrative inherited-identity transport.

Pure import. Must install before PI10's inherited transport in a product
owner. No Native input, clock/RAW edit, bank/counter reset or selector write.
Diagnostic scientific R01 remains literal in acquisition/replay systems.
"""
from pathlib import Path
import copy,hashlib,json,re
VERSION='DEE.PI11.product_inherited_permission.R02'
SCHEMA='DEE.PI11.exact_operational_permission.R01'
CONTRACT='PI11_USO_OPERATIVO_R01.json'
SYSTEM='DEE.Cognitive.System.1.1.life.v1'
KEY='DEE.Cognitive.PI11.persistent_habitat.native_continuation.R01'
PI10KEY='DEE.Cognitive.PI10.adaptive_query.two_native_traces.R02'
FI8KEY='DEE.Cognitive.PI11.explicit_FI_eight_offer_lot.R01'
SERVICE='DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1'
C2CKEY='DEE.Cognitive.PI04.C2C.coordination.R01'
C2CSHA='0cf6bf8508e071a1c8cf1448023a096bc43336d66b8a1deb98f488b29b4205fd'
EP='eci01-pi11-episodio';STATE='eci01-pi11-estado';_INSTALLED=False
def need(ok,msg):
    if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def root():return Path(__file__).resolve().parents[1]
def entries(a):return dict(a.world.runtime.snapshot_metadata_entries)
def raw_identity(a):return json.loads(entries(a)[SYSTEM])
def selected():
    f=root()/'estado/ACTIVO.json';return read(f).get('life_id')if f.is_file()else None
def contract():
    p=read(root()/'contratos'/CONTRACT)
    need(p.get('schema')==SCHEMA and re.fullmatch('ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_PI11_[A-Z0-9_]{1,20}',str(p.get('life_id',''))),'Exact PI11 operational identity/schema')
    need(p.get('profile')=='fisica_directa'and p.get('N')==67 and p.get('status')in('PREPARED_DIAGNOSTIC','COMMITTED','DIAGNOSTIC_INTERFACE_ONLY'),'Exact PI11 permission scope')
    if p['status']=='DIAGNOSTIC_INTERFACE_ONLY':
        need(p.get('all_adoption_gates_met')is False and re.fullmatch('[a-f0-9]{64}',str(p.get('diagnostic_scientific_basis_sha256',''))),'Interface testing does not claim adoption gates')
    else:need(p.get('all_adoption_gates_met')is True,'Product preparation/commit requires all actual adoption gates')
    need(p.get('allowed_modes')==[EP,STATE]and p.get('PI10_material_disabled')is True and p.get('historical_material_disabled')is True,'PI11 EP/STATE; historical preparation/stock calendars stay closed')
    need(p.get('public_FI_backend')=='PI11_new_FI8_same_frozen_body'and p.get('public_FI_domain')==[0,20]and p.get('internal_FI_redirected')is False and p.get('public_arithmetic_policy')=='legacy_partial'and p.get('C2C_protocol_sha256')==C2CSHA and p.get('new_FI8_key')==FI8KEY and p.get('new_FI8_total')==8,'Explicit finite new public supply; frozen FI/C2C/arithmetic body')
    prior=p.get('previous_principal',{})
    need(prior.get('life_id')=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01'and prior.get('tick')==947395 and prior.get('snapshot_sha256')=='fd7372b7f2adc9040866fab8adfaca0d79e0bd18e997c0abc0651fe4fa3c23dc','Exact protected PI10 parent cut')
    need(p.get('PI11_protocol_sha256')==sha(root()/'capacidades/PROTOCOLO_PI11_R01.json'),'Exact evaluated habitat protocol')
    need(isinstance(p.get('source_ordinal'),int)and 1<=p['source_ordinal']<=24,'Actual finite acquired source history')
    required={'pi11_actor_R01.py','pi11_habitat_persistente_R01.py','pi11_dispatcher_R01.py','pi11_identidad_heredada_R02.py','pi11_lote_FI8_R01.py','PI11_FI8_SUMINISTRO_R01.json','PROTOCOLO_PI11_R01.json','PI11_EXPERIMENTO_R01.json','PI11_PLUGINS_R01.json','pi10_transporte_ancestral_R01.py','pi10_permiso_operativo_R02.py'}
    need(required<=set(p.get('frozen_files_sha256',{})),'Complete fixed product/scientific code binding required')
    for name,digest in p['frozen_files_sha256'].items():
        need(Path(name).name==name and sha(Path(__file__).with_name(name))==digest,'Frozen PI11 dependency changed: '+name)
    if p['status']=='COMMITTED':need(re.fullmatch('[a-f0-9]{64}',str(p.get('adoption_decision_sha256',''))),'Actual committed decision required')
    else:need(p.get('adoption_decision_sha256')is None,'Prepared profile cannot claim commitment')
    return p
def applies(a):
    f=root()/'contratos'/CONTRACT
    return f.is_file()and raw_identity(a).get('life_id')==read(f).get('life_id')
def diagnostic_marker(p):
    """Explicit isolated product-interface test, never an operational bypass."""
    system=root().resolve();marker=system/'contratos/PI11_INTERFAZ_DIAGNOSTICA_R01.json'
    if not marker.is_file():return False
    need(not(system/'estado/ACTIVO.json').exists()and system.name=='sistema'and system.parent.parent.name=='estados'and system.parent.parent.parent.name=='PROGRESION_INTEGRADA_11','Interface diagnostic only in explicit PI11 clone')
    m=read(marker)
    expected={'schema','life_id','system','contract_sha256','allow_material_interface_test','not_a_principal','initial_tick','maximum_new_Native_ticks','initial_material_calls','maximum_material_calls','allowed_material_modes','scientific_basis_sha256'}
    need(set(m)==expected and m['schema']=='DEE.PI11.explicit_product_interface_diagnostic.R01'and m['life_id']==p['life_id']and Path(m['system']).resolve()==system and m['contract_sha256']==sha(system/'contratos'/CONTRACT)and m['allow_material_interface_test']is True and m['not_a_principal']is True,'Exact separately authorized diagnostic target/contract')
    need(p['status']=='DIAGNOSTIC_INTERFACE_ONLY'and p['all_adoption_gates_met']is False and m['scientific_basis_sha256']==p['diagnostic_scientific_basis_sha256'],'Interface permission is not a prepared/adopted product')
    need(type(m['initial_tick'])is int and m['initial_tick']>=947395 and type(m['initial_material_calls'])is int and m['initial_material_calls']>=0 and m['maximum_new_Native_ticks']==4032 and m['maximum_material_calls']==2 and m['allowed_material_modes']==[EP,'eci01-balance'],'Only two fixed material interface checks within4032ticks')
    return True
def diagnostic_budget(a,p,mode):
    need(diagnostic_marker(p),'Explicit interface marker required');m=read(root()/'contratos/PI11_INTERFAZ_DIAGNOSTICA_R01.json')
    need(mode in m['allowed_material_modes'],'Only the fixed EP and inherited comparison interface are enabled')
    service=json.loads(entries(a)[SERVICE]);calls=service.get('material_calls')
    need(type(calls)is int and 0<=calls-m['initial_material_calls']<m['maximum_material_calls'],'Finite diagnostic call budget exhausted; do not reset marker')
    bound=2016 if mode==EP else 1300
    need(m['initial_tick']<=int(a.tick)and int(a.tick)+bound<=m['initial_tick']+m['maximum_new_Native_ticks'],'No diagnostic request beyond fixed prospective tick allowance')
def acquired(a,p=None):
    p=contract()if p is None else p;e=entries(a)
    old=json.loads(e[PI10KEY]);need(old.get('ready')and old.get('admitted')and old.get('ordinal')==14 and len(old.get('rows',[]))==14 and not old.get('pending')and not old.get('uncertain'),'PI10 fourteen-offer history and stock must remain literal')
    need(hashlib.sha256(e[PI10KEY].encode('utf8')).hexdigest()==p['PI10_history_sha256'],'Acquired PI10 history changed')
    m=json.loads(e[KEY]);need(m.get('ready')and m.get('ordinal')==len(m.get('rows',[]))and p['source_ordinal']<=m['ordinal']<=24 and not m.get('pending')and not m.get('uncertain')and m.get('protocol_sha256')==p['PI11_protocol_sha256'],'Exact closed acquired PI11 continuation, no reset')
    fi=json.loads(e[FI8KEY]);need(fi.get('version')=='DEE.PI11.explicit_new_FI8_supply.R01'and fi.get('ready')and fi['ordinal']==len(fi['rows'])and 0<=fi['ordinal']<=8 and not fi.get('pending')and not fi.get('uncertain')and fi.get('explicit_new_supply',{}).get('offers')==8,'Actual explicitly admitted finite FI supply')
    return m
def identity(a):
    from capacidades import pi10_transporte_ancestral_R01 as t
    p=contract();c=t.config();i=raw_identity(a)
    need(i.get('life_id')==c.get('life_id')==p['life_id']and i.get('profile')=='fisica_directa'and int(a.world.runtime.dimension)==67 and c.get('role')=='real','Exact real PI11 N67 continuation')
    e=entries(a)
    for key,digest in c['inherited_metadata_sha256'].items():need(hashlib.sha256(e[key].encode('utf8')).hexdigest()==digest,'Acquired ancestor metadata changed: '+key)
    current=selected()
    if current==p['life_id']:need(p['status']=='COMMITTED','Selected PI11 requires actual commitment')
    elif current==p['previous_principal']['life_id']:need(p['status']=='PREPARED_DIAGNOSTIC','Unselected moved world must remain prepared')
    else:need(diagnostic_marker(p),'No selected or explicitly diagnostic PI11 permission')
    # Identity is also used *inside* legal in-flight operations. A pending
    # journal is rejected at public admission/opening, not misread as a loss
    # of administrative identity halfway through recording that operation.
    return i
def profile(a):
    if not applies(a):return None
    identity(a);p=contract();acquired(a,p);return p
def validate_external(a,row,*,payload):
    if not applies(a):return
    identity(a)
    if payload.get('operacion')in('reanudar','pausar','guardar','detener'):
        need(row is None and set(payload)=={'operacion'},'Exact technical transport control');return
    p=profile(a);material_allowed=selected()==p['life_id']or diagnostic_marker(p)
    need(payload.get('operacion')=='sesion'and payload.get('retorno','omit')=='omit'and payload.get('actuador','closed')=='closed','Fixed public PI11 session/closed actuator')
    need(isinstance(row,dict),'One explicit public situation')
    mode=str(row.get('modo',''))
    if not material_allowed:
        from capacidades import pi10_transporte_ancestral_R01 as t
        need(row=={'modo':mode}and mode in t.STATES|{STATE,'eci01-pi10-estado'},'Prepared world permits only state and transport, no material action');return
    if selected()is None and mode not in(STATE,'eci01-pi10-estado'):
        diagnostic_budget(a,p,mode)
    if mode.startswith('eci01-pi11-'):need(row=={'modo':mode}and mode in(EP,STATE),'Selected PI11 cannot reinstall/reset, resupply or override action/wait')
    if mode.startswith('eci01-pi10-'):need(row=={'modo':'eci01-pi10-estado'},'PI10 stock is historical in PI11')
    if mode.startswith(('eci01-pi07-','eci01-pi08-','eci01-pi09-')):
        from capacidades import pi10_transporte_ancestral_R01 as t
        need(mode in t.STATES,'Historical material calendars remain closed')
    need(mode not in('eci01-pi05-c2c-ampliar','eci01-pi05-c2c-extension-estado'),'No C2C resupply/reset')
def propose_C2C_identity(metadata):
    p=contract();life=p['life_id'];prior=p['previous_principal']['life_id']
    need(metadata.get('life_id')in(prior,life)and not any(metadata.get(k)for k in('pending','uncertain','halted_reason'))and metadata.get('protocol_sha256')==C2CSHA and metadata.get('arm')=='real'and metadata.get('ready')and metadata.get('admitted')and metadata['ordinal']==len(metadata['rows'])<=32,'Exact closed inherited C2C; identity only')
    new=copy.deepcopy(metadata);old=new['life_id'];new['life_id']=life
    return new,{'metadata_old_life_id':old,'metadata_new_life_id':life,'changed_paths':[]if old==life else['/life_id'],'new_ticks':0,'not_learning':True}
def validate_public(a,row):
    need(applies(a)and isinstance(row,dict)and row.get('modo')=='eci01-balance','Exact inherited public comparison')
    p=profile(a);need(selected()==p['life_id']or diagnostic_marker(p),'Public comparison requires selected or explicit interface diagnostic')
    from capacidades import acceso_integrado_eci01 as public,pi11_lote_FI8_R01 as access
    public.validate(a,row);access.validate(a,{'modo':access.QUERY,'izquierda':row['izquierda'],'derecha':row['derecha']})
def execute_public(a,row,*,actuator='closed',directory=None):
    validate_public(a,row)
    from capacidades import pi11_lote_FI8_R01 as access
    before={k:entries(a)[k]for k in(*access.OLD_KEYS,PI10KEY)}
    value=access.dispatch(a,{'modo':access.QUERY,'izquierda':row['izquierda'],'derecha':row['derecha']},actuator=actuator,directory=directory)
    need(all(entries(a)[k]==v for k,v in before.items()),'Historical FI/PI10 progress changed; no double consumption')
    return {**value,'public_outer_request':dict(row),'PI11_public_permission':VERSION,'internal_FI_redirected':False,'new_supply_added_by_this_query':0,'explicit_new_supply_not_learning':True}
def install(a):
    global _INSTALLED
    if _INSTALLED or not applies(a):return
    from capacidades import pi10_transporte_ancestral_R01 as t,pi10_permiso_operativo_R02 as permission
    p=contract();t.identity=identity
    permission.LIFE=p['life_id'];permission.PARENT=p['previous_principal']['life_id'];permission.profile=profile;permission.propose_C2C_identity=propose_C2C_identity;permission.validate_public=validate_public;permission.execute_public=execute_public;permission.validate_external=validate_external
    # All other scientific body functions stay literal. Their globals receive
    # exact current administrative identity; no physical fields are altered.
    t.install(a);permission.install(a);identity(a);acquired(a,p);_INSTALLED=True
def code_files():return (Path(__file__),root()/'contratos'/CONTRACT)
