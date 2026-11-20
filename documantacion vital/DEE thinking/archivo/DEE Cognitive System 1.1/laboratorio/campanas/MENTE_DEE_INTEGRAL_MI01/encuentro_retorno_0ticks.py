"""Exact local pre/post context at the first reserved reply-path loss."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades.observador_causal_retrospectivo_01 import Snapshot
Rsite=[27,56,43];frames=[]
for t in range(25004,25013):
    p=E/('MI01_ASOCIACION_FIJADA_473.T'+str(t)+'.DIAGNOSTICO_NO_OPERATIVO.deetsnap.gz');x=Snapshot(p);neighbours=[]
    for dx in(-1,0,1):
        for dy in(-1,0,1):
            for dz in(-1,0,1):
                site=[(Rsite[0]+dx)%67,(Rsite[1]+dy)%67,(Rsite[2]+dz)%67];v=x.observation(site)
                if v['raw']!='0':neighbours.append({**v,'offset':[dx,dy,dz],'points_toward_R':v['direction']==[-dx,-dy,-dz]and any((dx,dy,dz))})
    frames.append({'tick':t,'target':x.observation(Rsite),'designated_incoming_data':x.observation([26,56,42]),'nonzero_context27':neighbours,'source':str(p.relative_to(R)),'source_sha256':x.encoded_sha256})
out={'native_ticks':0,'target':Rsite,'frames':frames,'scope':'Full stored worlds back each local extraction. NonzeroRAW/zero-state fields are not discarded. Candidate incoming vectors are geometric dependencies, not unique packet identities.'};atomic_json(E/'ENCUENTRO_RETORNO_474_0TICKS.json',out);print(json.dumps(frames,ensure_ascii=False))
