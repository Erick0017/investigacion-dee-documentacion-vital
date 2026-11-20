"""A new equality hypothesis: native zero-direction result, not silence.

Instrument initially tests whether a late zero-load cue can retain a
comparison consequence. No success decoder is fitted after observations.
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
value,signal={'equal':(86,True),'less':(56,True),'more':(110,True),'no_object':(None,True),'equal_no_signal':(86,False)}[a.case]
s=Store(a.system);parent='ES01_MAIN_03';life='ES01_EQUAL_EXP1_'+a.case;s.fork(parent,life,kind='CANDIDATE')
data={'case':a.case,'life':life,'parent':s.record(parent),'frames':[],'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'predefined_question':'Does the active native zero-direction equality product, not a silent or rejected reading, contribute material to a later arbitrary zero-load cue and remote query? No linguistic acquisition is presumed.'}
def trial(x):
 w=x.world;c=x.quantity.geometry['center'];T=e.tick_at_or_after(x.tick,phase=3,lead=8);hub=e.move(c,(0,1,0),4);requests=[]
 def port(role,target,v):
  ch=d.ChannelSpec();ch.name='EF01.EQUAL.EXP1.'+role;ch.injection_site=d.Coordinate(*e.move(target,v,-3));ch.direction=d.Direction(*v);ch.state=1;ch.semantic=1;ch.allow_experience=True;ch.allow_probe=True;p=d.InterfaceSpec();p.name=ch.name;p.channel=ch;w.declare_interface(p);return ch.name
 cue=port('cue',c,(0,1,0));read=port('read',hub,(0,0,1))
 if value is not None:x.quantity.present_object(value,round_index=(T-70)//67)
 x.quantity.input('quantity.reader',7,T-1,True)
 if signal:
  r=w.submit(cue,0,T-2);requests.append({'port':cue,'payload':0,'tick':T-2,'id':int(r.id)})
 r=w.probe(read,0,T+69);requests.append({'port':read,'payload':0,'tick':T+69,'id':int(r.id)})
 for tick,label,site in((T-1,'pre_comparison',c),(T,'comparison',c),(T+1,'cue_encounter',c),(T+5,'remote_cue',hub),(T+71,'pre_query',hub),(T+72,'query',hub)):
  x.run_until(tick);data['frames'].append({'label':label,'tick':x.tick,'record':observe(w,site),'moore':moore27(w,site),'physical':physical(w,occupation=True)})
 data['receipts']=[{**r,'receipt':exact_receipt(w.runtime.receipt(r['id']))}for r in requests];data['words']=e.query_words(x);data['post']=physical(w,occupation=True)
 return {'tick':x.tick,'query':data['frames'][-1]['record'],'old_words':data['words']['FORMAS_ACCESIBLES']}
data['commit']=s.mutate(life,'EF01_EQUALITY_ZERO_DIRECTION_HYPOTHESIS_NOT_SILENCE',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
