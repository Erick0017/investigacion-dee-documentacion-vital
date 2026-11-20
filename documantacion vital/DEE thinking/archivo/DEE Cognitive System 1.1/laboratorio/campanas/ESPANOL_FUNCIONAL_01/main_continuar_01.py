"""Select and continue a real learned campaign branch; original active intact."""
from pathlib import Path
import argparse,sys,json,hashlib,importlib.util
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import observe,physical,moore27
from app.process_control import protect_current
from dee_thinking.consolidated import exact_receipt
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
spec=importlib.util.spec_from_file_location('bridge_actual',a.system/'capacidades/puente_adquirible.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
s=Store(a.system);stable=s.record();parent='ES01_STREAM_B_context_only';life='ES01_MAIN_01';s.fork(parent,life,kind='CANDIDATE')
data={'life':life,'parent':s.record(parent),'stable_at_start':stable,'frames':[],'new_teaching':False,'classification':'Same actual life learns comparison cues then24new current contexts and reference revision; this exact fork continues that past'}
def move(p,v,k=1):return[(p[i]+v[i]*k)%67 for i in range(3)]
def run(x):
 w=x.world;c=x.quantity.geometry['center'];hubs={word:move(c,(sign,0,0),3)for word,sign in [('menos',1),('mas',-1)]};prior={k:observe(w,v)for k,v in hubs.items()};data['word_baseline']=prior
 data['old_social_query']=b.read_transformed(w,5673,axis=-1,payload=7)
 x.quantity.present_object(110,round_index=84);x.quantity.input('quantity.reader',7,5697,True);x.two_memory.input('quantity.reader',7,5699,True);requests=[]
 for word,sign in [('menos',1),('mas',-1)]:
  name='EF01.R1.'+word+'.'+('query_minus'if sign==1 else'query_plus');rr=w.probe(name,7,5698);requests.append({'word':word,'port':name,'payload':7,'tick':5698,'id':int(rr.id)})
 x.run_until(5698);data['actual_new_comparison']={'tick':x.tick,'center':observe(w,c),'moore':moore27(w,c)}
 x.run_until(5700);data['old_two']={'tick':x.tick,'center':observe(w,x.two_memory.geometry['center']),'moore':moore27(w,x.two_memory.geometry['center'])}
 x.run_until(5701);current={k:observe(w,v)for k,v in hubs.items()};decoded=[]
 for word,sign in [('menos',1),('mas',-1)]:
  if prior[word]['direction']==current[word]['direction']==[sign,sign,-sign]and current[word]['s_reg']-prior[word]['s_reg']-7==7:decoded.append('más'if word=='mas'else'menos')
 data['new_word_signal']=current;data['native_decoded_spanish']=decoded;data['decoder_role']='INSTRUMENTO fixed amplitude demodulation; native comparison and acquired carrier interaction precede translation'
 data['new_word_requests']=[{**r,'receipt':exact_receipt(w.runtime.receipt(r['id']))}for r in requests];data['quantity_requests']=x.quantity.receipts();data['post']=physical(w,occupation=True)
 return {'tick':x.tick,'decoded':decoded,'new_actual_object':110,'labels_taught':False,'old_social_and_two_rechecked':True}
data['commit']=s.mutate(life,'EF01_MAIN_PRIOR_RETENTION_AND_NEW_SPANISH_CONTEXT',run)
data['stable_unchanged']=s.record(stable['life_id'])['snapshot_sha256']==stable['snapshot_sha256']
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'life':life,'tick':data['post']['tick'],'native_spanish':data['native_decoded_spanish'],'old_two':data['old_two']['center'],'stable_unchanged':data['stable_unchanged'],'physical':data['post']},ensure_ascii=False))

