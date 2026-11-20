"""Bounded diagnosis of the failed additional-context accumulation in35.

Separate a second event, its word cue and the first material recall. These
are alternative futures, not a favorable replacement for E1_PAISAJE_01.
"""
from pathlib import Path
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
from app.lives import Store
from app.native_tools import physical
from app.process_control import protect_current
from capacidades import paisaje_causal_01 as pc,espanol_funcional_01 as e,ensenanza_lexica_03 as f
from instrumentos_pc01 import receipts,sha,Trace
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='PC01_CONTINUIDAD28_far_guard';life='PC01_FACTORES38_'+a.case;s.fork(parent,life,kind='DIAGNOSTIC_COPY');data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'lessons':[],'reserved':[],'criteria_before':'After35failure, oneboundedfactorstudy: omitthesecondlessonentirely, keepsecondactualeventsbutomittheirwordcue, orkeepbothlessonsbutomitthefirsthistorical-formprobe(panel). Same initialfullworldandfuturecalendar. Ordinarycontextquestionsandnewexperiencescontinueinallarms; lessinterventionisnotitselfawinningmethod. No semanticdecoderchanges.','schedule':[[1,5],[-1,5],[3,4],[-3,6],[5,2],[-5,4],[1,2],[-1,6],[3,6],[-3,2],[5,4],[-5,6]]}
def trial(x):
    data['pre']=physical(x.world,occupation=True);tr=Trace(x,a.out/'CAMPO_DOS_LECCIONES_Y_LECTOR.jsonl.gz',start=39752,end=40032).install()
    data['lessons'].append(f.teach(x,frame='lexical05',parameter=1,word='cerca',phase_shift=12,load=3))
    if a.case=='no_second':
        target=e.tick_at_or_after(x.tick,phase=8,lead=5)+13;x.run_until(target);data['omission']='Secondactualeventsandtheirwordcuesomittedatmatchedcalendar'
    else:data['lessons'].append(f.teach(x,frame='lexical05',parameter=-1,word='lejos',phase_shift=8,load=3,signal=a.case!='second_events_no_cue'))
    if a.case=='no_first_assay':
        target=x.tick
        for phase in e.prepare(x)['relational_words_v2']['lexical05']['lexical_v3']['learned_phases']:target=e.tick_at_or_after(target,phase=phase,lead=3)
        x.run_until(target);data['first_assay_omitted']={'end_tick':target,'ordinary_context_queries_still_used':True}
    else:data['first_recall']=f.query(x,frame='lexical05')
    for k,L in data['schedule']:data['reserved'].append(pc.current_dose(x,parameter=k,load=L))
    data['old_after']={'less':e.context(x,value=64,method='B'),'more':e.context(x,value=117,method='B'),'contact':e.contact_query(x,frame='contactoA'),'free':e.contact_query(x,frame='freeRepair5'),'time':e.temporal_query(x,frame='secuenciaA')};data['trace']=tr.close();data['post']=physical(x.world,occupation=True);data['receipts']=receipts(x.world.runtime)
    return{'tick':x.tick,'responses':[r['SPANISH_DECODED']for r in data['reserved']],'less':data['old_after']['less']['TRADUCCION']['SPANISH_DECODED'],'more':data['old_after']['more']['TRADUCCION']['SPANISH_DECODED'],'contact':data['old_after']['contact']['SPANISH_DECODED'],'free':data['old_after']['free']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'PC01_SECOND_EXPERIENCE_VS_FIRST_MATERIAL_ASSAY38',trial);(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
