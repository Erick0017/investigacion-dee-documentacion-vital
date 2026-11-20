"""Selective native intervention on the observed zero-load residual encounter."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical,moore27
from app.process_control import protect_current
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_receipt
from capacidades import espanol_funcional_01 as e
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
s=Store(a.system);parent='ES01_MAIN_03';life='ES01_SOCIAL_CAUSE3_'+a.case;s.fork(parent,life,kind='DIAGNOSTIC_COPY')
data={'case':a.case,'life':life,'parent':s.record(parent),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'hypothesis_before':'AtT8645 acquired B free carrier[0,1,-1] and zero-load residual[-1,0,1] converge at[17,34,54], producing[-1,1,0]. A native guard at the residual pre-site, not the B route, should preserve the original content.'}
def trial(x):
 site=[18,34,53]if a.case=='cut_residual'else[18,34,62]
 ch=d.ChannelSpec();ch.name='EF01.DIAG.RESIDUAL3';ch.injection_site=d.Coordinate(*site);ch.direction=d.Direction(0,0,0);ch.state=1;ch.semantic=4;ch.allow_experience=True;ch.allow_probe=True
 p=d.InterfaceSpec();p.name=ch.name;p.channel=ch;x.world.declare_interface(p);r=x.world.submit(ch.name,0,8643)
 data['intervention']={'site':site,'tick':8643,'requested_id':int(r.id),'native_material_guard':True,'not_RAW_edit':True}
 data['transfer']=e.contact_social(x,source_frame='freeRepair5',communication='causeResidual3',distance=5,trace_receiver=True)
 data['later']=e.contact_social_query(x,communication='causeResidual3',use=True)
 data['intervention']['receipt']=exact_receipt(x.world.runtime.receipt(r.id));data['words']=e.query_words(x);data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'returned':data['transfer']['SPANISH_DECODED'],'later_use':data['later']['SPANISH_DECODED'],'words':data['words']['FORMAS_ACCESIBLES']}
data['commit']=s.mutate(life,'EF01_SELECTIVE_RESIDUAL_INTERVENTION',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
