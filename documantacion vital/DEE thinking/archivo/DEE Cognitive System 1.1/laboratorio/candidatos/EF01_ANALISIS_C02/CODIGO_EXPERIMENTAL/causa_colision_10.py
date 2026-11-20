"""Selective native cut of the actual S158 countercarrier, diagnostic only."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical,observe,moore27
from app.process_control import protect_current
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_receipt
from capacidades import espanol_funcional_01 as e,ensenanza_lexica_03 as f
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
s=Store(a.system);parent='ES01_LONG7_D_no_material_queries';life='ES01_COLLISION10_'+a.case;s.fork(parent,life,kind='DIAGNOSTIC_COPY')
data={'case':a.case,'life':life,'parent':s.record(parent),'frames':[],'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'hypothesis_before':'The actually observed S158[-1,1,1] incoming source cancels the acquired[1,1,1] atT22457. Cut only its earlier physical route, not the learned near word. Its prior functional ownership is not inferred fromS alone; no intervention will be promoted to MAIN.'}
def trial(x):
 data['teaching']=f.teach(x,frame='lexical05',parameter=5,word='cerca',phase_shift=8);start=x.tick;hub=next(b['hub']for b in e.prepare(x)['relational_words_v2']['lexical05']['banks']if b['id']=='d5')
 site=[39,57,15]if a.case=='cut_countercarrier'else[39,65,15]
 ch=d.ChannelSpec();ch.name='EF01.DIAG.COLLISION10';ch.injection_site=d.Coordinate(*site);ch.direction=d.Direction(0,0,0);ch.state=1;ch.semantic=4;ch.allow_experience=True;ch.allow_probe=True;p=d.InterfaceSpec();p.name=ch.name;p.channel=ch;x.world.declare_interface(p);r=x.world.submit(ch.name,0,start+55)
 for dt in(54,55,56,57,58,59,66,67):
  x.run_until(start+dt);word=e.move(hub,(1,1,1),dt);data['frames'].append({'tick':x.tick,'dt':dt,'word_site':word,'record':observe(x.world,word),'word_moore':moore27(x.world,word),'guard_record':observe(x.world,site),'guard_moore':moore27(x.world,site)})
 data['guard']={'site':site,'receipt':exact_receipt(x.world.runtime.receipt(r.id))};data['new_recall']=f.query(x,frame='lexical05',phase=21);data['old_recall']=f.query(x,frame='lexical05');data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'old_word_at_collision':next(row['record']for row in data['frames']if row['dt']==58),'new_phase_recall':data['new_recall']['SPANISH_DECODED'],'all_words':data['old_recall']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'EF01_OBSERVED_COLLISION_CAUSAL_NATIVE_CUT10',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
