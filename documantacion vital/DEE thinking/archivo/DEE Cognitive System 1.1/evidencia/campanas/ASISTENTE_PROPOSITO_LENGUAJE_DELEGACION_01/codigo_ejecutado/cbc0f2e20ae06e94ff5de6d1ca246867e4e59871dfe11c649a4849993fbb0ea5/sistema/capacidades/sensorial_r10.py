"""ONE alternative T0 R10: remote balanced fan-in, no trained-state copying.

R9 body, law, N and feedback remain. Only additional RAW-empty corridors from
T0 are designed; four independent observations per side meet through v27.
"""
from capacidades.geometria_distribuida_mi02_r9 import unified_recipe as baseline
from capacidades.geometria_distribuida_mi02 import compile_geometry
from capacidades import arquitectura_distribuida_mi02_r8 as body
from capacidades import ente_evolucion_02_core as core
REVISION='EO02.sensorial.r10.t0.balanced_remote.v1'
def design():
    _,g=baseline('intact');opened={tuple(p)for p in g['opened']};anchors={tuple(q['site']):(q['load'],tuple(q['direction']))for q in g['anchors']};pinned={tuple(p)for p in g['pinned']}
    extra=set();paths=[];sources=[]
    for name,x,y,dy in [('left',5,10,1),('right',7,16,-1)]:
        H=(x,y,23);J=(x,y,21);K=(x,13,18)
        for sx,sy in[(-1,-1),(-1,1),(1,-1),(1,1)]:
            p=(x+sx,y+sy,24);v=(-sx,-sy,-1);sources.append({'side':name,'site':list(p),'direction':list(v),'arrival':-25,'injection':-26});extra.add(p)
        path=[(x,y,23),(x,y,22),(x,y,21),(x,y+dy,20),(x,y+2*dy,19),K,(x,13,17),(x,13,16),(x,13,15)]
        extra.update(path);paths.append({'side':name,'sites':[list(p)for p in path]})
        extra.add((x,y-dy,22));extra.add((x,13+dy,19))
    conflicts=[list(p)for p in extra if p in anchors or p in pinned]
    if conflicts:raise ValueError('R10 opening would overwrite an explicit prepared anchor/pin: '+str(conflicts))
    before=set(opened);opened.update(extra)
    g.update({'experimental_architecture':'EO02_SENSORIAL_R10_T0','architecture_revision':REVISION,
      'r10_remote_sources':sources,'r10_paths':paths,'r10_newly_opened':[list(p)for p in sorted(opened-before)],
      'opened':[list(p)for p in sorted(opened)],'no_eo01_state_or_learned_fields_imported':True,
      'retained_protocol_schema':'MI02.unified.r9 describes compatibility, not identity with an EO01 life'})
    return compile_geometry(26,opened,anchors,pinned),g
def submit(a,values):
    if len(values)!=8 or any(type(v)is not int or not 0<=v<=32 for v in values):raise ValueError('8 independent raw uint0..32 required')
    c=core._plan(a)['critical_tick'];rows=[];specs=[]
    for side,x,y,dy,idx in[('left',5,10,1,[0,2,4,6]),('right',7,16,-1,[1,3,5,7])]:
        for j,(sx,sy)in enumerate([(-1,-1),(-1,1),(1,-1),(1,1)]):
            specs.append((side+'.component.'+str(j),(x+sx,y+sy,24),(-sx,-sy,-1),c-26,values[idx[j]]))
        specs.append((side+'.turn1',(x,y-dy,22),(0,dy,-1),c-24,0))
        specs.append((side+'.turn2',(x,13+dy,19),(0,-dy,-1),c-21,0))
    for name,p,v,t,value in specs:rows.append(body.send(a,'EO02.R10.'+name,p,v,t,value))
    return{'revision':REVISION,'requests':rows,'critical_tick':c,'head_tick':c-25,'target_tick':c-17,
      'raw_components':values,'prepared_generic_resources':4,'core_public_zeros_are_two_additional_resources':True,'no_host_aggregates_in_native_inputs':True}
