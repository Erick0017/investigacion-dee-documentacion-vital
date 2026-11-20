"""Causal parents of the later recurring context carrier, not load lineage."""
from pathlib import Path
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
from app.lives import Store
from app.native_tools import physical
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,ensenanza_lexica_03 as f
from instrumentos_pc01 import Trace,guard,receipts,sha
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='ES01_MAIN_05';life='PC01_GHOST09_'+a.case;s.fork(parent,life,kind='DIAGNOSTIC_COPY');data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'phases':[],'interventions':[],'criteria_before':'Reproduce only the original lexical prefix through current_1, now globally observed around birth. Source protection atd-3hub+3YZ is a new preparedSEM4; sham+9Z. Other variants omit earlier word probes or the laterBcontribution; all omit/sham costs explicit. No native carrier is labelled by equal load alone.'}
def cap(x,label,row):data['phases'].append({'label':label,'tick':x.tick,'result':row})
def trial(x):
    f.prepare(x,frame='lexical05',mode='relative_path',origin=(38,50,8),guarded=True,renew_sources=True)
    if a.case in('source_guard','guard_sham'):data['interventions'].append(guard(x.world,'PC01.GHOST09.SOURCE',[42,63,21 if a.case=='source_guard'else 30],10326))
    if a.case in('orbit_guard','orbit_sham'):data['interventions'].append(guard(x.world,'PC01.GHOST09.ORBIT',[39,57 if a.case=='orbit_guard'else 65,15],10326))
    cap(x,'teach_near3',f.teach(x,frame='lexical05',parameter=3,word='cerca',phase_shift=0));cap(x,'first_near_recall',f.query(x,frame='lexical05'));cap(x,'teach_far3',f.teach(x,frame='lexical05',parameter=-3,word='lejos',phase_shift=4));cap(x,'both_recall',f.query(x,frame='lexical05'))
    tr=Trace(x,a.out/'CAMPO_COMPLETO.jsonl.gz',start=10720,end=10940).install()
    cap(x,'current_0',f.context(x,frame='lexical05',parameter=-3,load=5,decoder='strict',emit_word_queries=a.case!='omit_prior_queries'))
    cap(x,'current_1',f.context(x,frame='lexical05',parameter=3,load=3,decoder='strict',event_b=a.case!='no_current_B',offroute=a.case=='B_offroute'))
    data['trace']=tr.close();cap(x,'forms_after',f.query(x,frame='lexical05'));cap(x,'old_contact',e.contact_query(x,frame='contactoA'));cap(x,'old_free',e.contact_query(x,frame='freeRepair5'));data['post']=physical(x.world,occupation=True);data['receipts']=receipts(x.world.runtime)
    return{'tick':x.tick,'contexts':[r['result']['SPANISH_DECODED']for r in data['phases']if r['label'].startswith('current')],'forms':data['phases'][-3]['result']['SPANISH_DECODED'],'contact':data['phases'][-2]['result']['SPANISH_DECODED'],'free':data['phases'][-1]['result']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'PC01_NATIVE_CONTEXT_CARRIER_BIRTH_CAUSAL09',trial);(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
