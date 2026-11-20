"""Main history accumulates two new temporal events without a use reset."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical,observe,moore27
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
s=Store(a.system);parent='ES01_CONTACT_ACCESS5_x18';life='ES01_MAIN_03';s.fork(parent,life,kind='CANDIDATE')
data={'life':life,'parent':s.record(parent),'phases':[],'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'predefined_scope':'One continuing world, current AB and BA events in the same prepared physical frame; retrieving both historical relations does not assert both are true of the same current pair.'}
def capture(x,label,row):data['phases'].append({'label':label,'tick':x.tick,'result':row,'physical':physical(x.world,occupation=True)})
def trial(x):
 e.temporal_prepare(x,frame='secuenciaA',origin=(8,8,22))
 capture(x,'actual_AB5',e.temporal_experience(x,frame='secuenciaA',order='AB',interval=5))
 for j in range(3):capture(x,'AB5_read_'+str(j),e.temporal_query(x,frame='secuenciaA'))
 capture(x,'actual_BA5_additional_not_reset',e.temporal_experience(x,frame='secuenciaA',order='BA',interval=5,additional=True))
 for j in range(3):capture(x,'both_old_and_new_order_'+str(j),e.temporal_query(x,frame='secuenciaA'))
 for frame in('contactoA','freeRepair5'):capture(x,'prior_'+frame,e.contact_query(x,frame=frame))
 for value in(59,117):capture(x,'new_comparison_'+str(value),e.context(x,value=value,method='B'))
 capture(x,'temporal_after_new_comparisons',e.temporal_query(x,frame='secuenciaA'))
 capture(x,'comparison_forms',e.query_words(x))
 target=e.tick_at_or_after(x.tick,phase=5,lead=1);x.two_memory.input('quantity.reader',7,target-1,True);x.run_until(target)
 data['old_two']={'tick':x.tick,'observation':observe(x.world,x.two_memory.geometry['center']),'moore':moore27(x.world,x.two_memory.geometry['center'])}
 data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'not_a_free_language_claim':True,'phases':len(data['phases'])}
data['commit']=s.mutate(life,'EF01_MAIN_ACCUMULATED_TEMPORAL_AND_CONTACT_AND_MAGNITUDE_RELATIONS',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'life':life,'tick':data['post']['tick'],'rows':[{'label':r['label'],'response':r['result'].get('SPANISH_DECODED',r['result'].get('FORMAS_ACCESIBLES',r['result'].get('TRADUCCION',{}).get('SPANISH_DECODED')))}for r in data['phases']]},ensure_ascii=False))
