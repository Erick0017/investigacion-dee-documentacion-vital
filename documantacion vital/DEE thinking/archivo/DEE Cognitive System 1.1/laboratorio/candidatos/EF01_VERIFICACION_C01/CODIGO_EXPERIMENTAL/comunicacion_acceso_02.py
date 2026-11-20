"""One receiver-route diagnostic and two declared distance revisions."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
source,distance,trace={'free_trace5':('freeRepair5',5,True),'free_distance7':('freeRepair5',7,False),'free_distance9':('freeRepair5',9,False),'toca_distance7':('contactoA',7,False)}[a.case]
s=Store(a.system);parent='ES01_MAIN_03';life='ES01_SOCIAL_ACCESS2_'+a.case;s.fork(parent,life,kind='DIAGNOSTIC_COPY'if trace else'CANDIDATE')
data={'case':a.case,'life':life,'parent':s.record(parent),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
def trial(x):
 data['transfer']=e.contact_social(x,source_frame=source,communication='socialAccess2',distance=distance,trace_receiver=trace)
 data['later']=e.contact_social_query(x,communication='socialAccess2');data['use']=e.contact_social_query(x,communication='socialAccess2',use=True)
 data['words']=e.query_words(x);data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'return':data['transfer']['SPANISH_DECODED'],'later':data['later']['SPANISH_DECODED'],'use':data['use']['SPANISH_DECODED'],'words':data['words']['FORMAS_ACCESIBLES']}
data['commit']=s.mutate(life,'EF01_SOCIAL_B_ROUTE_DIAGNOSTIC_AND_DISTANCE_REVISION',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
