"""Short executions of byte-preserved original CPC3 genealogy on installed4.5.

Only the auditor's JSON integer representation and compressed storage change.
No physical recipe, event, decoder or original source is patched.
"""
import argparse,hashlib,importlib.util,json,os,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCES=ROOT/'genealogia/fuentes'
def original(name,filename):
 spec=importlib.util.spec_from_file_location(name,SOURCES/filename)
 module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module
def exact(value,key=''):
 if isinstance(value,dict):return {k:exact(v,k) for k,v in value.items()}
 if isinstance(value,(list,tuple)):return [exact(v,key) for v in value]
 if isinstance(value,int) and not isinstance(value,bool) and (key.lower().startswith(('raw','clock')) or abs(value)>2**53-1):return str(value)
 return value
class Log:
 def __init__(self,path):self.path=path
 def append(self,item):
  row=exact(item);row['monotonic_ns']=str(time.monotonic_ns());row['wall_utc']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
  with self.path.open('a',encoding='utf-8') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
  return row
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out;out.mkdir(parents=True,exist_ok=False)
 manifest={'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'kind':'Historical source execution on4.5; not integrated into E1',
  'physical_changes':'NONE','instrument_changes':'RAW/clock exact JSON strings, bounded selected cases, gzip wrapper instead of deep native path',
  'sources':{f:hashlib.sha256((SOURCES/f).read_bytes()).hexdigest() for f in('6817b3d21cd551841d0a.py','0442685348239b6a6346.py','057ca2b25e4ca1045533.py')},
  'frozen_contrasts':{'order':['AB','BA','AA','none'],'mobile':['paired','unpaired','opposite','reserved dose'],
   'forecast':['paired open','paired closed','omitted','unpaired','memory equalized','reserved origin/dose','context changes after forecast']}}
 (out/'FROZEN.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
 lab=original('laboratorio','6817b3d21cd551841d0a.py');sessionmod=original('cp01_session','0442685348239b6a6346.py')
 pred=original('cp02_predictor','057ca2b25e4ca1045533.py')
 from dee_thinking.persistence import save_world_snapshot,load_world_snapshot
 cp01=[]
 for order in('AB','BA','AA','none'):
  w=lab.make_body();before=lab.body_panel(w)
  receipts=lab.body_experience(w,order) if order!='none' else[]
  if order=='none':w.advance(2) # Historical relational preparation starts at32, not0.
  result,child=lab.body_probe(w,in_fork=False)
  cp01.append({'case_id':'CP01_ORDER_'+order,'before':before,'receipts':receipts,'result':result,'final':lab.physical(w),
   'modality':'ORIGINAL_RELATIVE_BODY_AND_READER'})
  (out/'CP01.json').write_text(json.dumps(exact(cp01),ensure_ascii=False,indent=2),encoding='utf-8')
  save_world_snapshot(w,out/('CP01_ORDER_'+order+'.deetsnap.gz'))
 for label,teachers,paired,origin,query in [('paired',(7,11),True,(0,0,0),13),('unpaired',(7,11),False,(0,0,0),13),
    ('opposite',(11,7),True,(0,0,0),13),('reserve',(13,19),True,(4,7,3),17)]:
  w,rs=lab.learned_mobile(teachers,paired=paired,origin=origin)
  response,child=lab.mobile_query(w,query,in_fork=False)
  cp01.append({'case_id':'CP01_MOBILE_'+label,'receipts':rs,'response':response,'final':lab.physical(w)})
  (out/'CP01.json').write_text(json.dumps(exact(cp01),ensure_ascii=False,indent=2),encoding='utf-8')
 (out/'CP01.json').write_text(json.dumps(exact(cp01),ensure_ascii=False,indent=2),encoding='utf-8')
 s=sessionmod.Session.create(slots=4,feedback=False);s.experience(5,7,11);s.signal('s0',0);s.world.run_until(8)
 s.world.runtime.set_snapshot_metadata('cp01.session.v1',json.dumps(s.state,separators=(',',':')))
 save_world_snapshot(s.world,out/'CP01_PENDING.deetsnap.gz')
 loaded,_=load_world_snapshot(out/'CP01_PENDING.deetsnap.gz');restored=sessionmod.Session(loaded,json.loads(loaded.runtime.snapshot_metadata('cp01.session.v1')))
 s.advance_to(11);restored.advance_to(11)
 continuation={'before_query_pending':8,'read_tick':11,'physical_equal':lab.physical(s.world)==lab.physical(restored.world),
  'responses_original':s.observe(),'responses_restored':restored.observe(),'scope':'External MOD31 habitat preserved as external, not reclassified as native v27 action'}
 (out/'CP01_CONTINUATION.json').write_text(json.dumps(exact(continuation),ensure_ascii=False,indent=2),encoding='utf-8')
 log=Log(out/'PREDICCIONES.jsonl');cp02=[]
 for opened in(True,False):
  for mode in('paired','none','unpaired','equalized'):
   s=pred.PredictorSession(pred.build(),pred.PersistentTransportHabitat(opened));rs=s.experience_past_results('paired' if mode=='equalized' else mode)
   if mode=='equalized':s=pred.memory_equalized(s)
   ident='CP02_'+str(int(opened))+'_'+mode
   em=s.predict([60,100],log,ident);ev=[s.evaluate(t,log,ident) for t in(60,100)]
   cp02.append({'case_id':ident,'modality':'DIAGNOSTIC_FORK' if mode=='equalized' else'INDEPENDENT_PREPARATION',
    'receipt':rs,'emission':em,'evaluations':ev,'final':pred.physical(s.world)})
   (out/'CP02.json').write_text(json.dumps(exact(cp02),ensure_ascii=False,indent=2),encoding='utf-8')
 for opened,origin,payload in((True,(12,18,15),13),(False,(18,12,15),11)):
  s=pred.PredictorSession(pred.build(origin),pred.PersistentTransportHabitat(opened));s.experience_past_results('paired')
  ident='CP02_RESERVED_'+str(int(opened));em=s.predict([67,107],log,ident,payload);ev=[s.evaluate(t,log,ident) for t in(67,107)]
  cp02.append({'case_id':ident,'emission':em,'evaluations':ev,'final':pred.physical(s.world)})
 s=pred.PredictorSession(pred.build(),pred.PersistentTransportHabitat(True,80));s.experience_past_results('paired')
 em=s.predict([60,100],log,'CP02_CHANGED');ev=[s.evaluate(t,log,'CP02_CHANGED') for t in(60,100)]
 cp02.append({'case_id':'CP02_CHANGED','emission':em,'evaluations':ev,'interpretation':'A valid miss under changed regularity is retained, not silently excluded.'})
 (out/'CP02.json').write_text(json.dumps(exact(cp02),ensure_ascii=False,indent=2),encoding='utf-8')
 result={'CP01_rows':len(cp01),'CP02_rows':len(cp02),'CP01_pending_restore_equal':continuation['physical_equal'],
  'forecast_emissions_precede_target':all(r['emission']['emission_tick']<e['target_tick'] for r in cp02 for e in r['evaluations']),
  'scope':'Finite historical contracts and unchanged sources. New JSON types are instrumentation only. Not evidence of integration of forecast into E1.'}
 (out/'SUMMARY.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result))
if __name__=='__main__':main()
