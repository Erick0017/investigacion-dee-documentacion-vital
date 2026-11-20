"""PI04 E3: same useful apparatus, contingent versus frozen replay returns.

Opt-in through the existing owner. No engine import at module load, no life
creation/promotion, no action policy and no reset of inherited PI03 resources.
The Native opportunity body is extracted from frozen PI03 and preserved below;
only its return selection, pre-query calendar guard and record label differ.
"""
from pathlib import Path
import hashlib,json,os

VERSION='PI04.E3.contingency_extension.R01'
KEY='DEE.Cognitive.PI04.E3.contingency.R01'
FOLDER='PI04_E3_CONTINGENCIA_R01'
ADMIT='eci01-pi04-e3-admitir'
OPPORTUNITY='eci01-pi04-e3-oportunidad'
STATE='eci01-pi04-e3-estado'
MODES={ADMIT,OPPORTUNITY,STATE}
PREFIX='ECI02_PI03_REPRO_PI04_'
SOURCE_T=775355
SOURCE_RAW='70f9c38f09267f65706330129ebf51a08518455cd70a9291dad410258f9e136f'
SOURCE_CLOCKS='ac1e25f8c35be3844bd54f002c3ce6bf5e49c70aff3bf561622e265056960ecd'
SOURCE_TASK_SHA='b136e79abb6e07efcd8b69da0a37cc8d667d7140788e18c490975f8e2a88e40b'
COUNT=18
# This is apparatus configuration, not the participant's policy.
SUPPLIES=[{'after_E3':2,'cantidad':4,'conexion':-1,'demora_periodos':2},
          {'after_E3':6,'cantidad':4,'conexion':1,'demora_periodos':4},
          {'after_E3':10,'cantidad':4,'conexion':-1,'demora_periodos':2},
          {'after_E3':14,'cantidad':4,'conexion':1,'demora_periodos':4}]
SPECS=[{'connection':1,'delay_laps':4}for _ in range(2)]+[
       {'connection':r['conexion'],'delay_laps':r['demora_periodos']}for r in SUPPLIES for _ in range(r['cantidad'])]

def _task():
    from capacidades import pi03_tarea_diferida_R02 as task
    return task
def _pure():
    from capacidades import e3_retorno_desacoplado_R01 as pure
    return pure
def _guard(*args,**kwargs):return _task()._guard(*args,**kwargs)
def _get(*args,**kwargs):return _task()._get(*args,**kwargs)
def _save(*args,**kwargs):return _task()._save(*args,**kwargs)
def _record(*args,**kwargs):return _task()._record(*args,**kwargs)
def _r1():return _task()._r1()
def _helper():return _task()._helper()
def _device(*args,**kwargs):return _task()._device(*args,**kwargs)
def _bank_observations(*args,**kwargs):return _task()._bank_observations(*args,**kwargs)
def _sha(data):return hashlib.sha256(data).hexdigest()
def _entries(a):return dict(a.world.runtime.snapshot_metadata_entries)
def _e3_get(a):
    from dee_thinking.persistence import decode_metadata
    entries=_entries(a)
    if KEY not in entries:raise ValueError('Explicit E3 admission required; never infer a control from filenames')
    m=decode_metadata(entries[KEY])
    if m['version']!=VERSION:raise ValueError('Exact E3 revision required')
    return m
def _e3_save(a,m):
    from dee_thinking.persistence import encode_metadata
    a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(m))
def _e3_record(a,m,directory,event):
    from dee_thinking.persistence import encode_metadata
    home=Path(directory)/FOLDER;home.mkdir(parents=True,exist_ok=True)
    data=(json.dumps({'index':m['log_count'],'tick':int(a.tick),**event},ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode('utf-8')
    count=m['log_count']+1;chain=_sha(bytes.fromhex(m['log_chain_sha256'])+data)
    encode_metadata(dict(m,log_count=count,log_chain_sha256=chain))
    with(home/'eventos.jsonl').open('ab')as f:f.write(data);f.flush();os.fsync(f.fileno())
    m['log_count']=count;m['log_chain_sha256']=chain;_e3_save(a,m)

def validate_literal(row):
    if type(row)is not dict:raise ValueError('Exact E3 literal required')
    mode=row.get('modo')
    if mode==ADMIT:
        if row.get('brazo')=='real'and set(row)=={'modo','brazo'}:return
        if row.get('brazo')=='desacoplado'and set(row)=={'modo','brazo','plan'}:
            p=_pure().validate_plan(_pure().unpack_plan(row['plan']))
            if len(p['slots'])!=COUNT:raise ValueError('Exactly18 signals from the full included real history required')
            for i,s in enumerate(p['slots']):
                if s['ordinal']!=i or s['calendar']['delay_laps']!=SPECS[i]['delay_laps']:raise ValueError('Plan differs from frozen18-opportunity environment')
            return
        raise ValueError('Real admission or explicit sealed control plan only; no arbitrary input file/action/target')
    if mode in(OPPORTUNITY,STATE)and set(row)=={'modo'}:return
    raise ValueError('Unknown E3 operation or unapproved fields')

def _identity(a,directory=None):
    if _sha(Path(_task().__file__).read_bytes())!=SOURCE_TASK_SHA:raise ValueError('Frozen inherited opportunity source changed; no unreviewed body/API substitution')
    p,ph,r01,identity=_guard(a,directory,material=True)
    if not identity['life_id'].startswith(PREFIX):raise ValueError('E3 only explicit PI04 diagnostic/candidate clone, never ACTIVO or another inherited life')
    if tuple(r01['origin'])!=(19,54,5)or int(a.world.runtime.dimension)!=67:raise ValueError('Inherited Q geometry/N differ; no replacement architecture')
    return p,ph,r01,identity
def _closed_task(a,directory=None):
    state=_get(a)
    if state.get('control')!='real'or state.get('serie')!='continuous'or not state.get('ready')or any(state.get(k)for k in('pending','uncertain','halted_reason','supply_pending')):
        raise ValueError('Closed inherited real continuous task required; no uncertain retry or reset')
    from capacidades import pi03_proteccion_cola_OP3 as support
    guard=support.get(a)
    if not guard.get('ready')or guard.get('uncertain'):raise ValueError('Qualified inherited post-read P0 support required, never reinstall it silently')
    legacy_key='DEE.Cognitive.PI02.continuous_workbench.R04'
    entries=_entries(a)
    if legacy_key in entries:
        legacy=_task()._decode(entries[legacy_key])
        if legacy.get('enabled')or legacy.get('active')is not None:raise ValueError('E3 requires the old O/H bridge explicitly paused with no unfinished FI job; do not hide competing scheduled work')
    if directory is not None:_task().operational_dependencies(a,directory)
    return state
def _connection(device,index):
    start=0
    for b in device.m['blocks']:
        end=start+b['opportunities']
        if start<=index<end:return b['connected_motor']
        start=end
    raise ValueError('No real environmental resource block for this opportunity')
def _environment(a,directory,m):
    state=_closed_task(a,directory);ordinal=m['ordinal']
    if ordinal>=COUNT:raise ValueError('Frozen18 opportunities exhausted; no implicit extension')
    if state['opportunity']!=m['start_opportunity']+ordinal:raise ValueError('E3/task cumulative history differs')
    if state['opportunity']>=len(state['schedule']):raise ValueError('Next explicit R03 supply required before E3 opportunity')
    spec=SPECS[ordinal];device=_device(directory)
    if state['schedule'][state['opportunity']]['delay_laps']!=spec['delay_laps']or _connection(device,state['opportunity'])!=spec['connection']:
        raise ValueError('Environmental condition differs from predeclared E3 block; do not adapt to a response')
    return state
def _normalize_calendar(calendar,banks,start):
    return {k:int(calendar[k])for k in('query_tick','query_read_tick','outcome_injection_tick','contact_tick','delay_laps')}|{
            'reference_contact_phase':(int(banks[0]['clock'])+int(calendar['contact_tick'])-int(start))%782}
def _e3_prequery(a,calendar,banks,start):
    m=_e3_get(a);normalized=_pure().checked_calendar(_normalize_calendar(calendar,banks,start))
    if not m.get('uncertain')or not m.get('pending'):raise ValueError('Durable E3 opportunity intent required')
    if m['arm']=='desacoplado':_pure().replay_signal(m['plan'],m['ordinal'],normalized)
    return normalized
def _e3_feedback(a,actual_failed,calendar,banks,start):
    if type(actual_failed)is not bool:raise ValueError('Actual environmental consequence must remain a bool')
    m=_e3_get(a);normalized=_normalize_calendar(calendar,banks,start)
    return actual_failed if m['arm']=='real'else _pure().replay_signal(m['plan'],m['ordinal'],normalized)

def validate(a,row):
    validate_literal(row)
    if row['modo']==STATE:return
    _identity(a)
    if row['modo']==ADMIT:
        if KEY in _entries(a):raise ValueError('E3 already admitted; no reset/replacement of its acquired history')
        if int(a.tick)!=SOURCE_T:raise ValueError('Frozen E3 must start from the complete actual775355 cut')
        m=_closed_task(a)
        if m['opportunity']!=24 or len(m['schedule'])!=26:raise ValueError('Preserve24completed/twoavailable source counters')
        return
    m=_e3_get(a)
    if m.get('pending')or m.get('uncertain')or m.get('halted_reason'):raise ValueError('Preserved E3 pending/uncertain/halted operation; no resend')
    if m['ordinal']>=COUNT:raise ValueError('Frozen E3 opportunity limit reached')
    _task().validate(a,{'modo':_task().OPPORTUNITY})

def admit(a,row,directory):
    validate(a,row);_identity(a,directory);state=_closed_task(a,directory)
    from app.native_tools import physical
    before=physical(a.world)
    if before['RAW_sha256']!=SOURCE_RAW or before['clocks_sha256']!=SOURCE_CLOCKS:raise ValueError('Source physical identity differs from frozen775355; do not choose a latest tick')
    folder=Path(directory)/FOLDER
    if folder.exists():raise ValueError('Unmatched E3 files preserved; no overwrite')
    m={'version':VERSION,'campaign':'PROGRESION_INTEGRADA_04','arm':row['brazo'],'life_id':_identity(a,directory)[3]['life_id'],
       'source_tick':SOURCE_T,'source_physical':before,'start_opportunity':state['opportunity'],'ordinal':0,
       'plan':None if row['brazo']=='real'else _pure().unpack_plan(row['plan']),'rows':[],'pending':None,'uncertain':False,'halted_reason':None,
       'log_count':0,'log_chain_sha256':'00'*32,
       'attribution':'Prepared18offers/calendar/couplings; Native supplies every actual action. Control signal plan is auditor intervention, never a cognitive policy.'}
    _e3_save(a,m);_e3_record(a,m,directory,{'kind':'E3_ADMISSION','arm':m['arm'],'plan':m['plan'],'specs':SPECS,'supplies':SUPPLIES,'source':before,'zero_native_ticks':True})
    if physical(a.world)!=before:raise RuntimeError('E3 administrative admission unexpectedly changed Native physical arrays/tick')
    return {'version':VERSION,'admitted':True,'arm':m['arm'],'new_native_ticks':0,'start_opportunity':24,'opportunities':COUNT,'explicit_supplies':SUPPLIES}

# BEGIN_EXACT_PI03_OPPORTUNITY_BODY
def _op_body(a, directory):
    p, ph, r01, identity = _guard(a, directory)
    m = _get(a)
    device = _device(directory)
    if device.m["opportunity"] != m["opportunity"] or device.m["pending"] is not None or device.m["feedback_pending"] is not None or device.m["uncertain"]:
        raise ValueError("Full task/device progress is not coherent; no reset or resend")
    start = int(a.tick)
    before_banks = _bank_observations(a, r01)
    if int(before_banks[0]["clock"]) % 782 != int(before_banks[1]["clock"]) % 782:
        raise ValueError("Acquired bank clocks diverged; no phase repair")
    spec = m["schedule"][m["opportunity"]]
    helper = _helper()
    calendar = helper.schedule_trial(start, int(before_banks[0]["clock"]), spec["delay_laps"])
    _e3_prequery(a, calendar, before_banks, start)
    ready_tick = calendar["outcome_injection_tick"] - 1
    end_tick = calendar["contact_tick"] + 2
    if end_tick - start > p["max_ticks_per_opportunity"]:
        raise ValueError("Fixed useful opportunity exceeds finite1500tick bound")
    m["uncertain"] = True
    m["pending"] = {"phase": "query_planned", "calendar": calendar, "spec": spec,
                    "opportunity": m["opportunity"], "request_ids": []}
    _record(a, m, directory, {"kind": "OPPORTUNITY_INTENT", "calendar": calendar,
                            "spec": spec, "bank_before": before_banks})
    requests = helper.submit_query(a.world, calendar["query_tick"], prefix=r01["prefix"])
    m["pending"]["request_ids"] = [r["id"] for r in requests]
    _save(a, m)
    a.run_until(calendar["query_read_tick"])
    reader = helper.read_fixed(a.world, r01["origin"])
    choice = reader["choice"]
    emitted_motor = r01["zero_motor"] if choice == 0 else choice
    if type(emitted_motor) is not int or emitted_motor not in (-1, 1):
        emitted_motor = None
    applied_motor = None if m["control"] == "actuator_null" else emitted_motor
    action = device.begin(applied_motor, int(a.tick), ready_tick)
    copy = None
    if emitted_motor is not None:
        # Fixed efference copies the material motor command BEFORE the declared
        # downstream actuator-null cut; it never substitutes an optimal action.
        copy = helper.submit_motor_copy(a.world, emitted_motor, calendar["seed_tick"], prefix=r01["prefix"])
        requests.append(copy)
    m["pending"] = {"phase": "actual_effect_inflight", "calendar": calendar,
                    "spec": spec, "opportunity": m["opportunity"],
                    "request_ids": [r["id"] for r in requests]}
    _record(a, m, directory, {"kind": "ACTUAL_MOTOR_AND_EFFERENCE", "reader": reader,
                            "emitted_motor": emitted_motor, "applied_motor": applied_motor,
                            "material_zero_default": choice == 0, "action": action, "copy_request": copy,
                            "scope": "Zero is a declared fixed actuator default; NULL remains no-action. Consequence path stores no chosen bank."})
    frames = {calendar["seed_tick"] + 1: "eligibility_first_step",
              calendar["seed_tick"] + 33: "eligibility_half_lap",
              ready_tick: "actual_delayed_environment_consequence",
              calendar["outcome_injection_tick"]: "generic_future_input_boundary",
              calendar["collision_tick"]: "native_hub_composition",
              calendar["contact_tick"]: "native_bank_contact",
              calendar["contact_tick"] + 1: "bank_update_and_disposal",
              end_tick: "settled_contact_context"}
    if spec["delay_laps"] > 1:
        frames[calendar["seed_tick"] + 67] = "eligibility_one_lap"
    effect = None
    returned_failed = None
    outcome = None
    for tick, label in sorted(frames.items()):
        a.run_until(tick)
        if tick == ready_tick:
            effect = device.complete_due(tick)
            # Only actual generic consequence (or declared constant control).
            # There is no motor/route lookup, expected value or bank parameter.
            returned_failed = _e3_feedback(a, effect["failed"], calendar, before_banks, start)
            outcome = helper.submit_generic_outcome(a.world, returned_failed,
                        calendar["outcome_injection_tick"], prefix=r01["prefix"])
            requests.append(outcome)
            device.mark_feedback_scheduled(outcome["id"], outcome["requested_tick"])
            m["pending"] = {"phase": "generic_outcome_scheduled", "calendar": calendar,
                            "spec": spec, "opportunity": m["opportunity"],
                            "request_ids": [r["id"] for r in requests],
                            "generic_failed": returned_failed}
            _record(a, m, directory, {"kind": "ACTUAL_DELAYED_EFFECT_AND_GENERIC_RETURN", "effect": effect,
                                    "returned_failed": returned_failed, "outcome_request": outcome})
        _record(a, m, directory, _r1()._frame(a, r01, label))
    receipts = _r1()._receipts(a, requests)
    if outcome is None:
        raise RuntimeError("Frozen consequence boundary was not executed; preserve pending future")
    outcome_receipt = next(r["receipt"] for r in receipts if r["id"] == outcome["id"])
    reconciliation = device.reconcile_feedback(outcome_receipt)
    admitted = all(r["receipt"]["status"] == "applied" for r in receipts)
    after_banks = _bank_observations(a, r01)
    result = {"version": VERSION, "opportunity": m["opportunity"], "spec": spec,
              "control": "PI04_E3_" + _e3_get(a)["arm"], "before_tick": start, "after_tick": int(a.tick),
              "new_native_ticks": int(a.tick) - start, "calendar": calendar,
              "reader": reader, "emitted_motor": emitted_motor, "applied_motor": applied_motor,
              "actual_effect": effect, "returned_failed": returned_failed,
              "requests": receipts, "reconciliation": reconciliation,
              "bank_before": before_banks, "bank_after": after_banks,
              "useful_product": bool(effect and not effect["failed"]),
              "attribution": "Native relative-bank selection and eligibility interaction; offered query/calendar, inverse efference, zero default, device law and transduction prepared. Useful learning requires controls."}
    m["opportunity"] += 1
    m["rows"].append({"opportunity": result["opportunity"], "spec": spec,
                      "reader_choice": choice, "useful_product": result["useful_product"],
                      "effect_sha256": effect["actual_product_sha256"], "after_tick": int(a.tick)})
    m["products"] = list(device.m["products"])
    m["rejections"] = list(device.m["rejections"])
    m["uncertain"] = not admitted or not reconciliation["finished"]
    m["pending"] = None if not m["uncertain"] else {"phase": "rejected_or_unreconciled_preserved", "request_ids": [r["id"] for r in requests]}
    if choice is None:
        m["halted_reason"] = "First NULL reader preserved, actual no-action/rejection and generic return recorded; diagnostic required before new opportunities"
    _record(a, m, directory, {"kind": "OPPORTUNITY_COMPLETED", "result": result})
    return result
# END_EXACT_PI03_OPPORTUNITY_BODY

def opportunity(a,directory):
    validate(a,{'modo':OPPORTUNITY});_identity(a,directory);m=_e3_get(a);_environment(a,directory,m)
    m['uncertain']=True;m['pending']={'phase':'before_original_physical_opportunity','ordinal':m['ordinal']}
    _e3_save(a,m);_e3_record(a,m,directory,{'kind':'E3_OPPORTUNITY_INTENT','ordinal':m['ordinal'],'arm':m['arm']})
    result=_op_body(a,directory)
    normalized=_normalize_calendar(result['calendar'],result['bank_before'],result['before_tick'])
    row={'ordinal':m['ordinal'],'calendar':normalized,'failed':result['actual_effect']['failed']}
    m['rows'].append(row);m['ordinal']+=1
    state=_get(a);m['uncertain']=bool(state.get('uncertain'));m['pending']=state.get('pending')
    if state.get('halted_reason'):m['halted_reason']=state['halted_reason']
    result['PI04_E3']={'arm':m['arm'],'ordinal':row['ordinal'],'actual_failed':row['failed'],'returned_failed':result['returned_failed'],
                       'calendar':normalized,'legacy_task_counters_preserved':True,
                       'request_actual_environment_failed_field_scope':'Inherited helper names its admitted signal bit actual_environment_failed; the true device effect is separately actual_effect.failed/PI04_E3.actual_failed.'}
    _e3_record(a,m,directory,{'kind':'E3_OPPORTUNITY_COMPLETED','result':result})
    if m['ordinal']==COUNT and m['arm']=='real':
        result['PI04_E3']['replay_plan']=_pure().build_permuted_plan(m['rows'],source_identity={'life_id':m['life_id'],'source_tick':SOURCE_T,'actual_end_tick':int(a.tick),'shared_prefix_not_independent_replica':True})
        result['PI04_E3']['replay_plan_encoded']=_pure().pack_plan(result['PI04_E3']['replay_plan'])
    if m['ordinal']==COUNT and m['arm']=='desacoplado':result['PI04_E3']['manipulation']=_pure().summarize_manipulation(m['plan'],[r['failed']for r in m['rows']])
    return result
def state(a,directory=None):
    if KEY not in _entries(a):return {'version':VERSION,'admitted':False,'new_native_ticks':0}
    m=_e3_get(a);result={'version':VERSION,'admitted':True,'new_native_ticks':0,'progress':m}
    if m['ordinal']==COUNT and m['arm']=='real':
        result['replay_plan']=_pure().build_permuted_plan(m['rows'],source_identity={'life_id':m['life_id'],'source_tick':SOURCE_T,'actual_end_tick':int(a.tick),'shared_prefix_not_independent_replica':True})
        result['replay_plan_encoded']=_pure().pack_plan(result['replay_plan'])
    if m['ordinal']==COUNT and m['arm']=='desacoplado':result['manipulation']=_pure().summarize_manipulation(m['plan'],[r['failed']for r in m['rows']])
    return result
def dispatch(a,row,actuator='closed',directory=None):
    validate(a,row)
    if row['modo']==STATE:return state(a,directory)
    if directory is None or actuator!='closed':raise ValueError('Existing exclusive owner and fixed closed actuator required')
    return admit(a,row,directory)if row['modo']==ADMIT else opportunity(a,directory)
def uncertain(a):
    return KEY in _entries(a)and bool(_e3_get(a).get('uncertain'))
def operational_dependencies(a,directory):
    if KEY not in _entries(a):return False
    m=_e3_get(a);_identity(a,directory);_task().operational_dependencies(a,directory)
    chain='00'*32;count=0
    with(Path(directory)/FOLDER/'eventos.jsonl').open('rb')as f:
        for line in f:
            event=json.loads(line)
            if event['index']!=count:raise ValueError('E3 journal order mismatch')
            chain=_sha(bytes.fromhex(chain)+line);count+=1
    if chain!=m['log_chain_sha256']or count!=m['log_count']:raise ValueError('E3 metadata/journal mismatch; preserve, never replay')
    if not m['uncertain']and _get(a)['opportunity']!=m['start_opportunity']+m['ordinal']:raise ValueError('E3 inherited task continuation differs')
    if m['arm']=='desacoplado':_pure().validate_plan(m['plan'])
    return {'version':VERSION,'admitted':True,'arm':m['arm'],'completed':m['ordinal'],'included':COUNT,'uncertain':m['uncertain'],'pending':m['pending'],'log_count':count,'log_chain_sha256':chain,'full_inherited_task_required':True,'new_native_ticks':0}
