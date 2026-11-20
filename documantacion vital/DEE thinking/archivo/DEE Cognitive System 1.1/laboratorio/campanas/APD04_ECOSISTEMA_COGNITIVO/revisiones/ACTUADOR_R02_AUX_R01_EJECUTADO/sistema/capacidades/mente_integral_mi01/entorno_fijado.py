"""Finite peripheral events fixed independently of participant responses."""
from capacidades.integracion_situada_01 import ic_native_core as n
from . import saved,put

def prepare(a,*,name,start_tick):
    if start_tick<a.tick+4:raise ValueError('Future peripheral events only')
    cfg=saved(a);scenes=cfg.setdefault('peripheral_scenes',{})
    if name in scenes:raise ValueError('Already lived environmental preparation')
    S=n.configuration(a)['center'];site=n.move(S,(1,-1,1),12);rr=[]
    for i,(dt,payload,sign)in enumerate([(7,1,1),(10,0,-1),(19,3,1),(31,7,-1),(89,1,1),(94,3,-1),(147,0,1),(209,7,-1)]):
        rr.append(n.submit(a,'MI01.environment.'+name+'.'+str(i),site,(0,0,sign),start_tick+dt,payload))
    scenes[name]={'site':site,'pre':n.obs(a,site),'requests':rr,'scope':'Eight fixed peripheral normal inputs, dose22, non67relative offsets. No labels distinguish signal/noise to DEE. No source moves, overwrite, useful-input filter or post-response selection.'};put(a,cfg);return scenes[name]
