"""One actual main continuation: two current contact experiences and old words."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical,moore27,observe
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
s=Store(a.system);parent='ES01_MAIN_01';life='ES01_MAIN_02';s.fork(parent,life,kind='CANDIDATE')
data={'life':life,'parent':s.record(parent),'phases':[],'criteria_before':'Toca/native[-axis,1,0]; no toca/native[-axis,1,-1]. Positive free flight is not general negation. Quantity fixed delta7 decoder unchanged.','new_experiences_not_imported_memories':True,'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
def capture(x,label,row):
 data['phases'].append({'label':label,'tick':x.tick,'result':row,'physical':physical(x.world,occupation=True)})
def trial(x):
 data['initial']=physical(x.world,occupation=True);e.prepare(x)
 for frame,base,present in [('contactoA',[28,34,54],True),('vueloB',[28,20,54],False)]:
  e.contact_prepare(x,frame=frame,base=base);capture(x,'teaching_'+frame,e.contact_teach(x,frame=frame,present=present))
  for j in range(3):capture(x,'read_'+frame+'_'+str(j),e.contact_query(x,frame=frame))
  capture(x,'comparison_forms_after_'+frame,e.query_words(x))
 capture(x,'previous_contact_after_new_free',e.contact_query(x,frame='contactoA'))
 capture(x,'previous_free_after_contact_query',e.contact_query(x,frame='vueloB'))
 for value in(84,112,86):capture(x,'reserved_current_magnitude_'+str(value),e.context(x,value=value,method='B'))
 capture(x,'contact_after_new_magnitudes',e.contact_query(x,frame='contactoA'))
 capture(x,'free_after_new_magnitudes',e.contact_query(x,frame='vueloB'))
 capture(x,'comparison_form_retention',e.query_words(x))
 target=e.tick_at_or_after(x.tick,phase=5,lead=1);x.two_memory.input('quantity.reader',7,target-1,True);x.run_until(target)
 data['old_two']={'tick':x.tick,'observation':observe(x.world,x.two_memory.geometry['center']),'moore':moore27(x.world,x.two_memory.geometry['center'])}
 data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'phases':len(data['phases']),'old_two':data['old_two']['observation'],'not_automatic_semantic_verdict':True}
data['commit']=s.mutate(life,'EF01_MAIN_TWO_CONTACT_RELATIONS_AFTER_COMPARISON_HISTORY',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'life':life,'tick':data['post']['tick'],'rows':[{'label':r['label'],'response':r['result'].get('SPANISH_DECODED',r['result'].get('FORMAS_ACCESIBLES',r['result'].get('TRADUCCION',{}).get('SPANISH_DECODED')))}for r in data['phases']]},ensure_ascii=False))
