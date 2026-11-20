"""Finite prepared native-opportunity protocol; never an action policy.

The controller here only commits environmental inputs and observes fixed
boundaries through the original session owner. All actions are native fields.
Recorded targets/frames are not read by the kernel or used to select inputs.
"""
import json
from dee_thinking.persistence import encode_metadata,decode_metadata
from app.native_tools import physical
import ic_native_core as ic
KEY='DEE.Cognitive.System.1.1.IC01.body.protocol.v1'

def get(a):
    e=dict(a.world.runtime.snapshot_metadata_entries)
    return json.loads(decode_metadata(e[KEY])['operational_json'])if KEY in e else None

def put(a,state):a.world.runtime.set_snapshot_metadata(KEY,encode_metadata({'operational_json':json.dumps(state,ensure_ascii=False,separators=(',',':'))}))

def qualified(read):return read['state']==1 and read['semantic']==1 and read['s_reg']>0 and read['direction'][0]==1 and abs(read['direction'][1])==1 and read['direction'][2]==0

def arm(a,*,name,contexts,guards='none',mode='intact'):
    old=get(a)
    if old and a.tick<old['end_tick']:raise ValueError('Finish or continue the existing committed protocol, never replace pending opportunities')
    if old and a.tick!=old['end_tick']:raise ValueError('The protocol was advanced outside its current boundary; no silent re-creation or favorable reset')
    if guards!='none':raise ValueError('The admitted finite R6 protocol does not include the unsuccessful R8/R9 guard candidates')
    plan=ic.situated(a,name=name,availability=tuple(contexts),mode=mode,trace=False,compact=True,gap=0,stream=True,queue_only=True)
    state={**plan,'schema':'IC01.body.fixed_opportunity_protocol.r1','start_tick':a.tick,'progress_tick':a.tick,'frames':[],'phase':'QUEUED','clock_is_prepared_not_learned':True,'history_not_a_policy_table':True}
    put(a,state);return{'start_tick':a.tick,'end_tick':state['end_tick'],'queries':[p['query_tick']for p in plan['plans']],'contexts':list(contexts),'guards':plan['guards'],'actual_initial_action':ic.obs(a,plan['center'])if plan['first_action_already_formed']else None}

def attach(a,*,record=True):
    state=get(a)
    if state is None:raise ValueError('No committed native body protocol')
    original=a.run_until;S=state['center'];events={}
    for p in state['plans']:
        for role,t in [('action',p['query_tick']),('contact',p['query_tick']+4),('return_source',p['query_tick']+8),('next_action',p['return_tick'])]:events.setdefault(t,[]).append((role,p))
    frames=[]
    def capture(when):
        roles=events[when];row={'tick':when,'roles':[{'role':role,'index':p['index'],'context':p['availability']}for role,p in roles],'selector':ic.obs(a,S),'action_qualified':qualified(ic.obs(a,S))}
        if any(role=='contact'for role,p in roles):row['contacts']={str(r):ic.obs(a,ic.move(S,(1,r,0),4))for r in(-1,1)}
        if any(role=='next_action'for role,p in roles):row['global']=physical(a.world,occupation=True)
        frames.append(row)
    if record and a.tick in events:capture(a.tick)
    def advance(target):
        if target>state['end_tick']:raise ValueError('Requested advance exceeds the finite committed native opportunities; explicitly arm a new block at its boundary')
        for t in sorted(t for t in events if a.tick<t<=target):
            original(t)
            if record:capture(t)
        result=original(target);state['progress_tick']=a.tick
        if a.tick==state['end_tick']:
            state['phase']='AT_ACTION_BOUNDARY';g=ic.configuration(a);g['stream_action_tick']=a.tick;g['last_selector_tick']=a.tick;ic.save(a,g)
        else:state['phase']='IN_PROGRESS_WITH_EXACT_PENDING_INPUTS'
        # Bounded operational progress. Detailed observations are experiment
        # results returned to the caller, not a participant memory to be queried.
        state['frames']=[];put(a,state);return result
    a.run_until=advance
    return{'frames':frames,'state':state,'original_run_until':original,'detach':lambda:setattr(a,'run_until',original)}

def finish(a,*,record=True):
    h=attach(a,record=record)
    try:a.run_until(h['state']['end_tick'])
    finally:h['detach']()
    requests=[ic.receipts(a,rr)for rr in h['state']['requests']]
    return{'native_frames':h['frames'],'requests':requests,'end_tick':a.tick,'final_action':ic.obs(a,h['state']['center']),'operational_protocol':get(a)}

def report(a):
    s=get(a)
    return{'tick':a.tick,'protocol':None if s is None else{k:s[k]for k in('name','start_tick','progress_tick','end_tick','phase')},'native_action':None if s is None else ic.obs(a,s['center']),'scope':'Passive state and fixed opportunity protocol; no free cognition or autonomous clock claimed'}
