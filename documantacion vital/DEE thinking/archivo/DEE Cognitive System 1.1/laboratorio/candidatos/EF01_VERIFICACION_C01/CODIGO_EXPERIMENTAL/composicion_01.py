"""Native coincidence and consequence of two acquired relation carriers.

This fixed composer is instrumentally prepared; it is not learned grammar.
The full combination is never supplied as a teaching packet or host answer.
"""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical,observe,moore27
from app.process_control import protect_current
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_receipt
from capacidades import espanol_funcional_01 as e
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
plans={'full':(False,False,False,3,'AB',3),'cut_contact':(True,False,False,3,'AB',3),'sham_contact':(False,True,False,3,'AB',3),'offroute_B':(False,False,True,3,'AB',3),'interval5_reserve':(False,False,False,5,'AB',3),'BA3_reserve':(False,False,False,3,'BA',3),'load5_reserve':(False,False,False,3,'AB',5)}
cut,sham,off,interval,order,load=plans[a.case];s=Store(a.system);parent='ES01_MAIN_03';life='ES01_COMPOSE1_'+a.case;s.fork(parent,life,kind='DIAGNOSTIC_COPY')
data={'case':a.case,'life':life,'parent':s.record(parent),'frames':[],'requests':[],'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'criteria_before':{'join_state':1,'join_semantic':1,'join_direction':[-1,1,1],'action_state':1,'action_semantic':1,'action_direction':[0,1,1],'scope':'Fixed native coincidence of contact and AB interval3 form; not generalized grammar, learned route or conscious inference.'}}
def trial(x):
 w=x.world;e.temporal_prepare(x,frame='composeTime',origin=(5,32,28));data['teaching']=e.temporal_experience(x,frame='composeTime',order=order,interval=interval,a_load=load,b_load=load,offroute=off)
 tg=e.prepare(x)['temporal_frames']['composeTime'];t=e.tick_at_or_after(x.tick,phase=tg['acquired_at']%67,lead=3);cq=t-7;J=[12,58,54];effect=[6,64,60]
 source=e.prepare(x)['contact_frames']['contactoA'];data['geometry']={'source_frame':source,'temporal_frame':tg,'temporal_read_tick':t,'contact_phase_tick':cq,'join':J,'join_tick':t+13,'effect':effect,'effect_tick':t+19}
 def port(role,site,v,semantic=1):
  c=d.ChannelSpec();c.name='EF01.COMPOSE1.'+role;c.injection_site=d.Coordinate(*site);c.direction=d.Direction(*v);c.state=1;c.semantic=semantic;c.allow_experience=True;c.allow_probe=True;q=d.InterfaceSpec();q.name=c.name;q.channel=c;w.declare_interface(q);return c.name
 def send(name,payload,tick,probe=False):
  r=(w.probe if probe else w.submit)(name,payload,tick);data['requests'].append({'port':name,'payload':payload,'tick':tick,'id':int(r.id)})
 for key,b in source['banks'].items():
  send(b['query'],5,cq-3,True)
  cutsite=e.move(b['hub'],(-b['axis'],1,b['z']),3)
  if sham:cutsite=e.move(cutsite,(0,0,1),9)
  if cut or sham:send(port(key+'.cut',cutsite,(0,0,0),4),0,cq+1)
 send(port('consequence',e.move(effect,(1,0,0),-3),(1,0,0)),7,t+16)
 data['component_temporal_query']=e.temporal_query(x,frame='composeTime')
 for tick,label,site in((t+12,'pre_join',J),(t+13,'join',J),(t+18,'pre_consequence',effect),(t+19,'consequence',effect)):
  x.run_until(tick);data['frames'].append({'tick':x.tick,'label':label,'record':observe(w,site),'moore':moore27(w,site),'physical':physical(w,occupation=True)})
 data['requests']=[{**r,'receipt':exact_receipt(w.runtime.receipt(r['id']))}for r in data['requests']]
 data['comparison_retention']=e.query_words(x);data['old_temporal_retention']=e.temporal_query(x,frame='secuenciaA');data['post']=physical(w,occupation=True)
 return {'tick':x.tick,'join':data['frames'][1]['record'],'consequence':data['frames'][3]['record'],'comparison':data['comparison_retention']['FORMAS_ACCESIBLES']}
data['commit']=s.mutate(life,'EF01_NATIVE_CONTACT_TEMPORAL_COMPOSITION',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
