"""Pure transaction mocks: no DEE import or Native execution."""
from pathlib import Path
import copy,hashlib,importlib.util,json,types
P=Path(__file__).resolve().parents[1]
SRC=P/'codigo/PI05_INTEGRACION_R01_DRAFT/capacidades/pi05_c2c_ofertas_R01.py'
OUT=P/'control/EXTENSION30_PI05_PRUEBAS_PURAS_R01.json'
def need(v,s):
 if not v:raise AssertionError(s)
def load():
 s=importlib.util.spec_from_file_location('pi05_ext_pure',SRC);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(b):return hashlib.sha256(b).hexdigest()
def run(case,fail=False):
 m=load();protocol,_=m._protocol();life='ECI02_PI03_REPRO_PI04_PI05_MOCK_'+case
 root=P/'control/EXTENSION30_MOCKS_R01'/life
 need(not root.exists(),'Refuse existing pure mock directory');root.mkdir(parents=True)
 home=root/'device';home.mkdir();(home/'reservoir').mkdir()
 resources=[]
 for i in range(26):
  b=hashlib.sha256(('old'+str(i)).encode()).digest()*2;n='%04d.resource'%i;(home/'reservoir'/n).write_bytes(b);resources.append({'name':n,'bytes':64,'sha256':sha(b)})
 progress={'arm':'real','ordinal':22,'rows':[{'ordinal':i,'actual':i%2}for i in range(22)],'ready':True,'pending':None,'uncertain':False,'halted_reason':None,'protocol_sha256':protocol['original_protocol_sha256'],'log_count':1,'log_chain_sha256':'00'*32}
 device_state={'ordinal':22,'resources':resources,'products':[{'name':'old.product','sha256':'old'}],'rejections':[{'name':'old.rejection'}],'pending':None,'feedback_pending':None,'uncertain':False}
 original_progress=copy.deepcopy(progress);original_device=copy.deepcopy(device_state);metadata={};physical={'N':67,'tick':818074,'RAW_sha256':'a'*64,'clocks_sha256':'b'*64}
 runtime=types.SimpleNamespace(snapshot_metadata_entries=[],dimension=67,receipts=[])
 a=types.SimpleNamespace(tick=818074,world=types.SimpleNamespace(runtime=runtime))
 class Device:
  def __init__(self):self.m=device_state;self.home=home;self.fail=fail
  def save(self):
   if self.fail:raise OSError('PURE simulated failed device write')
   (home/'ESTADO_DISPOSITIVO.json').write_text(json.dumps(self.m,sort_keys=True),encoding='utf8')
 device=Device()
 base=types.SimpleNamespace(KEY='mock.base',__file__='mock_not_imported')
 base._hardware=lambda:types.SimpleNamespace(_identity=lambda a,p:{'life_id':life},protocol=lambda:({},'hash'))
 base._identity=lambda a,directory,operation:(None,None,{'life_id':life})
 base.STATE='mock.state';base._get=lambda a:progress;base._save=lambda a,v:None
 base._device=lambda directory:device;base._physical=lambda a:copy.deepcopy(physical)
 base.operational_dependencies=lambda a,directory:{'verified':True}
 def record(a,v,directory,event):
  with(root/'old_journal.jsonl').open('a',encoding='utf8')as f:f.write(json.dumps(event)+'\n')
  v['log_count']+=1
 base._record=record
 m._base=lambda:base;m._effective=lambda base=None:types.SimpleNamespace(operational_dependencies=lambda a,directory:need(len(device.m['resources'])==30,'effective30resource count'))
 m._entries=lambda a:dict(metadata)
 def put(a,v):metadata[m.KEY]=json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
 m._put=put
 need(m.effective_component(a,base)is base,'No-key forwarding must remain literal old26')
 try:
  result=m.dispatch(a,{'modo':m.EXTEND},directory=root)
 except OSError:
  need(fail,'Unexpected write failure');result={'failure_preserved':True}
 if fail:
  ext=json.loads(metadata[m.KEY]);need(ext['uncertain']and not ext['ready']and ext['pending']['phase']=='failed_extension_preserved','Failed transaction must remain fenced')
  need(len(list((home/'reservoir').glob('*.resource')))==30,'Created resources must remain as adverse evidence; no deletion')
 else:
  need(result['new_native_ticks']==0 and device.m['ordinal']==22 and len(device.m['resources'])==30,'Explicit0tick4supply without counter reset')
  need(device.m['resources'][:26]==original_device['resources']and device.m['products']==original_device['products']and device.m['rejections']==original_device['rejections'],'Prior resources/products/rejections unchanged')
  need(progress['rows']==original_progress['rows']and progress['protocol_sha256']==protocol['effective_protocol_sha256'],'Past rows unchanged/new protocol attributed honestly')
  need(progress['protocol_history'][-1]['previous_protocol_sha256']==original_progress['protocol_sha256'],'Old protocol provenance retained')
  dep=m.operational_dependencies(a,root);need(dep['ready']and dep['journal']['count']==2,'Committed journal chain/count verified')
  need(m.dispatch(a,{'modo':m.STATE},directory=root)['new_native_ticks']==0,'State mode is0tick')
  for r in device.m['resources']:
   b=(home/'reservoir'/r['name']).read_bytes();need(len(b)==r['bytes']==64 and sha(b)==r['sha256'],'Actual resource bytes/hash')
 try:m.dispatch(a,{'modo':m.EXTEND},directory=root)
 except ValueError:pass
 else:raise AssertionError('Repeated extension must be refused, not reset')
 need(physical=={'N':67,'tick':818074,'RAW_sha256':'a'*64,'clocks_sha256':'b'*64},'No fake physical changes')
 return {'case':case,'simulated_failure':fail,'prior_rows_unchanged':progress['rows']==original_progress['rows'],'prior_26_resource_references_unchanged':device.m['resources'][:26]==original_device['resources'],'new_resource_files_retained':len(list((home/'reservoir').glob('*.resource')))-26,'repeat_refused':True,'journal_checked':not fail,'uncertain':m.uncertain(a),'result':result}
if __name__=='__main__':
 need(not OUT.exists(),'No overwrite of prior proof');cases=[run('COMMIT'),run('FAIL',True)]
 proof={'schema':'DEE.PI05.explicit_environment30.pure_transaction_checks.v1','Native_ticks':0,'DEE_imports':0,'all_worlds_and_receipts_are_mocks':True,'actual_extension_source_sha256':sha(SRC.read_bytes()),'protocol_dependencies_verified_by_hash':True,'cases':cases}
 OUT.write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({'proof':str(OUT),'sha256':sha(OUT.read_bytes()),'Native_ticks':0,'cases':len(cases)}))
