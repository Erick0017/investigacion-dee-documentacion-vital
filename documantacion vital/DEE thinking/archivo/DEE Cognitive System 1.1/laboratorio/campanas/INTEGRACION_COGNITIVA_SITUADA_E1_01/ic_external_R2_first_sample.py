"""Fixed external transduction, no policy or hidden correct action.

The body/quantity readout is an explicit preparation variant, never chosen
after inspecting the desired torque. Raw environmental cost is an experience,
not a host-selected change to the route selector or a learned control policy.
"""
import json
from dee_thinking.persistence import encode_metadata,decode_metadata
from capacidades.habitat_externo_01 import _Worker
from app.native_tools import physical,observe,exact_receipt
import ic_body as body
KEY='DEE.Cognitive.System.1.1.IC01.external.v1'

def saved(a):
    m=dict(a.world.runtime.snapshot_metadata_entries)
    return json.loads(decode_metadata(m[KEY])['bridge_json'])if KEY in m else None
def store(a,s):a.world.runtime.set_snapshot_metadata(KEY,encode_metadata({'bridge_json':json.dumps(s,ensure_ascii=False,allow_nan=False,separators=(',',':'))}))
def command(read,readout):
    if readout=='body'and body.qualified(read):return 2*read['direction'][1]
    if readout=='magnitude'and read['state']==1 and read['semantic']==1 and read['direction']in([1,0,0],[-1,0,0]):return 2*read['direction'][0]
    return 0

def run(a,*,steps=4,seed=81017,mode='closed',readout='body',feedback='cost',reader='omit',reset=False,codec=1):
    if mode not in('closed','nulled','delay1')or readout not in('body','magnitude')or feedback not in('cost','omit')or reader not in('omit','probe'):raise ValueError('Frozen external variant')
    previous=saved(a)
    if codec not in(1,2):raise ValueError('Explicit codec revision')
    if previous and not reset and previous['readout']!=readout:raise ValueError('Cannot silently switch motor readout in a life')
    w=_Worker()
    try:
        if previous and not reset:
            init=w.call('restore',snapshot=previous['environment']);o=init['observation'];prior=previous['previous_observation'];index=previous['index']
        else:init=w.call('reset',seed=seed,g=10.0);o=init['observation'];prior=list(o);index=0
        environment_initial=w.call('snapshot')['snapshot'];before=physical(a.world,occupation=True);rows=[]
        last_object=previous.get('last_object_input_tick',-1)if previous and not reset else-1
        last_feedback=previous.get('last_feedback_input_tick',-1)if previous and not reset else-1
        if readout=='body':
            p=body.get(a)
            if not p:raise ValueError('A committed continuous body protocol is required')
            query_ticks=sorted(set([p1['query_tick']for p1 in p['plans']]+[p['end_tick']]))
            query_ticks=[t for t in query_ticks if t>=a.tick]
            if len(query_ticks)<steps:raise ValueError('Not enough committed native opportunities, no responsive rescue')
        else:query_ticks=[70+67*max(0,(a.tick+8-70+66)//67)+67*i for i in range(steps)]
        for t in query_ticks[:steps]:
            visible=prior if mode=='delay1'else o;q=max(1,min(145,round(73+40*visible[1])))
            k=(t-70)//67 if readout=='magnitude'else max(0,(a.tick+1-65+66)//67);object_at=65+67*k;rr=[];dropped=[]
            if codec==2 and object_at<=last_object:dropped.append({'kind':'sensor','reason':'FIXED_FIRST_SAMPLE_PER_NATIVE_SLOT','slot':object_at,'value':q})
            else:
                a.quantity.present_object(q,round_index=k);rr=[dict(x)for x in a.quantity.state['requests'][-2:]];last_object=object_at
                if reader=='probe':rr.append(a.input('quantity.reader',7,69+67*k,'probe','FIXED_SENSOR_READER'))
            # No waiting for a preferred sensor response. Body cadence is fixed.
            a.run_until(t);native=body.ic.obs(a,body.get(a)['center'])if readout=='body'else observe(a.world,a.quantity.geometry['center']);cmd=command(native,readout)
            torque=0 if mode=='nulled'else cmd;response=w.call('step',torque=torque)
            cost=max(0,min(20,round(-response['reward'])));reference_at=67*max(0,(a.tick+1+66)//67)
            feedback_requests=[]
            if feedback=='cost'and not(codec==2 and reference_at<=last_feedback):
                for port,payload in [('quantity.reference.cue',0),('quantity.reference.resource',cost)]:
                    rec=a.quantity.input(port,payload,reference_at);feedback_requests.append({'id':int(rec['id']),'port':port,'payload':payload,'tick':reference_at})
                last_feedback=reference_at
            elif feedback=='cost':dropped.append({'kind':'raw_cost','reason':'FIXED_FIRST_SAMPLE_PER_NATIVE_SLOT','slot':reference_at,'value':cost})
            rows.append({'index':index,'tick':a.tick,'observation_before':list(o),'visible_before_codec':list(visible),'q_sin':q,'sensor_input_tick':object_at,'sensor_reader':reader,'native':native,'native_command':cmd,'executed_torque':torque,'response':response,'raw_cost_codec':cost,'feedback_mode':feedback,'feedback_input_tick':reference_at,'requests':rr+feedback_requests,'codec_revision':codec,'dropped_rate_samples':dropped,'information_not_sent':['cos(theta)','angular_velocity','hidden_state','seed','future','desired_action'],'first_action_can_precede_this_observation_admission':object_at>t})
            prior=list(o);o=response['observation'];index+=1
            s={'schema':'IC01.external.exact.v2','environment':w.call('snapshot')['snapshot'],'previous_observation':prior,'last_observation':o,'index':index,'mode':mode,'readout':readout,'feedback':feedback,'reader':reader,'ratio':'52 native ticks per0.05 environmental seconds for body;67 for magnitude','reset_environment_without_DEE_reset':reset,'codec_revision':codec,'last_object_input_tick':last_object,'last_feedback_input_tick':last_feedback,'prior_codec_if_changed':None if previous is None or previous.get('codec_revision',1)==codec else previous.get('codec_revision',1)}
            store(a,s)
        for row in rows:
            row['requests']=[{**r,'receipt':exact_receipt(a.world.runtime.receipt(r['id']))}for r in row['requests']]
        return{'identity':w.identity,'initial_native':before,'initial_environment':environment_initial,'rows':rows,'final_environment':s,'final_native':physical(a.world,occupation=True),'attribution':'Prepared codec and feedback opportunities. Native body selection and native acquisition of raw cost are not automatically learned Pendulum control. Pending sensor/cost inputs remain in the complete native snapshot.'}
    finally:w.close()
