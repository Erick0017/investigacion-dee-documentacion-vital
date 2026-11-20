"""Calibrate prepared directional SEM4 emission under frozen official v27."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from app.lives import WorldAdapter

def new(life,load):
    sources=archive();N=11;placements=[];opened={(x,5,5)for x in range(2,9)}
    for x in range(N):
        for y in range(N):
            for z in range(N):
                p=(x,y,z)
                if p in opened and p!=(2,5,5):continue
                q=d.InitialPlacement();q.site=d.Coordinate(*p);q.clock=0;q.raw=d.pack_record(1,load,1,0,0,4)if p==(2,5,5)else d.pack_record(0,0,0,0,0,4);q.role='Prepared directional source or inert boundary, not acquired content';placements.append(q)
    recipe=d.OrganizationRecipe.research(N,placements,0);recipe.execution=d.TickOptions(d.Backend.LAZY,1);a=WorldAdapter(d.OrganizationalWorld.create(recipe));p=E/(life+'.PREPARACION_T0.deetsnap.gz');a.save(p);Store().import_state(p,life,'fisica_directa',expected=sha(p));atomic_json(E/(life+'.CONSTRUCCION.json'),{'sources':sources,'new_untrained_T0':True,'prepared_source_load':load,'one_unchanged_native_source_no_external_packets':True})

def trial(a):
    rows=[]
    for t in range(1,26):a.run_until(t);rows.append({'tick':t,'sites':[obs(a,[x,5,5])for x in range(2,10)]})
    return{'rows':rows,'source_prepared_not_learned':True,'uses_beyond_initial_stored_packet_count':sum(v['state']>0 for r in rows for v in r['sites'][1:]),'physical':physical(a.world,occupation=True)}
for load in(0,5):
    life='MI02_EMISOR10_'+str(load);new(life,load);run(life,'EMISOR10_'+str(load),trial)
