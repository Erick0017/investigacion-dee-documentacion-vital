"""First actual continuation, no reconstruction of the official system."""
from pathlib import Path
import argparse,json,sys,time,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
sys.path.insert(0,str(a.system));from app.lives import Store
from app.native_tools import identity,physical,observe,moore27
from app.process_control import protect_current
protect_current(output=a.out/'RECURSOS.json')
import importlib.util
spec=importlib.util.spec_from_file_location('ef_bridge',a.system/'capacidades/puente_adquirible.py');bridge=importlib.util.module_from_spec(spec);spec.loader.exec_module(bridge)
a.out.mkdir(parents=True,exist_ok=False)
s=Store(a.system);original=s.record();assert original['life_id']=='E1_SOCIAL_11' and original['physical']['tick']==3154
s.fork(original['life_id'],'ES01_MAIN_R0',kind='CANDIDATE')
data={'case_id':'ES01_P00','kind':'NATIVE_CONTINUATION_BASELINE_NOT_NEW_SPANISH_LEARNING','engine':identity(a.system),'original':original,'events':[]}
def trial(x):
    data['pre']=physical(x.world,occupation=True)
    data['social']=bridge.read_transformed(x.world,3194,axis=-1,payload=7)
    x.quantity.present_object(81,round_index=47)
    x.quantity.input('quantity.reader',7,3218,True)
    x.two_memory.input('quantity.reader',7,3220,True)
    x.run_until(3219)
    data['quantity']={'tick':x.tick,'center':observe(x.world,x.quantity.geometry['center']),'neighborhood':moore27(x.world,x.quantity.geometry['center'])}
    x.run_until(3221)
    data['old_two']={'tick':x.tick,'center':observe(x.world,x.two_memory.geometry['center']),'neighborhood':moore27(x.world,x.two_memory.geometry['center'])}
    data['receipts']=x.receipts()
    data['post']=physical(x.world,occupation=True)
    return {'events':'prior social access, actual new object81 vs acquired reference78, old R36/O16','post':data['post']}
data['committed']=s.mutate('ES01_MAIN_R0','EF01_BASELINE',trial)
data['parent_unchanged']=s.record(original['life_id'])['snapshot_sha256']==original['snapshot_sha256']
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'case':data['case_id'],'life':'ES01_MAIN_R0','tick':data['post']['tick'],'quantity':data['quantity']['center'],'old_two':data['old_two']['center'],'parent_unchanged':data['parent_unchanged']},ensure_ascii=False))

