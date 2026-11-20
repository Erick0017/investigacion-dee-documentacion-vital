"""Apply mapped current-event interference on a prospective late-life fork.

The actual +1 A/B encounter worked but its YZ6 product met -XYZ433 at
T36463. Fixed native interception/diversion before that encounter is P0;
new word binding and use still have to be produced by the native history.
"""
from pathlib import Path
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
from app.lives import Store
from app.native_tools import physical
from app.process_control import protect_current
from capacidades import paisaje_causal_01 as pc,espanol_funcional_01 as e,ensenanza_lexica_03 as f
from instrumentos_pc01 import guard,witness,receipts,sha
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='ES01_LATE_ACCESS29_passive';life='PC01_NUEVO27_'+a.case;s.fork(parent,life,kind='CANDIDATE');data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'reserved':[],'criteria_before':'Mappedactual+1eventinterferenceat36463. FixednativeSEM4guard46,56,14beforearrivalat36461, orzero-loadX-Z? exactdeclaredpulse(1,-1,1)from45,57,13at36460toyield+Z433; +9Yshams. Pairednew+1wordlessonatphase8load3followedbyfirstrecallandheldout+1load5; oldcontexts3,-3,5,-5actualpresentedtoallphases. No hiddenrepairor future-basedselection; all armsretainfailures. Omittedwordcuecontrol testsnativeassociation, notawordlist.','schedule':[[1,5],[3,3],[-3,5],[5,5],[-5,3],[1,3],[1,5]]}
def trial(x):
    data['pre']=physical(x.world,occupation=True);start=e.tick_at_or_after(x.tick,phase=8,lead=5)
    if a.case in('guard','guard_sham','no_word_cue'):data['intervention']=guard(x.world,'PC01.EVENT27.GUARD',[46,65 if a.case=='guard_sham'else 56,14],start-2)
    else:data['intervention']=guard(x.world,'PC01.EVENT27.DIVERT',[45,66 if a.case=='divert_sham'else 57,13],start+4,direction=(1,-1,1),semantic=1,payload=0)
    oldrun=x.run_until;data['witnesses']=[]
    def watch(target):
        for t in(start+4,start+5,start+6,start+7,start+8,start+12,start+13):
            if x.tick<t<=target:oldrun(t);data['witnesses'].append({'tick':x.tick,'intercept':witness(x.world,[46,56,14],3),'original_collision':witness(x.world,[44,58,16],3)})
        oldrun(target)
    x.run_until=watch;data['lesson']=f.teach(x,frame='lexical05',parameter=1,word='cerca',phase_shift=8,load=3,signal=a.case!='no_word_cue');x.run_until=oldrun;x.save(a.out/'DESPUES_NUEVA_ENSENANZA_COMPLETA.deetsnap.gz');data['first_recall']=f.query(x,frame='lexical05',phase=(start+13)%67)
    for k,L in data['schedule']:data['reserved'].append(pc.current_dose(x,parameter=k,load=L))
    data['old_after']={'less':e.context(x,value=67,method='B'),'more':e.context(x,value=120,method='B'),'contact':e.contact_query(x,frame='contactoA'),'free':e.contact_query(x,frame='freeLate27'),'time':e.temporal_query(x,frame='secuenciaA')};data['post']=physical(x.world,occupation=True);data['receipts']=receipts(x.world.runtime)
    return{'tick':x.tick,'new_lesson_d1':data['lesson']['ENTE']['post_signal']['d1'],'responses':[r['SPANISH_DECODED']for r in data['reserved']],'less':data['old_after']['less']['TRADUCCION']['SPANISH_DECODED'],'more':data['old_after']['more']['TRADUCCION']['SPANISH_DECODED'],'contact':data['old_after']['contact']['SPANISH_DECODED'],'free':data['old_after']['free']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'PC01_NATIVE_EVENT_ROUTE_INTERVENTION_BEFORE_NEW_LESSON27',trial);(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
