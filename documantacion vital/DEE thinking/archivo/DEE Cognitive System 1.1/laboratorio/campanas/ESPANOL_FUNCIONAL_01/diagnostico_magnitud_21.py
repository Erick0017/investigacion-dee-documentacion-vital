"""Late magnitude access witnesses, without repairing or re-teaching MAIN."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical,observe,moore27
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
s=Store(a.system);parent='E1_ESPANOL_01';life='ES01_MAG_DIAG21_'+a.case;s.fork(parent,life,kind='DIAGNOSTIC_COPY')
data={'case':a.case,'life':life,'parent':s.record(parent),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'trace':[],
 'question_before':'At the current lived state, distinguish missing physical operands from an occupied/altered reader. No external memory cleaning, reference refill, or decoder change. Actual object61 has the same fixed format cue5.'}
def trial(x):
 c=x.quantity.geometry['center'];baseline=e.tick_at_or_after(x.tick,phase=6,lead=5);center=baseline+64;first=len(x.quantity.state['requests']);x.quantity.present_object(61,round_index=(center-70)//67)
 if a.case!='no_new_reader':x.quantity.input('quantity.reader',7,center-1,True)
 sites={'center':c,'reference_operand':e.move(c,(-1,0,0)),'object_operand':e.move(c,(1,0,0)),'reference_hub':x.quantity.geometry['reference_hub'],'object_hub':x.quantity.geometry['object_hub']}
 for t in range(center-6,center+5):
  x.run_until(t);data['trace'].append({'tick':t,'records':{key:observe(x.world,p)for key,p in sites.items()},'center_moore':moore27(x.world,c),'reference_moore':moore27(x.world,x.quantity.geometry['reference_hub'])})
 data['word_forms']=e.query_words(x);data['receipts']=x.quantity.receipts()[first:];data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'native_center':[(r['tick'],r['records']['center']['direction'],r['records']['center']['s_reg'])for r in data['trace']],'forms':data['word_forms']['FORMAS_ACCESIBLES']}
data['commit']=s.mutate(life,'EF01_LATE_MAGNITUDE_OPERAND_READER_LOCAL_TRACE21',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
