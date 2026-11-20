"""Fixed sensory/motor instrument on an actual lived MI02 native body.

No controller, desired action, target, private social content or historical
answer enters this adapter. Separate-process published Pendulum is reused.
"""
import json
from dee_thinking.persistence import encode_metadata,decode_metadata
from capacidades.habitat_externo_01 import _Worker
from capacidades import arquitectura_distribuida_mi02_r6 as body
from app.native_tools import physical
KEY='DEE.Cognitive.System.1.1.MI02.external.v1'

def saved(a):
    m=dict(a.world.runtime.snapshot_metadata_entries)
    return json.loads(decode_metadata(m[KEY])['bridge_state_json'])if KEY in m else None

def put(a,s):a.world.runtime.set_snapshot_metadata(KEY,encode_metadata({'bridge_state_json':json.dumps(s,allow_nan=False,ensure_ascii=False)}))

def state(a):return{'bridge':saved(a),'native':body.inspect(a),'passive_no_new_ticks':True}

def run(a,*,steps=16,seed=82001,reset_environment=False,mode='closed',sensor_mode='all',ticks_per_step=19):
    if type(steps)is not int or not 1<=steps<=128 or mode not in('closed','nulled','delay1')or sensor_mode not in('all','omit'):raise ValueError('Declared finite bridge/control required')
    if ticks_per_step not in(17,19,23):raise ValueError('Predeclared fixed temporal ratios only')
    s=body.get(a)
    if s is None:raise ValueError('Lived MI02 body required, no new universe created')
    old=saved(a);w=_Worker();rows=[];before=physical(a.world,occupation=True)
    try:
        if old and not reset_environment:
            o=w.call('restore',snapshot=old['environment'])['observation'];prior=old['previous_observation'];index=old['index']
        else:
            o=w.call('reset',seed=seed,g=10.0)['observation'];prior=list(o);index=0
        initial=w.call('snapshot')['snapshot']
        if initial['elapsed']+steps>200:raise ValueError('External episode horizon; explicit reset required, never reset DEE')
        for k in range(steps):
            t=a.tick;visible=prior if mode=='delay1'else o
            # Three legitimate measurements, no relational/optimal-action sensor.
            prepared_sensors=s.get('external_sensors')
            # The unified profile has prepared transient sensory channels,
            # distinct from its persistent social context and motor ports.
            # Its fixed two-channel codec deliberately discards angular speed;
            # no posthoc choice of the currently useful observation is made.
            sensor=[(v['name'],None,visible[v['observation_index']],float(v['scale']))for v in prepared_sensors[:2]]if prepared_sensors else[('sin',1,visible[1],1.0),('cos',-1,visible[0],1.0),('omega',0,visible[2],8.0)]
            requests=[];coded=[]
            for name,r,v,scale in sensor:
                value=max(0,min(20,round(10+10*float(v)/scale)))
                if prepared_sensors:
                    port=next(v for v in prepared_sensors if v['name']==name);origin=port['origin'];direction=port['direction']
                else:
                    P=body.xyz(a,s['Q'],(r,-1,-1));direction=(-r,0,1)if r else(-1,0,1);origin=body.xyz(a,P,direction,-3)
                coded.append({'variable':name,'visible':v,'scale':scale,'payload':value,'resolution':0.1*scale,'saturated':abs(v)>scale,'origin':origin,'direction':list(direction)})
                if sensor_mode=='all':requests.append(body.send(a,'MI02.external.sensor.'+name,origin,direction,t+1,value))
            action_delay=8 if prepared_sensors else 7
            a.run_until(t+action_delay);read=body.obs(a,s['Q']);valid=body.qualified(read);command=(2 if read['direction'][0]>=0 else-2)if valid else 0
            torque=0 if mode=='nulled'else command
            response=w.call('step',torque=torque)
            a.run_until(t+ticks_per_step)
            rows.append({'index':index,'tick_sensor':t+1,'tick_action':t+action_delay,'tick_end':a.tick,'observation_before':list(o),'visible':list(visible),'codec':coded,'requests':body.receipts(a,requests),'native':read,'qualified_material_output':valid,'native_torque':command,'executed_torque':torque,'response':response,'mode':mode,'sensor_mode':sensor_mode,'codec_revision':'MI02.fixed.context2.r3'if prepared_sensors else'MI02.fixed.legacy3.r2','discarded_measurements':['angular_velocity']if prepared_sensors else[]})
            prior=list(o);o=response['observation'];index+=1
            current={'schema':'MI02.external.fixedcodec.r3','environment':w.call('snapshot')['snapshot'],'last_observation':list(o),'previous_observation':prior,'index':index,'mode':mode,'sensor_mode':sensor_mode,'ticks_per_step':ticks_per_step,'neutral_rule':'Only absent/invalid material output gives external zero torque. No intelligent waiting is inferred.','reset_environment_only':bool(reset_environment),'no_policy_or_reward_update':True,'codec_revision':'context2'if prepared_sensors else'legacy3'};put(a,current)
        return{'identity':w.identity,'initial_native':before,'initial_environment':initial,'rows':rows,'final_native':physical(a.world,occupation=True),'final_bridge':current,'attribution':'Prepared limited sensors and signed actuator; actual DEE state selects material directions. Not a learned Pendulum policy. Raw external consequences are not transformed into a correct memory/selector update by the host.'}
    finally:w.close()
