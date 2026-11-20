"""Two physically separated candidates after an actual failed main free reader."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical,moore27
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
base={'x18':[18,34,54],'x36':[36,34,54]}[a.case];s=Store(a.system);parent='ES01_MAIN_02';life='ES01_CONTACT_ACCESS5_'+a.case;s.fork(parent,life,kind='CANDIDATE')
data={'case':a.case,'life':life,'parent':s.record(parent),'base':base,'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'queries':[]}
def trial(x):
 e.contact_prepare(x,frame='freeRepair5',base=base);data['teaching']=e.contact_teach(x,frame='freeRepair5',present=False)
 for j in range(6):
  row=e.contact_query(x,frame='freeRepair5');row['round']=j;row['physical']=physical(x.world,occupation=True);row['neighborhoods']={k:moore27(x.world,b['hub'])for k,b in e.prepare(x)['contact_frames']['freeRepair5']['banks'].items()};data['queries'].append(row)
 data['retained_contact']=e.contact_query(x,frame='contactoA');data['old_words']=e.query_words(x);data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'free_responses':[r['SPANISH_DECODED']for r in data['queries']],'old_contact':data['retained_contact']['SPANISH_DECODED'],'old_words':data['old_words']['FORMAS_ACCESIBLES']}
data['commit']=s.mutate(life,'EF01_CONTACT_ACCESS_SEPARATION_R5',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(data['commit']['result'],ensure_ascii=False))
