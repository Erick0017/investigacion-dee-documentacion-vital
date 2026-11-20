"""Teach two extra spatial contexts in the physically protected wide lineage.

Existing quantities/spatial/contact/free history is inherited by exact fork,
not re-created. Same-phase vs staggered lessons test composition/interference;
omitted word cues keep the new actual material events. All later queries use
all protocol opportunities, never a target-selected native answer route.
"""
from pathlib import Path
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
from app.lives import Store
from app.native_tools import physical
from app.process_control import protect_current
from capacidades import paisaje_causal_01 as pc,espanol_funcional_01 as e,ensenanza_lexica_03 as f
from instrumentos_pc01 import receipts,sha
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='PC01_CONTINUIDAD28_far_guard';life='E1_PAISAJE_01'if a.case=='staggered'else'PC01_APRENDIZAJE35_'+a.case;s.fork(parent,life,kind='CANDIDATE');data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'lessons':[],'reserved':[],'criteria_before':'Actual+1cercaand-1lejosload3encounters, nottwo newNSMprimitives. Same-phase12/12vsstaggered12/8; omittedarbitrarywordcuesstaggeredcontrolkeepsphysicalevents. Allframephaseopportunitiesusedforeachnewscene. Newloads2/4/6plus5reserved, noPythonanswersintroduced. Inheritedwidecontext/magnitudereference/contact/freecapabilitiesmustbechecked, notsummedfromanotherworld. NewlearnedlabelsnotwrittenasRAW.','schedule':[[1,5],[-1,5],[3,4],[-3,6],[5,2],[-5,4],[1,2],[-1,6],[3,6],[-3,2],[5,4],[-5,6]]}
def trial(x):
    data['pre']=physical(x.world,occupation=True)
    data['lessons'].append(f.teach(x,frame='lexical05',parameter=1,word='cerca',phase_shift=12,load=3,signal=a.case!='no_word_cues'));x.save(a.out/'DESPUES_MAS_UNO_COMPLETO.deetsnap.gz')
    data['lessons'].append(f.teach(x,frame='lexical05',parameter=-1,word='lejos',phase_shift=12 if a.case=='same_phase'else 8,load=3,signal=a.case!='no_word_cues'));x.save(a.out/'DESPUES_MENOS_UNO_COMPLETO.deetsnap.gz')
    data['first_recall']=f.query(x,frame='lexical05')
    for j,(k,L)in enumerate(data['schedule']):
        data['reserved'].append(pc.current_dose(x,parameter=k,load=L))
        if j==5:x.save(a.out/'MITAD_RESERVAS_COMPLETO.deetsnap.gz')
    data['old_after']={'less':e.context(x,value=64,method='B'),'more':e.context(x,value=117,method='B'),'contact':e.contact_query(x,frame='contactoA'),'free':e.contact_query(x,frame='freeRepair5'),'time':e.temporal_query(x,frame='secuenciaA')};data['post']=physical(x.world,occupation=True);data['receipts']=receipts(x.world.runtime)
    return{'tick':x.tick,'initial_bindings':[r['ENTE']['post_signal']['d1'if i==0 else'd-1']for i,r in enumerate(data['lessons'])],'responses':[r['SPANISH_DECODED']for r in data['reserved']],'less':data['old_after']['less']['TRADUCCION']['SPANISH_DECODED'],'more':data['old_after']['more']['TRADUCCION']['SPANISH_DECODED'],'contact':data['old_after']['contact']['SPANISH_DECODED'],'free':data['old_after']['free']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'PC01_ADDITIONAL_TWO_CONTEXT_LEARNING_AND_RETENTION35',trial);(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
