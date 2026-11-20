"""Causal controls for distance7, including equal-material sham and cut."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
source,cut,sham={'free_cut7':('freeRepair5',True,False),'free_sham7':('freeRepair5',False,True),'toca_cut7':('contactoA',True,False),'toca_sham7':('contactoA',False,True)}[a.case]
s=Store(a.system);parent='ES01_MAIN_03';life='ES01_SOCIAL_RESERVE4_'+a.case;s.fork(parent,life,kind='CANDIDATE')
data={'case':a.case,'life':life,'parent':s.record(parent),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'distance_fixed_before_reserve':7}
def trial(x):
 data['transfer']=e.contact_social(x,source_frame=source,communication='reserveSocial4',distance=7,cut_message=cut,sham=sham)
 data['use']=e.contact_social_query(x,communication='reserveSocial4',use=True);data['words']=e.query_words(x);data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'return':data['transfer']['SPANISH_DECODED'],'use':data['use']['SPANISH_DECODED'],'words':data['words']['FORMAS_ACCESIBLES']}
data['commit']=s.mutate(life,'EF01_DISTANCE7_CAUSAL_RESERVES',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
