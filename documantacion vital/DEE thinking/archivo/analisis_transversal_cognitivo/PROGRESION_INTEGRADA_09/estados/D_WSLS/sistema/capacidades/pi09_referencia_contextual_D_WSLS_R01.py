"""Optional diagnostic material reference; no Native/DEE import on load.

D_R02 stays literal. Only its private second episode's existing `forced`
assignment receives the prospective WSLS action. Native choice stays recorded.
The context is the actual released bit, not cue/goal/action-evaluation metadata.
"""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json
VERSION='DEE.PI09.D.material_context_WSLS.R01';KEY='DEE.Cognitive.PI09.D.material_context_WSLS.R01';FOLDER='PI09_D_WSLS_R01'
PREPARE='eci01-pi09-d-wsls-preparar';EPISODE='eci01-pi09-d-wsls-episodio';STATE='eci01-pi09-d-wsls-estado';MODES={PREPARE,EPISODE,STATE}
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_D_WSLS_01'
SOURCE=Path(__file__).with_name('pi09_entorno_persistente_D_R02.py');SOURCE_SHA='c9938b50fbdf68d94954eaf341abae025faa307e4c8d24d23862c7b78bf085f8'
PROTOCOL=Path(__file__).with_name('PROTOCOLO_PI09_D_WSLS_R01.json');SEAL=Path(__file__).with_name('SELLO_PI09_D_WSLS_R01.json');SECOND_SHA='500db3042c14bd23bb839de5e2dbf8bb715040dec2c1d740db270ad8026b5f9f'
_PRIVATE=None
def need(ok,why):
    if not ok:raise ValueError(why)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def initial_policy():return {'motor_by_bit':{'0':-1,'1':1},'completed_updates':0,'pending_action':None,'host_reference_not_Native_policy':True}
def reference_action(m):
    bit=m['sample_register']['released_bit'];need(type(bit)is int and bit in(0,1),'Only actual registered material bit0/1, no cue/goal')
    r=m['material_WSLS_reference'];need(r['pending_action']is None,'Incomplete prior reference action must be preserved, not replayed')
    motor=r['motor_by_bit'][str(bit)];need(motor in(-1,1),'Fixed binary reference motor')
    r['pending_action']={'ordinal':m['ordinal'],'actual_released_bit':bit,'actual_reference_motor':motor}
    return 'pulso'if motor==1 else'nada'
def update_policy(m,actual_failed,ordinal):
    need(type(actual_failed)is bool,'Actual physical FI/message failure only');r=m['material_WSLS_reference'];action=r['pending_action'];need(action is not None and action['ordinal']==ordinal and r['completed_updates']==ordinal,'One terminal reference update per ordinal')
    bit=str(action['actual_released_bit']);used=action['actual_reference_motor'];need(r['motor_by_bit'][bit]==used,'Reference table was edited between action and consequence')
    r['motor_by_bit'][bit]=-used if actual_failed else used;r['completed_updates']+=1;r['pending_action']=None
    return {'ordinal':ordinal,**action,'actual_failed':actual_failed,'next_motor_for_same_bit':r['motor_by_bit'][bit],'host_reference_not_acquired_Native_WSLS':True}
def transformed_second(text):
    node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)and n.name=='episode');body=ast.get_source_segment(text,node)
    before="forced=row.get('forzar')if row['modo']==CALIBRATE else None;ablation="
    after="forced=_material_reference_action(m);ablation="
    need(body.count(before)==1,'Exact existing forced-action assignment required; no additional scientific adapter')
    return body.replace(before,after)
def protocol(material=False):
    p=read(PROTOCOL);need(p['schema']=='DEE.PI09.D.material_context_WSLS.protocol.R01'and p['life_id']==LIFE and p['initial_second_motor_by_bit']=={'0':-1,'1':1}and p['maximum_opportunities']==6 and p['maximum_ticks']==13063,'Exact prospective reference rule')
    d=_private();base,bh=d._base_protocol(False)
    if material:
        seal=read(SEAL);dseal=read(Path(__file__).with_name('SELLO_PI09_D_R02.json'))
        need(seal['schema']=='DEE.PI09.D.material_context_WSLS.source_seal.R01'and seal['life_id']==LIFE and seal['protocol_sha256']==sha(PROTOCOL)and seal['same_D_source_prefix']==dseal['source_prefix']and seal['D_source_seal_sha256']==sha(Path(__file__).with_name('SELLO_PI09_D_R02.json')),'Exact same pre-D source; independent reference seal')
        need(seal['Root_optional_execution_authorized']is True and seal['minimum_prospective_world_slot']==16 and seal['closure_ticks_reserved']==13000,'Root actual prospective budget authorization required; prepared code alone is insufficient')
        for name,digest in seal['files_sha256'].items():need(Path(name).name==name and sha(Path(__file__).with_name(name))==digest,'Sealed reference dependency changed: '+name)
        need({Path(__file__).name,PROTOCOL.name,SOURCE.name}<=set(seal['files_sha256']),'Reference and literal D sources pinned')
    return base,bh
def identity(a):
    c=_private()._core();_,_,_,decode,_=c._native();v=decode(dict(a.world.runtime.snapshot_metadata_entries)[c.body.SYSTEM_KEY])
    need(v.get('life_id')==LIFE and v.get('profile')=='fisica_directa'and int(a.world.runtime.dimension)==67,'Exact single diagnostic material-reference identity')
    need(not(Path(__file__).resolve().parents[1]/'estado/ACTIVO.json').exists(),'Material WSLS reference can never be selected')
    _private()._bridge()._C().LIFE=LIFE;return v
def _private():
    global _PRIVATE
    if _PRIVATE is not None:return _PRIVATE
    need(sha(SOURCE)==SOURCE_SHA,'D_R02 must stay literal');s=importlib.util.spec_from_file_location('capacidades._D_WSLS_private_literal_D2',SOURCE);d=importlib.util.module_from_spec(s);s.loader.exec_module(d);_PRIVATE=d
    d.VERSION,d.KEY,d.FOLDER=VERSION,KEY,FOLDER;d.PREPARE,d.EPISODE,d.STATE,d.MODES=PREPARE,EPISODE,STATE,MODES;d.LIVES={'real':LIFE};d.REPRO_IDS=[]
    d._base_protocol=d.protocol;d.protocol=protocol;d._identity=identity
    original=d._core;configured=set()
    def core():
        c=original()
        if id(c)not in configured:
            file=d._bridge()._C().SECOND_SOURCE;need(sha(file)==SECOND_SHA,'Literal second episode source changed')
            c._material_reference_action=reference_action;exec(compile(transformed_second(file.read_text('utf-8-sig')),str(file)+':material_reference_forced_only','exec'),c.__dict__);configured.add(id(c))
        return c
    d._core=core
    return d
def literal(row):need(isinstance(row,dict)and set(row)=={'modo'}and row['modo']in MODES,'Fixed reference mode only; no force/action/answer/target argument')
def mapped(row):return {'modo':row['modo'],'brazo':'real'}if row['modo']==PREPARE else row
def validate_literal(row):literal(row)
def validate(a,row):
    literal(row);d=_private();d.validate(a,mapped(row))
    if row['modo']==EPISODE:
        m=d._get(a);need(m['ordinal']<6 and m['material_WSLS_reference']['pending_action']is None and m['material_WSLS_reference']['completed_updates']==m['ordinal'],'Finite coherent six-use reference; no missing update/reset')
def dispatch(a,row,*,actuator='closed',directory=None):
    validate(a,row);d=_private()
    if row['modo']==STATE:return d.state(a)
    need(actuator=='closed'and directory is not None,'Explicit owned diagnostic path')
    if row['modo']==PREPARE:
        result=d.prepare(a,mapped(row),directory);m=d._get(a);m['material_WSLS_reference']=initial_policy();d._core()._record(a,m,directory,{'kind':'MATERIAL_WSLS_REFERENCE_RULE_ADMITTED','rule':copy.deepcopy(m['material_WSLS_reference']),'no_new_Native_input_or_tick':True})
        return {**result,'material_WSLS_reference':copy.deepcopy(m['material_WSLS_reference']),'maximum_reference_opportunities':6,'never_selected':True}
    result=d.episode(a,directory);m=d._get(a);update=update_policy(m,result['actual_failed'],result['ordinal']);d._core()._record(a,m,directory,{'kind':'MATERIAL_WSLS_REFERENCE_UPDATED_FROM_ACTUAL_CONSEQUENCE','reference_update':update})
    return {**result,'material_WSLS_reference_update':update,'reference_actual_second_action_is_host_WSLS_not_Native_policy':True}
def operational_dependencies(a,directory):
    d=_private();entries=dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in entries:return {'version':VERSION,'present':False,'new_native_ticks':0}
    identity(a);value=d.operational_dependencies(a,directory);m=d._get(a);need(m['ordinal']<=6 and m['material_WSLS_reference']['completed_updates']==m['ordinal'],'Reference progress/update integrity')
    return {**value,'maximum_reference_opportunities':6,'never_selected':True}
def uncertain(a):
    d=_private();entries=dict(a.world.runtime.snapshot_metadata_entries)
    return KEY in entries and(d.uncertain(a)or d._get(a).get('material_WSLS_reference',{}).get('pending_action')is not None)
def code_files():return list(dict.fromkeys([Path(__file__),PROTOCOL,SEAL,SOURCE,*_private().code_files()]))
