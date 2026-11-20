"""New-current-context use of acquired Spanish comparison signals.

Generator supplies actual magnitudes. Both memory banks receive identical
anti-X opportunities; the fixed native reducer must combine past and present.
No observer result chooses a response input. Evaluation is performed afterward.
"""
from pathlib import Path
import argparse,json,sys,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import observe,physical,moore27
from app.process_control import protect_current
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_receipt
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
plans={'full_less':('paired',56,False,False,False),'full_more':('paired',93,False,False,False),'full_equal':('paired',73,False,False,False),'no_words_less':('omitted',56,False,False,False),'no_history_event':('noevent',56,False,False,False),'context_omitted':('paired',56,True,False,False),'cut_less':('paired',56,False,True,False),'sham_less':('paired',56,False,True,True)}
parent,value,no_current,cut,sham=plans[a.case];s=Store(a.system);life='ES01_CTX1_'+a.case;s.fork('ES01_R6_'+parent,life,kind='CANDIDATE')
data={'case':a.case,'life':life,'parent':s.record('ES01_R6_'+parent),'value':value,'new_context_omitted':no_current,'cut':cut,'sham':sham,'frames':[],'requests':[],'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'not_class_or_result_sent_to_participant':True}
def move(p,v,k=1):return[(p[i]+v[i]*k)%67 for i in range(3)]
def trial(x):
 w=x.world;c=x.quantity.geometry['center'];words={k:{'site':move(c,(sign,0,0),3),'sign':sign}for k,sign in [('menos',1),('mas',-1)]}
 def port(name,site,v):
  ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(*move(site,v,-3));ch.direction=d.Direction(*v);ch.state=1;ch.semantic=1;ch.allow_experience=True;ch.allow_probe=True;p=d.InterfaceSpec();p.name=name;p.channel=ch;w.declare_interface(p)
 def send(name,load,t,probe=True):
  rr=(w.probe if probe else w.submit)(name,load,t);data['requests'].append({'port':name,'payload':load,'tick':t,'is_probe':probe,'id':int(rr.id)})
 def frame(label):
  data['frames'].append({'label':label,'tick':x.tick,'physical':physical(w,occupation=True),'center':observe(w,c),'words':{k:{'physical':observe(w,v['site']),'moore':moore27(w,v['site'])}for k,v in words.items()}})
 for word,g in words.items():
  port('EF01.context.'+word,g['site'],(-g['sign'],0,0))
  if cut:port('EF01.cut.'+word,move(move(c,(g['sign'],0,0),1),(0,0,1),8 if sham else 0),(-g['sign'],0,0))
 if not no_current:x.quantity.present_object(value,round_index=59)
 x.quantity.input('quantity.reader',7,4022,True)
 for word in words:
  send('EF01.context.'+word,7,4023)
  if cut:send('EF01.cut.'+word,0,4021,False)
 frame('pre')
 for t in range(4022,4030):x.run_until(t);frame('new_context')
 x.save(a.out/'T4029.deetsnap.gz')
 for word,g in words.items():send('EF01.R1.'+word+'.'+('query_minus'if g['sign']==1 else'query_plus'),7,4090)
 x.two_memory.input('quantity.reader',7,4089,True)
 x.run_until(4090);frame('old_two_window');x.run_until(4093);frame('retention_no_reteaching')
 data['word_requests_final']=[{**r,'receipt':exact_receipt(w.runtime.receipt(r['id']))}for r in data['requests']]
 data['quantity_requests_final']=x.quantity.receipts()
 data['old_two']=observe(w,x.two_memory.geometry['center'])
 data['post']=physical(w,occupation=True);return{'tick':x.tick,'context_method':'Prepared native anti-X query, possible destructive read counted'}
data['commit']=s.mutate(life,'EF01_NEW_CONTEXT_COMPOSITION_R1',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
chosen=next(f for f in data['frames']if f['tick']==4026)
print(json.dumps({'case':a.case,'words':{k:v['physical']for k,v in chosen['words'].items()},'old_two':data['old_two'],'post':data['post']},ensure_ascii=False))

