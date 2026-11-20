"""Matched continuation and first causal departure of the free-flight signal."""
from pathlib import Path
from types import SimpleNamespace
import argparse,sys,json,gzip,tempfile,shutil
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
from app.lives import Store
from app.native_tools import physical,observe
from app.process_control import protect_current
from capacidades import paisaje_causal_01 as pc,espanol_funcional_01 as e,ensenanza_lexica_03 as f,igualdad_fisica_03 as eq
from dee_thinking.persistence import encode_metadata
from instrumentos_pc01 import witness,frame,receipts,sha
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='PC01_APLICACION14_guard';life='PC01_FREE19_'+a.case;s.fork(parent,life,kind='DIAGNOSTIC_COPY');schedule=[[5,2],[-3,4],[3,6],[-5,6],[5,4],[-3,2],[3,4],[-5,2],[5,6],[-5,4],[3,2],[-3,6]];data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'trials':[],'criteria_before':'Investigate free-reader loss observed after dose17, never infer forgetting from disappearance of one predicted route. Same complete parent. Actual-dose versus passive control, and same actual-dose with final lexical/contact probes selectively omitted at the exact original calendar. Replaytrace must match original17RAW/clocks. All altered assay doses are diagnostic controls, not improved learning methods that simply forbid questions.','fixed_calendar':{'last_current_scene':28630,'final_word_assays_end':28697,'contact_query_tick':28749,'free_query_tick':28816}}
def nominal(t):return[(22-(t-25399))%67,(38+t-25399)%67,(50-(t-25399))%67]
def trial(x):
    data['pre']=physical(x.world,occupation=True);data['initial_source']=observe(x.world,nominal(x.tick));oldrun=x.run_until;first=None
    def watched(target):
        nonlocal first
        while x.tick<target and first is None:
            t=x.tick;site=nominal(t);dest=nominal(t+1);source=observe(x.world,site);pre_rt=x.world.runtime.fork();oldrun(t+1);post=observe(x.world,dest)
            if not e.valid(post,(-1,1,-1)):
                pre=SimpleNamespace(runtime=pre_rt);first={'pre_tick':t,'post_tick':x.tick,'source_pre':source,'nominal_destination':dest,'post':post,'pre_radius3':witness(pre,dest,3),'post_radius3':witness(x.world,dest,3),'pre_global':frame(pre),'post_global':frame(x.world)}
                with tempfile.TemporaryDirectory(prefix='pc01-free-pre-')as tmp:
                    p=Path(tmp)/'world.deetsnap';pre_rt.save_snapshot(str(p));z=a.out/'PRE_SNAPSHOT_NATIVE_DIAGNOSTIC_ONLY.deetsnap.gz'
                    with p.open('rb')as src,gzip.open(z,'wb')as dst:shutil.copyfileobj(src,dst)
                    first['native_pre_snapshot']={'file':z.name,'sha256':sha(z),'scope':'Complete native runtime+queue; Pythonlegacy session bookkeeping is not refreshed in this diagnostic copy. NOT advertisedasacontinuablefullE1snapshot.'}
                x.save(a.out/'POST_FALLO_COMPLETO_E1.deetsnap.gz')
        oldrun(target)
    if a.case=='trace_events':x.run_until=watched
    if a.case!='passive_common':
        for j,(k,L)in enumerate(schedule):
            data['trials'].append(pc.current_dose(x,parameter=k,load=L));x.world.runtime.set_snapshot_metadata('DEE.Cognitive.System.1.1.PC01.dose17',encode_metadata({'schema':'PC01.dose17.v1','case':'reserved','completed_episodes':j+1,'actual_curriculum':schedule,'last_tick':x.tick,'decoder':'qualifiednativeXplus2Lmaterialincrement','no_expected_words_in_state':True}))
    else:x.run_until(28630)
    data['before_assays']=physical(x.world,occupation=True)
    if a.case in('events_no_word_assays','events_only_final_free'):x.run_until(28697)
    else:data['forms']=f.query(x,frame='lexical05')
    if a.case in('events_no_contact_assay','events_only_final_free'):x.run_until(28749)
    else:data['contact']=e.contact_query(x,frame='contactoA')
    data['free']=e.contact_query(x,frame='freeRepair5');data['time']=e.temporal_query(x,frame='secuenciaA');data['equal']=eq.query(x);data['comparison_forms']=e.query_words(x);data['first_nominal_departure']=first;x.run_until=oldrun;data['post']=physical(x.world,occupation=True);data['receipts']=receipts(x.world.runtime)
    return{'tick':x.tick,'first_departure':None if first is None else first['post_tick'],'free':data['free']['SPANISH_DECODED'],'contact':data.get('contact',{}).get('SPANISH_DECODED'),'current_words':[r['SPANISH_DECODED']for r in data['trials']]}
data['commit']=s.mutate(life,'PC01_FREE_ROUTE_VS_NEW_EVENTS_AND_ASSAY_DOSE19',trial)
if a.case=='trace_events':
    ref=s.record('PC01_DOSIS17_reserved')['physical'];data['replay_equivalence']={k:data['post'][k]==ref[k]for k in('tick','RAW_sha256','clocks_sha256')}
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
