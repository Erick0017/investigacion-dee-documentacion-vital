"""Pure transport contracts/Fake callbacks. No Native, Owner, DB or world read."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,sys,types
H=Path(__file__).resolve().parent;P=H.parent;checks=[]
def load(name,file):
    s=importlib.util.spec_from_file_location(name,file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def check(name,v):
    assert v,name
    checks.append(name)
def reject(name,fn):
    try:fn()
    except(ValueError,KeyError):checks.append(name);return
    raise AssertionError(name)
transport=load('_D_transport_contract_test',H/'pi09_transporte_D_R02.py');alias=load('_D_R02_readonly_contract_test',H/'pi09_antecedente_R02_readonly_D_R01.py');fi=load('_D_FI8_contract_test',H/'pi09_FI8_D_alias_R01.py');dispatcher=load('_D_dispatch_contract_test',H/'pi09_dispatcher_D_R02.py')
package=types.ModuleType('capacidades');package.__path__=[];sys.modules['capacidades']=package;sys.modules['capacidades.pi09_transporte_D_R02']=transport
fixture=H/'PRUEBA_OVERLAY_D_R02_FAKE_ONLY';fixture.mkdir(exist_ok=False);fakecap=fixture/'sistema/capacidades';fakecap.mkdir(parents=True);(fakecap/'pi09_consulta_selectiva_R02.py').write_bytes((H/'pi09_consulta_selectiva_R02.py').read_bytes())
transport.__file__=str(fakecap/'pi09_transporte_D_R02.py');dispatcher.__file__=str(fakecap/'pi09_dispatcher_D_R02.py')
oldmeta={'C':'literal_C_history','B':'literal_B_history'};oldscope={'life_id':None,'inherited_metadata_sha256':{k:hashlib.sha256(v.encode()).hexdigest()for k,v in oldmeta.items()}};scope={'schema':'DEE.PI09.D.exact_readonly_transport_scope.R02','role':'real','life_id':None,'parent_R02_ordinal':12}
transport.base=lambda:types.SimpleNamespace(config=lambda:oldscope);transport.read=lambda _:scope
def make(role,slug):
    life='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_'+slug+'_01';scope.update(role=role,life_id=life);oldscope['life_id']=life
    entries=[*oldmeta.items(),(transport.SYSTEM,json.dumps({'life_id':life,'profile':'fisica_directa'}))]
    return types.SimpleNamespace(world=types.SimpleNamespace(runtime=types.SimpleNamespace(snapshot_metadata_entries=entries,dimension=67)))
# Fake FI8 still calls its identity callback for every state/dependency path.
calls=[]
fakefi=types.SimpleNamespace(validate_literal=lambda row:None,validate=lambda a,row:calls.append(('validate',transport.current(a)['life_id'],row['modo'])),dispatch=lambda a,row,**kw:{'life_id':transport.current(a)['life_id'],'new_native_ticks':0},operational_dependencies=lambda a,directory:{'life_id':transport.current(a)['life_id'],'new_native_ticks':0,'present':True},uncertain=lambda a:False,code_files=lambda:())
fi._PRIVATE=fakefi
fakeancestor=types.SimpleNamespace(validate=lambda a,row:transport.current(a),state=lambda a:{'life_id':transport.current(a)['life_id'],'new_native_ticks':0},operational_dependencies=lambda a,directory:{'life_id':transport.current(a)['life_id'],'present':True,'new_native_ticks':0},uncertain=lambda a:False,code_files=lambda:())
alias._PRIVATE=fakeancestor
for role,slug in [('real','DISCOVERY'),('none','STAGE3_NONE'),('yoked','STAGE3_YOKE'),('reproduction','DREPRO'),('reference','D_WSLS')]:
    a=make(role,slug);expected=scope['life_id'];check(role+' exact N67 identity',transport.current(a)['life_id']==expected)
    check(role+' FI8 readonly operational dependencies current identity',fi.operational_dependencies(a,None)['life_id']==expected)
    check(role+' ancestral R02 readonly dependencies current identity',alias.operational_dependencies(a,None)['life_id']==expected)
    check(role+' readonly aliases expose files contract without DEE',Path(alias.__file__)in alias.code_files()and Path(fi.__file__)in fi.code_files())
    fi.validate(a,{'modo':fi.STATE});alias.validate(a,{'modo':alias.STATE})
    if role!='real':
        reject(role+' refuses external FI8 admission',lambda a=a:fi.validate(a,{'modo':fi.ADMIT}));reject(role+' refuses external FI8 query',lambda a=a:fi.validate(a,{'modo':fi.QUERY,'izquierda':14,'derecha':3}))
reject('Historical R02 EP always unavailable',lambda:alias.validate_literal({'modo':'eci01-pi09-episodio'}));reject('Historical R02 PREPARE always unavailable',lambda:alias.validate_literal({'modo':'eci01-pi09-preparar','brazo':'native_real'}))
a=make('real','DISCOVERY');a.world.runtime.dimension=66;reject('Dimension cannot relax identity',lambda:transport.current(a));a.world.runtime.dimension=67
a.world.runtime.snapshot_metadata_entries[0]=('C','changed');reject('C/B historical leaf change rejected',lambda:transport.current(a));a=make('real','DISCOVERY')
# Exercise the pre-promotion external guard without any real world or callback.
active=fakecap.parent/'estado/ACTIVO.json';active.parent.mkdir();active.write_text(json.dumps({'life_id':'OLD_SELECTED_NATIVE'}),'utf8')
identity={'life_id':scope['life_id']};dispatcher.allowed=lambda _:identity
testplugin=types.SimpleNamespace(MODES={'eci01-pi09-d-episodio','eci01-pi09-d-estado'},__file__='pi09_entorno_persistente_D_R02.py',validate=lambda a,row:True)
dispatcher.modules=lambda:[testplugin]
reject('Prepared-load dispatcher forbids material D episode',lambda:dispatcher.validate(a,{'modo':'eci01-pi09-d-episodio'}));check('Prepared-load dispatcher allows D STATE only',dispatcher.validate(a,{'modo':'eci01-pi09-d-estado'})is True)
reject('Old R02 episode not registered',lambda:dispatcher._for({'modo':'eci01-pi09-episodio'}))
# Prove Owner/queue adaptation is only import-source names in their AST.
source=P/'estados/DISCOVERY/sistema'
class Normalize(ast.NodeTransformer):
    def visit_ImportFrom(self,node):
        if node.module:node.module=node.module.replace('pi09_dispatcher_D_R02','pi09_dispatcher_R02').replace('pi09_transporte_D_R02','pi09_transporte_heredado_R02')
        for alias_ in node.names:alias_.name=alias_.name.replace('pi09_dispatcher_D_R02','pi09_dispatcher_R02').replace('pi09_transporte_D_R02','pi09_transporte_heredado_R02')
        return node
for name in('mundo_genesis_apd05.py','cola_local.py'):
    text=(source/'app'/name).read_text('utf-8-sig');changed=text.replace('pi09_dispatcher_R02','pi09_dispatcher_D_R02')
    if name.startswith('mundo'):changed=changed.replace('pi09_transporte_heredado_R02','pi09_transporte_D_R02')
    check(name+' only import names changed; all scientific/owner body AST literal',ast.dump(ast.parse(text),include_attributes=False)==ast.dump(Normalize().visit(ast.parse(changed)),include_attributes=False))
check('No DEE imported',not any(n=='dee_thinking'or n.startswith('dee_thinking.')for n in sys.modules))
names=['pi09_transporte_D_R02.py','pi09_antecedente_R02_readonly_D_R01.py','pi09_FI8_D_alias_R01.py','pi09_dispatcher_D_R02.py','instalar_overlay_D_PI09_R02.py']
for name in names:ast.parse((H/name).read_text('utf8'))
proof={'schema':'DEE.PI09.D.code_overlay.fake_contract_and_AST_tests.R02','passed':True,'count':len(checks),'checks':checks,'fixture_is_FAKE_NOT_AN_ACTUAL_WORLD':True,'Native_executed':False,'DEE_imported':False,'Owner_or_SQLite_or_actual_world_read':False,'target_code_or_seal_written':False,'source_sha256':{n:hashlib.sha256((H/n).read_bytes()).hexdigest()for n in names}}
out=P/'control/PRUEBAS_OVERLAY_D_PI09_R02.json'
with out.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'passed':True,'count':len(checks),'proof':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}))
