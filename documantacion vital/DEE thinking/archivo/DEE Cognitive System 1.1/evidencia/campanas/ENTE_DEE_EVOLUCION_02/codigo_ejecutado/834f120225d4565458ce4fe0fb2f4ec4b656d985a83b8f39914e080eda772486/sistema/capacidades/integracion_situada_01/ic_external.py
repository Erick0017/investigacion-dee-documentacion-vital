"""Fixed external transduction, no policy or hidden correct action.

The body/quantity readout is an explicit preparation variant, never chosen
after inspecting the desired torque. Raw environmental cost is an experience,
not a host-selected change to the route selector or a learned control policy.
"""
import json
from dee_thinking.persistence import encode_metadata,decode_metadata
from capacidades.habitat_externo_01 import _Worker
from app.native_tools import physical,observe,exact_receipt
from . import ic_body as body
KEY='DEE.Cognitive.System.1.1.IC01.external.v1'

def saved(a):
    m=dict(a.world.runtime.snapshot_metadata_entries)
    return json.loads(decode_metadata(m[KEY])['bridge_json'])if KEY in m else None
def store(a,s):a.world.runtime.set_snapshot_metadata(KEY,encode_metadata({'bridge_json':json.dumps(s,ensure_ascii=False,allow_nan=False,separators=(',',':'))}))
def command(read,readout):
    if readout=='body'and body.qualified(read):return 2*read['direction'][1]
    if readout=='magnitude'and read['state']==1 and read['semantic']==1 and read['direction']in([1,0,0],[-1,0,0]):return 2*read['direction'][0]
    return 0

def run(a,*,steps=4,seed=81017,mode='closed',readout='body',feedback='cost',reader='omit',reset=False,codec=1,stop_invalid=None,checkpoint=None,social_ports=None,clamp_sensor=False):
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
        if int(environment_initial['elapsed'])+steps>200:raise ValueError('Declared Pendulum episode horizon would be exceeded. Request an explicit environmental reset, never a DEE reset.')
        last_object=previous.get('last_object_input_tick',-1)if previous and not reset else-1
        last_feedback=previous.get('last_feedback_input_tick',-1)if previous and not reset else-1
        invalid_count=previous.get('invalid_count',0)if previous and not reset else 0
        previous_motor_tick=previous.get('last_motor_tick',previous.get('last_object_input_tick',-5)+5 if previous.get('readout')=='magnitude'else None)if previous and not reset else None
        if readout=='body':
            p=body.get(a)
            if not p:raise ValueError('A committed continuous body protocol is required')
            query_ticks=sorted(set([p1['query_tick']for p1 in p['plans']]+[p['end_tick']]))
            query_ticks=[t for t in query_ticks if t>=a.tick]
            if len(query_ticks)<steps:raise ValueError('Not enough committed native opportunities, no responsive rescue')
        else:query_ticks=[70+67*max(0,(a.tick+8-70+66)//67)+67*i for i in range(steps)]
        for t in query_ticks[:steps]:
            visible=prior if mode=='delay1'else o;q=73 if clamp_sensor else max(1,min(145,round(73+40*visible[1])))
            k=(t-70)//67 if readout=='magnitude'else max(0,(a.tick+1-65+66)//67);object_at=65+67*k;rr=[];dropped=[]
            if codec==2 and object_at<=last_object:dropped.append({'kind':'sensor','reason':'FIXED_FIRST_SAMPLE_PER_NATIVE_SLOT','slot':object_at,'value':q})
            else:
                a.quantity.present_object(q,round_index=k);rr=[dict(x)for x in a.quantity.state['requests'][-2:]];last_object=object_at
                if reader=='probe':rr.append(a.input('quantity.reader',7,69+67*k,'probe','FIXED_SENSOR_READER'))
            # No waiting for a preferred sensor response. Body cadence is fixed.
            a.run_until(t);native=body.ic.obs(a,body.get(a)['center'])if readout=='body'else observe(a.world,a.quantity.geometry['center']);cmd=command(native,readout);raw_quantity_command=cmd;social_reads=[]
            if social_ports is not None:
                if readout!='magnitude':raise ValueError('Declared mixed wiring requires native magnitude output')
                cmd=cmd//2
                for b in social_ports:
                    received=observe(a.world,b['target']);qual=received['state']==1 and received['semantic']==1 and received['s_reg']>0 and received['direction']==[b['sign'],0,0];contribution=b['sign']if qual else 0;cmd+=contribution;social_reads.append({'bank':b['sign'],'target':b['target'],'native':received,'qualified':qual,'prepared_gain1_command':contribution})
                cmd=max(-2,min(2,cmd))
            torque=0 if mode=='nulled'else cmd;response=w.call('step',torque=torque)
            cost=max(0,min(20,round(-response['reward'])));reference_at=67*max(0,(a.tick+1+66)//67)
            feedback_requests=[]
            if feedback=='cost'and not(codec==2 and reference_at<=last_feedback):
                for port,payload in [('quantity.reference.cue',0),('quantity.reference.resource',cost)]:
                    rec=a.quantity.input(port,payload,reference_at);feedback_requests.append({'id':int(rec['id']),'port':port,'payload':payload,'tick':reference_at})
                last_feedback=reference_at
            elif feedback=='cost':dropped.append({'kind':'raw_cost','reason':'FIXED_FIRST_SAMPLE_PER_NATIVE_SLOT','slot':reference_at,'value':cost})
            rows.append({'index':index,'tick':a.tick,'observation_before':list(o),'visible_before_codec':list(visible),'q_sin':q,'sensor_input_tick':object_at,'sensor_reader':reader,'native':native,'native_command':cmd,'raw_quantity_command_gain2':raw_quantity_command,'social_reads':social_reads,'external_motor_wiring':'quantity_gain1_plus_social_gain1'if social_ports is not None else'original_gain2','sensor_clamped':clamp_sensor,'executed_torque':torque,'response':response,'raw_cost_codec':cost,'feedback_mode':feedback,'feedback_input_tick':reference_at,'requests':rr+feedback_requests,'codec_revision':codec,'dropped_rate_samples':dropped,'information_not_sent':['cos(theta)','angular_velocity','hidden_state','seed','future','desired_action'],'first_action_can_precede_this_observation_admission':object_at>t})
            prior=list(o);o=response['observation'];index+=1
            s={'schema':'IC01.external.exact.v2','environment':w.call('snapshot')['snapshot'],'previous_observation':prior,'last_observation':o,'index':index,'mode':mode,'readout':readout,'feedback':feedback,'reader':reader,'ratio':'52 native ticks per0.05 environmental seconds for body;67 for magnitude','reset_environment_without_DEE_reset':reset,'codec_revision':codec,'last_object_input_tick':last_object,'last_feedback_input_tick':last_feedback,'prior_codec_if_changed':None if previous is None or previous.get('codec_revision',1)==codec else previous.get('codec_revision',1)}
            store(a,s)
            rows[-1]['native_ticks_since_previous_motor']=None if previous_motor_tick is None else a.tick-previous_motor_tick
            rows[-1]['explicit_native_only_gap']=previous_motor_tick is not None and a.tick-previous_motor_tick!=(67 if readout=='magnitude'else 52)
            previous_motor_tick=a.tick;s['last_motor_tick']=a.tick;store(a,s)
            if social_ports is not None:s['motor_wiring']='quantity_gain1_plus_social_gain1';s['social_ports']=social_ports;s['sensor_clamped']=clamp_sensor;store(a,s)
            if checkpoint:checkpoint(a,len(rows))
            valid=(body.qualified(native)if readout=='body'else native['state']==1 and native['semantic']==1 and native['direction']in([1,0,0],[-1,0,0],[0,0,0]))
            rows[-1]['qualified_in_declared_domain']=valid
            invalid_count=0 if valid else invalid_count+1;s['invalid_count']=invalid_count;store(a,s)
            if stop_invalid is not None and invalid_count>=stop_invalid:
                s['stop_reason']='PREDECLARED_CONSECUTIVE_INVALID_OUTPUTS_'+str(stop_invalid);store(a,s);break
        for row in rows:
            row['requests']=[{**r,'receipt':exact_receipt(a.world.runtime.receipt(r['id']))}for r in row['requests']]
        return{'identity':w.identity,'initial_native':before,'initial_environment':environment_initial,'rows':rows,'final_environment':s,'final_native':physical(a.world,occupation=True),'attribution':'Prepared codec and feedback opportunities. Native body selection and native acquisition of raw cost are not automatically learned Pendulum control. Pending sensor/cost inputs remain in the complete native snapshot.'}
    finally:w.close()

def run_clocked(a,*,steps=17,mode='closed',feedback='cost',sensor='live',social_output=True,seed=81017,social_wire='delivery6',stop_invalid_body=None):
    """Declared motor clock13 with fixed, simultaneous physical output wires.

    The added social actuator reads both actual E1 delivery descendants six
    native steps downstream. Summing/clipping torques is external wiring, not
    claimed native composition or a host policy computed from Pendulum state.
    """
    if mode not in('closed','nulled')or feedback not in('cost','omit')or sensor not in('live','clamp'):raise ValueError('Clocked variant')
    old=saved(a);w=_Worker()
    try:
        if old:
            initial=w.call('restore',snapshot=old['environment']);o=initial['observation'];prior=old['previous_observation'];index=old['index']
        else:initial=w.call('reset',seed=seed,g=10.0);o=initial['observation'];prior=list(o);index=0
        anchor=old.get('next_motor_tick',a.tick)if old and old.get('schema')=='IC01.external.motor13.v1'else a.tick
        if anchor<a.tick:raise ValueError('Motor clock was skipped, no adaptive rescue')
        last_object=old.get('last_object_input_tick',-1)if old else-1;last_feedback=old.get('last_feedback_input_tick',-1)if old else-1
        before=physical(a.world,occupation=True);initial_env=w.call('snapshot')['snapshot'];rows=[];S=body.get(a)['center'];invalid_body=0
        body_ticks={p['query_tick']for p in body.get(a)['plans']}|{body.get(a)['end_tick']}
        if social_wire not in('delivery6','direct'):raise ValueError('Fixed physical social wire')
        for i in range(steps):
            t=anchor+13*i;visible=list(o);q=73 if sensor=='clamp'else max(1,min(145,round(73+40*visible[1])))
            k=max(0,(a.tick+1-65+66)//67);slot=65+67*k;rr=[];drops=[]
            if slot>last_object:
                a.quantity.present_object(q,round_index=k);rr.extend(dict(x)for x in a.quantity.state['requests'][-2:]);last_object=slot
            else:drops.append({'kind':'sensor','slot':slot,'fixed_first_sample_not_useful_sample':True,'q':q})
            a.run_until(t);native=body.ic.obs(a,S);body_cmd=command(native,'body');social_reads=[];social_cmds=[]
            for bank in a.geometry['cpc9_return']['banks']:
                direction=[bank['sign'],0,0]if social_wire=='direct'else[bank['sign'],1,1];site=bank['message_site']if social_wire=='direct'else body.ic.move(bank['delivery_site'],direction,6);read=body.ic.obs(a,site)
                valid=read['state']==1 and read['semantic']==1 and read['s_reg']>0 and read['direction']==direction
                cmd=2*bank['sign']if valid and social_output else 0;social_cmds.append(cmd);social_reads.append({'bank':bank['id'],'site':site,'read':read,'qualified':valid,'prepared_wire_command':cmd})
            unclipped=body_cmd+sum(social_cmds);cmd=max(-2,min(2,unclipped));executed=0 if mode=='nulled'else cmd;response=w.call('step',torque=executed)
            cost=max(0,min(20,round(-response['reward'])));reference_at=67*max(0,(a.tick+1+66)//67)
            if feedback=='cost'and reference_at>last_feedback:
                for port,payload in [('quantity.reference.cue',0),('quantity.reference.resource',cost)]:
                    rec=a.quantity.input(port,payload,reference_at);rr.append({'id':int(rec['id']),'port':port,'payload':payload,'tick':reference_at})
                last_feedback=reference_at
            elif feedback=='cost':drops.append({'kind':'raw_cost','slot':reference_at,'fixed_first_sample_not_useful_sample':True,'cost':cost})
            rows.append({'index':index,'tick':a.tick,'observation_before':visible,'q_sin':q,'sensor':sensor,'sensor_slot':slot,'native_body':native,'body_command':body_cmd,'social_reads':social_reads,'unclipped_motor_sum':unclipped,'native_wire_command':cmd,'executed_torque':executed,'response':response,'raw_cost_codec':cost,'feedback':feedback,'requests':rr,'rate_drops':drops,'motor_interval_native_ticks':13,'dt_external_seconds':'0.05','decoder_role':'Prepared simultaneous actuator wiring, not learned native language/composition. No last-valid-output cache.'})
            prior=list(o);o=response['observation'];index+=1
            state={'schema':'IC01.external.motor13.v1','environment':w.call('snapshot')['snapshot'],'previous_observation':prior,'last_observation':o,'index':index,'mode':mode,'readout':'body_plus_social_wires','feedback':feedback,'sensor':sensor,'last_object_input_tick':last_object,'last_feedback_input_tick':last_feedback,'next_motor_tick':t+13,'clock_anchor_tick':anchor,'ratio':'13 native ticks per0.05 external seconds','social_output_enabled':social_output,'social_wire':social_wire,'clock_transition_from_prior_bridge_explicit':not(old and old.get('schema')=='IC01.external.motor13.v1')};store(a,state)
            if t in body_ticks:invalid_body=0 if body.qualified(native)else invalid_body+1
            rows[-1]['is_body_opportunity']=t in body_ticks;rows[-1]['consecutive_invalid_body_opportunities']=invalid_body
            if stop_invalid_body is not None and invalid_body>=stop_invalid_body:
                state['stop_reason']='PREDECLARED_'+str(stop_invalid_body)+'_CONSECUTIVE_INVALID_BODY_OPPORTUNITIES';store(a,state);break
        for row in rows:row['requests']=[{**r,'receipt':exact_receipt(a.world.runtime.receipt(r['id']))}for r in row['requests']]
        return{'identity':w.identity,'initial_native':before,'initial_environment':initial_env,'rows':rows,'final_environment':state,'final_native':physical(a.world,occupation=True),'limits':'Direct action from acquired route plus fixed social output wires, not learned Pendulum balance. First-sample decimation is sensor bandwidth, not semantic selection. Raw reward return has not been assumed to update a correct policy.'}
    finally:w.close()
