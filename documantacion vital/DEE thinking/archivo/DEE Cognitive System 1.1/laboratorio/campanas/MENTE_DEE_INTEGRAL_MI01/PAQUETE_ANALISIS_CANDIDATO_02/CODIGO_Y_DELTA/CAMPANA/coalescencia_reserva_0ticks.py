"""Inspect the missing intermediate datum, not only its later empty reader."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades.observador_causal_retrospectivo_01 import Snapshot
target=[25,56,41];frames=[]
for t in(25007,25008,25009,25010):
    p=E/('MI01_ASOCIACION_FIJADA_473.T'+str(t)+'.DIAGNOSTICO_NO_OPERATIVO.deetsnap.gz');x=Snapshot(p);incoming=[];allcontext=[]
    for dx in(-1,0,1):
        for dy in(-1,0,1):
            for dz in(-1,0,1):
                if not any((dx,dy,dz)):continue
                site=[(target[0]+dx)%67,(target[1]+dy)%67,(target[2]+dz)%67];v=x.observation(site)
                if v['raw']!='0':allcontext.append(v)
                if v['raw']!='0'and v['direction']==[-dx,-dy,-dz]:incoming.append(v)
    frames.append({'tick':t,'target':x.observation(target),'incoming_geometric_dependencies':incoming,'context_nonzero':allcontext,'snapshot':str(p.relative_to(R)),'snapshot_sha256':x.encoded_sha256})
out={'native_ticks':0,'target':target,'frames':frames,'scope':'Candidates follow the complete stored pre/post state; multiple ancestors retained. No unique past is inferred from the last state or equal load.'};atomic_json(E/'COALESCENCIA_RESERVA_475_0TICKS.json',out);print(json.dumps(out,ensure_ascii=False))
