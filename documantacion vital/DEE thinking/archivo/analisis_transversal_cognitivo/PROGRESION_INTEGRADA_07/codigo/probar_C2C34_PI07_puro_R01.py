"""Fake-only external supply transactions, no Native world or code apply."""
from pathlib import Path
from types import SimpleNamespace
import copy,hashlib,importlib.util,json,sys
P=Path(__file__).resolve().parents[1];H=P/'codigo';SRC=H/'FUENTES_C2C34_PI07_R01/capacidades/pi07_c2c_ofertas_R01.py';OUT=P/'control/C2C34_FAKE_R01';OUT.mkdir(exist_ok=False)
def sha(b):return hashlib.sha256(b).hexdigest()
def need(v,s):
 if not v:raise AssertionError(s)
def load():
 s=importlib.util.spec_from_file_location('C2C34_FAKE',SRC);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def run(case,fail=False):
 m=load();p,ph=m._protocol();root=OUT/case/m.LIFE;root.mkdir(parents=True);home=root/'device';home.mkdir();(home/'reservoir').mkdir()
 resources=[]
 for i in range(30):
  data=hashlib.sha256(('old'+str(i)).encode()).digest()*2;name='%04d.resource'%i;(home/'reservoir'/name).write_bytes(data);resources.append({'name':name,'bytes':64,'sha256':sha(data)})
 progress={'arm':'real','ordinal':30,'rows':[{'ordinal':i,'actual':i%2}for i in range(30)],'ready':True,'pending':None,'uncertain':False,'halted_reason':None,'protocol_sha256':p['original_protocol_sha256'],'log_count':0,'log_chain_sha256':'00'*32}
 state={'ordinal':30,'resources':resources,'products':[{'prior_product':True}],'rejections':[{'prior_rejection':True}],'pending':None,'feedback_pending':None,'uncertain':False};oldprogress=copy.deepcopy(progress);oldstate=copy.deepcopy(state)
 previous_literal=json.dumps({'version':'OLD30_LITERAL','ready':True,'pending':None,'uncertain':False,'history':[26,30]},sort_keys=True);metadata={m.PREVIOUS_KEY:previous_literal};physical={'N':67,'tick':123456,'RAW_sha256':'a'*64,'clocks_sha256':'b'*64}
 a=SimpleNamespace(tick=123456,world=SimpleNamespace(runtime=SimpleNamespace(dimension=67,receipts=[])))
 class Device:
  def __init__(self):self.m=state;self.home=home
  def save(self):
   if fail:raise OSError('FAKE controlled write failure')
   (home/'ESTADO_DISPOSITIVO.json').write_text(json.dumps(self.m),encoding='utf8')
 device=Device();base=SimpleNamespace(STATE='mock.state',_selected_life_id=lambda:None,_hardware=lambda:SimpleNamespace(_identity=lambda a,p:{'life_id':m.LIFE},protocol=lambda:({},'fake')),_identity=lambda a,d,operation:(None,None,{'life_id':m.LIFE}),_get=lambda a:progress,_save=lambda a,v:None,_device=lambda d:device,_physical=lambda a:copy.deepcopy(physical),operational_dependencies=lambda a,d:{'verified':True})
 def record(a,v,d,event):
  with(root/'inherited_C2C_journal.jsonl').open('a',encoding='utf8')as f:f.write(json.dumps(event)+'\n')
  v['log_count']+=1
 base._record=record;m._base=lambda:base;m._effective=lambda base=None:SimpleNamespace(operational_dependencies=lambda a,d:need(len(device.m['resources'])==34,'Exact34effective resources'))
 m._entries=lambda a:dict(metadata);m._put=lambda a,v:metadata.__setitem__(m.KEY,json.dumps(v,sort_keys=True))
 try:result=m.dispatch(a,{'modo':m.EXTEND},directory=root)
 except OSError:
  need(fail,'Unexpected failure');result={'failed_preserved':True}
 need(metadata[m.PREVIOUS_KEY]==previous_literal,'Historical30KEY literal unchanged')
 need(progress['rows']==oldprogress['rows']and device.m['products']==oldstate['products']and device.m['rejections']==oldstate['rejections']and device.m['resources'][:30]==oldstate['resources']and device.m['ordinal']==30,'No old counters/history/product/resource reset')
 need(len(list((home/'reservoir').glob('*.resource')))==34,'All4external actual64Bresources retained')
 if not fail:
  need(result['new_native_ticks']==0 and result['requests']==[]and result['resources_after']==34,'Zero Native supply')
  need(progress['protocol_sha256']==p['effective_protocol_sha256']and progress['protocol_history'][-1]['previous_protocol_sha256']==p['original_protocol_sha256'],'Honest newprotocol/history')
  need(m.operational_dependencies(a,root)['journal']['count']==2,'Journal hash/count verified')
 else:need(m.uncertain(a)and not json.loads(metadata[m.KEY])['ready'],'Failure fenced and preserved')
 try:m.dispatch(a,{'modo':m.EXTEND},directory=root)
 except ValueError:pass
 else:raise AssertionError('Refill/reset allowed')
 return{'case':case,'simulated_failure':fail,'old30_KEY_literal_unchanged':True,'old_rows_products_rejections_and30resourceprefix_unchanged':True,'four_resources_actual_files_preserved':True,'repeat_refused':True,'result':result}
cases=[run('COMMIT'),run('FAILED_DEVICE_SAVE',True)];m=load();p,ph=m._protocol()
need(not any(n.startswith(('dee_thinking','app.'))for n in sys.modules),'No DEE/app imported')
out=P/'control/C2C34_PI07_PRUEBAS_PURAS_R01.json'
with out.open('x',encoding='utf8')as f:json.dump({'schema':'DEE.PI07.external34.fake_transactions.v1','module_sha256':sha(SRC.read_bytes()),'extension_manifest_sha256':ph,'effective_protocol_sha256':p['effective_protocol_sha256'],'cases':cases,'Native_executed':False,'product_or_S7_modified':False,'all_worlds_receipts_and_devices_are_Fake':True,'scope':'Pure protocol/hash validation and Fake resource/metadata transaction only. Not real supply, operational use, old function retention or new learning.'},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'proof':str(out),'sha256':sha(out.read_bytes()),'cases':len(cases),'Native_executed':False}))
