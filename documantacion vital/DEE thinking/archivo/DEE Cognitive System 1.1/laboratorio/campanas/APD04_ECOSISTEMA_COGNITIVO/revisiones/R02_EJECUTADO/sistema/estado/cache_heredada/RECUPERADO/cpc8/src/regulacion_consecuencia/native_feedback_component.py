# Minimal inert adapter of byte-preserved historical V2 source207340….
# Only the builder name and one creation statement change. No Runtime is allocated,
# no physical initialization/formula is altered and the complete recipe is returned.
# The original source and exact textual diff are included beside this adapter.
"""CPC8 research: native contact consequence -> R14 -> regulatory routing.

Fresh initial physical preparation only; no sensor callback, future rollout,
external error/policy calculation, teaching map or response lookup. The current
world medium differs by direction, at equal inventory. Fixed source/normalizer
geometry and finite retain/switch rule are researcher-prepared, not discovered.
"""
from __future__ import annotations
import dee_thinking as dee
from dee_thinking import _native as d

def move(q,v,t=1,n=67):return tuple((q[i]+v[i]*t)%n for i in range(3))

def prepare_component(*,medium=1,mode='intact',translation=(0,0,0),n=67,lanes=(-1,1)):
    if medium not in (-1,1) or mode not in ('intact','omit_actuator','sham_actuator','cut_feedback','cut_negative_return'):
        raise ValueError('Frozen physical condition outside domain')
    if n not in (67,131):raise ValueError('Only declared two research geometries')
    origin=move((30,30,30),(0,0,0),n=n)
    origin=tuple((origin[i]+translation[i])%n for i in range(3))
    placements=[];occupied={};ports={};records=[]
    def put(q,load,dr,role,clock=0):
        p=d.InitialPlacement();p.site=d.Coordinate(*q);p.raw=d.pack_record(1,load,*dr,1);p.clock=clock;p.role=role
        if q in occupied:
            raise ValueError('Initial overlap at'+str(q)+' '+occupied[q]+' vs '+role)
        occupied[q]=role;placements.append(p)
        records.append({'site':list(q),'load':load,'direction':list(dr),'clock':str(clock),'role':role})
    def arrive(q,t,dr,load,role):put(move(q,dr,-t,n),load,dr,role)
    first_action=move(origin,(1,0,0),n=n)
    first_report=move(first_action,(0,0,1),n=n)
    put(origin,7,(1,0,0),'Prepared initial controller policyP, not learned',11)
    arrive(first_action,1,(-1,0,1),47,'Common first action opportunity')
    arrive(first_report,2,(1,1,-1),31,'Previously available sourceP expectation +1')
    ports['expectation']=first_report
    regulators=[]
    if tuple(lanes) not in ((-1,1),(1,)):raise ValueError('Unfrozen lane geometry')
    for e in lanes:
        hub=move(first_report,(e,1,0),3,n);ports[f'comparison.{e}']=hub
        # A separate zero-load physical actuator samples the same current world
        # medium for each fixed comparison lane. Medium is not a utility label.
        base=move(hub,(0,-1,-2),n=n);act=move(base,(-1,0,-1),n=n)
        if mode!='omit_actuator':
            if mode=='sham_actuator':act=move(act,(0,1,0),12,n)
            put(act,0,(1,0,0),f'Consequence probe actuator lane{e}')
        arrive(move(base,(0,0,-1),n=n),1,(-1,0,1),0,f'Consequence probe common interaction lane{e}')
        arrive(base,2,(medium,1,-1),1,f'Current physical world medium lane{e}')
        ports[f'world_contact.{e}']=base
        ports[f'actual_before_merge.{e}']=move(hub,(medium,0,-1),n=n)
        for c in (-1,1):
            gate1=move(base,(c,1,0),n=n)
            gate2=move(base,(c,1,1),n=n)
            arrive(gate1,3,(-c,-1,1),0,f'Prepared zero-load consequence turn1 lane{e}/{c}')
            if mode=='cut_feedback' or (mode=='cut_negative_return' and c==-1):gate2=move(gate2,(0,1,0),12,n)
            arrive(gate2,4,(-c,0,0),0,f'Prepared zero-load consequence turn2 lane{e}/{c}')
        for dx in (0,e):
            key=f'{e}_{dx}';wp=move(hub,(dx,1,1),4,n)
            normal=(1,-1,-1) if dx==0 else (-dx,0,-1)
            arrive(wp,9,normal,11,'Prepared finite R14 comparison-to-policy '+key)
            ports['policy.'+key]=wp
            for label,policy,action in (('P',(1,0,0),(0,0,1)),('Q',(0,1,0),(-1,1,1))):
                query=move(wp,policy,n=n)
                arrive(query,10,(-1,0,1),17,'Symmetric prepared regulatory opportunity '+key+label)
                contact=move(query,action,2,n)
                threat=tuple(-x for x in action)
                arrive(contact,12,threat,7,'Current interfering stream '+key+label)
                danger=move(contact,threat,n=n)
                arrive(danger,13,(1,0,0),3,'Useful delivery stream '+key+label)
                receiver=move(danger,(1,0,0),2,n)
                ident=key+'.'+label
                ports['regulatory_action.'+ident]=query
                ports['interception.'+ident]=contact
                ports['resource_contact.'+ident]=danger
                ports['delivery.'+ident]=receiver
                regulators.append({'id':ident,'source':label,'action':list(action),'query':list(query),
                    'contact':list(contact),'danger':list(danger),'receiver':list(receiver)})
    recipe=d.OrganizationRecipe.research(n,placements,0)
    recipe.execution=d.TickOptions(d.Backend.LAZY,1)
    revision='v1' if tuple(lanes)==(-1,1) else 'v2_single_comparison_lane'
    org=d.OrganizationSpec();org.id='native_feedback';org.recipe_id='CPC8.native_consequence_regulation.'+revision
    org.ports={k:d.Coordinate(*v) for k,v in ports.items()}
    recipe.organizations=[org]
    recipe.domain='Finite prepared R14 + native current-contact consequence + regulatory interception; new research apparatus, not a general reinforcement learner.'
    world=recipe  # Inert recipe; the caller creates the sole owner Runtime.
    geometry={'N':n,'revision':revision,'lanes':list(lanes),'ports':{k:list(v) for k,v in ports.items()},'regulators':regulators,'initial_placements':records,
        'medium':medium,'mode':mode,'translation':list(translation),'ticks':{'world_contact':2,'comparison':5,'policy':9,'action':10,'interception':12,'delivery':15},
        'resources':{'initial_records':len(placements),'physical_base_buffers':32*n**3},
        'information_audit':'medium changes only current-world direction at equal load. Two zero-load probe interactions convert that consequence into a native carrier. No Python output-to-input callback; no results/targets imports.',
        'attribution':'Finite retain-P/switch-Q transformation and routing prepared. A positive result would show a strategy state changed by received physical consequence, not acquisition of an arbitrary update rule.'}
    return world,geometry

def record(world,site):
    o=world.runtime.observe(d.Coordinate(*site));r=o.record
    return {'tick':int(o.tick),'site':list(site),'raw':str(o.raw),'clock':str(o.clock),'state':int(r.state),
        's_reg':int(r.s_reg),'direction':[int(r.dx),int(r.dy),int(r.dz)],'semantic':int(r.semantic)}

def neighborhood(world,site):
    n=world.runtime.dimension
    return [record(world,move(site,(x,y,z),n=n)) for x in (-1,0,1) for y in (-1,0,1) for z in (-1,0,1)]

