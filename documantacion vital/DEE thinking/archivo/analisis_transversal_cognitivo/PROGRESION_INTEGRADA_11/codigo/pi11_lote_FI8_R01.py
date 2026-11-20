"""Explicit new finite FI8 supply on the exact inherited physical apparatus.

No engine is imported on module load. Admission adds a new administrative
KEY/journal with eight external opportunities, zero Native ticks/inputs and
unchanged old counters/banks/clocks. Queries run the literal PI07 access in
an isolated namespace. This is P0 supply/transport, never new learning.
"""
from pathlib import Path
import hashlib,importlib.util,json,os,re
VERSION='DEE.PI11.explicit_new_FI8_supply.R01'
KEY='DEE.Cognitive.PI11.explicit_FI_eight_offer_lot.R01';FOLDER='PI11_FI_LOTE8_R01'
ADMIT='eci01-pi11-fi-lote-admitir';QUERY='eci01-pi11-fi-lote-consultar';STATE='eci01-pi11-fi-lote-estado';MODES={ADMIT,QUERY,STATE}
SCOPE=Path(__file__).with_name('PI11_FI8_SUMINISTRO_R01.json')
OLD_KEYS=('DEE.Cognitive.PI09.explicit_FI_eight_offer_lot.R01','DEE.Cognitive.PI07.regulated_FI_access.R01','DEE.Cognitive.PI07.regulation.environment.R03')
SOURCE=Path(__file__).with_name('pi07_acceso_FI_regulado_R01.py');SOURCE_SHA='cefe1174debca3650fffeba22f1f1c2d03420211993734e319b9e47684c5db46'
REG_SOURCE=Path(__file__).with_name('pi07_regulacion_R03.py');REG_SHA='40648fd81c5b1f278ee9c18d0d464c5a4b5e9fd808054afe6ff072a10fda0ac5'
_PRIVATE=None
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(data):return hashlib.sha256(data).hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def entries(a):return dict(a.world.runtime.snapshot_metadata_entries)
def scope():
    c=read(SCOPE)
    need(c.get('schema')=='DEE.PI11.explicit_FI8_supply_scope.R01'and c.get('offers')==8 and c.get('Native_admission_ticks')==0 and c.get('Native_admission_inputs')==0,'Exact finite explicit zero-Native supply')
    need(re.fullmatch('ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_PI11_[A-Z0-9_]{1,20}',str(c.get('life_id',''))),'Explicit PI11 identity')
    need(set(c.get('old_metadata_sha256',{}))==set(OLD_KEYS)and type(c.get('admit_not_before_tick'))is int and c['admit_not_before_tick']>=947395,'Exact preserved antecedents and reached cut')
    need(c.get('same_frozen_body_sha256')==SOURCE_SHA and c.get('physical_banks_reset')is False and c.get('not_learning')is True,'No physical/content replacement')
    return c
def identity(a):
    from capacidades import pi10_transporte_ancestral_R01 as transport
    i=transport.identity(a);c=scope();need(i['life_id']==c['life_id']and int(a.world.runtime.dimension)==67,'Exact existing PI11 N67 descendant');return i
def component():
    global _PRIVATE
    if _PRIVATE is None:
        need(sha(SOURCE.read_bytes())==SOURCE_SHA and sha(REG_SOURCE.read_bytes())==REG_SHA,'Frozen physical access/regulation source changed')
        sp=importlib.util.spec_from_file_location('capacidades._PI11_FI8_literal_access',SOURCE);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
        rp=importlib.util.spec_from_file_location('capacidades._PI11_FI8_literal_R03_identity',REG_SOURCE);reg=importlib.util.module_from_spec(rp);rp.loader.exec_module(reg);reg._identity=identity;m.regulation=reg
        m.VERSION,m.KEY,m.FOLDER=VERSION,KEY,FOLDER;m.START,m.QUERY,m.STATE=ADMIT,QUERY,STATE;m.NEW_MODES={ADMIT,QUERY,STATE};m.MODES={*reg.MODES,*m.NEW_MODES};_PRIVATE=m
    return _PRIVATE
def old_literals(a):
    e=entries(a);c=scope();result={}
    for key in OLD_KEYS:
        need(key in e and sha(e[key].encode('utf8'))==c['old_metadata_sha256'][key],'Inherited FI/R03 history changed: '+key)
        m=json.loads(e[key]);need(not m.get('pending')and not m.get('uncertain'),'Antecedent is incomplete')
        if key!=OLD_KEYS[2]:need(type(m.get('ordinal'))is int and 0<=m['ordinal']<=8 and m['ordinal']==len(m.get('rows',[])),'Closed finite old FI history')
        result[key]=e[key]
    return result
def validate_literal(row):
    need(isinstance(row,dict)and row.get('modo')in MODES,'Exact PI11 FI8 mode')
    if row['modo']in(ADMIT,STATE):need(set(row)=={'modo'},'Admission/state accepts no counter, response, reader or capacity')
    else:need(set(row)=={'modo','izquierda','derecha'}and all(type(row[k])is int and 0<=row[k]<=20 for k in('izquierda','derecha')),'Two public operands0..20 only')
def validate(a,row):
    validate_literal(row);identity(a)
    if row['modo']==STATE:return
    m=component();m.protocol(True);old_literals(a)
    if row['modo']==ADMIT:
        need(not m.regulation._selected(a),'New supply only in explicit diagnostic, never silently on ACTIVO')
        need(int(a.tick)>=scope()['admit_not_before_tick'],'Supply cannot precede reached authorized cut')
        need(KEY not in entries(a),'Existing supply/progress preserved; never reset or refill')
    else:
        need(KEY in entries(a),'Explicit new supply must be admitted first');m.validate(a,row)
def plan_values(old,regulation_literal,tick,protocol_hash):
    need(set(old)==set(OLD_KEYS)and type(tick)is int and tick>=947395,'Actual complete old literals/cut')
    for key in OLD_KEYS:
        v=json.loads(old[key]);need(not v.get('pending')and not v.get('uncertain'),'No uncertain ancestor')
    return {'version':VERSION,'protocol_sha256':protocol_hash,'ready':True,'ordinal':0,'rows':[],'pending':None,'uncertain':False,'log_count':0,'log_chain_sha256':'00'*32,'R03_metadata_literal_sha256':sha(regulation_literal.encode('utf8')),'explicit_new_supply':{'offers':8,'old_metadata_sha256':{k:sha(v.encode('utf8'))for k,v in old.items()},'old_ordinals':{k:json.loads(old[k])['ordinal']for k in OLD_KEYS[:2]},'admitted_at_tick':tick,'Native_inputs':0,'Native_ticks':0,'physical_banks_reset':False,'not_energy':True,'not_learning':True}}
def state(a):
    identity(a);present=KEY in entries(a);p=component()._get(a)if present else None
    return {'version':VERSION,'present':present,'progress':p,'new_native_ticks':0,'new_lot_total':8,'new_lot_remaining':None if p is None else 8-p['ordinal'],'old_lots_literal_unchanged':True,'P0_external_supply_not_learning':True}
def admit(a,directory):
    validate(a,{'modo':ADMIT});m=component();before_entries=entries(a);old=old_literals(a);before=m.body._physical(a);home=m._home(directory,a)
    need(not home.exists()and home.parent.is_dir(),'Fresh exact journal namespace and existing owned home required')
    for node in(home,*home.parents):need(not node.exists()or not(node.is_symlink()or getattr(node.lstat(),'st_file_attributes',0)&1024),'No linked new FI lot')
    _,ph=m.protocol(True);progress=plan_values(old,before_entries[m.regulation.KEY],int(a.tick),ph)
    event={'index':0,'tick':int(a.tick),'kind':'EXPLICIT_NEW_PI11_FI8_SUPPLY_ZERO_NATIVE','old_metadata_sha256':progress['explicit_new_supply']['old_metadata_sha256'],'new_offers':8,'old_ordinals':progress['explicit_new_supply']['old_ordinals'],'same_physical_access':True,'not_learning':True}
    line=(json.dumps(m.body._safe(event),ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode('utf8');progress.update(log_count=1,log_chain_sha256=sha(bytes.fromhex('00'*32)+line));encoded=m.body._encoded(progress)
    home.mkdir()
    with(home/'eventos.jsonl').open('xb')as f:f.write(line);f.flush();os.fsync(f.fileno())
    a.world.runtime.set_snapshot_metadata(KEY,encoded)
    need(m.body._physical(a)==before and all(entries(a).get(k)==v for k,v in before_entries.items())and set(entries(a))==set(before_entries)|{KEY},'Zero-Native supply changed physical/ancestral state')
    return {**state(a),'admitted':True,'new_offers_added_now':8,'physical_unchanged':True,'all_old_metadata_literal_unchanged':True,'requests':[]}
def dispatch(a,row,*,actuator='closed',directory=None):
    validate(a,row)
    if row['modo']==STATE:return state(a)
    need(actuator=='closed'and directory is not None,'Exact owned home and closed actuator')
    if row['modo']==ADMIT:return admit(a,directory)
    before=old_literals(a);value=component().query(a,row,directory);need(old_literals(a)==before,'Old FI/R03 quota/history changed')
    return {**value,'explicit_new_FI_lot':KEY,'old_FI_literals_unchanged':True,'P0_supply_not_learning':True}
def operational_dependencies(a,directory):
    if KEY not in entries(a):return {'version':VERSION,'present':False,'new_native_ticks':0}
    identity(a);old_literals(a);v=component().operational_dependencies(a,directory);m=component()._get(a)
    need(m['explicit_new_supply']['old_metadata_sha256']==scope()['old_metadata_sha256'],'Supply antecedent binding changed')
    return {**v,'new_lot_total':8,'old_lots_not_reset':True}
def uncertain(a):return KEY in entries(a)and bool(component()._get(a).get('uncertain'))
def code_files():return tuple(dict.fromkeys([Path(__file__),SCOPE,*component().code_files()]))
