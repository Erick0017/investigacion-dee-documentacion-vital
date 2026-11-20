"""Native route cut/sham at the first tracked reference interaction, no RAW edit."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical,observe,moore27
from app.process_control import protect_current
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_receipt
from capacidades import espanol_funcional_01 as e,igualdad_fisica_03 as f
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
s=Store(a.system);parent='ES01_MAIN_04';life='ES01_REF_CAUSE25_'+a.case;s.fork(parent,life,kind='DIAGNOSTIC_COPY')
data={'case':a.case,'life':life,'parent':s.record(parent),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'phases':[],
 'criteria_before':'R0 nativeSEM4 at foreign route[47,38,33], before first tracked collisionT9986; equal-dose sham+9Z. Do not touch the reference field or clocks. Then replay the remaining declared equality events and test new magnitude61/119 plus equality/contact/free/time access. No claim that this earlier alternate future is the current MAIN.'}
def cap(x,label,row):data['phases'].append({'label':label,'tick':x.tick,'result':row})
def trial(x):
 site=[47,38,33]if a.case=='cut'else[47,38,42];ch=d.ChannelSpec();ch.name='EF01.REF25.'+a.case;ch.injection_site=d.Coordinate(*site);ch.direction=d.Direction(0,0,0);ch.state=1;ch.semantic=4;ch.allow_experience=True;ch.allow_probe=True;p=d.InterfaceSpec();p.name=ch.name;p.channel=ch;x.world.declare_interface(p);receipt=x.world.submit(ch.name,0,9983);oldrun=x.run_until;data['witnesses']=[]
 def observed_run(target):
  for t in(9982,9985,9986,9987):
   if x.tick<t<=target:
    oldrun(t);data['witnesses'].append({'tick':t,'record':observe(x.world,[49,36,35]),'moore':moore27(x.world,[49,36,35])})
  oldrun(target)
 x.run_until=observed_run
 f.prepare(x);cap(x,'equality_teaching',f.present(x,value=86,teacher=True,probe_lead=1))
 for j in range(3):cap(x,'equality_recall_'+str(j),f.query(x))
 for value in(86,56,110,86):cap(x,'current_equality_'+str(value),f.context(x,value=value,probe_lead=1))
 for frame in('contactoA','freeRepair5'):cap(x,'previous_'+frame,e.contact_query(x,frame=frame))
 cap(x,'previous_time',e.temporal_query(x,frame='secuenciaA'));cap(x,'previous_comparison_forms',e.query_words(x));cap(x,'equal_after',f.query(x))
 data['new_less']=e.context(x,value=61,method='B');data['new_more']=e.context(x,value=119,method='B');data['final_equal']=f.query(x);data['guard_receipt']=exact_receipt(x.world.runtime.receipt(receipt.id));data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'new_less':data['new_less']['TRADUCCION']['SPANISH_DECODED'],'new_more':data['new_more']['TRADUCCION']['SPANISH_DECODED'],'equal_form':data['final_equal']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'EF01_CAUSAL_NATIVE_REFERENCE_ROUTE_PROTECTION25',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
