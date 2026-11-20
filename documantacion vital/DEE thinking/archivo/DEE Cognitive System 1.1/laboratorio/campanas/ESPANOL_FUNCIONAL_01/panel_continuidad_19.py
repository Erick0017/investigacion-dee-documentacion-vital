"""Affected old contracts on an explicit evaluation copy, not on stable/main."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical,observe,moore27
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,puente_adquirible as b
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
s=Store(a.system);parent='E1_ESPANOL_01';life='ES01_PANEL19_'+a.case;s.fork(parent,life,kind='DIAGNOSTIC_COPY')
data={'case':a.case,'life':life,'parent':s.record(parent),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'criteria_before':'Current relative-order and magnitude form queries are material interventions on an evaluation copy. No missing old S04 response is filled or re-taught. New Spanish state itself remains untouched.'}
def trial(x):
 data['temporal']=e.temporal_query(x,frame='secuenciaA')
 data['magnitude_current_less']=e.context(x,value=61,method='B')
 data['magnitude_current_more']=e.context(x,value=119,method='B')
 target=e.tick_at_or_after(x.tick,phase=5,lead=3);x.two_memory.input('quantity.reader',7,target-1,True);x.run_until(target)
 data['old_two']={'record':observe(x.world,x.two_memory.geometry['center']),'moore':moore27(x.world,x.two_memory.geometry['center']),'receipts':x.two_memory.receipts()}
 target=e.tick_at_or_after(x.tick,phase=45,lead=3);data['old_social']=b.read_transformed(x.world,target,axis=-1,payload=7)
 data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'two_direction':data['old_two']['record']['direction'],'time':data['temporal']['SPANISH_DECODED'],'old_social':data['old_social']['ENTE']}
data['commit']=s.mutate(life,'EF01_AFFECTED_PREVIOUS_CONTRACTS_CURRENT_EVALUATION19',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'life':life,'tick':data['post']['tick'],'two':data['old_two']['record']['direction'],'time':data['temporal']['SPANISH_DECODED']},ensure_ascii=False))
