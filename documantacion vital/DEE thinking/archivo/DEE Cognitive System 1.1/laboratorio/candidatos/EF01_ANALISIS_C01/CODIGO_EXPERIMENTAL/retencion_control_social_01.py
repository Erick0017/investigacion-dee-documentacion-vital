"""Matched old-social access controls; do not repair or resume stable parent."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical,moore27
from app.process_control import protect_current
from capacidades import puente_adquirible as b
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
parent={'no_new_spanish':'ES01_MAIN_R0','no_word_teaching':'ES01_STREAM_B_no_word_teaching','opposite_word_teaching':'ES01_STREAM_B_opposite_teaching'}[a.case]
s=Store(a.system);life='ES01_SOCIAL_CONTROL_'+a.case;s.fork(parent,life,kind='DIAGNOSTIC')
data={'case':a.case,'life':life,'parent':s.record(parent),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
def trial(x):
 data['pre']=physical(x.world,occupation=True);data['read']=b.read_transformed(x.world,5673,axis=-1,payload=7)
 g=b.geometry(x.world);data['neighborhoods']={f['id']:{br['id']:moore27(x.world,br['use_site'])for br in f['branches']}for f in g['forms']};data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'matched_read_tick':5673,'control':a.case}
data['commit']=s.mutate(life,'EF01_OLD_SOCIAL_MATCHED_RETENTION_CONTROL',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'case':a.case,'tick':data['post']['tick'],'read':data['read']['ENTE']},ensure_ascii=False))
