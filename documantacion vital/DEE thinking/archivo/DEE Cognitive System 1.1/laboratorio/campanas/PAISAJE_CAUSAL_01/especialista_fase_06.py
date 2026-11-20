"""Protocol-correct contrast to the deliberately off-phase sparse panel03."""
from pathlib import Path
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
from app.lives import Store
from app.native_tools import physical
from app.process_control import protect_current
from instrumentos_pc01 import Trace,receipts,sha
from dee_thinking import _native as d
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='R65_N67_VIVIDO';life='PC01_ESPECIALISTA06_'+a.case;s.fork(parent,life,kind='DIAGNOSTIC_COPY');data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'criteria_before':'OnlyF00,F01,F06 from the historical first group, correct query boundaryT2847, then the same phase after three67tickreturns. Existing alternating reader is declared host protocol, not an acquired access policy. Same first-group phase, signs+/-/+ and payload are audited after evolution. Panel03phase0wasoutside this historical query calendar, not evidence of forgetting.'}
def trial(x):
    forms=[x._form(k)for k in(0,1,6)];names=[f['id']for f in forms];data['pre']=physical(x.world,occupation=True);data['forms']=forms
    for f in forms:
        counter=x.state['DCS_query_counts'][f['id']];role='read.plus'if counter%2==0 else'read.minus';p=next(p for p in x.world.interfaces if p.name==f['ports'][role]);site=p.channel.injection_site;ch=d.ChannelSpec();ch.name='PC01.SPECIAL06.'+f['id'];ch.injection_site=d.Coordinate((site.x+9)%67,site.y,site.z);ch.direction=p.channel.direction;ch.state=1;ch.semantic=1;ch.allow_experience=True;ch.allow_probe=True;port=d.InterfaceSpec();port.name=ch.name;port.channel=ch;x.world.declare_interface(port)
    tr=Trace(x,a.out/'CAMPO_COMPLETO.jsonl.gz',start=2843,end=2987).install()
    if a.case in('probe7','zero'):data['first_query']=x.query(names,2847,payload=0 if a.case=='zero'else 7)
    elif a.case=='offroute':
        data['sham']=[x.session.input('PC01.SPECIAL06.'+f['id'],7,2847,True)for f in forms];x.run_until(2850)
    elif a.case=='no_probe':x.run_until(2850)
    else:raise ValueError('Declared four conditions only')
    x.run_until(2987);data['trace']=tr.close();data['before_later']=physical(x.world,occupation=True);data['later_query']=x.query(names,3048,payload=9);data['receipts']=receipts(x.world.runtime);data['post']=physical(x.world,occupation=True)
    return{'tick':x.tick,'responses':[{'form':r['form'],'query_index':r['query_index'],'direction':r['physical']['direction'],'state':r['physical']['state'],'s_reg':r['physical']['s_reg'],'receipt':r['receipt']}for r in data['later_query']['responses']]}
data['commit']=s.mutate(life,'PC01_SPECIALIZED_VALIDATED_PHASE_CONTRAST06',trial);(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result']))
