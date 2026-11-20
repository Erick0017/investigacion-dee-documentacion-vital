"""Finite-use operational adapter for the validated two-level P1 organization.

This adapter admits a COMPLETE already learned queued state, never creates one.
The future generic request/resources are already present in its own Runtime.
Neither history label nor learned content is read to choose a route or output.
Use is deliberately phase-bounded: a second successful use was not validated.
"""
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation,exact_receipt
from dee_thinking.persistence import encode_metadata,decode_metadata
KEY='DEE.Cognitive.System.1.1.MA02.P1.FIRST_USE.v1'
SOURCE_KEY='MA02.P1.SELECTOR.CAUSAL.v1'
N=67;E=(33,33,33);D=(34,32,33);V=((1,0,0),(0,1,0))
def add(p,v,k=1):return tuple((p[i]+k*v[i])%N for i in range(3))
def observe(a,p):return exact_observation(a.world.runtime.observe(d.Coordinate(*p)))
def _get(a):
    entries=dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in entries:raise ValueError('P1 finite-use contract not admitted; no new individual substituted')
    return decode_metadata(entries[KEY])
def admit(a):
    entries=dict(a.world.runtime.snapshot_metadata_entries)
    if KEY in entries:return state(a)
    if int(a.world.runtime.dimension)!=N or SOURCE_KEY not in entries:raise ValueError('Requires validated complete P1 causal first-use snapshot, N67')
    m=decode_metadata(entries[SOURCE_KEY])
    if m.get('E')!=list(E)or m.get('D')!=list(D)or int(a.tick)!=129:raise ValueError('Requires original prepared learned pre-query T129; no rewind or recipe substitution')
    rs=m['requests'];queries=[x for x in rs if x.get('port')=='generic.current.query']
    if len(queries)!=1:raise ValueError('Expected exactly one queued generic query')
    q=queries[0]
    if q['direction']!=[0,0,1]or q['payload']!=0 or q['site']!=list(add(E,(0,0,1),-3))or q['tick'] not in(130,197):raise ValueError('Different query protocol; not silently generalized')
    if observe(a,E)['raw']!='0':raise ValueError('Selector already active: recipe does not certify another first use')
    gates=[x for x in rs if x.get('port','').startswith('generic.gate.')]
    if len(gates)!=4 or any(x['payload']!=7 or x['tick']!=q['tick']+6 for x in gates):raise ValueError('Incomplete fixed resources')
    # Verify selected prepared immutable interface geometry only. Never inspect
    # bank payloads or decode the history latch to decide an action.
    for p in(add(E,(-1,0,0)),add(E,(0,0,1))):
        o=observe(a,p)
        if o['semantic']!=4 or o['state']!=1:raise ValueError('Prepared field absent')
    info={'revision':'MA02.P1.first_use.R1','source_snapshot_label':m['label'],'admitted_tick':int(a.tick),'query_tick':q['tick'],'read_tick':q['tick']+8,'end_tick':q['tick']+15,'used':False,'scope':'P0 anatomy and externally initiated generic current query; prior touch changes native X/Y access P1. Two learned contents physically distinguish route selection from content. No P2/R2, repeated service or inherited E1 knowledge.'}
    a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(info));return state(a)
def state(a):
    m=_get(a)
    return {'INSTRUMENTO':{'tick':int(a.tick),'N':int(a.world.runtime.dimension),'protocol':m,'decoder':'Fixed all four gates, unique SEM1 pureZ; no history/content input'},'ENTE':{'classification':'New T0 composed native two acquired supports plus generic-touch trace and native gradient access selector','memory_has_not_been_read_by_this_status':True},'INTERPRETACION':{'P0':'Prepared XNOR/local-field anatomy, generic request, both-route resources and fixed reader','P1':'Native first access changes under past touch with content-specific use, causal cuts and reserved timing','P2_R2':'Not demonstrated. Continued R02/R03/R04 cycle attempts abstained after first action.'}}
def use(a,*,detailed=False):
    m=_get(a)
    if m['used']:raise ValueError('Finite first-use contract already consumed; do not recreate, re-teach or rewind this life')
    if int(a.tick)>=m['query_tick']:raise ValueError('Current state is past certified pre-query boundary; preserve and diagnose instead of substituting a checkpoint')
    rs=decode_metadata(dict(a.world.runtime.snapshot_metadata_entries)[SOURCE_KEY])['requests'];frames=[]
    for t in range(int(a.tick),m['end_tick']+1):
        a.run_until(t)
        if detailed and(t>=m['query_tick']or t==m['admitted_tick']):
            frames.append({'tick':t,'selector':observe(a,E),'trace':observe(a,D),'local_context':[observe(a,add(E,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
        if t==m['read_tick']:
            panel=[observe(a,add(add(E,v,4),(0,0,s)))for v in V for s in(-1,1)]
            cs=[{'site':p['site'],'sign':p['direction'][2],'s_reg':p['s_reg']}for p in panel if p['state']>0 and p['semantic']==1 and p['direction']in([0,0,-1],[0,0,1])]
    m['used']=True;m['used_through_tick']=int(a.tick);a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(m))
    return {'kind':'native_two_level_P1_first_use','read_tick':m['read_tick'],'end_tick':int(a.tick),'reader':{'panel':panel,'candidates':cs,'formed_native_command':cs[0]['sign']if len(cs)==1 else None,'uses_target_or_history_label':False},'requests':[{**r,'receipt':exact_receipt(a.world.runtime.receipt(r['id']))}for r in rs],'frames':frames,'scope':m['scope']}
