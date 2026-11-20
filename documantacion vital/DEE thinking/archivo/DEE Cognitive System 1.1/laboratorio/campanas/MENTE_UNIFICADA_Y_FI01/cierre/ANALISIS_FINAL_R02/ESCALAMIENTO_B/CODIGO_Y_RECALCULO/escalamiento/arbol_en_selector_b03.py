"""B03 new P0 connection: converge away from E, then single +X arrival.

Motivation: B02 formed the correct summed datum yet its double +/-Z approach
altered the comparator's context and sometimes blocked/lost old accesses.
This revision does not delete that adverse future or edit any reference.
"""
from pathlib import Path
from arbol_en_selector_b02 import plan as previous_plan
from arbol_umbral_adquirido_b01 import internal_A_close,native_imports,memory_guard
HERE=Path(__file__).resolve().parent
REVISION='FI01.B03.remote_convergence_single_final_approach.r1'
def plan(level=8,E=(15,15,15),N=67):
    g=previous_plan(level,E,N)
    shift=lambda p:[(p[0]-2)%N,p[1],p[2]]
    for key in('raw_sources','generic_sources','nodes'):
        for s in g[key]:
            s['site']=shift(s['site'])
            if 'head'in s:s['head']=shift(s['head'])
    opened={tuple(shift(p))for p in g['opened']}
    C=[(E[0]-3)%N,E[1],E[2]];D=[(E[0]-1)%N,E[1],E[2]]
    g['generic_sources'].append({'id':'remote_root.constant_exit_X','site':[(C[0]-1)%N,C[1],C[2]],'direction':[1,0,0],'injection_tick_relative':35,'payload':0})
    opened.update(tuple((C[0]+dx)%N if i==0 else C[i]for i in range(3))for dx in(-1,0,1,2))
    g.update(revision=REVISION,opened=list(map(list,sorted(opened))),datum_site=D,remote_aggregate_site=C,datum_relative_tick=38,
      input_to_datum_ticks=g['input_to_datum_ticks']+2,fixed_final_approaches=[[1,0,0]],
      new_P0_resource='One fixed zero-load +X arrival at C=E−3X at root+36, same for all data. Native reducer combines two root products plus it, then transports to E−X.',
      caveat='One new connection, not validated merely by this plan. Reference and old memory impacts are measured; no clearance based on state=0.')
    return g
def enqueue(adapter,components,*,level=8,E=(15,15,15),leaf_tick=None,close_path=None,prefix='FI01.B03'):
    authorization=internal_A_close(Path(close_path)if close_path else HERE.parent/'CIERRE_INTERNO_A.json')
    ni=native_imports();body=ni[-2];g=plan(level,E,int(adapter.world.runtime.dimension))
    if len(components)!=level or any(type(v)is not int or not 0<=v<=32 for v in components):raise ValueError('One actual raw0..32 per component')
    leaf=adapter.tick+2 if leaf_tick is None else leaf_tick
    if leaf<=adapter.tick:raise ValueError('Future legal inputs required')
    root=leaf-g['raw_relative_tick'];requests=[]
    for s in g['raw_sources']:requests.append(body.send(adapter,prefix+'.'+s['id'],s['site'],s['direction'],root+s['injection_tick_relative'],components[s['component_index']]))
    for s in g['generic_sources']:requests.append(body.send(adapter,prefix+'.'+s['id'],s['site'],s['direction'],root+s['injection_tick_relative'],0))
    memory_guard()
    return {'revision':REVISION,'authorization':authorization,'geometry':g,'leaf_tick':leaf,'root_tick':root,'datum_tick':root+38,'requests':requests,'raw_components':components,
      'host_assistance':'Fixed raw codec and generic resources only. No summed input, selected bank, expected action, field write or fallback.'}
