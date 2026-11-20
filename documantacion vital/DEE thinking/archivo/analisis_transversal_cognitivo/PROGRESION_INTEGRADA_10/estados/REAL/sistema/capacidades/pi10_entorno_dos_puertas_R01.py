"""Fixed two-bin local environment, not a policy or DEE engine.

No DEE imports, shell, network, credentials or free-form file access. The
owner supplies an actual frozen Native observation BEFORE query1's choice;
this prepares a finite offer. Only a subsequent observed Native command picks
the attempted bin. The hidden available-bin value is never an actor input.

The 64-byte resource is host material whose content is the measured Native
RAW uint64 repeated eight times. It is not energy, food, a Native memory or
the expected response. File transfer is a real local effect of the fixed
transducer. physical_delivered and attributed_useful remain distinct.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os

VERSION='DEE.PI10.fixed_two_bin_environment.R01'
FOLDER='PI10_RECURSOS_R01'
MODES={'need','bypass','need_return'}
TOTAL=24

def need(ok,why):
    if not ok:raise ValueError(why)

def _sha(data):return hashlib.sha256(data).hexdigest()

def _read(p):return json.loads(p.read_text('utf-8-sig'))

def _write_new(p,v):
    with p.open('x',encoding='utf8')as f:
        json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())

def _regular_path(p):
    p=Path(p).absolute()
    for n in(p,*p.parents):
        need(not n.is_symlink(),'No symlink environment path, including a dangling link')
        if n.exists():need(not(getattr(n.lstat(),'st_file_attributes',0)&1024),'No reparse environment path')
    return p

def _home(home):
    p=_regular_path(home)
    need(p.is_dir(),'Existing owner-provided diagnostic/operational home required')
    return p.resolve(strict=True)

def _ordinal(n):
    need(type(n)is int and 0<=n<TOTAL,'Finite explicitly supplied PI10 offer ordinal0..23')
    return n

def _raw_uint(value):
    if type(value)is int:raw=value
    elif isinstance(value,str)and value.isdecimal():raw=int(value)
    else:raise ValueError('Exact Native uint64 RAW, never bool/float/expected bit')
    need(0<=raw<2**64,'RAW outside uint64');return raw

def _decode(raw):
    raw=_raw_uint(raw);ds=[(raw>>n)&15 for n in(48,52,56)]
    return {'raw':raw,'state':raw&0xffffffff,'s_reg':(raw>>32)&65535,
            'semantic':raw>>60,'direction':[n-16 if n&8 else n for n in ds]}

def _sample(sample):
    need(isinstance(sample,dict),'Actual frozen observation dictionary required')
    d=_decode(sample['raw'])
    for name in('state','s_reg','semantic','direction'):
        need(sample.get(name)==d[name],'Observation does not decode from actual RAW: '+name)
    need(sample.get('active')is(d['state']>0),'Observation active flag differs from RAW')
    need(type(sample.get('tick'))is int and sample['tick']>=0,'Actual Native sample tick required')
    need(isinstance(sample.get('site'),(list,tuple))and len(sample['site'])==3 and all(type(n)is int and 0<=n<67 for n in sample['site']),'Actual fixed Native site in N67')
    if d['raw']==0:bit=0;kind='actual_exact_RAW0_absence'
    elif d['state']>0 and d['semantic']==1 and d['direction']==[0,0,1]:bit=1;kind='actual_active_SEM1_plusZ'
    elif d['state']>0 and d['semantic']==1 and d['direction']==[1,0,0]:bit=0;kind='actual_active_SEM1_plusX'
    else:raise ValueError('NULL/unrecognized Native observation; no target or preferred-bit fallback')
    return d,bit,kind

def _offer(home,ordinal):return _home(home)/FOLDER/('oferta_%04d'%_ordinal(ordinal))

def _payload(raw):return _raw_uint(raw).to_bytes(8,'little',signed=False)*8

def prepare_offer(home,ordinal,actual_sample,gate_mode,*,actual_tick=None,query_tick=None):
    """Prepare only the environmental resource, before query1's decision.

    A/both need regimes follow the real RAW direction; bypass supplies bin0.
    No decision, target, expected response, future or bank argument is taken.
    An existing or partially written offer is preserved and never reused.
    """
    _ordinal(ordinal);need(gate_mode in MODES,'Known fixed environment regime')
    d,bit,kind=_sample(actual_sample)
    actual_tick=actual_sample['tick']if actual_tick is None else actual_tick
    query_tick=actual_sample['tick']+1 if query_tick is None else query_tick
    need(type(actual_tick)is int and actual_tick==actual_sample['tick'],'Immediate actual sample, no stale-time relabelling')
    need(type(query_tick)is int and actual_tick==query_tick-1,'Offer must be placed at measured q1-1, before query1 choice')
    root=_home(home);base=_regular_path(root/FOLDER)
    need(not base.exists()or base.is_dir(),'Environment root is not a directory')
    base.mkdir(exist_ok=True)
    target=_regular_path(base/('oferta_%04d'%ordinal));need(not target.exists(),'Used/partial offer preserved; no replenishment or retry')
    target.mkdir()
    for n in(0,1):(target/('puerta%d'%n)).mkdir()
    available=0 if gate_mode=='bypass'else bit
    data=_payload(d['raw']);resource=target/('puerta%d'%available)/'recurso64.bin'
    value={'schema':VERSION+'.offer','ordinal':ordinal,'gate_mode':gate_mode,
      'prepared_utc':datetime.now(timezone.utc).isoformat(),'prepared_tick':actual_tick,'query1_tick':query_tick,
      'sample':dict(actual_sample),'sample_RAW_sha256':_sha(d['raw'].to_bytes(8,'little')),
      'actual_preview_bit':bit,'actual_preview_kind':kind,'available_bin':available,
      'payload_source':'Actual frozen Native RAW uint64, little-endian8bytes repeated8; not a response target',
      'resource':{'relative_file':'puerta%d/recurso64.bin'%available,'bytes':64,'sha256':_sha(data)},
      'supply':'One new finite host-environment offer; independent of ancestor D/FI/C2C counters',
      'prepared_environment_not_learned':True,'available_bin_not_Native_input':True,'no_actor_policy_or_bank_update':True}
    _write_new(target/'PREPARACION_INTENTADA.json',value)
    with resource.open('xb')as f:f.write(data);f.flush();os.fsync(f.fileno())
    need(resource.stat().st_size==64 and _sha(resource.read_bytes())==value['resource']['sha256'],'Resource write/read mismatch')
    _write_new(target/'OFERTA.json',value)
    return {**value,'environment_relative_home':FOLDER+'/oferta_%04d'%ordinal,
      'manifest_file':str(target/'OFERTA.json'),'manifest_sha256':_sha((target/'OFERTA.json').read_bytes()),
      'new_Native_inputs':0,'new_Native_ticks':0}

def _checked_offer(home,ordinal):
    target=_offer(home,ordinal);manifest=_regular_path(target/'OFERTA.json')
    need(manifest.is_file(),'Complete prepared offer required; partial/future offer is not invented')
    v=_read(manifest);need(v.get('schema')==VERSION+'.offer'and v['ordinal']==ordinal and v['gate_mode']in MODES,'Fixed own offer identity/regime')
    d,bit,_=_sample(v['sample']);available=0 if v['gate_mode']=='bypass'else bit
    need(v['available_bin']==available and v['resource']['relative_file']=='puerta%d/recurso64.bin'%available,'Offer availability law changed')
    data=_payload(d['raw']);need(v['resource']['bytes']==64 and v['resource']['sha256']==_sha(data),'Offer must contain actual Native data, never expected response')
    return target,v,data

def _command(actual_route,native_choice,reader_observation,command_valid,command_receipt):
    need(actual_route is None or(type(actual_route)is int and actual_route in(0,1)),'Only two fixed routes or no command')
    native_valid=type(native_choice)is int and native_choice in(-1,0,1)
    if reader_observation is not None:
        r=_decode(reader_observation['raw'])
        for name in('state','s_reg','semantic','direction'):need(reader_observation.get(name)==r[name],'Reader observation RAW mismatch')
        signature=r['state']>0 and r['semantic']==1 and r['direction'][0]in(-1,0,1)and r['direction'][1]==1 and r['direction'][2]in(-1,0)
        need(native_valid==bool(signature),'Raw Native output validity is not an expected action')
        if signature:need(native_choice==r['direction'][0],'Fixed central Native choice decoder')
    if command_valid is None:command_valid=native_valid
    need(type(command_valid)is bool and(not command_valid or native_valid),'Explicit Native command validity')
    if command_receipt is not None:
        need(isinstance(command_receipt,dict)and command_receipt.get('status')in('applied','rejected_conflict','rejected_invalid','rejected_past','rejected_closed','rejected_quota'),'Terminal own command/efference receipt required')
        if command_receipt['status']!='applied':command_valid=False
    route=(1 if native_choice==1 else 0)if command_valid else None
    need(actual_route==route,'Route must follow the observed Native output; no fallback or target-based correction')
    return route,command_valid

def act_on_observed_motor(home,ordinal,actual_route_orNone,*,native_choice=None,reader_observation=None,command_valid=None,q1_valid=True,fi_choice=None,fi_required=False,actual_tick=None,command_receipt=None):
    """Attempt only the selected bin. No expected/optimal-route input exists.

    Resource transfer is preserved even if query1 was NULL. Attribution and
    the declared whole-task failure require a valid query1 selection as well;
    a neutral bridge after silence is not credited to DEE as chosen NoQuery.
    """
    target,v,data=_checked_offer(home,ordinal)
    need(not(target/'ACCION_INTENTADA.json').exists()and not(target/'RESULTADO.json').exists(),'No repeated action or replay into an already-used offer')
    need(type(q1_valid)is bool and type(fi_required)is bool,'Explicit validity/work contract flags')
    need(type(actual_tick)is int and actual_tick>=v['query1_tick'],'Actual output tick after preparation required')
    route,valid=_command(actual_route_orNone,native_choice,reader_observation,command_valid,command_receipt)
    fiok=(not fi_required)or(type(fi_choice)is int and fi_choice==1)
    intent={'schema':VERSION+'.action_intent','ordinal':ordinal,'actual_tick':actual_tick,
      'native_choice':native_choice,'observed_reader':reader_observation,'command_receipt':command_receipt,
      'actual_route':route,'command_valid':valid,'q1_valid':q1_valid,'FI_required':fi_required,'actual_Native_FI_choice':fi_choice,
      'only_selected_bin_attempted':True,'no_fallback_or_policy':True,'at_utc':datetime.now(timezone.utc).isoformat()}
    _write_new(target/'ACCION_INTENTADA.json',intent)
    delivered=False;product=None;attempted=None
    if route is not None:
        attempted=_regular_path(target/('puerta%d'%route)/'recurso64.bin')
        if fiok and attempted.exists():
            need(attempted.is_file()and attempted.read_bytes()==data,'Resource content changed before Native command')
            destination=target/'entregado64.bin';need(not destination.exists(),'Delivered resource already exists')
            os.replace(attempted,destination)
            need(destination.read_bytes()==data and not attempted.exists(),'Actual resource move/readback failed')
            delivered=True;product={'relative_file':'entregado64.bin','file':str(destination),'bytes':64,'sha256':_sha(destination.read_bytes()),'payload_source':'Measured Native RAW from the prepared offer'}
    attributed=bool(delivered and q1_valid and valid)
    result={'schema':VERSION+'.result','ordinal':ordinal,'gate_mode':v['gate_mode'],
      'offer_manifest_sha256':_sha((target/'OFERTA.json').read_bytes()),'available_bin':v['available_bin'],
      'prepared_tick':v['prepared_tick'],'action_tick':actual_tick,'actual_route':route,
      'Native_q2_choice':native_choice,'Native_command_valid':valid,'Native_q1_valid':q1_valid,
      'FI_required':fi_required,'actual_Native_FI_choice':fi_choice,'FI_work_satisfied':fiok,
      'selected_bin_had_resource':route==v['available_bin']if route is not None else False,
      'physical_delivered':delivered,'attributed_useful':attributed,'actual_failed':not attributed,
      'product':product,'attempted_only_selected_bin':None if attempted is None else str(attempted),
      'process_error':None,'new_Native_inputs':0,'new_Native_ticks':0,
      'scope':'Prepared host resource law and fixed output transduction; no cognitive policy, bank choice or Native memory write.'}
    _write_new(target/'RESULTADO.json',result)
    return result

def verify_offer(home,ordinal):
    """Passive file/readback check; no action, replenishment or DEE call."""
    target,v,data=_checked_offer(home,ordinal)
    result_file=target/'RESULTADO.json'
    if not result_file.exists():
        source=target/v['resource']['relative_file'];need(source.is_file()and source.read_bytes()==data,'Unconsumed prepared resource missing/changed')
        return {'schema':VERSION+'.verification','ordinal':ordinal,'action_complete':False,'resource_present':True,'Native_executed':False}
    result=_read(result_file)
    need(result['schema']==VERSION+'.result'and result['ordinal']==ordinal,'Own final result required')
    expected=bool(result['Native_command_valid']and result['actual_route']==v['available_bin']and result['FI_work_satisfied'])
    need(result['physical_delivered']is expected and result['attributed_useful']is bool(expected and result['Native_q1_valid']),'Outcome/attribution law changed')
    source=target/v['resource']['relative_file'];product=target/'entregado64.bin'
    if expected:need(not source.exists()and product.is_file()and product.read_bytes()==data,'Delivered bytes not conserved')
    else:need(source.is_file()and source.read_bytes()==data and not product.exists(),'Failed attempt must not consume or fabricate a resource')
    need(result['actual_failed']is(not result['attributed_useful']),'Whole-task consequence mismatch')
    return {'schema':VERSION+'.verification','ordinal':ordinal,'action_complete':True,'physical_delivered':expected,
      'attributed_useful':result['attributed_useful'],'product_sha256':_sha(data)if expected else None,'Native_executed':False}
