"""Existing validated bare repertoire: sparse perturbation versus no probe."""
from pathlib import Path
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
from app.lives import Store
from app.native_tools import physical,observe
from app.process_control import protect_current
from instrumentos_pc01 import Trace,guard,receipts,sha,native_digest
from dee_thinking import _native as d
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='R65_N67_VIVIDO';life='PC01_ESPECIALISTA03_'+a.case;s.fork(parent,life,kind='DIAGNOSTIC_COPY');data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'scope':'Existing bare learned physical repertoire, separate from E1. Three explicit form ports only, never65semantic concepts or endogenous source selection.'}
def trial(x):
    t=((x.tick+6+66)//67)*67;forms=[x._form(k)for k in(0,32,64)];data['pre']=physical(x.world,occupation=True);data['ports']=forms;data['perturbations']=[]
    for f in forms:
        p=next(p for p in x.world.interfaces if p.name==f['ports']['read.plus']);site=p.channel.injection_site;q=[(site.x+9)%67,site.y,site.z];ch=d.ChannelSpec();ch.name='PC01.SPECIAL.'+f['id'];ch.injection_site=d.Coordinate(*q);ch.direction=p.channel.direction;ch.state=1;ch.semantic=1;ch.allow_experience=True;ch.allow_probe=True;port=d.InterfaceSpec();port.name=ch.name;port.channel=ch;x.world.declare_interface(port)
    tr=Trace(x,a.out/'CAMPO_COMPLETO.jsonl.gz',start=t-4,end=t+2*67+4).install()
    data['pre_normalized_native']=native_digest(x.world.runtime)
    if a.case!='no_probe':
        for f in forms:
            name='PC01.SPECIAL.'+f['id']if a.case=='offroute'else f['ports']['read.plus'];r=x.session.input(name,0 if a.case=='zero'else 7,t,True);data['perturbations'].append(r)
            if a.case!='offroute':x.state['DCS_query_counts'][f['id']]+=1
    x.run_until(t+2*67+4);data['trace']=tr.close();data['before_common_test']=physical(x.world,occupation=True)
    # Assessment uses the existing protocol's declared alternating reader.
    # Which physical reader is used is logged; it is not learned attention.
    test=((x.tick+6+66)//67)*67;data['later_function']=x.query([f['id']for f in forms],test,payload=7);data['receipts']=receipts(x.world.runtime);data['post']=physical(x.world,occupation=True)
    return{'tick':x.tick,'responses':[{'form':r['form'],'direction':r['physical']['direction'],'state':r['physical']['state'],'s_reg':r['physical']['s_reg'],'query_index':r['query_index']}for r in data['later_function']['responses']]}
data['commit']=s.mutate(life,'PC01_SPECIALIZED_QUERY_CAUSAL_MAPPING03',trial);(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result']))
