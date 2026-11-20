"""Four-world history effects of the real material word-reader on lateE1."""
from pathlib import Path
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
from app.lives import Store
from app.native_tools import physical,SYSTEM_KEY
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,ensenanza_lexica_03 as lex,puente_lexico_10 as b
from instrumentos_pc01 import Trace,frame,native_digest,receipts,sha
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='ES01_LATE_ACCESS29_passive';life='PC01_FACTORIAL07_'+a.case;s.fork(parent,life,kind='DIAGNOSTIC_COPY');hasH=a.case in('W10','W11');hasI=a.case in('W01','W11');data={'case':a.case,'life':life,'parent':s.record(parent),'H':hasH,'I':hasI,'source_sha256':sha(__file__),'H_reads':[],'criteria_before':'H=6equalcalendar bursts of existing all-phase lexical and bridge material queries. I=one currentA/Bscene+3load5 without word-query dose, fixed phase13; sensor/parser supplies no answer. Iomission removes actualA/Binputs, not the observation clock. Exact pair equality beforeI includes full native queue serialization, omitting only documentary life identity. This may show history-dependent access/interference, not necessarily learning.'}
def trial(x):
    data['pre']=physical(x.world,occupation=True);start=e.tick_at_or_after(x.tick,phase=22,lead=10);tr=Trace(x,a.out/'MUESTRAS_CAMPO.jsonl.gz',start=x.tick,end=None,stride=13).install()
    for j in range(6):
        boundary=start+201*j;x.run_until(boundary)
        if hasH:data['H_reads'].append({'lexical':lex.query(x,frame='lexical05'),'bridge':b.query(x,bridge='near5Bridge')})
        x.run_until(boundary+200)
    data['before_I']={'physical':physical(x.world,occupation=True),'frame':frame(x.world),'receipts':receipts(x.world.runtime)};clone=x.world.runtime.fork();clone.erase_snapshot_metadata(SYSTEM_KEY);data['before_I']['native_projection']=native_digest(clone)
    data['I_result']=lex.context(x,frame='lexical05',parameter=3,load=5,phase=13,decoder='strict',event_a=hasI,event_b=hasI,emit_word_queries=False);data['immediate']=frame(x.world);x.run_until(x.tick+2*67);data['late']=frame(x.world);data['trace']=tr.close();data['post']=physical(x.world,occupation=True);data['receipts']=receipts(x.world.runtime)
    return{'tick':x.tick,'H':hasH,'I':hasI,'native_response':data['I_result']['SPANISH_DECODED'],'occupied':data['post']['occupied']}
data['commit']=s.mutate(life,'PC01_LATE_E1_HISTORY_INPUT_FACTORIAL07',trial);(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
