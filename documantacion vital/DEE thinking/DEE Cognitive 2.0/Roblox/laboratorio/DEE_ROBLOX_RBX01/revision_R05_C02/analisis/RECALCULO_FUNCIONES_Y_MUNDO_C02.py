"""Passive C02 recalculation from primary files, never a Native execution.

Accepts fixed function JSONs, Native events.jsonl and World event arrays,
checkpoint JSONs, export chunks or relay JSONL cumulative event copies.
Summary counters/PASS fields are not evidence. Aliases are deduplicated and
unknown/missing values stay unknown, including numeric NULL versus real zero.
"""
from pathlib import Path
import argparse
import collections
import csv
import hashlib
import json
import re

SCHEMA='DEE.RBX01.C02.passive_function_world_recalculation.R01'


def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)


def formed_integer(value):
    return type(value)is int


def read_input(path, manifest, issues):
    path=Path(path).resolve(strict=True)
    before=path.stat();raw=path.read_bytes();after=path.stat()
    record={'path':str(path),'bytes_read':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
            'stable_size_mtime_during_read':(before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)}
    manifest.append(record)
    if not record['stable_size_mtime_during_read']:
        issues.append({'file':str(path),'issue':'SOURCE_CHANGED_DURING_READ'})
    if len(raw)>64_000_000:
        raise ValueError('Primary exceeds declared64MB per-file bound: '+str(path))
    text=raw.decode('utf-8-sig')
    try:return json.loads(text)
    except json.JSONDecodeError:
        rows=[]
        lines=text.splitlines()
        for i,line in enumerate(lines):
            if not line.strip():continue
            try:rows.append(json.loads(line))
            except json.JSONDecodeError:
                issues.append({'file':str(path),'line':i+1,'issue':'UNREADABLE_JSON_LINE_PRESERVED_NOT_COUNTED'})
        return rows


def primary_paths(arguments):
    found=[]
    for item in arguments:
        path=Path(item)
        found.extend(sorted(path.glob('*.json')) if path.is_dir() else [path])
    # Exact path aliases only; content duplicates are checked by operation ID.
    return list(dict.fromkeys(p.resolve()for p in found))


def event_rows(value, key='kind'):
    """Unwrap known evidence containers only, never infer events from summaries."""
    if isinstance(value,list):
        for row in value:yield from event_rows(row,key)
    elif isinstance(value,dict):
        if key in value:
            yield value
        for name in ('events','items'):
            if isinstance(value.get(name),list):
                yield from event_rows(value[name],key)
        if isinstance(value.get('event_log_raw'),str)and value['event_log_raw']:
            yield from event_rows(json.loads(value['event_log_raw']),key)


def receipt_union(rows, life, output, issues, locator):
    requested=0;aliases=0
    for row in rows:
        requested+=1
        if not isinstance(row,dict)or type(row.get('id'))is not int or not isinstance(row.get('receipt'),dict):
            issues.append({'locator':locator,'issue':'REQUEST_WITHOUT_EXACT_RECEIPT'});continue
        rec=row['receipt'];key=(life,row['id'])
        if rec.get('id')!=row['id']:
            issues.append({'locator':locator,'id':row['id'],'issue':'RECEIPT_ID_MISMATCH'});continue
        value={'life_id':life,'id':row['id'],'channel':row.get('channel',row.get('port')),
               'payload':row['payload']if'payload'in row else row.get('value'),
               'requested_tick':row.get('requested_tick',row.get('tick')),
               'receipt':rec}
        if key in output:
            aliases+=1
            if output[key]!=value:
                issues.append({'locator':locator,'id':row['id'],'issue':'CONFLICTING_RECEIPT_ALIAS'})
        else:output[key]=value
    return requested,aliases


def parse_functions(paths, manifest, issues, all_receipts):
    functions={};rows=[];duplicate_files=0
    for path in paths:
        value=read_input(path,manifest,issues)
        if not isinstance(value,dict)or value.get('schema')not in('DEE.RBX01.C02.function_primary.R01','DEE.RBX01.C02.function_primary.R02'):
            issues.append({'file':str(path),'issue':'NOT_A_C02_FUNCTION_PRIMARY'});continue
        context=value['context'];key=(value['life_id'],context['operation_id'])
        digest=manifest[-1]['sha256']
        if key in functions:
            duplicate_files+=1
            if functions[key]['file_sha256']!=digest:
                issues.append({'file':str(path),'issue':'CONFLICTING_FUNCTION_OPERATION_ID'})
            continue
        visible=value['visible_tool'];result=value['native_function'];kind=visible['kind']
        record={'life_id':value['life_id'],'session_id':context['session_id'],
                'seq':context['sequence'],'observation_id':context['observation_id'],
                'operation_id':context['operation_id'],'kind':kind,
                'slot':visible.get('slot'),'form':visible.get('form'),'visible_tool':visible,
                'left':visible.get('left'),'right':visible.get('right'),
                'teacher_mode':value.get('teacher_mode'),'before_tick':value['before_tick'],
                'after_tick':value['after_tick'],'fixed_deadline_tick':value['fixed_deadline_tick'],
                'finished_before_fixed_deadline':value['after_tick']<value['fixed_deadline_tick'],
                'memory_value':None,'operation':None,'numeric_result':None,'numeric_formed':False,
                'correct_selected_arithmetic':None,'selected_opcode_matches_native_sign':None,
                'file':str(path),'file_sha256':digest}
        complete=all(x.get('receipt',{}).get('id')==x.get('id')and
                     x.get('receipt',{}).get('status')=='applied'
                     for x in value.get('requests_normalized',[]))
        record['input_admission_complete']=complete
        record['public_tool_result']=value.get('public_tool_result')
        if kind=='CALCULATE':
            recalled=result.get('recall')or{}
            record['memory_value']=recalled.get('native_sign')
            record['operation']=result.get('operation')
            record['numeric_result']=result.get('numeric_result')
            record['numeric_formed']=formed_integer(record['numeric_result'])
            memory=record['memory_value']
            if type(memory)is int and memory in(-1,1):
                record['selected_opcode_matches_native_sign']=record['operation']=={1:'suma',-1:'diferencia'}[memory]
            elif memory is not None:
                issues.append({'file':str(path),'issue':'OUT_OF_CONTRACT_MEMORY_EMISSION','value':memory})
            if (formed_integer(visible.get('left'))and formed_integer(visible.get('right'))and
                    record['operation']in('suma','diferencia')):
                reference=(visible['left']+visible['right']if record['operation']=='suma'else visible['left']-visible['right'])
                record['audit_only_selected_arithmetic_reference']=reference
                record['correct_selected_arithmetic']=record['numeric_formed']and record['numeric_result']==reference
            record['status']=result.get('status',result.get('reason'))
        elif kind=='LESSON':
            record['lessons']=[]
            if isinstance(result,list):
                for lesson in result:
                    native=lesson.get('native_lesson',{})
                    record['lessons'].append({'form':lesson.get('form'),
                        'observed_sign':lesson.get('observed_sign'),
                        'input_tick':native.get('input_tick'),'teacher_tick':native.get('teacher_tick'),
                        'teacher_delay':(native['teacher_tick']-native['input_tick']
                                         if type(native.get('teacher_tick'))is int and type(native.get('input_tick'))is int else None)})
        requested,aliases=receipt_union(value.get('requests_normalized',[]),value['life_id'],all_receipts,issues,str(path))
        record['request_rows']=requested;record['request_aliases_seen']=aliases
        record['capability_materially_executed']=requested>0
        public=record['public_tool_result']
        record['public_numeric_result']=public.get('numeric_result')if isinstance(public,dict)else record['numeric_result']
        record['validated_numeric_result_available']=complete and formed_integer(record['public_numeric_result'])
        functions[key]=record;rows.append(record)
    return functions,rows,duplicate_files


def parse_native(paths,manifest,issues,all_receipts,functions):
    observed={};aliases=0;feedback=[];phases=[]
    for source in paths:
        override,path=source if isinstance(source,tuple)else(None,source)
        value=read_input(path,manifest,issues)
        inferred=None
        if override:
            inferred=override
        elif path.parent.name in('RBX02_NATIVE_C02','RBX02_NATIVE_C02_R02')and re.fullmatch(r'ECI02_[A-Z0-9_]+',path.parent.parent.name):
            inferred=path.parent.parent.name
        if inferred is None:
            lives=set()
            for event in event_rows(value):
                if event.get('kind')=='PHASE_COMPLETED'and event.get('mode')=='eci01-rbx01-function':
                    digest=event.get('result',{}).get('evidence',{}).get('primary',{}).get('sha256')
                    lives.update(f['life_id']for f in functions.values()if f['file_sha256']==digest)
            if len(lives)==1:inferred=lives.pop()
        if inferred is None:
            inferred='UNRESOLVED:'+str(path)
            issues.append({'file':str(path),'issue':'NATIVE_LIFE_UNRESOLVED_USE_LIFE_EQUALS_PATH_ARGUMENT'})
        for event in event_rows(value):
            if event.get('kind')!='PHASE_COMPLETED':continue
            result=event.get('result',{});mode=event.get('mode')
            # The journal path is the owned life folder/RBX02_NATIVE_C02/events.
            life=inferred
            key=(str(path),event.get('index'))
            digest=hashlib.sha256(canonical(event).encode('utf8')).hexdigest()
            if key in observed:
                aliases+=1
                if observed[key]!=digest:issues.append({'file':str(path),'issue':'CONFLICTING_NATIVE_LOG_INDEX'})
                continue
            observed[key]=digest;phases.append({'life_id':life,'mode':mode,'tick':event.get('tick')})
            evidence=result.get('evidence',{})
            if mode=='eci01-rbx01-feedback':
                requested,alias=receipt_union(evidence.get('requests',[]),life,all_receipts,issues,str(path)+':'+str(event.get('index')))
                returns=[r for r in evidence.get('requests',[])if'.outcome.'in str(r.get('channel',''))]
                feedback.append({'life_id':life,'tick':event.get('tick'),
                    'actual_failure':evidence.get('actual_physical_failed'),
                    'applied_failure':evidence.get('applied_generic_failed'),
                    'feedback_arm':evidence.get('feedback_arm'),
                    'return_ids':[r.get('id')for r in returns],
                    'requested_rows':requested,'aliases_seen':alias,
                    'whole_cycle_ticks':evidence.get('whole_cycle_ticks')})
            if mode=='eci01-rbx01-function':
                locator=evidence.get('primary',{})
                # Primary file hash is validated against an actual local file,
                # not the actor's all_requested_applied summary flag.
                matches=[f for f in functions.values()if f['life_id']==life and f['file_sha256']==locator.get('sha256')]
                if len(matches)!=1:
                    issues.append({'file':str(path),'index':event.get('index'),'issue':'FUNCTION_PRIMARY_LOCATOR_UNRESOLVED'})
    return {'completed_phases':phases,'feedback':feedback,'log_aliases':aliases}


def parse_world(paths,manifest,issues):
    events=[];seen={};aliases=0;order=0;views=[]
    for path in paths:
        value=read_input(path,manifest,issues)
        if isinstance(value,dict)and value.get('schema')=='DEE.RBX01.C02.world_checkpoint.v1'and isinstance(value.get('events'),list):
            views.append({'file':str(path),'representation':'FULL_INTERNAL_WORLD_CHECKPOINT',
                          'totalRows':len(value['events']),'partial':False})
        for container in value if isinstance(value,list)else[value]:
            if isinstance(container,dict)and container.get('kind')=='PUBLIC_OBSERVER_SAMPLE'and isinstance(container.get('event_log_view'),dict):
                views.append({'file':str(path),**container['event_log_view']})
        for event in event_rows(value):
            # Relay observer envelopes are not actions. Only Body events have
            # an actual sequence and sessionId. Empty prestart session stays so.
            if event.get('observerTailProjection'):
                issues.append({'file':str(path),'row':event.get('fullLogRowIndex'),
                               'issue':'PROJECTED_AUDITOR_TAIL_ROW_NOT_COUNTED_AS_FULL_EVENT'})
                continue
            if not isinstance(event.get('data'),dict)or type(event.get('seq'))is not int:continue
            digest=hashlib.sha256(canonical(event).encode('utf8')).hexdigest()
            if digest in seen:aliases+=1;continue
            seen[digest]=True;order+=1
            events.append({'source_file':str(path),'source_sha256':digest,'first_seen_order':order,**event})
    return events,aliases,views


def link_world(events,functions,issues):
    by_context=collections.defaultdict(list)
    for function in functions.values():
        by_context[(function['session_id'],function['seq'])].append(function)
    # Arrays/relay snapshots preserve append order, including restored prefixes.
    # No unobserved motion, trajectory interpolation or inferred key collection.
    chains=[];world_functions=[];state={};actions={};feedbacks={};locks=[]
    for event in events:
        session=event.get('sessionId','');kind=event['kind'];data=event['data']
        track=state.setdefault(session,{'A':None,'A_source':None,'round':None})
        if kind=='PHYSICAL_CONTACT'and data.get('kind')=='KEY':
            track.update(A=None,A_source=None,round=data.get('round'))
        if kind=='ACTION_EXECUTED':
            action=data.get('action',{});aid=action.get('actionId')
            if aid:
                if aid in actions and actions[aid]!=data:
                    issues.append({'action_id':aid,'issue':'CONFLICTING_WORLD_ACTION_ID'})
                actions[aid]=data
        if kind=='FEEDBACK_COMPLETED':
            fid=data.get('feedbackOperationId')
            if fid:feedbacks[(session,fid)]=data
        if kind=='EVALUATOR_LOCK_CHECK':
            locks.append({'session_id':session,'seq':event['seq'],
                          'participant':event.get('participant'),'actual_code':data.get('actualCode'),
                          'expected_code_private_audit_only':data.get('expectedCode'),
                          'code_present':data.get('codePresent'),'accepted':data.get('accepted'),
                          'source_event_sha256':event['source_sha256']})
        if kind!='FUNCTION_APPLIED':continue
        request=data.get('request',{});output=data.get('output',{})
        candidates=by_context[(session,event['seq'])]
        matching=[f for f in candidates if f['kind']==request.get('kind')and f['slot']==request.get('slot')and f['form']==request.get('form')]
        native=matching[0]if len(matching)==1 else None
        public=(native.get('public_tool_result')or native)if native else{}
        exact=(native is not None and canonical(request)==canonical(native['visible_tool'])and
               canonical({k:output.get(k)for k in('memory_value','operation','numeric_result')})==
               canonical({k:public.get(k)for k in('memory_value','operation','numeric_result')}))
        world_functions.append({'session_id':session,'seq':event['seq'],'participant':event.get('participant'),
            'kind':request.get('kind'),'slot':request.get('slot'),'form':request.get('form'),
            'actual_numeric':output.get('numeric_result'),'native_primary_resolved':native is not None,
            'native_output_same_in_world':exact if native else None,
            'native_input_admission_complete':native.get('input_admission_complete')if native else None,
            'raw_observed_numeric_before_R02_admission_policy':native.get('numeric_result')if native else None,
            'native_operation_id':native['operation_id']if native else None,
            'source_event_sha256':event['source_sha256']})
        if request.get('kind')!='CALCULATE':continue
        actual=output.get('numeric_result')
        if request.get('slot')=='A':
            track['A']=actual if formed_integer(actual)else None
            track['A_source']=event['source_sha256']
        elif request.get('slot')=='B':
            chains.append({'session_id':session,'seq':event['seq'],'participant':event.get('participant'),
                'round':track['round'],'actual_prior_A':track['A'],'actual_B_left_input':request.get('left'),
                'actual_intermediate_transport_verified':formed_integer(track['A'])and request.get('left')==track['A'],
                'A_event_sha256':track['A_source'],'B_event_sha256':event['source_sha256'],
                'actual_B_output':actual,'native_B_primary_resolved':native is not None})
    return {'functions':world_functions,'chains':chains,'locks':locks,
            'actual_action_ids':list(actions),'actual_feedback_ids':[list(k)for k in feedbacks],
            'action_outcomes':dict(collections.Counter(v.get('result',{}).get('outcome')for v in actions.values())),
            'actual_collisions':sum(v.get('result',{}).get('collision')is True for v in actions.values())}


def csv_write(path,rows):
    if not rows:return
    fields=list(dict.fromkeys(k for row in rows for k in row))
    with path.open('x',encoding='utf8',newline='')as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
        for row in rows:writer.writerow({k:canonical(v)if isinstance(v,(list,dict))else v for k,v in row.items()})


def recalculate(function_paths,native_paths,world_paths,output):
    output=Path(output).resolve()
    if output.exists():raise FileExistsError('New output directory required; preserve prior evidence')
    manifest=[];issues=[];receipts={}
    functions,rows,duplicate_functions=parse_functions(primary_paths(function_paths),manifest,issues,receipts)
    native_specs=[]
    for text in native_paths:
        text=str(text)
        life=None;path=text
        if '='in text:
            life,path=text.split('=',1)
            if not re.fullmatch(r'ECI02_[A-Z0-9_]+',life):raise ValueError('Explicit Native life=path syntax required')
        native_specs.append((life,Path(path).resolve()))
    native=parse_native(native_specs,manifest,issues,receipts,functions)
    events,world_aliases,world_views=parse_world([Path(p).resolve()for p in world_paths],manifest,issues)
    world=link_world(events,functions,issues)
    statuses=collections.Counter(r['receipt'].get('status')for r in receipts.values())
    calculations=[r for r in rows if r['kind']=='CALCULATE']
    result={'schema':SCHEMA,'Native_executed':False,'new_experience':False,
        'sources':manifest,'issues':issues,'coverage':{
            'function_primaries':len(rows),'function_file_aliases':duplicate_functions,
            'world_events':len(events),'world_event_aliases':world_aliases,
            'world_source_views':world_views,
            'full_world_checkpoint_provided':any(v.get('representation')=='FULL_INTERNAL_WORLD_CHECKPOINT'for v in world_views),
            'tail_only_samples_are_not_a_complete_world_history':True,
            'unique_receipts_observed':len(receipts),'receipt_statuses':dict(statuses),
            'no_function_primary_does_not_prove_no_function_executed':True,
            'incomplete_cycles_may_need_saved_pending_metadata_for_all_input_IDs':True},
        'Native_functions':rows,'Native_phases':native,'World':world,
        'descriptive_denominators':{'calculation_primaries':len(calculations),
            'numeric_formed':sum(r['numeric_formed']for r in calculations),
            'validated_numeric_outputs_available':sum(r['validated_numeric_result_available']for r in calculations),
            'numeric_NULL_or_missing':sum(not r['numeric_formed']for r in calculations),
            'selected_arithmetic_correct':sum(r['correct_selected_arithmetic']is True for r in calculations),
            'selected_arithmetic_incorrect':sum(r['correct_selected_arithmetic']is False for r in calculations),
            'selected_arithmetic_not_evaluable':sum(r['correct_selected_arithmetic']is None for r in calculations)},
        'scope':'Passive archived recalculation only. Prepared pipeline is not a Native plan. Function correctness, task lock success, acquisition and agency are different questions. Shared-prefix controls are not independent replicas. No capability or PASS inference from absent evidence.'}
    output.mkdir(parents=True)
    with(output/'RECALCULO.json').open('x',encoding='utf8')as stream:stream.write(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    csv_write(output/'FUNCIONES_NATIVE.csv',rows)
    csv_write(output/'COMPOSICION_OBSERVADA.csv',world['chains'])
    csv_write(output/'CORRESPONDENCIA_NATIVE_MUNDO.csv',world['functions'])
    csv_write(output/'RECIBOS_UNICOS.csv',list(receipts.values()))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--functions',nargs='*',default=[])
    parser.add_argument('--native-events',nargs='*',default=[])
    parser.add_argument('--world-events',nargs='*',default=[])
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    value=recalculate(args.functions,args.native_events,args.world_events,args.output)
    print(json.dumps({'output':str(args.output.resolve()),'coverage':value['coverage'],
                      'issues':len(value['issues']),'Native_executed':False},ensure_ascii=False,indent=2))
