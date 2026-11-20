"""Second local bottleneck after the first guard; no new repair/ticks."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades.observador_causal_retrospectivo_01 import Snapshot
target=[40,30,43];frames=[]
for t in(25093,25094):
    p=E/('MI01_SEGUNDO_OBSTACULO_479.T'+str(t)+'.DIAGNOSTICO_NO_OPERATIVO.deetsnap.gz');x=Snapshot(p);incoming=[];context=[]
    for dx in(-1,0,1):
        for dy in(-1,0,1):
            for dz in(-1,0,1):
                if not any((dx,dy,dz)):continue
                v=x.observation([(target[0]+dx)%67,(target[1]+dy)%67,(target[2]+dz)%67])
                if v['raw']!='0':context.append(v)
                if v['raw']!='0'and v['direction']==[-dx,-dy,-dz]:incoming.append(v)
    frames.append({'tick':t,'target':x.observation(target),'incoming_geometric_dependencies':incoming,'context_nonzero':context,'snapshot':str(p.relative_to(R)),'snapshot_sha256':x.encoded_sha256})
pre,post=frames;vectors=[sum(v['direction'][j]for v in pre['incoming_geometric_dependencies'])for j in range(3)];payload=sum(v['s_reg']for v in pre['incoming_geometric_dependencies']);out={'native_ticks':0,'frames':frames,'directional_sum_of_recorded_incoming':vectors,'payload_sum_of_recorded_incoming':payload,'post_matches_sum_and_null_direction':post['target']['s_reg']==payload and post['target']['direction']==[0,0,0],'interpretation':'A retained scalar load150 does not by itself preserve the former private-content sign, which was directional. This is a local forward reconstruction supported by stored states, not a separately intervened proof of each second contributor or global information loss. No second repair was attempted.'};atomic_json(E/'SEGUNDO_ENCUENTRO_481_0TICKS.json',out);print(json.dumps(out,ensure_ascii=False))
