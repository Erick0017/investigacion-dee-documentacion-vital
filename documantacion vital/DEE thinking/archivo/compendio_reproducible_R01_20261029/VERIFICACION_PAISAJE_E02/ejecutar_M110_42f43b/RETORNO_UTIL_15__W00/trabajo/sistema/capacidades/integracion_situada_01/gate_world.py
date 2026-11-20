"""Finite scalar gate coupled to the existing native comparator.

The environment applies contact/wear laws; it does NOT choose E1's action.
Its resistance, utility and records never supply the comparator's answer.
Fixed phases and the comparison/actuator law are prepared instrumentation.
"""
import json,re
from dee_thinking.persistence import encode_metadata,decode_metadata
from app.native_tools import physical,observe
from . import ic_native_core as core
KEY='DEE.Cognitive.System.1.1.CICLO02.gate.v1'

def get(a):
    e=dict(a.world.runtime.snapshot_metadata_entries)
    return json.loads(decode_metadata(e[KEY])['environment_json'])if KEY in e else None
def put(a,s):a.world.runtime.set_snapshot_metadata(KEY,encode_metadata({'environment_json':json.dumps(s,ensure_ascii=False,separators=(',',':'))}))

def prepare(a,*,name,phase=20):
    if get(a)is not None:raise ValueError('Gate already exists; continue its actual state, do not reset acquired history')
    if not isinstance(name,str)or not re.fullmatch(r'[A-Za-z0-9_.-]{1,48}',name)or phase!=20:raise ValueError('Explicit ID and validated fixed reference phase20 required')
    t0=20+67*max(0,(a.tick+8-20+66)//67);rr=[]
    for port,v in [('quantity.reference.cue',5),('quantity.reference.resource',0)]:
        r=a.quantity.input(port,v,t0);rr.append({'id':int(r['id']),'port':port,'payload':v,'tick':t0,'role':'COMMON_DECLARED_ZERO_BASELINE_NOT_A_FUTURE_ANSWER'})
    s={'name':name,'prepared_at':a.tick,'reference_phase':20,'comparison_phase':23,'baseline_tick':t0,
       'initial_resistance':0,'resistance':0,'index':0,'last_action_tick':None,'next_earliest_tick':t0+70,
       'pending_baseline':rr,'not_a_metabolism':True,'prepared_policy':'Native gradient comparator; -X7 attempt, +X7 retreat, other=neutral',
       'learning_scope':'Raw action-caused wear is acquired as a native reference; no law discovery or general policy learning is claimed.'}
    put(a,s);return s

def run(a,*,forces,wear=6,mode='intact'):
    s=get(a)
    if s is None:raise ValueError('Prepare the declared gate explicitly; never silently make a new universe or reference')
    if mode not in('intact','omit','null_action','sham'):raise ValueError('Explicit coupled or causal-control mode required')
    if not isinstance(forces,(list,tuple))or not 1<=len(forces)<=32 or any(type(v)is not int or not 0<=v<=100 for v in forces):raise ValueError('Finite actual force observations0..100, not class labels')
    wear=[wear]*len(forces)if type(wear)is int else list(wear)
    if len(wear)!=len(forces)or any(type(v)is not int or not 0<=v<=20 for v in wear):raise ValueError('Fixed material wear quanta0..20, one per opportunity')
    initial=physical(a.world,occupation=True);rows=[];rr=list(s['pending_baseline']);start_index=s['index']
    lower=max(s['next_earliest_tick'],a.tick+8)
    first=90+67*max(0,(lower-90+66)//67)
    # Immutable curriculum/calendar before the first response is observed.
    plan=[{'index':start_index+i,'tick':first+134*i,'force':q,'wear':w}for i,(q,w)in enumerate(zip(forces,wear))]
    for opportunity in plan:
        i=opportunity['index'];t=opportunity['tick'];force=opportunity['force'];quantum=opportunity['wear'];k=(t-90)//67
        a.quantity.present_object(force,reference_time=20,round_index=k);inputs=[dict(r)for r in a.quantity.state['requests'][-2:]]
        r=a.quantity.input('quantity.reader',7,t-1,True);inputs.append({'id':int(r['id']),'port':'quantity.reader','payload':7,'tick':t-1})
        a.run_until(t-1);pre={'reference':observe(a.world,a.quantity.geometry['reference_site']),'object':observe(a.world,a.quantity.geometry['object_site']),'center':observe(a.world,a.quantity.geometry['center'])}
        a.run_until(t);native=observe(a.world,a.quantity.geometry['center'])
        valid=native['state']==1 and native['semantic']==1 and native['s_reg']==7 and native['direction']in([1,0,0],[-1,0,0])
        # Fixed transduction only. The force and resistance do not select this.
        native_action=-native['direction'][0]if valid else 0
        action=0 if mode=='null_action'else native_action
        old=s['resistance'];opened=action==1 and force>old;jam=action==1 and not opened
        event_wear=quantum if action==1 else 0
        s['resistance']+=event_wear;returns=[];at=t+64
        if mode!='omit':
            pairs=[('quantity.other.cue',0),('quantity.other.event',event_wear)]if mode=='sham'else[('quantity.reference.cue',0),('quantity.reference.resource',event_wear)]
            for port,value in pairs:
                r=a.quantity.input(port,value,at);returns.append({'id':int(r['id']),'port':port,'payload':value,'tick':at})
        rr.extend(inputs+returns)
        rows.append({'index':i,'tick':t,'force_sensor':force,'wear_available':quantum,'native_pre':pre,'native_response':native,
                     'valid':valid,'native_action':native_action,'executed_action':action,
                     'environment':{'force':force,'resistance_before':old,'resistance_after':s['resistance'],'opened':opened,'jam':jam,'wear':event_wear},
                     'utility_auditor_only':int(opened)-int(jam),'useful_auditor_only':bool(opened or(action==-1 and force<=old)),
                     'return_input_tick':at,'requests':inputs+returns,'no_utility_or_resistance_sent':True})
        s['index']=i+1;s['last_action_tick']=t;s['next_earliest_tick']=t+134;put(a,s)
    # Fixed drain, not adaptive waiting until an answer becomes favorable.
    a.run_until(plan[-1]['tick']+134);put(a,s)
    return{'initial':initial,'plan_frozen_before_responses':plan,'mode':mode,'rows':rows,'requests':core.receipts(a,rr),
           'final_environment':s,'final':physical(a.world,occupation=True),
           'attribution':'Acquired scalar consequence reference used by prepared native comparison. Environment evaluates actual contact, not the desired action; Python never writes native memory or selects a route from the answer.'}
