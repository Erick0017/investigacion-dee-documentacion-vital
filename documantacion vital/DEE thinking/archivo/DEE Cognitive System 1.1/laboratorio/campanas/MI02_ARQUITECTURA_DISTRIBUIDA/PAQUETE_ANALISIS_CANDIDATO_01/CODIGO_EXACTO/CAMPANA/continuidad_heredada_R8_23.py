"""R8 on a real MI01 fork, appended physical frame, no historical clearing."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from capacidades.geometria_distribuida_mi02 import return_geometry
from capacidades import arquitectura_distribuida_mi02_r8 as b
life='E1_MI02_HEREDADA_R8';checkpoint='estado/checkpoints/E1_MI01_MAIN.T24752.bec543681d6d.deetsnap.gz'
assert sha(S/checkpoint)=='23114e8445f2b651ce9dfd53011b9749b357e1fa9a4191e87982b0fafec081a4'
fork('E1_MI01_MAIN',life,checkpoint)
def mount(a):
    n=int(a.world.runtime.dimension);C=[40,40,10];g=return_geometry(n,C);opened=g['opened'];anchors=g['anchors'];pinned=g['pinned'];pre=[];requests=[];t=a.tick+2
    positions=[[(C[0]+x)%n,(C[1]+y)%n,(C[2]+z)%n]for x in range(-8,9)for y in range(-8,9)for z in range(-8,9)]
    nonzero=[obs(a,p)for p in positions if int(obs(a,p)['raw'])]
    if nonzero:raise ValueError('Protected history inside proposed peripheral box; no clearing permitted')
    for p in positions:
        k=tuple(p)
        if k in opened and k not in anchors and k not in pinned:continue
        state=1 if k in anchors else 0;value=anchors[k][0]if state else 0;direction=anchors[k][1]if state else(0,0,0);name='MI02.A8.frame.'+'.'.join(map(str,p));ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(*p);ch.direction=d.Direction(*direction);ch.state=state;ch.semantic=4;ch.allow_experience=True;ch.allow_probe=True;it=d.InterfaceSpec();it.name=name;it.channel=ch;a.world.declare_interface(it);r=a.world.submit(name,value,t);requests.append({'id':int(r.id),'site':p,'port':name,'tick':t,'state':state,'load':value})
    a.run_until(t+1)
    return{'center':C,'nonzero_RAW_before':len(nonzero),'legal_requests':receipts(a,requests),'architecture_added_not_acquired':True,'inherited_RAW_and_clocks_not_edited':True,'integration_limit':'This tests an added native action-learning region inside a genuinely inherited world. It does not by itself show that all old MI01 knowledge is accessed by that region.'}
run(life,'HEREDADA_R8_MONTAJE23',mount)
run(life,'HEREDADA_R8_ADQUIRIR23',lambda a:b.prepare(a,center=[40,40,10]))
fork(life,'MI02_HEREDADA_R8_SIN_RETORNO23')
seq=[-1]*5+[1]*5+[-1]*5
atomic_json(E/'PROTOCOLO_HEREDADA_R8_23.json',{'exact_parent_sha256':'23114e8445f2b651ce9dfd53011b9749b357e1fa9a4191e87982b0fafec081a4','conditions':seq,'candidate':life,'control':'MI02_HEREDADA_R8_SIN_RETORNO23','question':'Can the R8 physical learning mechanism operate in an exact inherited N67 world when its local added preparation and actual native clock domain are declared?','not_claimed':'No transfer of old MI01 learned content into the new region; no full integration of all historical abilities.'})
for name,mode in[(life,'intact'),('MI02_HEREDADA_R8_SIN_RETORNO23','omit_return')]:
    z=run(name,'HEREDADA_R8_VIVIR23_'+mode,lambda a,mode=mode:b.live(a,availability=seq,mode=mode,trace=True))
    print(json.dumps({'life':name,'useful':sum(v['useful_material_action']for v in z['rows']),'opportunities':len(z['rows']),'choices':[v['physical_choice']for v in z['rows']],'final':z['final']['physical']},ensure_ascii=False),flush=True)
