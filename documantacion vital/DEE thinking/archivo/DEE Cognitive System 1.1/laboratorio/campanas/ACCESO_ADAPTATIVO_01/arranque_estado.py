"""Single passive installed-instrument and complete-state check for AA01."""
from pathlib import Path
import argparse,json,sys,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(a.system.parent/'laboratorio/campanas/PAISAJE_CAUSAL_01'))
from app.lives import Store
from app.native_tools import identity,physical,SYSTEM_KEY
from agenda_binaria_pc01 import queue_state
from instrumentos_pc01 import native_digest
from dee_thinking.persistence import decode_metadata
ev=a.system.parent/'evidencia/campanas/ACCESO_ADAPTATIVO_01';dest=ev/'ESTADO_INICIAL.json'
if dest.exists():raise FileExistsError('Startup already recorded; inspect it rather than repeat')
s=Store(a.system);data={'identity':identity(a.system),'active':json.loads((a.system/'estado/ACTIVO.json').read_bytes()),'states':{},'no_material_probe_or_native_advance':True}
for name in('PC01_CONTINUIDAD28_far_guard','PC01_CONTINUIDAD28_far_divert','PC01_NORMALIZADO45','PC01_RETENCION40_guard','PC01_RETENCION40_divert','E1_PAISAJE_01'):
    rec,x=s.load(name);data['states'][name]={'record':rec,'full_snapshot':str(s.snapshot(rec)),'physical':physical(x.world,occupation=True),'native_digest':native_digest(x.world.runtime),'agenda':queue_state(x.world.runtime),'adapter_class':type(x).__name__,'protocol_progress':{k:v for k,v in vars(x).items()if k!='world'and isinstance(v,(dict,list,str,int,bool,type(None)))},'metadata':{k:decode_metadata(v)for k,v in dict(x.world.runtime.snapshot_metadata_entries).items()if k.startswith('DEE.Cognitive.System')}}
data['selected_main_parent']='PC01_CONTINUIDAD28_far_guard';data['selection_reason']='Broad coexisting functions with complete N67 history, before the experimental transformed reader. Separate41/45 reference does not donate learned fields.'
data['sources']=[{'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size}for path in(a.system.parent/'ADDENDUM_MANUAL_MAESTRO_EF01_PAISAJE01_EDICION_1_1.md',a.system.parent/'CONTINUIDAD_PAISAJE_CAUSAL_01.json',a.system/'contratos/PAISAJE_CAUSAL_01.json')]
dest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'selected':data['selected_main_parent'],'states':{n:{'tick':v['physical']['tick'],'N':v['physical']['N'],'pending':len(v['agenda']['pending'])}for n,v in data['states'].items()},'identity':data['identity']['native_sha256']}))
