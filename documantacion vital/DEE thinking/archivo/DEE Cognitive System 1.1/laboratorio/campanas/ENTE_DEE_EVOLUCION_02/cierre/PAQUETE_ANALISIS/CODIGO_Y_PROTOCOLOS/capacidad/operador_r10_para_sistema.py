"""Operational R10 adapter candidate. Copy alongside sensorial_r10.py only
after the closed scientific cut; no laboratory imports or absolute paths.

This API continues a compatible complete R10 snapshot. It never creates or
substitutes a world if loading/preflight fails, and never writes learned RAW.
"""
import json
from dee_thinking.persistence import encode_metadata,decode_metadata
from capacidades import sensorial_r10 as sensor
from capacidades import integracion_distribuida_mi02_r6 as native
from capacidades import cierre_funcional_cf01 as cf
from capacidades import ente_evolucion_02_core as core
from app.native_tools import physical
KEY='DEE.Cognitive.System.1.1.EO02.sensorialR10.service.v1'
REVISION='EO02.R10.operative_adapter.1'
def check(a):
    s=native.saved(a)
    if not s or s.get('geometry',{}).get('experimental_architecture')!='EO02_SENSORIAL_R10_T0':
        raise ValueError('This function requires the complete explicitly new R10 architecture; EO01/EO02 R9 is not silently substituted')
    cf.geometry(a);return s['geometry']
def saved(a):
    entries=dict(a.world.runtime.snapshot_metadata_entries)
    return decode_metadata(entries[KEY])if KEY in entries else None
def put(a,s):a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(json.loads(json.dumps(s,allow_nan=False))))
def state(a):
    g=check(a)
    return{'revision':REVISION,'architecture':g['architecture_revision'],'physical':physical(a.world,occupation=True),
      'witness':cf.witness(a),'service':saved(a),'assistance':'Prepared remote fan-in4 per side, six generic0 carriers, inherited2-tick fixed motor reader, external gate and opportunities. Own/context contents are acquired by this distinct life; not EO01 memories.'}
class Gate:
    def __init__(self,components,reference):self.components=list(components);self.reference=reference
    def act(self,*,formed,executed,posture,public,native_tick):
        # ENVIRONMENT only, after the action. The aggregate is never submitted.
        L=sum(self.components[::2]);R=sum(self.components[1::2]);gate=1 if L+self.reference>=R else-1
        complete=executed is not None and executed==gate
        before={'law':'R10.eight_component_gate.v1','raw_components':self.components,'reference':self.reference,'gate_not_injected':gate,'calculated_after_emission':True}
        observed={'tick':native_tick,'movement':executed is not None,'contact':executed is not None and not complete,'actuator_posture':posture,
          'job_completed':complete,'effect':'passed'if complete else'contact'if executed is not None else'no_movement'}
        return{'before':before,'after':{**before,'observed':observed},'observed':observed}
def classify(a,*,observations,reference=4,actuator='closed',feedback='real',trace=False):
    check(a)
    if not 1<=len(observations)<=32 or any(len(v)!=8 or any(type(x)is not int or not 0<=x<=32 for x in v)for v in observations):
        raise ValueError('One to32 frames of8 separate raw integers0..32 are required; larger admitted ranges are not a performance guarantee')
    if type(reference)is not int or not-64<=reference<=64:raise ValueError('Explicit external calibration required')
    if actuator not in('closed','nulled')or feedback not in('real','omit','decoupled'):raise ValueError('Explicit finite physical control mode')
    s=saved(a)or{'revision':REVISION,'attempts':0,'valid':0,'completed':0,'reference':4,'external_changes':[]}
    if reference!=s['reference']:
        s['external_changes'].append({'at_tick':int(a.tick),'before':s['reference'],'after':reference,'external_environment_only':True});s['reference']=reference
    rows=[]
    for values in observations:
        requests=sensor.submit(a,list(values))
        result=core.external_episode(a,public=[0,0],reference=reference,actuator=actuator,feedback=feedback,trace=trace,environment=Gate(values,reference))
        # Fixed zero public packets are resources, not solved aggregate values.
        from capacidades.arquitectura_distribuida_mi02_r8 import receipts
        s['attempts']+=1;s['valid']+=int(result['formed_native_command']is not None);s['completed']+=int(result['job_completed']);s['last_tick']=int(a.tick)
        s['last_components']=list(values);put(a,s)
        rows.append({'raw_components':list(values),'sensory_extra':requests,'sensory_extra_receipts':receipts(a,requests['requests']),'native':result})
    return{'revision':REVISION,'rows':rows,'final':state(a),
      'scope':'Eight-variable material sum-and-history comparison under the declared phase/geometry, not8independent learned policies, joint32capacity, language or general control.'}
