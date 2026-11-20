"""Pure transaction tests. Real C2C protocol/Device/journal validators; FAKE
runtime/hardware boundary. This is explicitly NOT the pending Root world test.
"""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,types,sys
P=Path(__file__).resolve().parents[1];CAP=P/'codigo/PI08_A1_INSTALACION_R02/capacidades';OUT=P/'control/PRUEBAS_A1_PURAS_R02';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_TX_FAKE'
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def filehash(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 if OUT.exists():raise FileExistsError('Fake test evidence preserved')
 OUT.mkdir();owned=OUT/LIFE;owned.mkdir();m=load('PI08_A1_FAKE_TRANSACTION',CAP/'pi08_integracion_c2c_R01.py');body=load('PI08_REAL_C2C_FAKE_BOUNDARY',CAP/'pi04_coordinacion_central_C2C.py');body.PROTOCOL=CAP/'PROTOCOLO_PI05_C2C_30_R01.json';body._decode=json.loads
 physical={'N':67,'tick':123456,'RAW_sha256':'a'*64,'clocks_sha256':'b'*64}
 class Hardware:
  def protocol(self):return{},'c'*64
  def _identity(self,a,p,directory=None):return{'life_id':LIFE,'profile':'fisica_directa'}
  def _get(self,a):return{'ready':True,'pending':None,'uncertain':False}
 hardware=Hardware();body._hardware=lambda:hardware;body._physical=lambda a:copy.deepcopy(physical)
 class Runtime:
  dimension=67;receipts=()
  def __init__(self,entries):self.entries=entries;self.writes=0
  @property
  def snapshot_metadata_entries(self):return tuple(self.entries.items())
  def set_snapshot_metadata(self,key,value):self.entries[key]=value;self.writes+=1
 class Adapter:
  tick=123456
  def __init__(self,entries):self.world=types.SimpleNamespace(runtime=Runtime(entries))
 home=owned/body.FOLDER;home.mkdir();device=body.Device.prepare(home/'dispositivo',30,body.protocol()[0]['environment'])
 for resource in device.m['resources']:(device.home/'reservoir'/resource['name']).rename(device.home/'consumed'/resource['name'])
 device.m['ordinal']=30;device.save();line=b'{"kind":"FAKE_HISTORY_NOT_NATIVE"}\n';(home/'eventos.jsonl').write_bytes(line)
 c2={'version':body.VERSION,'life_id':'FAKE_PREPARATION_ONLY','arm':'real','ordinal':30,'rows':[{'ordinal':i,'FAKE':True}for i in range(30)],'protocol_sha256':body.protocol()[1],'admitted':True,'ready':True,'pending':None,'uncertain':False,'halted_reason':None,'log_count':1,'log_chain_sha256':hashlib.sha256(bytes(32)+line).hexdigest()}
 old=types.SimpleNamespace(KEY='DEE.Cognitive.PI05.C2C.explicit_environment30.R01');a=Adapter({body.KEY:json.dumps(c2),old.KEY:json.dumps({'ready':True,'pending':None,'uncertain':False})})
 # Only the explicit Fake package boundary; no official engine is imported.
 old._effective=lambda base:base;old.effective_component=lambda adapter,base,for_dependencies=False:base
 package=types.ModuleType('capacidades');package.pi05_c2c_ofertas_R01=old;sys.modules['capacidades']=package
 m._encode=lambda value:json.dumps(value,sort_keys=True,separators=(',',':'));m._decode=json.loads;m._base=lambda:(body,old,body)
 real_component32=m._component32
 def component32(directory):
  comp=real_component32(directory);comp._decode=json.loads;comp._hardware=lambda:hardware;comp._physical=lambda adapter:copy.deepcopy(physical);return comp
 m._component32=component32
 def fake_boundary_full_chain(adapter,directory,prepared,proposed):
  entries=dict(adapter.world.runtime.snapshot_metadata_entries);entries[body.KEY]=m._encode(proposed);projected=m._ReadOnlyAdapter(adapter,entries);comp=component32(directory);comp.protocol(material=True,evaluation=True);comp._identity(projected,directory,operation=comp.STATE);deps=comp.operational_dependencies(projected,directory)
  return{'FAKE_RUNTIME_AND_HARDWARE':True,'real_frozen_C2C_protocol_Device_journal_validated':True,'C2C':deps,'dispatcher_real_world_test_pending':True}
 m._full_chain_preflight=fake_boundary_full_chain
 checks={};before_entries=copy.deepcopy(a.world.runtime.entries);before_tree=m._copytree_manifest(device.home)
 try:m.prepare(a,owned,'34');checks['invalid34_rejected']=False
 except ValueError as exc:checks['invalid34_rejected']=str(exc)=='One bounded2..32-opportunity schedule required'
 checks['invalid34_no_stage_or_metadata_write']=not m._home(owned).exists()and a.world.runtime.entries==before_entries and a.world.runtime.writes==0
 prepared=m.prepare(a,owned);token=prepared['token'];checks['valid_prepare_no_life_or_old_device_write']=a.world.runtime.entries==before_entries and a.world.runtime.writes==0 and m._copytree_manifest(device.home)==before_tree
 files_before=sorted(str(p.relative_to(owned))for p in owned.rglob('*')if p.is_file());again=m.prepare(a,owned);checks['repeat_prepare_idempotent']=again['already_prepared']and again['token']==token and a.world.runtime.writes==0 and files_before==sorted(str(p.relative_to(owned))for p in owned.rglob('*')if p.is_file())
 try:m.commit(a,owned,token,interrupt_before=True);checks['declared_precommit_interrupt']=False
 except RuntimeError as exc:checks['declared_precommit_interrupt']=str(exc).startswith('PI08_DECLARED_PRECOMMIT_INTERRUPTION')
 checks['interrupt_preserves_source_and_no_life_write']=a.world.runtime.entries==before_entries and a.world.runtime.writes==0 and m._copytree_manifest(device.home)==before_tree
 result=m.commit(a,owned,token);checks['commit_valid32_no_counter_or_history_reset']=result['committed']and json.loads(a.world.runtime.entries[body.KEY])['rows']==c2['rows']and json.loads(a.world.runtime.entries[body.KEY])['ordinal']==30 and len(body.Device(m._device_home(owned)).m['resources'])==32 and m._copytree_manifest(device.home)==before_tree
 writes=a.world.runtime.writes;tree=m._copytree_manifest(m._home(owned));repeat=m.commit(a,owned,token);checks['repeat_commit_no_duplicate_files_or_metadata']=repeat['already_committed']and a.world.runtime.writes==writes and m._copytree_manifest(m._home(owned))==tree
 reopened=Adapter(copy.deepcopy(a.world.runtime.entries));deps=component32(owned).operational_dependencies(reopened,owned);checks['fake_reopen_actual_Device_and_journal_contracts']=deps['prepared_resources']==32 and deps['ordinal']==30 and not deps['uncertain']
 checks['no_DEE_or_app_module_imported']=not any(name=='dee_thinking'or name.startswith(('dee_thinking.','app.'))for name in sys.modules)
 if not all(checks.values()):raise AssertionError(checks)
 proof={'schema':'DEE.PI08.A1.pure_transaction_FAKE_runtime.v1','checks':checks,'FAKE_NOT_NATIVE':True,'actual_component_used':'Frozen C2C3177 protocol(material/evaluation), Device/file/hash/journal validator','mocked_boundary':'Runtime metadata/physical/hardware identity and external full-dispatcher boundary; actual owner round trip remains mandatory.','Native_executed':False,'Native_worlds_created':0,'code_files':{'A1':filehash(CAP/'pi08_integracion_c2c_R01.py'),'C2C':filehash(CAP/'pi04_coordinacion_central_C2C.py')},'pending_real_tests':['Root actual complete world: reject34 without scientific mutation','Root realprepare/declaredinterrupt/commit/repeatedrequest/reopen through existing queue','Root full dispatcher/R03/FI dependencies and unchanged Native landscape/agenda/receipts']}
 target=OUT/'RESULTADO_FAKE_SIN_NATIVE.json';target.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'proof':str(target),'sha256':filehash(target),'checks':checks,'Native_executed':False}))
if __name__=='__main__':main()
