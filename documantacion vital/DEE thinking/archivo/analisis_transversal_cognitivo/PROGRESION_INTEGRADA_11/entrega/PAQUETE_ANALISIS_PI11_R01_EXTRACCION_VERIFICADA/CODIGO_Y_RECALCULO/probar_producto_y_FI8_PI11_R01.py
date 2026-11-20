"""Pure product/FI8 checks. In-memory histories and namespace mocks only."""
from pathlib import Path
import ast,hashlib,importlib.util,json,sys,types
H=Path(__file__).resolve().parent
def load(name,file):
    sp=importlib.util.spec_from_file_location(name,H/file);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def need(ok,msg):
    if not ok:raise AssertionError(msg)
def rejected(fn,*args,**kw):
    try:fn(*args,**kw)
    except ValueError:return
    raise AssertionError('Expected rejection before any effect')
def main():
    before=set(sys.modules);lot=load('PI11_pure_new_FI8','pi11_lote_FI8_R01.py');permission=load('PI11_pure_product_permission','pi11_identidad_heredada_R02.py');adopt=load('PI11_pure_adopter','pi11_adoptar_R01.py');public=load('PI11_pure_public','pi11_gestor_publico_R01.py')
    need(not any(n.startswith(('dee_thinking','dee_universe'))for n in set(sys.modules)-before),'Pure imports')
    old={lot.OLD_KEYS[0]:json.dumps({'ordinal':6,'rows':[{}]*6,'pending':None,'uncertain':False}),lot.OLD_KEYS[1]:json.dumps({'ordinal':7,'rows':[{}]*7,'pending':None,'uncertain':False}),lot.OLD_KEYS[2]:json.dumps({'ready':True,'pending':None,'uncertain':False})};literal=dict(old)
    planned=lot.plan_values(old,old[lot.OLD_KEYS[2]],1000000,'0'*64)
    need(old==literal and planned['ordinal']==0 and planned['rows']==[]and planned['explicit_new_supply']['offers']==8 and planned['explicit_new_supply']['old_ordinals']=={lot.OLD_KEYS[0]:6,lot.OLD_KEYS[1]:7},'New external quota; old histories preserved')
    for mode in(lot.ADMIT,lot.STATE):lot.validate_literal({'modo':mode})
    lot.validate_literal({'modo':lot.QUERY,'izquierda':0,'derecha':20})
    for row in({'modo':lot.ADMIT,'offers':9},{'modo':lot.QUERY,'izquierda':1,'derecha':2,'sensor_ablation':True},{'modo':lot.QUERY,'izquierda':True,'derecha':2},{'modo':lot.QUERY,'izquierda':21,'derecha':2}):rejected(lot.validate_literal,row)
    life='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_PI11_TEST';prior='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01'
    p={'life_id':life,'status':'PREPARED_DIAGNOSTIC','previous_principal':{'life_id':prior},'source_ordinal':16,'PI11_protocol_sha256':'a'*64}
    oldpi10=json.dumps({'ready':True,'admitted':True,'ordinal':14,'rows':[{}]*14,'pending':None,'uncertain':False})
    p['PI10_history_sha256']=hashlib.sha256(oldpi10.encode()).hexdigest()
    e={permission.SYSTEM:json.dumps({'life_id':life,'profile':'fisica_directa'}),permission.PI10KEY:oldpi10,permission.KEY:json.dumps({'ready':True,'ordinal':16,'rows':[{}]*16,'pending':None,'uncertain':False,'protocol_sha256':'a'*64}),permission.FI8KEY:json.dumps({'version':lot.VERSION,'ready':True,'ordinal':3,'rows':[{}]*3,'pending':None,'uncertain':False,'explicit_new_supply':{'offers':8}})}
    runtime=types.SimpleNamespace(dimension=67,snapshot_metadata_entries=e.items());a=types.SimpleNamespace(world=types.SimpleNamespace(runtime=runtime))
    transport=types.ModuleType('capacidades.pi10_transporte_ancestral_R01');transport.config=lambda:{'life_id':life,'role':'real','inherited_metadata_sha256':{}};transport.STATES={'eci01-pi09-estado'}
    package=types.ModuleType('capacidades');package.__path__=[];package.pi10_transporte_ancestral_R01=transport;saved={k:sys.modules.get(k)for k in('capacidades','capacidades.pi10_transporte_ancestral_R01')};sys.modules['capacidades']=package;sys.modules['capacidades.pi10_transporte_ancestral_R01']=transport
    permission.contract=lambda:p;permission.selected=lambda:prior;permission.diagnostic_marker=lambda p:False;permission.applies=lambda a:True
    try:
        permission.identity(a);permission.acquired(a,p)
        payload={'operacion':'sesion','retorno':'omit','actuador':'closed'}
        permission.validate_external(a,{'modo':permission.STATE},payload=payload)
        rejected(permission.validate_external,a,{'modo':permission.EP},payload=payload)
        p['status']='COMMITTED';permission.selected=lambda:life
        permission.validate_external(a,{'modo':permission.EP},payload=payload)
        rejected(permission.validate_external,a,{'modo':permission.EP,'answer':1},payload=payload)
        rejected(permission.validate_external,a,{'modo':lot.ADMIT},payload=payload)
        rejected(permission.validate_external,a,{'modo':'eci01-pi10-episodio'},payload=payload)
        in_flight=json.loads(e[permission.KEY]);in_flight.update(pending={'phase':'LEGAL_JOURNAL_INTENT'},uncertain=True);e[permission.KEY]=json.dumps(in_flight);runtime.snapshot_metadata_entries=e.items()
        permission.identity(a);rejected(permission.profile,a)
        permission.validate_external(a,None,payload={'operacion':'detener'})
        in_flight.update(pending=None,uncertain=False);e[permission.KEY]=json.dumps(in_flight);e[permission.SERVICE]=json.dumps({'material_calls':50});runtime.snapshot_metadata_entries=e.items();a.tick=1000000
        p.update(status='DIAGNOSTIC_INTERFACE_ONLY',all_adoption_gates_met=False);permission.selected=lambda:None;permission.diagnostic_marker=lambda p:True
        marker={'initial_tick':1000000,'maximum_new_Native_ticks':4032,'initial_material_calls':50,'maximum_material_calls':2,'allowed_material_modes':[permission.EP,'eci01-balance']};permission.read=lambda path:marker
        permission.validate_external(a,{'modo':permission.EP},payload=payload)
        e[permission.SERVICE]=json.dumps({'material_calls':52});runtime.snapshot_metadata_entries=e.items();rejected(permission.validate_external,a,{'modo':permission.EP},payload=payload)
        e[permission.SERVICE]=json.dumps({'material_calls':50});runtime.snapshot_metadata_entries=e.items();a.tick=1003000;rejected(permission.validate_external,a,{'modo':permission.EP},payload=payload)
        permission.validate_external(a,None,payload={'operacion':'detener'})
    finally:
        for k,v in saved.items():
            if v is None:sys.modules.pop(k,None)
            else:sys.modules[k]=v
    for f in H.glob('*.py'):ast.parse(f.read_text('utf-8-sig'))
    need(not any(n.startswith(('dee_thinking','dee_universe'))for n in set(sys.modules)-before),'No Native import')
    print(json.dumps({'schema':'DEE.PI11.pure_product_FI8_tests.R01','passed':True,'Native_imported':False,'Native_ticks':0,'file_writes':0,'tests':['new quota8 preserves old6/8 and7/8','four literal override/domain rejections','prepared EP refused/state allowed','committed EP valid','answer/resupply/old calendar refused','legal pending journal retains identity but cannot admit new material','technical stop remains available','interface-only permission without adoption claims','interface call/tick budgets reject exhausted tests','pure imports and AST']}))
if __name__=='__main__':main()
