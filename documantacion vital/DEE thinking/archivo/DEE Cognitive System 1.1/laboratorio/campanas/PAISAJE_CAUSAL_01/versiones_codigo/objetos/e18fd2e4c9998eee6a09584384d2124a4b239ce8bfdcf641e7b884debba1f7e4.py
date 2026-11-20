"""Find the new free-route failure without treating a successful panel as forever.

Exact diagnostic replay of25, not a new acquisition replicate. Passive
tracking starts at the complete successful24parent; only on first departure
are global and radius3 witnesses retained. No intervention in this world.
"""
from pathlib import Path
from types import SimpleNamespace
import argparse,sys,json,gzip,tempfile,shutil
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
from app.lives import Store
from app.native_tools import physical,observe
from app.process_control import protect_current
from capacidades import paisaje_causal_01 as pc,espanol_funcional_01 as e,recuperacion_magnitud_26 as m,ensenanza_lexica_03 as f,igualdad_fisica_03 as eq
from instrumentos_pc01 import receipts,sha,witness,frame
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='PC01_LIBRE24_divert';life='PC01_LIMITE30_'+a.case;s.fork(parent,life,kind='DIAGNOSTIC_COPY');data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'magnitude':[],'spatial':[],'old':[],'scope':'Technicalreproduction25toidentifynewfirstdeparture, notanotherindependentlearner or hiddenrollback. Original25and28futuresremainunchanged.'}
def nominal(t):return[(22-(t-30491))%67,(38+t-30491)%67,(50-(t-30491))%67]
def trial(x):
    data['pre']=physical(x.world,occupation=True);data['source_initial']=observe(x.world,nominal(x.tick));oldrun=x.run_until;first=None
    def watched(target):
        nonlocal first
        while x.tick<target and first is None:
            t=x.tick;pre_rt=x.world.runtime.fork();source=observe(x.world,nominal(t));oldrun(t+1);post=observe(x.world,nominal(t+1))
            if not e.valid(post,(-1,1,-1)):
                pre=SimpleNamespace(runtime=pre_rt);first={'pre_tick':t,'post_tick':x.tick,'source_pre':source,'destination':nominal(t+1),'post':post,'pre_global':frame(pre),'post_global':frame(x.world),'pre_radius3':witness(pre,nominal(t+1),3),'post_radius3':witness(x.world,nominal(t+1),3)}
                with tempfile.TemporaryDirectory(prefix='pc01-limit30-')as tmp:
                    p=Path(tmp)/'world.deetsnap';pre_rt.save_snapshot(str(p));z=a.out/'PRE_NATIVE_DIAGNOSTIC_ONLY.deetsnap.gz'
                    with p.open('rb')as src,gzip.open(z,'wb')as dst:shutil.copyfileobj(src,dst)
                    first['native_pre']={'file':z.name,'sha256':sha(z),'scope':'CompletenativeRTincludingqueue; not refreshedlegacyPythonprotocolbookkeeping. Diagnostic, nota normalcontinuableE1export.'}
        oldrun(target)
    x.run_until=watched;data['new_experience']=m.reacquire(x,value=86,teaching='paired',guard='on_route')
    for v in(61,119):data['magnitude'].append({'value':v,'result':e.context(x,value=v,method='B')})
    for k,L in((-3,4),(5,6)):data['spatial'].append(pc.current_dose(x,parameter=k,load=L))
    data['old'].append({'contact':e.contact_query(x,frame='contactoA'),'free':e.contact_query(x,frame='freeRepair5')})
    for v in(70,120):data['magnitude'].append({'value':v,'result':e.context(x,value=v,method='B')})
    data['communication']=pc.communicate_existing_word(x,communication='PC01_integration25_receiver')
    for k,L in((3,2),(-5,4)):data['spatial'].append(pc.current_dose(x,parameter=k,load=L))
    for v in(64,117):data['magnitude'].append({'value':v,'result':e.context(x,value=v,method='B')})
    data['old'].append({'contact':e.contact_query(x,frame='contactoA'),'free':e.contact_query(x,frame='freeRepair5')});data['time_form']=e.temporal_query(x,frame='secuenciaA');data['equal_form']=eq.query(x);data['word_forms']=f.query(x,frame='lexical05');x.run_until=oldrun;data['first_departure']=first;data['post']=physical(x.world,occupation=True);data['receipts']=receipts(x.world.runtime)
    return{'tick':x.tick,'initial_free':data['source_initial'],'first_departure':None if first is None else first['post_tick'],'late_free_words':data['old'][-1]['free']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'PC01_PASSIVE_REPLAY_OF25_NEW_FREE_LIMIT30',trial);ref=s.record('PC01_INTEGRACION25_paired_guard')['physical'];data['replay_equivalence']={k:data['post'][k]==ref[k]for k in('tick','RAW_sha256','clocks_sha256')};(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'result':data['commit']['result'],'replay':data['replay_equivalence']},ensure_ascii=False))
