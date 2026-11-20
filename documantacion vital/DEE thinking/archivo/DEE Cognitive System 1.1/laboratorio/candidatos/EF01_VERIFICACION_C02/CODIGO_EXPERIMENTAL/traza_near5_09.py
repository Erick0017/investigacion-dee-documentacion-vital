"""First learned near5 carrier: passive path witness versus normal query dose."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical,observe,moore27
from app.process_control import protect_current
from dee_thinking.consolidated import exact_receipt
from capacidades import espanol_funcional_01 as e,ensenanza_lexica_03 as f
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
s=Store(a.system);parent='ES01_LONG7_D_no_material_queries';life='ES01_NEAR_TRACE9_'+a.case;s.fork(parent,life,kind='DIAGNOSTIC_COPY')
data={'case':a.case,'life':life,'parent':s.record(parent),'frames':[],'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope_before':'Track the actually acquired[1,1,1]11 carrier after the same later phase8 lesson. Prediction is not itself genealogy; all pre/post neighborhoods accompany the first departure and samples.'}
def trial(x):
 data['teaching']=f.teach(x,frame='lexical05',parameter=5,word='cerca',phase_shift=8);entry=e.prepare(x)['relational_words_v2']['lexical05'];bank=next(b for b in entry['banks']if b['id']=='d5');start=x.tick;hub=bank['hub'];data['acquisition_boundary']=physical(x.world,occupation=True);x.save(a.out/('T'+str(x.tick)+'_ADQUIRIDO.deetsnap.gz'));requests=[]
 if a.case=='available_queries':
  t=x.tick
  for phase in entry['lexical_v3']['learned_phases']:
   target=e.tick_at_or_after(t,phase=phase,lead=3)
   for b in entry['banks']:
    r=x.world.probe(b['query'],7,target-3);requests.append({'port':b['query'],'payload':7,'tick':target-3,'id':int(r.id)})
   t=target
 first=None
 for dt in range(1,68):
  site=e.move(hub,(1,1,1),dt);pre=moore27(x.world,site);x.run_until(start+dt);record=observe(x.world,site);post=moore27(x.world,site)
  if not e.valid(record,(1,1,1))and first is None:
   first={'dt':dt,'tick':x.tick,'site':site,'pre':pre,'post':post,'record':record};x.save(a.out/('T'+str(x.tick)+'_PRIMER_CAMBIO.deetsnap.gz'))
  if dt%8==0 or dt in(1,2,3,66,67)or first and abs(first['dt']-dt)<=2:data['frames'].append({'dt':dt,'tick':x.tick,'site':site,'pre':pre,'post':post,'record':record})
 data['first_path_departure']=first;data['before_new_probe_at_hub']=observe(x.world,hub);data['requests']=[{**r,'receipt':exact_receipt(x.world.runtime.receipt(r['id']))}for r in requests]
 data['after_selective_new_phase_query']=f.query(x,frame='lexical05',phase=21);data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'first_departure':None if first is None else{'tick':first['tick'],'dt':first['dt'],'record':first['record']},'before_new_probe':data['before_new_probe_at_hub'],'after_new_phase_query':data['after_selective_new_phase_query']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'EF01_NEW_NEAR5_PHYSICAL_PATH_FIRST_FAILURE_TRACE',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
