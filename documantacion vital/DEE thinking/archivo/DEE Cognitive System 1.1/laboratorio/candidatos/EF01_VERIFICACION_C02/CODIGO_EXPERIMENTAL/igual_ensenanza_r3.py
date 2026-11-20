"""Third equality method: record the native alternate-route consequence.

The failed late cue to occupied comparison center is retained in r1.
This r2 records both candidate physical outputs equally after the event.
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
value,signal,delay,update,lead={'equal_lead3':(86,True,0,False,3),'less_lead3':(56,True,0,False,3),'more_lead3':(110,True,0,False,3),'equal_lead1':(86,True,0,False,1),'less_lead1':(56,True,0,False,1),'more_lead1':(110,True,0,False,1),'equal_no_word_cue':(86,False,0,False,3),'unpaired_equal':(86,True,1,False,3),'ref104_equal_reserve':(99,True,0,True,3)}[a.case]
s=Store(a.system);parent='ES01_MAIN_03';life='ES01_EQUAL_R3_'+a.case;s.fork(parent,life,kind='CANDIDATE')
data={'case':a.case,'life':life,'parent':s.record(parent),'frames':[],'requests':[],'queries':[],'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'criteria_before':{'igual':[1,-1,1],'diferente':[1,0,1],'state':1,'semantic':1,'scope':'Native alternate-route consequence of this current magnitude comparison, not arbitrary identity or a general logical negation.'}}
def trial(x):
 w=x.world;c=x.quantity.geometry['center'];T=e.tick_at_or_after(x.tick,phase=3,lead=8)
 if update:
  # Real declared addition to the acquired reference, never an overwritten target.
  rT=T;x.quantity.input('quantity.reference.cue',0,rT-3);x.quantity.input('quantity.reference.resource',13,rT-3);x.run_until(rT);T+=67
 slot=e.move(c,(0,0,1));banks={'igual':{'hub':e.move(slot,(0,-1,1),3),'signature':[1,-1,1]},'diferente':{'hub':e.move(slot,(0,0,1),3),'signature':[1,0,1]}}
 def port(name,hub):
  ch=d.ChannelSpec();ch.name='EF01.EQUAL.R3.'+name;ch.injection_site=d.Coordinate(*e.move(hub,(1,0,0),-3));ch.direction=d.Direction(1,0,0);ch.state=1;ch.semantic=1;ch.allow_experience=True;ch.allow_probe=True;p=d.InterfaceSpec();p.name=ch.name;p.channel=ch;w.declare_interface(p);return ch.name
 def send(name,payload,t,probe=False):
  r=(w.probe if probe else w.submit)(name,payload,t);data['requests'].append({'port':name,'payload':payload,'tick':t,'id':int(r.id)})
 x.quantity.present_object(value,round_index=(T-70)//67);x.quantity.input('quantity.reader',7,T-1,True)
 # This is a declared material diagnostic probe, not a sensor that computes equality.
 ch=d.ChannelSpec();ch.name='EF01.EQUAL.R3.material_probe';ch.injection_site=d.Coordinate(*e.move(c,(0,1,0),-lead));ch.direction=d.Direction(0,1,0);ch.state=1;ch.semantic=1;ch.allow_experience=True;ch.allow_probe=True
 pp=d.InterfaceSpec();pp.name=ch.name;pp.channel=ch;w.declare_interface(pp);send(ch.name,0,T+1-lead,True)
 data['equality_probe']={'lead':lead,'input_tick':T+1-lead,'declared_material_not_passive':True,'may_affect_intermediate_routes':True}
 for name,b in banks.items():
  b['cue']=port(name+'.cue',b['hub']);b['query']=port(name+'.query',b['hub'])
  if signal:send(b['cue'],5,T+1+delay)
 for tick,label,site in((T,'comparison',c),(T+1,'native_current_route',slot),(T+4+delay,'post_signal_equal',banks['igual']['hub'])):
  x.run_until(tick);data['frames'].append({'label':label,'tick':x.tick,'record':observe(w,site),'moore':moore27(w,site),'banks':{k:observe(w,b['hub'])for k,b in banks.items()}})
 target=T+4+delay+67
 for j in range(6):
  for name,b in banks.items():send(b['query'],7,target-3,True)
  x.run_until(target);records={k:observe(w,b['hub'])for k,b in banks.items()};labels=[k for k,b in banks.items()if e.valid(records[k],b['signature'])]
  data['queries'].append({'round':j,'tick':x.tick,'records':records,'SPANISH_DECODED':labels,'moore':{k:moore27(w,b['hub'])for k,b in banks.items()}});target+=67
 data['geometry']={'current_slot':slot,'banks':banks,'comparison_tick':T,'reference_updated_by13':update}
 data['receipts']=[{**r,'receipt':exact_receipt(w.runtime.receipt(r['id']))}for r in data['requests']]
 data['old_comparisons']=e.query_words(x);data['old_contact']=e.contact_query(x,frame='contactoA');data['post']=physical(w,occupation=True)
 return {'tick':x.tick,'new_forms':[r['SPANISH_DECODED']for r in data['queries']],'prior_words':data['old_comparisons']['FORMAS_ACCESIBLES'],'prior_contact':data['old_contact']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'EF01_EQUAL_DIFFERENT_NATIVE_ALTERNATE_ROUTE_TEACHING_R3',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
