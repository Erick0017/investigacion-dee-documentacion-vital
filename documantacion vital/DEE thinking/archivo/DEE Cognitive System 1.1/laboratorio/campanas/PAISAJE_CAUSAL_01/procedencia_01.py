"""New provenance coverage of existing EF01 encounters, not new replications."""
from pathlib import Path
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
from app.lives import Store
from app.native_tools import physical
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,igualdad_fisica_03 as f,ensenanza_lexica_03 as lex
from instrumentos_pc01 import Trace,native_digest,receipts,sha,witness
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
s=Store(a.system);near=a.case.startswith('near');watched=not a.case.endswith('plain');parent='ES01_LONG7_D_no_material_queries'if near else'ES01_MAIN_04';life='PC01_ORIGEN01_'+a.case;s.fork(parent,life,kind='DIAGNOSTIC_COPY')
data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'question':'Identify actual antecedents and boundary crossings of foreign carrier, beyond the known collision. Traced vs untraced exact protocol for observer validation.','phases':[]}
def cap(x,label,row):data['phases'].append({'label':label,'tick':x.tick,'result':row})
def trial(x):
    data['pre']=physical(x.world,occupation=True);data['pre_native']=native_digest(x.world.runtime);tr=None
    if watched:tr=Trace(x,a.out/'CAMPO_COMPLETO.jsonl.gz',start=x.tick,end=22460 if near else 9990).install()
    if near:
        cap(x,'existing_lesson',lex.teach(x,frame='lexical05',parameter=5,word='cerca',phase_shift=8));data['acquisition_tick']=x.tick
        x.run_until(22460)
    else:
        f.prepare(x);cap(x,'equality_teaching',f.present(x,value=86,teacher=True,probe_lead=1))
        for j in range(3):cap(x,'equality_recall_'+str(j),f.query(x))
        for value in(86,56,110,86):cap(x,'current_equality_'+str(value),f.context(x,value=value,probe_lead=1))
        for name in('contactoA','freeRepair5'):cap(x,'previous_'+name,e.contact_query(x,frame=name))
        cap(x,'previous_time',e.temporal_query(x,frame='secuenciaA'));cap(x,'previous_comparison_forms',e.query_words(x));cap(x,'equal_after',f.query(x))
    if tr:data['trace']=tr.close()
    data['post']=physical(x.world,occupation=True);data['post_native']=native_digest(x.world.runtime);data['receipts']=receipts(x.world.runtime)
    if not near:
        ref=s.record('ES01_MAIN_05')['physical'];data['original_physical_equivalence']={k:data['post'][k]==ref[k]for k in('tick','RAW_sha256','clocks_sha256')}
    return{'tick':x.tick,'RAW_sha256':data['post']['RAW_sha256'],'clocks_sha256':data['post']['clocks_sha256'],'trace_frames':0 if tr is None else tr.count}
data['commit']=s.mutate(life,'PC01_PROVENANCE_PASSIVE_NEW_COVERAGE',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result']))
