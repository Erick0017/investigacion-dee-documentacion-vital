"""Passive multi-scale views. Scientific IDs and predictions never enter RAW."""
from observations import *

def site(rt,q):
    r=record(rt.observe(c(q)));r['active_for_rule']=r['state']>0 and r['semantic']!=5
    r['material_center_present']=r['state']>0 and r['semantic']==1
    return r

def relational(rt,origin):
    n=rt.dimension;a=add(origin,(-1,0,0),1,n);b=add(origin,(1,0,0),1,n)
    ar,br=site(rt,a),site(rt,b)
    valid=ar['material_center_present'] and br['material_center_present']
    return {'tick':rt.current_tick,'A':ar,'B':br,'valid_relation':valid,
            'delta_validated':ar['s_reg']-br['s_reg'] if valid else None,
            'raw_load_difference_diagnostic':ar['s_reg']-br['s_reg'],
            'comparator':site(rt,origin),'gateA':gate(rt,a),'gateB':gate(rt,b)}

def panel(rt,sites):
    return {'tick':rt.current_tick,'sites':{k:site(rt,q) for k,q in sites.items()},
            'backend':str(rt.execution_options.backend),
            'last_tick_counters':{k:getattr(rt.last_tick_info,k) for k in ('evaluated','overflows','genesis','total_ns','used_threads')}}

def record_signature(r):return [r['state']>0,r['semantic'],r['s_reg'],r['direction']]

def fields_diff(a,b):
    fields=('raw','clock_uint64','state','semantic','s_reg','direction')
    return {k:{'left':a[k],'right':b[k]} for k in fields if a[k]!=b[k]}

def ballistic(rt,birth,start,direction):
    r=site(rt,add(start,direction,rt.current_tick-birth,rt.dimension))
    return {'observed':r,'unwrapped_prediction':[start[i]+direction[i]*(rt.current_tick-birth) for i in range(3)],
            'continuity_criterion':'declared ballistic segment, actual site sampled; collisions require a new segment',
            'uncertainty':'not a universal object or genealogy detector'}
