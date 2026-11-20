"""Locate the later bound revealed by28, not repeat the whole campaign."""
from pathlib import Path
from types import SimpleNamespace
import argparse,sys,json,gzip,tempfile,shutil
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
from app.lives import Store
from app.native_tools import physical,observe
from app.process_control import protect_current
from capacidades import paisaje_causal_01 as pc,espanol_funcional_01 as e
from instrumentos_pc01 import receipts,sha,witness,frame
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='PC01_INTEGRACION25_paired_guard';life='PC01_SEGUNDO32_'+a.case;s.fork(parent,life,kind='DIAGNOSTIC_COPY');data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'scope':'Onlythefirst536tickblockof28andmatchedpassivecontinuation. Technicalreplayusedtodiagnosenewlimit, notindependentcapacityreplication. Allnewinputslogged, nativeprecopykeptonlyatfirstdeparture.'}
def nominal(t):return[(22-(t-30491))%67,(38+t-30491)%67,(50-(t-30491))%67]
def trial(x):
    data['pre']=physical(x.world,occupation=True);data['source_initial']=observe(x.world,nominal(x.tick));oldrun=x.run_until;first=None
    def watched(target):
        nonlocal first
        while x.tick<target and first is None:
            t=x.tick;pre_rt=x.world.runtime.fork();source=observe(x.world,nominal(t));oldrun(t+1);post=observe(x.world,nominal(t+1))
            if not e.valid(post,(-1,1,-1)):
                pre=SimpleNamespace(runtime=pre_rt);first={'pre_tick':t,'post_tick':x.tick,'source_pre':source,'destination':nominal(t+1),'post':post,'pre_global':frame(pre),'post_global':frame(x.world),'pre_radius3':witness(pre,nominal(t+1),3),'post_radius3':witness(x.world,nominal(t+1),3)}
                with tempfile.TemporaryDirectory(prefix='pc01-second32-')as tmp:
                    p=Path(tmp)/'world.deetsnap';pre_rt.save_snapshot(str(p));z=a.out/'PRE_NATIVE_DIAGNOSTIC_ONLY.deetsnap.gz'
                    with p.open('rb')as src,gzip.open(z,'wb')as dst:shutil.copyfileobj(src,dst)
                    first['native_pre']={'file':z.name,'sha256':sha(z),'scope':'CompletenativeRTincludingqueue; not a refreshedlegacyPythonsessionexport. Diagnostic only.'}
        oldrun(target)
    x.run_until=watched
    if a.case=='full':data['magnitude']=e.context(x,value=61,method='B');data['spatial']=pc.current_dose(x,parameter=5,load=2)
    x.run_until(33119);x.run_until=oldrun;data['first_departure']=first;data['post']=physical(x.world,occupation=True);data['receipts']=receipts(x.world.runtime)
    return{'tick':x.tick,'initial_free':data['source_initial'],'first_departure':None if first is None else first['post_tick'],'native_free_at_end':observe(x.world,nominal(x.tick))}
data['commit']=s.mutate(life,'PC01_FIRST_BLOCK28_REPLAY_AND_PASSIVE_CAUSE32',trial)
if a.case=='full':
    ref=json.loads((a.out.parent.parent/'CONTINUIDAD_CARGA_28/intermediate_assays/PRIMARIOS.json').read_bytes())['blocks'][0]['physical'];data['replay_equivalence']={k:data['post'][k]==ref[k]for k in('tick','RAW_sha256','clocks_sha256')}
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'result':data['commit']['result'],'replay':data.get('replay_equivalence')},ensure_ascii=False))
