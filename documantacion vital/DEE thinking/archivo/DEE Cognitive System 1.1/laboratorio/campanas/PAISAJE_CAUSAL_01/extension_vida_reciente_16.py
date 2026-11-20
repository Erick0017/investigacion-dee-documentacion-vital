"""Apply the mapped route protection prospectively to the latest full E1.

The life forks at36403, never imports the earlier protected future. Two
previously unavailable physical contexts receive real new event/cue lessons.
"""
from pathlib import Path
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
from app.lives import Store
from app.native_tools import physical
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,ensenanza_lexica_03 as f,puente_lexico_10 as b,igualdad_fisica_03 as eq
from instrumentos_pc01 import guard,receipts,sha
from dee_thinking.persistence import encode_metadata
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='ES01_LATE_ACCESS29_passive';life='PC01_RECIENTE16_'+a.case;s.fork(parent,life,kind='CANDIDATE');data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'lessons':[],'reserved':[],'criteria_before':'Prospective application fromactualT36403, not a repaired old future. Teachactual+1cerca atphase8and-1lejos atphase12, load3, one event encounter plus later arbitrary cue. Fixed route guard39,57,15or equal-material sham39,65,15or no guard. Omitted word-cue control keeps actual environmental events and protection. Evaluateallphases/bridgeforeachscene, load5ispost-designreservefornewcontexts, no target-selected routing. NewcontextsarenotnewNSMprimitives and late evaluationcanitselfchangehistory.','schedule':[[1,5],[-1,5],[3,3],[-3,5],[5,5],[-5,3],[1,3],[-1,3],[3,5],[-3,3],[5,3],[-5,5],[1,5],[-1,5]]}
def trial(x):
    data['pre']=physical(x.world,occupation=True)
    if a.case in('guard','sham','no_word_cue'):
        data['protection']=guard(x.world,'PC01.RECIENTE16.ORBIT',[39,65 if a.case=='sham'else 57,15],x.tick+1);x.world.runtime.set_snapshot_metadata('DEE.Cognitive.System.1.1.PC01.prospective_guard',encode_metadata({'site':data['protection']['site'],'input_id':data['protection']['id'],'applied_prospectively_from':36403,'prepared_not_policy':True}))
    data['lessons'].append(f.teach(x,frame='lexical05',parameter=1,word='cerca',phase_shift=8,load=3,signal=a.case!='no_word_cue'));data['lessons'].append(f.teach(x,frame='lexical05',parameter=-1,word='lejos',phase_shift=12,load=3,signal=a.case!='no_word_cue'));data['after_new_experiences']=physical(x.world,occupation=True);x.save(a.out/'DESPUES_EXPERIENCIAS_COMPLETO.deetsnap.gz')
    for j,(k,load)in enumerate(data['schedule']):
        row=e.produce_relations(x,frame='lexical05',bridge='near5Bridge',parameter=k,load=load,legacy_word_probes=False,bridge_word_probe=False);data['reserved'].append({'episode':j+1,'parameter':k,'load':load,'result':row,'physical':physical(x.world,occupation=True)})
        if j in(1,7,13):x.save(a.out/('T'+str(x.tick)+'_CONTINUIDAD.deetsnap.gz'))
    data['old_after']={'less':e.context(x,value=67,method='B'),'more':e.context(x,value=120,method='B'),'contact':e.contact_query(x,frame='contactoA'),'free':e.contact_query(x,frame='freeLate27'),'time':e.temporal_query(x,frame='secuenciaA'),'equal_form':eq.query(x),'forms':f.query(x,frame='lexical05'),'bridge_form':b.query(x,bridge='near5Bridge')};data['post']=physical(x.world,occupation=True);data['receipts']=receipts(x.world.runtime)
    return{'tick':x.tick,'responses':[r['result']['SPANISH_DECODED']for r in data['reserved']],'less':data['old_after']['less']['TRADUCCION']['SPANISH_DECODED'],'more':data['old_after']['more']['TRADUCCION']['SPANISH_DECODED'],'contact':data['old_after']['contact']['SPANISH_DECODED'],'free':data['old_after']['free']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'PC01_PROSPECTIVE_NATIVE_GUARD_NEW_EXPERIENCES16',trial);(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
