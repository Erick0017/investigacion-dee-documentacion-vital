"""Pure role/permission regression. No Native imports or file writes."""
from pathlib import Path
import ast,hashlib,importlib.util,json,sys,types
H=Path(__file__).resolve().parent
def load(name,f):
    sp=importlib.util.spec_from_file_location(name,H/f);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def need(ok,msg):
    if not ok:raise AssertionError(msg)
def rejected(fn,*args,**kw):
    try:fn(*args,**kw)
    except ValueError:return
    raise AssertionError('Expected permission rejection')
def main():
    before=set(sys.modules);identity=load('PI11_control_identity_pure','pi11_identidad_diagnostica_R02.py');patch=load('PI11_control_patch_pure','aplicar_identidad_control_PI11_R02.py');cloner=load('PI11_control_cloner_pure','pi11_clonar_controles_R02.py');b=cloner.base()
    checked=[0];life='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_PI11_NONE01';a=object();actual_checked=identity.checked;identity.checked=lambda current:({'life_id':life},{'role':'none'})
    component=types.SimpleNamespace(protocol=lambda:({},identity.C2CSHA));identity.readonly_C2C(component,a);need(component.OPERATIONAL_LIFE_ID==life,'Administrative C2C consumer alias')
    rejected(identity.deny_public,a,{'modo':'eci01-balance'})
    transport=types.ModuleType('capacidades.pi10_transporte_ancestral_R01');transport.STATES={'eci01-pi09-estado'};package=types.ModuleType('capacidades');package.__path__=[];package.pi10_transporte_ancestral_R01=transport;saved={k:sys.modules.get(k)for k in('capacidades','capacidades.pi10_transporte_ancestral_R01')};sys.modules['capacidades']=package;sys.modules['capacidades.pi10_transporte_ancestral_R01']=transport
    try:
        session={'operacion':'sesion','retorno':'omit','actuador':'closed'}
        for mode in('eci01-pi11-preparar','eci01-pi11-episodio','eci01-pi11-estado','eci01-pi09-estado'):identity.validate_external(a,{'modo':mode},payload=session)
        rejected(identity.validate_external,a,{'modo':'eci01-balance'},payload=session);rejected(identity.validate_external,a,{'modo':'eci01-pi11-fi-lote-admitir'},payload=session)
        rejected(identity.validate_external,a,{'modo':'eci01-pi11-episodio','answer':1},payload=session)
        identity.validate_external(a,None,payload={'operacion':'detener'})
    finally:
        for k,v in saved.items():
            if v is None:sys.modules.pop(k,None)
            else:sys.modules[k]=v
    # Exercise actual installer order with a fake original permission consumer.
    # The consumer asks configure_C2C during bootstrap, exactly where R01 failed.
    identity.checked=actual_checked
    for role in('none','yoked','reproduction'):
        rolelife='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_PI11_'+role.upper()
        transport=types.ModuleType('capacidades.pi10_transporte_ancestral_R01');transport.config=lambda role=role,rolelife=rolelife:{'life_id':rolelife,'role':role};transport.identity=lambda current,rolelife=rolelife:{'life_id':rolelife};transport.STATES=set()
        perm=types.ModuleType('capacidades.pi10_permiso_operativo_R02');consumer=types.SimpleNamespace(protocol=lambda:({},identity.C2CSHA));perm.install=lambda current,perm=perm,consumer=consumer:perm.configure_C2C(consumer,current)
        package=types.ModuleType('capacidades');package.__path__=[];package.pi10_transporte_ancestral_R01=transport;package.pi10_permiso_operativo_R02=perm
        keys=('capacidades','capacidades.pi10_transporte_ancestral_R01','capacidades.pi10_permiso_operativo_R02');saved={k:sys.modules.get(k)for k in keys};sys.modules['capacidades']=package;sys.modules[keys[1]]=transport;sys.modules[keys[2]]=perm
        current=types.SimpleNamespace(world=types.SimpleNamespace(runtime=types.SimpleNamespace(dimension=67)));identity._INSTALLED=False
        try:
            identity.install(current)
            need(consumer.OPERATIONAL_LIFE_ID==rolelife and perm.public_allowed(current)is False and perm.diagnostic_real(current)is False,'Role-specific bootstrap without public retention')
            rejected(perm.validate_public,current,{'modo':'eci01-balance'})
        finally:
            for k,v in saved.items():
                if v is None:sys.modules.pop(k,None)
                else:sys.modules[k]=v
    original=(b.S/'app/mundo_genesis_apd05.py').read_text('utf-8-sig')
    # Apply exact parent PI11 hooks in RAM, then control-only import/guard.
    d={};source=H/'pi11_clonar_R01.py';m=load('PI11_control_hook_base',source.name)
    mem={'app/mundo_genesis_apd05.py':original,'app/cola_local.py':(b.S/'app/cola_local.py').read_text('utf-8-sig')}
    class Fake:
        def __init__(self,p=''):self.p=p
        def __truediv__(self,k):return Fake(self.p+'/'+k if self.p else k)
        def read_text(self,*args):return mem[self.p]
        def read_bytes(self):return mem[self.p].encode('utf8')
        def write_text(self,value,*args):mem[self.p]=value
    m.sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();m.patch_hooks(Fake());patched=patch.patch_owner(mem['app/mundo_genesis_apd05.py']);ast.parse(patched)
    need(patched.count('pi11_identidad_diagnostica_R02 as pi11_identity')==3,'Install and two admission guards')
    need(not any(n.startswith(('dee_thinking','dee_universe'))for n in set(sys.modules)-before),'No Native imported')
    print(json.dumps({'schema':'DEE.PI11.pure_control_identity_R02_regression.R01','passed':True,'Native_imported':False,'file_writes':0,'tests':['control C2C alias without REAL-only retention','actual installer order with NONE/YOKE/reproduction bootstrap consumer','public retention/resupply denied','only fixed PI11 experiment and readonly ancestor states','technical stop allowed','exact future clone hooks parse','R01 source pin retained']}))
if __name__=='__main__':main()
