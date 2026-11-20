"""Freeze a literal APD service curriculum, never choose a DEE response.

Pure standard-library preparation: no DEE, Store, subprocess, file tools or
native ticks. The selected physical API supplies the templates only after its
contract exists. Audit tags, timing and seeds are not part of actor payloads.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path

FORBIDDEN={'expected','target','evaluator_target','oracle','future','seed','case_id','respuesta_esperada','ruta_correcta','accion_optima'}

def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)

def inspect_literal(value):
    if isinstance(value,dict):
        if any(not isinstance(k,str)or k.lower()in FORBIDDEN for k in value):raise ValueError('Evaluator fields are not actor payloads')
        for v in value.values():inspect_literal(v)
    elif isinstance(value,list):
        for v in value:inspect_literal(v)
    elif type(value)not in(str,int,bool,type(None)):raise ValueError('Literal integer/string/boolean/null actor payloads only')

def payload(value,allowed_modes):
    inspect_literal(value)
    if not isinstance(value,dict)or set(value)-{'operacion','situaciones','actuador','retorno'}or value.get('operacion')!='sesion':raise ValueError('Existing session envelope only')
    rows=value.get('situaciones')
    if not isinstance(rows,list)or not 1<=len(rows)<=8 or any(not isinstance(r,dict)or r.get('modo')not in allowed_modes for r in rows):raise ValueError('1..8 literal rows admitted by an explicit candidate contract')
    if value.get('actuador','closed')not in('closed','nulled')or value.get('retorno','real')not in('real','omit'):raise ValueError('Declared actuator/return modes only')
    if len(canonical(value).encode('utf8'))>8192:raise ValueError('Existing8192-byte transport bound exceeded')
    return copy.deepcopy(value)

def build(config,*,draft=False):
    if config.get('freeze_status')!='READY_FOR_RESERVES'and not draft:raise ValueError('No physical API/candidate freeze: protocol is not executable')
    if config.get('request_prefix')!='apd60_':raise ValueError('Fresh APD prefix required; inherited MUFI IDs cannot be replayed')
    if config.get('nominal_events',480)!=480:raise ValueError('This bounded preparation uses480 opportunities')
    horizon=config.get('seconds',3900)
    if type(horizon)is not int or not 3720<=horizon<=4200:raise ValueError('Fixed sixty-minute horizon with declared pause/reload margin required')
    life=config.get('life_id')
    if not isinstance(life,str)or not life or any(c not in'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-'for c in life):raise ValueError('Explicit portable candidate identity required')
    modes=config.get('admitted_modes')
    if not isinstance(modes,list)or not modes or any(not isinstance(x,str)for x in modes):raise ValueError('Selected physical API mode names must be provided, not guessed')
    families=config.get('families')
    if not isinstance(families,dict)or not families:raise ValueError('Actual literal templates are required')
    cycle=config.get('family_cycle')
    if not isinstance(cycle,list)or not cycle or any(f not in families for f in cycle):raise ValueError('Explicit answer-independent family order required')
    normalized={}
    for family,templates in families.items():
        if not isinstance(family,str)or not isinstance(templates,list)or not templates:raise ValueError('Each supplied family must contain a real literal request')
        normalized[family]=[payload(v,modes)for v in templates]
    # Fixed exposure windows; later answers cannot reschedule or replace them.
    end=horizon-230;begins=(5,1300,2600);ends=(1140,2440,end)
    events=[];usage={f:0 for f in normalized}
    for regime,(begin,finish)in enumerate(zip(begins,ends),1):
        if finish<=begin:raise ValueError('Invalid fixed regime')
        for i in range(160):
            family=cycle[(len(events))%len(cycle)];templates=normalized[family];value=templates[usage[family]%len(templates)];usage[family]+=1
            index=len(events);events.append({'id':'apd60_'+str(index).zfill(5),'at_seconds':round(begin+(finish-begin)*(i+.5)/160,6),'regime':regime,'client':index%2,'audit_family_not_actor_input':family,'payload':copy.deepcopy(value)})
    fixed=config.get('fixed_events',[])
    if not isinstance(fixed,list):raise ValueError('Literal fixed environmental/teaching events only')
    occupied=set()
    for item in fixed:
        if not isinstance(item,dict)or set(item)-{'at_seconds','purpose','payload'}:raise ValueError('Fixed event schema')
        when=item.get('at_seconds')
        if type(when)not in(int,float)or not 0<when<horizon-120:raise ValueError('Fixed event outside final arrival window')
        available=[e for e in events if e['id']not in occupied]
        chosen=min(available,key=lambda e:(abs(e['at_seconds']-when),e['id']));occupied.add(chosen['id'])
        chosen.update(at_seconds=float(when),audit_family_not_actor_input=item.get('purpose','declared_fixed_event'),payload=payload(item['payload'],modes))
    events.sort(key=lambda e:(e['at_seconds'],e['id']))
    frozen={'schema':'DEE.APD01.prospective_service_curriculum.v1','status':'DRAFT_ONLY_NOT_EXECUTABLE'if draft else'FROZEN_FOR_ONE_SELECTED_CANDIDATE',
        'life_id':life,'backend':config.get('backend','mente_unificada'),'seconds':horizon,'nominal_events':len(events),'request_prefix':'apd60_',
        'events':events,'admitted_modes':modes,'regimes':[{'id':i,'planned_events':sum(e['regime']==i for e in events)}for i in(1,2,3)],
        'source_contract':config.get('source_contract'),'initial_cut':config.get('initial_cut'),
        'idle_interval_seconds':.1,'idle_quantum_ticks':1,'save_seconds':60,
        'technical_pause_windows':[600,1800,3000],'pause_seconds_after_actual_safe_boundary':3,
        'maximum_drain_seconds':120,'export_client_wait_seconds':120,'same_life_process_restart_at_second_pause':True,
        'pending_contract':config.get('pending_contract','UNDECIDED_DO_NOT_INVENT_A_PENDING_TOOL'),
        'assistance':'All exposure, literal templates, environmental changes and explicit teaching are prepared. No answer, useful-route calculation, favorable branch selection or response-dependent scheduling is implemented here.',
        'measurement':'Requested/admitted/rejected/completed/native-valid/correct/useful and cost are separate. Whole pause/reload intervals are discounted. No failure is removed and no horizon is extended to obtain success.',
        'configuration_sha256':hashlib.sha256(canonical(config).encode('utf8')).hexdigest(),'new_native_ticks':0}
    return frozen

def self_test():
    # Synthetic transport fixtures only. They are never sent to a DEE world or
    # claimed to teach words, perform arithmetic, choose routes or learn costs.
    base={'freeze_status':'DRAFT','request_prefix':'apd60_','life_id':'INSTRUMENT_ONLY','admitted_modes':['fixture'],
          'families':{'literal':[{'operacion':'sesion','situaciones':[{'modo':'fixture','formas':[11,7],'operandos':[3,8]}]}]},'family_cycle':['literal']}
    result=build(base,draft=True);checks={'480_events':len(result['events'])==480,'three_regimes':len(result['regimes'])==3,'unique_ids':len({e['id']for e in result['events']})==480,
        'all_payloads_literal_unchanged':all(e['payload']==base['families']['literal'][0]for e in result['events']),'auditor_fields_not_actor':all(set(e['payload'])=={'operacion','situaciones'}for e in result['events'])}
    for name,bad in [('target',{'operacion':'sesion','situaciones':[{'modo':'fixture','target':4}]}),('oversized',{'operacion':'sesion','situaciones':[{'modo':'fixture','text':'x'*8192}]}),('shell',{'operacion':'shell','situaciones':[{'modo':'fixture'}]})]:
        try:payload(bad,['fixture']);checks['reject_'+name]=False
        except ValueError:checks['reject_'+name]=True
    try:build(base);checks['draft_cannot_be_executed']=False
    except ValueError:checks['draft_cannot_be_executed']=True
    return {'schema':'DEE.APD01.protocol_builder.instrument_tests.v1','new_native_ticks':0,'DEE_imports':0,'checks':checks,'all_true':all(checks.values())}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--configuracion',type=Path);p.add_argument('--salida',type=Path);p.add_argument('--borrador',action='store_true');p.add_argument('--self-test',action='store_true');a=p.parse_args()
    if a.self_test:value=self_test()
    else:
        if a.configuracion is None or a.salida is None:p.error('--configuracion and --salida required')
        value=build(json.loads(a.configuracion.read_bytes()),draft=a.borrador)
    if a.salida:
        a.salida.parent.mkdir(parents=True,exist_ok=True)
        with a.salida.open('x',encoding='utf8')as f:json.dump(value,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(value if a.self_test else{'file':str(a.salida),'sha256':hashlib.sha256(a.salida.read_bytes()).hexdigest(),'status':value['status'],'events':len(value['events']),'new_native_ticks':0},ensure_ascii=False))
    return 0 if not a.self_test or value['all_true']else 1

if __name__=='__main__':raise SystemExit(main())
