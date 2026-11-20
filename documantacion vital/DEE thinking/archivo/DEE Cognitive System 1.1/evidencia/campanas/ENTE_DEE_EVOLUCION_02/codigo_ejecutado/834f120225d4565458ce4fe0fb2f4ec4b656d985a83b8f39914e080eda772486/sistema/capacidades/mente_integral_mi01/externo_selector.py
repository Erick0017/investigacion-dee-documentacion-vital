"""Fixed selector-to-Pendulum transduction; no balancing/control policy.

The actual native command determines signed torque. Neither observation,
reward, seed nor audit target selects it. Existing full external state is
continued; switching this codec is explicit and recorded, never a DEE reset.
"""
from capacidades.habitat_externo_01 import _Worker
from capacidades.integracion_situada_01 import ic_external as bridge,ic_native_core as n
from app.native_tools import physical,exact_receipt
from . import saved,material_command

def run(a,*,steps=1,mode='closed',feedback='cost',transition=False,habitat=None,motor_codec='signed_selector'):
    if not 1<=steps<=96 or mode not in('closed','nulled','delay1')or feedback not in('cost','omit'):raise ValueError('Finite fixed external protocol required')
    if motor_codec not in('signed_selector','native_body_roles'):raise ValueError('Fixed motor codec required')
    old=bridge.saved(a)
    if old is None:raise ValueError('Continue an existing complete external environment; no silent reset')
    if old['readout']!='mi01_selector'and not transition:raise ValueError('Explicit transition=True required for magnitude-to-selector motor wiring')
    w=_Worker();before=physical(a.world,occupation=True)
    try:
        o=w.call('restore',snapshot=old['environment'])['observation'];prior=list(old['previous_observation']);index=old['index'];initial_env=w.call('snapshot')['snapshot']
        if initial_env['elapsed']+steps>200:raise ValueError('External horizon reached; explicit environmental reset required, never a DEE restart')
        first=29+67*max(0,(a.tick-29+66)//67)
        if old['readout']=='mi01_selector'and first<=old.get('last_motor_tick',-1):first+=67
        last_object=old.get('last_object_input_tick',-1);last_feedback=old.get('last_feedback_input_tick',-1);rows=[];frames=[];S=n.configuration(a)['center']
        for j in range(steps):
            t=first+67*j;visible=prior if mode=='delay1'else o;q=max(1,min(145,round(73+40*visible[1])));slot=65+67*max(0,(a.tick+1-65+66)//67);requests=[];drops=[]
            if slot>last_object:
                a.quantity.present_object(q,round_index=(slot-65)//67);requests.extend(dict(r)for r in a.quantity.state['requests'][-2:]);last_object=slot
            else:drops.append({'kind':'sensor','slot':slot,'rule':'FIRST_SAMPLE_PER_FIXED_NATIVE_SLOT','value':q})
            if habitat:
                if saved(a)['native_habitats'][habitat].get('direct_failure'):
                    from .fallo_y_consulta import advance
                else:
                    from .habitat_nativo import advance
                frames.extend(advance(a,name=habitat,until=t)['frames'])
            else:a.run_until(t)
            native=n.obs(a,S);valid=material_command(native)and native['s_reg']>0
            # The body uses -Y as an information request, not a negative motor
            # act. This fixed role codec never reads utility or private B data.
            command=(2*native['direction'][1]if motor_codec=='signed_selector'else(2 if native['direction'][1]>0 else 0))if valid else 0;torque=0 if mode=='nulled'else command
            response=w.call('step',torque=torque);cost=max(0,min(20,round(-response['reward'])));at=67*max(0,(a.tick+1+66)//67)
            if feedback=='cost'and at>last_feedback:
                for port,value in [('quantity.reference.cue',0),('quantity.reference.resource',cost)]:
                    rec=a.quantity.input(port,value,at);requests.append({'id':int(rec['id']),'port':port,'payload':value,'tick':at})
                last_feedback=at
            elif feedback=='cost':drops.append({'kind':'raw_cost','slot':at,'rule':'FIRST_SAMPLE_PER_FIXED_NATIVE_SLOT','value':cost})
            rows.append({'index':index,'tick':a.tick,'visible_before_codec':list(visible),'observation_before':list(o),'sensor_q':q,'sensor_slot':slot,'native':native,'positive_load_command':valid,'native_command':command,'executed_torque':torque,'response':response,'raw_cost':cost,'feedback':feedback,'feedback_slot':at,'requests':requests,'dropped_samples':drops,'action_precedes_this_sensor_admission':slot>t,
              'motor_codec':motor_codec,'not_sent':['desired_action','private_B_raw','world_availability','future','seed','audit_utility','angular_velocity','cos(theta)']})
            prior=list(o);o=response['observation'];index+=1
            state={**old,'schema':'MI01.external.selector.exact.v1','environment':w.call('snapshot')['snapshot'],'previous_observation':prior,'last_observation':list(o),'index':index,'readout':'mi01_selector','mode':mode,'feedback':feedback,'last_object_input_tick':last_object,'last_feedback_input_tick':last_feedback,'last_motor_tick':a.tick,'motor_codec':motor_codec,'motor_wiring':'native_S_XY_positive_payload_to_2Y_torque_else_neutral0'if motor_codec=='signed_selector'else'native_S_XYpositiveY_payload_to_plus2_torque; negativeY_is_query_not_motor; absent_neutral0','ratio':'67 native ticks per0.05 external seconds; fixed phase29','codec_transition_from':old['readout']if old['readout']!='mi01_selector'else old.get('codec_transition_from'),'no_DEE_or_external_reset':True,'native_habitat':habitat};bridge.store(a,state)
        for row in rows:row['requests']=[{**r,'receipt':exact_receipt(a.world.runtime.receipt(r['id']))}for r in row['requests']]
        return{'identity':w.identity,'initial_native':before,'initial_environment':initial_env,'rows':rows,'native_habitat_frames':frames,'final_native':physical(a.world,occupation=True),'final_environment':state,
          'attribution':'Fixed external transduction. Native learned content/selection drives torque. Raw environmental cost is acquired by the existing quantity circuit, NOT asserted to optimize the selector. Neutral on absent/invalid output is external, not an intelligent native decision.'}
    finally:w.close()
