"""Exact MI01 past, new declared peripheral preparation, no transplanted memory."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from preparacion_fondo_inmovil_r5 import recipe
from capacidades import arquitectura_distribuida_mi02_r5 as b
life='E1_MI02_HEREDADA_A'
checkpoint='estado/checkpoints/E1_MI01_MAIN.T24752.bec543681d6d.deetsnap.gz'
assert sha(S/checkpoint)=='23114e8445f2b651ce9dfd53011b9749b357e1fa9a4191e87982b0fafec081a4'
fork('E1_MI01_MAIN',life,checkpoint)

def mount(a):
    n=int(a.world.runtime.dimension);assert n==67
    _,g=recipe();center=None;checks=[]
    for c in([40,40,10],[40,10,40],[10,40,40],[50,40,10]):
        nonzero=[]
        for x in range(-8,9):
            for y in range(-8,9):
                for z in range(-8,9):
                    p=[(c[0]+x)%n,(c[1]+y)%n,(c[2]+z)%n];v=obs(a,p)
                    if int(v['raw']):nonzero.append(v)
        checks.append({'center':c,'nonzero_RAW_count':len(nonzero)})
        if not nonzero:center=c;break
    if center is None:raise ValueError('No zeroRAW peripheral box in finite declared sites; no clearing permitted')
    openlocal={tuple(v)for v in g['open_sites']};anchors={tuple(v['site'])for v in g['material_anchors']};t=a.tick+2;rows=[]
    for x in range(17):
        for y in range(17):
            for z in range(17):
                local=(x,y,z)
                if local in openlocal or local in anchors:continue
                p=[(center[i]+local[i]-8)%n for i in range(3)]
                name='MI02.A.periphery.'+'.'.join(map(str,local));c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*p);c.direction=d.Direction(0,0,0);c.state=0;c.semantic=4;c.allow_experience=True;c.allow_probe=True;it=d.InterfaceSpec();it.name=name;it.channel=c;a.world.declare_interface(it);rr=a.world.submit(name,0,t);rows.append({'id':int(rr.id),'port':name,'site':p,'tick':t})
    a.run_until(t+1)
    return{'checks':checks,'selected_center':center,'requests':receipts(a,rows),'assistance':'New inert peripheral material installed by legal inputs only at previously zeroRAW sites. No inherited RAW/clock/learned memory is cleared. Original agenda and landscape remain elsewhere.','before_body':physical(a.world,occupation=True)}

mounted=run(life,'HEREDADA_A_MONTAJE_06',mount)
center=mounted['selected_center']
run(life,'HEREDADA_A_CUERPO_06',lambda a:b.prepare(a,center=center))
run(life,'HEREDADA_A_USOS_06',lambda a:b.live(a,availability=[-1,1,-1],trace=True))
print('Hereditary A lived full continuation preserved',flush=True)
