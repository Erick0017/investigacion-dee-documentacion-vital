"""One R9 continuation with a fixed common context sensor and actual consequences.

Context labels encode two equal peripheral raw values, never a chosen memory
port or a correct action. All contexts use the same body and motor reader.
The modelled environmental law is separate from the native decision.
"""
from pathlib import Path
import json
from dee_thinking.persistence import encode_metadata,decode_metadata
from capacidades import cierre_funcional_cf01 as cf
from capacidades import ente_evolucion_02_core as core
from capacidades import eo02_sensor_periferico as sensory
from capacidades.ente_evolucion_02 import LocalEnvironment,GateEnvironment
from capacidades import arquitectura_distribuida_mi02_r8 as body
KEY='DEE.Cognitive.System.1.1.MENTE_ACUMULATIVA.service.v1'
REVISION='MA.fixed_common_context.R9.3_social_probe'
CONTEXTS={'c1':(1,12),'c2':(2,16),'c3':(3,10),'c4':(4,18)}
def saved(a):
    q=dict(a.world.runtime.snapshot_metadata_entries)
    return decode_metadata(q[KEY])if KEY in q else None
def put(a,s):a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(json.loads(json.dumps(s,allow_nan=False))))
def state(a):
    cf.geometry(a)
    return {'revision':REVISION,'witness':cf.witness(a),'environment':saved(a),
      'scope':'One mutable relative reference and a prepared common context sensor. Multiple retained policies are a test, never assumed from four labels.'}
def session(a,*,situations,directory,feedback='real',actuator='closed',detailed=False):
    cf.geometry(a)
    if not 1<=len(situations)<=64:raise ValueError('One to64 bounded situations required')
    if feedback not in('real','omit','decoupled')or actuator not in('closed','nulled'):raise ValueError('Declared physical control required')
    # Validate the whole submitted batch before its first physical entry.
    for q in situations:
        if set(q)-{'contexto','valores','herramienta','regimen','privada_B'}or q.get('contexto')not in CONTEXTS:raise ValueError('Explicit c1..c4 and raw values required')
        if len(q.get('valores',[]))!=2 or any(type(v)is not int or not 0<=v<=64 for v in q['valores']):raise ValueError('Two independent raw integers0..64')
        if q.get('herramienta','puertas')not in('puertas','trabajadores','transaccion'):raise ValueError('Allowed local model or bounded real worker')
        if q.get('regimen','original')not in('original','revisado'):raise ValueError('Original or declared context1 environment revision')
        if q.get('regimen','original')=='revisado'and q['contexto']!='c1':raise ValueError('The fixed revision affects only the external context1 law')
        if 'privada_B'in q and(type(q['privada_B'])is not int or not 0<=q['privada_B']<=255):raise ValueError('Private current observation0..255, never a solved message')
    s=saved(a)or{'revision':REVISION,'attempts':0,'completed':0,'fixtures':{},'changes':[]}
    rows=[]
    for q in situations:
        cue,credit=CONTEXTS[q['contexto']]
        if q.get('regimen','original')=='revisado':credit=8
        raw=list(q['valores'])+[cue,cue]
        task=q.get('herramienta','puertas')
        key=q['contexto']+'.'+q.get('regimen','original')+'.'+task
        env=s['fixtures'].get(key)
        if env is None:
            env={'domain':task,'reference':credit,'created_at_tick':int(a.tick),'attempts':0,'completed_steps':0,'completed_transactions':0,'pending_transaction':None,'storage_epoch':key+'_'+str(a.tick),'environment_not_cognitive_memory':True}
            s['fixtures'][key]=env
        s['inflight']={'situation':q,'raw':raw,'start_tick':int(a.tick)};put(a,s)
        extra=sensory.submit_extra(a,raw)
        adapter=GateEnvironment(env,raw,lambda:put(a,s))
        if task in('trabajadores','transaccion'):adapter=LocalEnvironment(env,Path(directory)/env['storage_epoch'],raw,lambda:put(a,s))
        result=core.external_episode(a,public=raw[:2],reference=0,actuator=actuator,feedback=feedback,environment=adapter,private_B=q.get('privada_B'),trace=bool(detailed))
        extra['request_receipts']=body.receipts(a,extra['requests'])
        result.update(situation=q,raw_components=raw,sensory_extra=extra,external_event=adapter.last)
        s['attempts']+=1;s['completed']+=int(result['job_completed']);s['last_tick']=int(a.tick);s.pop('inflight',None);put(a,s)
        rows.append(result)
    return {'revision':REVISION,'rows':rows,'final':state(a),'attribution':'Native selection and update in one continued world; operator sets legitimate context and task, prepared sensor equal raw pair does not select a host memory/expert.'}
