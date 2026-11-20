"""Pure exact canonical D/C/B/readonly/FI8 identity callback wiring."""
from pathlib import Path
import hashlib,importlib.util,json,sys,types
H=Path(__file__).resolve().parent;CAP=H/'RP_D_FAMILIA_R01_PREPARADA/capsule';OUT=H/'PRUEBA_ALIAS_DRF_CANONICOS_PI09_R01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,path):s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def main():
 if OUT.exists():raise FileExistsError('Prior test preserved')
 OUT.mkdir();denied=[]
 class NoNative:
  def find_spec(self,name,path=None,target=None):
   if name.startswith(('dee_thinking','dee_runtime','dee_native','_dee','numpy')):denied.append(name);raise AssertionError('No Native/DEE import in pure callback wiring '+name)
 sys.meta_path.insert(0,NoNative());package=types.ModuleType('capacidades');package.__path__=[str(CAP/'capacidades')];sys.modules['capacidades']=package
 family=load('capacidades.pi09_reproduccion_D_familia_R01',CAP/'capacidades/pi09_reproduccion_D_familia_R01.py');root=H/'PRUEBA_RP_D_FAMILIA_PI09_R01/FAKE_01/sistema';family.__file__=str(root/'capacidades/pi09_reproduccion_D_familia_R01.py');family.CONFIG=root/'capacidades/PI09_REPRODUCCION_D_FAMILIA_R01.json';family.SOURCE=CAP/'capacidades/pi09_entorno_persistente_D_R02.py';config=json.loads(family.CONFIG.read_text('utf-8-sig'));life=config['bound_life_id']
 family.install_transport();from capacidades import pi09_transporte_D_R02 as transport
 transport.SCOPE=root/'capacidades/PI09_TRANSPORTE_D_R02.json';transport.base().SCOPE=root/'capacidades/PI09_TRANSPORTE_HEREDADO_R02.json'
 adapter=types.SimpleNamespace(world=types.SimpleNamespace(runtime=types.SimpleNamespace(dimension=67,snapshot_metadata_entries=((family.SYSTEM,json.dumps({'life_id':life,'profile':'fisica_directa'})),))))
 checks=[]
 assert transport.current is family._identity and transport.base().current is family._identity;checks.append('canonical_D_transport_and_private_ancestral_transport_both_use_family_identity')
 assert transport.applies(adapter)and transport.current(adapter)['life_id']==life;checks.append('actual_bound_D_scope_and_current_identity_accept_DRF')
 scope=transport.base().config();assert scope['life_id']==life;checks.append('literal_ancestral_R02_config_accepts_DRF_and_retains_C884835_pins')
 readonly=load('capacidades.pure_readonly_DRF',CAP/'capacidades/pi09_antecedente_R02_readonly_D_R01.py');assert readonly.identity(adapter)['life_id']==life and readonly.private()._C().LIFE==life;readonly.validate(adapter,{'modo':'eci01-pi09-estado'});checks.append('actual_readonly_R02_alias_and_current_home_namespace_accept_DRF_without_Native')
 fi8=load('capacidades.pure_FI8_identity_DRF',CAP/'capacidades/pi09_FI8_D_alias_R01.py');assert fi8.identity(adapter)['life_id']==life;checks.append('actual_FI8_alias_delegates_to_same_canonical_DRF_identity')
 assert not denied;result={'schema':'DEE.PI09.DRF.canonical_identity_callback.pure_tests.R01','passed':len(checks),'checks':checks,'Native_executed':False,'DEE_imports':0,'fake_runtime_identity_only':True,'actual_literal_source_modules_used':True,'actual_material_replay_pending':True}
 file=OUT/'RESULTADO.json';file.write_text(json.dumps(result,indent=2)+'\n','utf8');print(json.dumps({'passed':len(checks),'proof':str(file),'sha256':sha(file),'Native_executed':False}))
if __name__=='__main__':main()
