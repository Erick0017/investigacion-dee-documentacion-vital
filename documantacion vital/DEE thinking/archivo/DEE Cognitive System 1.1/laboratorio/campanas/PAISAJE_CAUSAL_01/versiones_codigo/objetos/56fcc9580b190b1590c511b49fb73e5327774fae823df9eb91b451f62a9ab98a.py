"""Apply the mapped occupied-destination mechanism through native inputs.

Main worlds receive no research-state edits. Fixed guard or a zero-load
directional encounter acts before the observed blocker/free collision.
"""
from pathlib import Path
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
from app.lives import Store
from app.native_tools import physical,observe
from app.process_control import protect_current
from capacidades import paisaje_causal_01 as pc,espanol_funcional_01 as e,ensenanza_lexica_03 as f,igualdad_fisica_03 as eq
from dee_thinking.persistence import encode_metadata
from instrumentos_pc01 import guard,witness,receipts,sha
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='PC01_APLICACION14_guard';life='PC01_LIBRE24_'+a.case;s.fork(parent,life,kind='CANDIDATE');schedule=[[5,2],[-3,4],[3,6],[-5,6],[5,4],[-3,2],[3,4],[-5,2],[5,6],[-5,4],[3,2],[-3,6]];data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'trials':[],'witnesses':[],'reserved':[],'criteria_before':'Whole12dose17actualcurriculum unchanged, noRAW/clockedits. At26160nativeSEM4intercepts the confirmedX142route at57,1,20; equal-zero-load sham57,10,20. AlternativezeroloadYZpulsefrom57,0,19at26162meets thatXcarrier at26163, retaining142butredirectingXYZ; sham+9Y. Evaluate originalcurrentuses/contact/free/time/wordforms, four new-orderreserves, same-worldnativewordcommunication and a finalfreequery. Anytradeoffremainsvisible; no globalpromotionfromonehit.','additional_reserve':[[3,4],[-5,6],[5,2],[-3,6]]}
def trial(x):
    data['pre']=physical(x.world,occupation=True)
    if a.case in('guard','sham'):intervention=guard(x.world,'PC01.FREE24.INTERCEPT',[57,1 if a.case=='guard'else 10,20],26160)
    else:intervention=guard(x.world,'PC01.FREE24.DIVERT',[57,0 if a.case=='divert'else 9,19],26162,direction=(0,1,1),semantic=1,payload=0)
    data['intervention']=intervention;x.world.runtime.set_snapshot_metadata('DEE.Cognitive.System.1.1.PC01.free24',encode_metadata({'schema':'PC01.free24.v1','mode':a.case,'input':intervention,'prepared_not_acquired_strategy':True,'history':'Exactforkoftheprotected14lifeT25467; allcurrentinputsidenticalto17'}));oldrun=x.run_until
    def watched(target):
        for t in(26159,26160,26161,26162,26163,26164,26165,26166,26167,26168,26229,26230):
            if x.tick<t<=target:
                oldrun(t);data['witnesses'].append({'tick':t,'counter_region':witness(x.world,[57,1,20],3),'free_region':witness(x.world,[59,1,20],3),'free_nominal':observe(x.world,[(22-(t-25399))%67,(38+t-25399)%67,(50-(t-25399))%67]),'diverted_nominal':observe(x.world,[(57+t-26163)%67,(1+t-26163)%67,(20+t-26163)%67]),'physical':physical(x.world,occupation=True)})
        oldrun(target)
    x.run_until=watched
    for j,(k,L)in enumerate(schedule):
        data['trials'].append(pc.current_dose(x,parameter=k,load=L));x.world.runtime.set_snapshot_metadata('DEE.Cognitive.System.1.1.PC01.dose17',encode_metadata({'schema':'PC01.dose17.v1','case':'reserved','completed_episodes':j+1,'actual_curriculum':schedule,'last_tick':x.tick,'decoder':'qualifiednativeXplus2Lmaterialincrement','no_expected_words_in_state':True}))
        if j in(3,11):x.save(a.out/('T'+str(x.tick)+'_CONTINUIDAD_COMPLETA.deetsnap.gz'))
    data['old_after']={'forms':f.query(x,frame='lexical05'),'contact':e.contact_query(x,frame='contactoA'),'free':e.contact_query(x,frame='freeRepair5'),'time':e.temporal_query(x,frame='secuenciaA'),'equal':eq.query(x),'comparison_forms':e.query_words(x)}
    for k,L in data['additional_reserve']:data['reserved'].append(pc.current_dose(x,parameter=k,load=L))
    data['free_after_more']=e.contact_query(x,frame='freeRepair5');data['communication']=pc.communicate_existing_word(x,communication='PC01_free24_receiver');data['current_after_social']=pc.current_dose(x,parameter=5,load=4);data['free_final']=e.contact_query(x,frame='freeRepair5');data['contact_final']=e.contact_query(x,frame='contactoA');x.run_until=oldrun;data['post']=physical(x.world,occupation=True);data['receipts']=receipts(x.world.runtime)
    return{'tick':x.tick,'all12words':[r['SPANISH_DECODED']for r in data['trials']],'contact':data['old_after']['contact']['SPANISH_DECODED'],'free_at_original_test':data['old_after']['free']['SPANISH_DECODED'],'reserved':[r['SPANISH_DECODED']for r in data['reserved']],'free_after_more':data['free_after_more']['SPANISH_DECODED'],'B_words':data['communication']['B_WORDS_DECODED'],'current_after_social':data['current_after_social']['SPANISH_DECODED'],'free_final':data['free_final']['SPANISH_DECODED'],'contact_final':data['contact_final']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'PC01_NATIVE_BLOCKER_PROTECTION_OR_DIVERSION24',trial);(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
