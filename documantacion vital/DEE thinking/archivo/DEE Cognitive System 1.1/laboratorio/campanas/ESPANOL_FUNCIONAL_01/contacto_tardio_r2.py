"""Current late contact -> acquired Spanish contact-form -> later native use.

No old contact snapshot is imported. Zero-load actuator/common carrier and a
current medium are actual admitted experiences in the ongoing world.
"""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import observe,physical,moore27
from app.process_control import protect_current
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_receipt
from dee_thinking.persistence import encode_metadata
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
plans={'contact':(True,1,1,0,False,False),'free':(False,1,1,0,False,False),'unpaired':(True,1,1,1,False,False),'no_signal':(True,1,1,0,True,False),'no_medium':(True,1,1,0,False,True),'reserve_load3':(True,3,1,0,False,False),'reserve_actor17':(True,1,17,0,False,False)}
present,medium,actor_state,delay,omit_signal,omit_medium=plans[a.case]
s=Store(a.system);parent='ES01_R6_paired';life='ES01_CONTACT2_'+a.case;s.fork(parent,life,kind='CANDIDATE')
data={'case':a.case,'life':life,'parent':s.record(parent),'new_relation':'Physical contact vs explicit free-flight outcome, not general logical negation','prepared':'Frame and fixed Spanish ports; not learned geometry or deictic perspective','requests':[],'frames':[],'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
def move(p,v,k=1):return[(p[i]+v[i]*k)%67 for i in range(3)]
def trial(x):
 w=x.world;base=[28,34,54];join=move(base,(0,0,-1));banks={};start=4020
 def port(name,site,v,state=1,lead=0):
  ch=d.ChannelSpec();ch.name='EF01.C1.'+name;ch.injection_site=d.Coordinate(*move(site,v,-lead));ch.direction=d.Direction(*v);ch.state=state;ch.semantic=1;ch.allow_experience=True;ch.allow_probe=True;q=d.InterfaceSpec();q.name=ch.name;q.channel=ch;w.declare_interface(q);return ch.name
 actor=move(join,(1,0,0),-4)
 if not present:actor=move(actor,(0,1,0),12)
 eventports={'actor':port('actor',actor,(1,0,0),actor_state),'common':port('common',move(join,(-1,0,1),-4),(-1,0,1)),'medium':port('medium',move(base,(1,1,-1),-5),(1,1,-1))}
 for axis in[-1,1]:
  for z,word in[(0,'toca'),(-1,'no_toca')]:
   key=word+('_izq'if axis==-1 else'_der');hub=move(base,(axis,1,z),4)
   banks[key]={'word':word,'axis':axis,'z':z,'hub':hub,'cue':port(key+'.cue',hub,(-axis,0,0),lead=3)}
 def send(name,payload,t,probe=False):
  rr=(w.probe if probe else w.submit)(name,payload,t);data['requests'].append({'port':name,'payload':payload,'tick':t,'probe':probe,'id':int(rr.id)})
 def capture(label,sites):
  data['frames'].append({'label':label,'tick':x.tick,'physical':physical(w,occupation=True),'sites':{k:{'record':observe(w,v),'moore':moore27(w,v)}for k,v in sites.items()},'comparison_words':{word:observe(w,move(x.quantity.geometry['center'],(sign,0,0),3))for word,sign in [('menos',1),('mas',-1)]}})
 send(eventports['actor'],0,start);send(eventports['common'],0,start)
 if not omit_medium:send(eventports['medium'],medium,start)
 if not omit_signal:
  for bank in banks.values():send(bank['cue'],5,start+6+delay)
 capture('before',{'contact_join':join,'contact_base':base})
 for t in[start+3,start+4,start+5,start+8,start+9,start+10]:
  x.run_until(t);capture('experience',{'contact_join':join,'contact_base':base,**{k:v['hub']for k,v in banks.items()}})
 # Reader follows the transformed material after each fixed current-use event.
 sites={k:b['hub']for k,b in banks.items()};next_read=start+76
 for round_index in range(6):
  targets={};reads={}
  for key,b in banks.items():
   reads[key]=port(key+'.r'+str(round_index),sites[key],(-b['axis'],0,0),lead=3)
   targets[key]=move(sites[key],(-b['axis'],1,b['z']),6)
   use=port(key+'.use'+str(round_index),targets[key],(b['axis'],0,0),lead=3)
   send(reads[key],5,next_read-3,True);send(use,7,next_read+3)
  x.run_until(next_read-1);capture('pre_read_'+str(round_index),sites)
  x.run_until(next_read);capture('read_'+str(round_index),sites)
  x.run_until(next_read+5);capture('pre_use_'+str(round_index),targets)
  x.run_until(next_read+6);capture('use_'+str(round_index),targets)
  if round_index in(0,5):x.save(a.out/('T'+str(x.tick)+'.deetsnap.gz'))
  # After use the +X/-X resource cancels X, returning Y/Z material.
  sites=targets;next_read+=67+6
 # Existing two learned comparison words must be tested after new contact.
 t=3490
 while t<x.tick+3:t+=67
 for word,sign in [('menos',1),('mas',-1)]:send('EF01.R1.'+word+'.'+('query_minus'if sign==1 else'query_plus'),7,t-3,True)
 x.run_until(t);capture('prior_words_retention',sites)
 data['geometry']={'base':base,'join':join,'start':start,'banks':banks,'last_sites':sites,'first_read':start+76,'read_step':73}
 data['receipts']=[{**r,'receipt':exact_receipt(w.runtime.receipt(r['id']))}for r in data['requests']]
 data['post']=physical(w,occupation=True)
 w.runtime.set_snapshot_metadata('DEE.Cognitive.System.1.1.EF01.contact.v1',encode_metadata(data['geometry']))
 return {'tick':x.tick,'teaching':'Current contact/free route, followed by physical cue and later query/use','actual_contacts_not_host_compared':True}
data['commit']=s.mutate(life,'EF01_LATE_CONTACT_LANGUAGE_R1',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'case':a.case,'post':data['post'],'first_use':next(f for f in data['frames']if f['label']=='use_0')['sites'],'retention':data['frames'][-1]['comparison_words']},ensure_ascii=False))

