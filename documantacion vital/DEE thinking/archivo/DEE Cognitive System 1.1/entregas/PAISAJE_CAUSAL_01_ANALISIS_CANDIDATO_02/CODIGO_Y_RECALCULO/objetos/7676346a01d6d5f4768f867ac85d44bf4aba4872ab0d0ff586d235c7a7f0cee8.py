"""Use existing complete states only; no native advance or material probe."""
from pathlib import Path
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
from app.lives import Store
from app.native_tools import physical
from app.process_control import protect_current
from agenda_binaria_pc01 import queue_state
from instrumentos_pc01 import receipts,sha,frame
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);data={'source_sha256':sha(__file__),'passive_no_evolution':True,'states':{}}
names=('PC01_APLICACION14_guard','PC01_FREE19_counter_events','PC01_FREE19_counter_passive')if a.case=='free21'else('ES01_MAIN_04','ES01_MAIN_05','ES01_LEXICAL5_source_guards_strict','ES01_LONG7_D_no_material_queries','PC01_ORIGEN01_reference_trace','PC01_ORIGEN01_near_trace','PC01_INFLUENCIA04_early','PC01_INFLUENCIA04_long','PC01_APLICACION14_guard')
for life in names:
    rec,x=s.load(life);before=physical(x.world);queue=queue_state(x.world.runtime);after=physical(x.world);data['states'][life]={'record':rec,'queue_state':queue,'receipts':receipts(x.world.runtime),'physical_unchanged':before==after}
    if a.case=='free21':data['states'][life]['full_sparse_frame']=frame(x.world)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({k:{'tick':v['queue_state']['tick'],'pending':len(v['queue_state']['pending']),'unchanged':v['physical_unchanged']}for k,v in data['states'].items()}))
