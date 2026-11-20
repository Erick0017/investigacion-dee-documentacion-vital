"""Passive queue-inclusive comparison and explicit existing interface map."""
from pathlib import Path
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
from app.lives import Store
from app.native_tools import SYSTEM_KEY,physical
from app.process_control import protect_current
from instrumentos_pc01 import native_digest,receipts,sha
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);data={'case':a.case,'read_only':True,'source_sha256':sha(__file__),'comparison':{},'worlds':{}}
for category in('reference','near'):
    hashes={}
    for mode in('trace','plain'):
        name='PC01_ORIGEN01_'+category+'_'+mode;rec,w=s.load(name);clone=w.world.runtime.fork();clone.erase_snapshot_metadata(SYSTEM_KEY);hashes[mode]=native_digest(clone)
        ports=[]
        for p in w.world.interfaces:
            c=p.channel;q=c.injection_site;v=c.direction;ports.append({'name':p.name,'site':[q.x,q.y,q.z],'direction':[v.dx,v.dy,v.dz],'state':c.state,'semantic':c.semantic})
        data['worlds'][name]={'record':rec,'all_interface_inputs':ports,'metadata':{k:v for k,v in dict(w.world.runtime.snapshot_metadata_entries).items()if k.startswith('DEE.Cognitive.System.1.1.ESPANOL')},'native_without_only_documental_life_metadata':hashes[mode],'receipts':receipts(w.world.runtime)}
    data['comparison'][category]={'same_all_native_bytes_except_explicit_life_metadata':hashes['trace']==hashes['plain'],'hashes':hashes,'normalization':'OnlySYSTEM_KEY erased on exact non-evolved runtime copies; physical arrays, input payload/queue/sequence, receipts, channels, phase, pause/execution and all other metadata retained.'}
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['comparison']))
