"""Bounded auxiliary reusable-reader test, not a replacement MAIN biography."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from app.lives import WorldAdapter
from capacidades import comparacion_efimera_mi02 as b
objects=[9,31,0,16,25,23,24,30,5,28,None,45,9,31,16,23]
atomic_json(E/'PROTOCOLO_EFIMERO_32.json',{'new_auxiliary_architecture':True,'reference_histories':[[32,10],[10,32],[None,None]],'current_objects':objects,'hypothesis':'An unsupported reader may become available again through native evolution while separately supported reference fields persist. Five coplanar baseline neighbours; current datum supplies sixth.','prepared_bias':2,'strict_output':'Native state>0 semantic1 direction(x,-1,-1), x=-1/0/+1. Other outputs remain out of declared cone, not corrected.','controls':['opposite reference history','no reference experience','datum omitted'],'not_MAIN_integration':True})
for case,values in[(210,(32,10)),(211,(10,32)),(212,(None,None))]:
    life='MI02_EFIMERO_'+str(case);r,g=b.recipe();sources=archive();a=WorldAdapter(d.OrganizationalWorld.create(r));p=E/(life+'.PREPARACION_T0.deetsnap.gz');a.save(p);Store().import_state(p,life,'fisica_directa',expected=sha(p));atomic_json(E/(life+'.RECETA_T0.json'),{'sources':sources,'geometry':g,'new_T0_no_trained_transplant':True})
    run(life,'EFIMERO32_ACQUIRE_'+str(case),lambda a,g=g,values=values:b.acquire(a,geometry=g,values=values))
    z=run(life,'EFIMERO32_READ_'+str(case),lambda a:b.read(a,objects=objects))
    print(json.dumps({'case':case,'classes':[(r['raw_current_observation'],r['native_class'],r['after_Q']['state'])for r in z['rows']],'memory_after':z['final']['memories']},ensure_ascii=False),flush=True)
