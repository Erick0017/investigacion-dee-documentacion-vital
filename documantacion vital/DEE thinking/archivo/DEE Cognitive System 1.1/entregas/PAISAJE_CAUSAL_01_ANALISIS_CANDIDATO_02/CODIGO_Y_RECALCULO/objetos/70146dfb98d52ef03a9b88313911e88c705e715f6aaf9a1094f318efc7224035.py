"""Apply the newly localized marker loss, not a change of decoder after failure.

In38 the +1 word died at39836, before the second lesson or first probe:
XYZ11 and -XYZ120 combined at57,10,35. Protect/redirect the latter route
natively and then test the same learned code and older functions.
"""
from pathlib import Path
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
from app.lives import Store
from app.native_tools import physical
from app.process_control import protect_current
from capacidades import paisaje_causal_01 as pc,espanol_funcional_01 as e,ensenanza_lexica_03 as f
from instrumentos_pc01 import receipts,sha,guard,witness
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='PC01_CONTINUIDAD28_far_guard';life='PC01_RETENCION40_'+a.case;s.fork(parent,life,kind='CANDIDATE');data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'reserved':[],'witnesses':[],'criteria_before':'Afterfirstlossin38,boundednewpreparationrevision. SEM4zeroat60,7,32boundary39824orzero-load(1,-1,1)pulsefrom59,8,31boundary39832targetsopposing120streamat39833. Correspondingshams+9Y. Same+1cercaordinarylessonphase12load3; no-wordcontrolusesidenticalevent/diversionbutomitsdocentmarker. No secondlesson; matchedcalendar39886thenfirstrecall. Frozenfixeddecoder and dose2L; sixnew+1questionsinterleavedwitholdfourcontexts. Untaught-1keptnegative/indeterminate,notcountedasretentionloss.','schedule':[[1,5],[3,4],[-3,6],[5,2],[-5,4],[1,2],[3,6],[-3,2],[5,4],[-5,6],[1,4],[1,6]]}
def trial(x):
    data['pre']=physical(x.world,occupation=True)
    if a.case in('guard','guard_sham'):data['intervention']=guard(x.world,'PC01.NEW40.GUARD',[60,16 if a.case=='guard_sham'else 7,32],39824)
    else:data['intervention']=guard(x.world,'PC01.NEW40.DIVERT',[59,17 if a.case=='divert_sham'else 8,31],39832,direction=(1,-1,1),semantic=1,payload=0)
    oldrun=x.run_until
    def watched(target):
        for t in(39823,39824,39832,39833,39834,39835,39836,39837,39890):
            if x.tick<t<=target:oldrun(t);data['witnesses'].append({'tick':t,'counter':witness(x.world,[60,7,32],3),'old_collision':witness(x.world,[57,10,35],3)})
        oldrun(target)
    x.run_until=watched;data['lesson']=f.teach(x,frame='lexical05',parameter=1,word='cerca',phase_shift=12,load=3,signal=a.case!='no_word_cue');x.run_until(39886);x.save(a.out/'ASOCIACION_Y_PRIMER_RETORNO_COMPLETO.deetsnap.gz');data['first_recall']=f.query(x,frame='lexical05')
    for k,L in data['schedule']:data['reserved'].append(pc.current_dose(x,parameter=k,load=L))
    data['untaught_minus1']=pc.current_dose(x,parameter=-1,load=5)
    data['old_after']={'less':e.context(x,value=64,method='B'),'more':e.context(x,value=117,method='B'),'contact':e.contact_query(x,frame='contactoA'),'free':e.contact_query(x,frame='freeRepair5'),'time':e.temporal_query(x,frame='secuenciaA')};x.run_until=oldrun;data['post']=physical(x.world,occupation=True);data['receipts']=receipts(x.world.runtime)
    return{'tick':x.tick,'lesson':data['lesson']['ENTE']['post_signal']['d1'],'responses':[r['SPANISH_DECODED']for r in data['reserved']],'untaught_minus1':data['untaught_minus1']['SPANISH_DECODED'],'less':data['old_after']['less']['TRADUCCION']['SPANISH_DECODED'],'more':data['old_after']['more']['TRADUCCION']['SPANISH_DECODED'],'contact':data['old_after']['contact']['SPANISH_DECODED'],'free':data['old_after']['free']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'PC01_CONSERVE_NEW_WORD_AFTER_CAUSAL_INTERFERENCE40',trial);(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
