"""Independent portable, zero-tick audit of APD03 Main archived event bytes.

This reads only a supplied evidence directory. It imports no engine, actor,
operational snapshot, queue, response generator, or live-system source.
The arithmetic table below is a post-action auditor, never an actor input.
"""
import argparse
import base64
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path


OPERATIONS={'suma':'add','agrega':'add','total':'add',
            'diferencia':'sub','resta':'sub','quita':'sub'}


def read(path):
    data=Path(path).read_bytes()
    return json.loads(gzip.decompress(data) if str(path).endswith('.gz') else data)


def digest(data):return hashlib.sha256(data).hexdigest()
def sha(path):return digest(Path(path).read_bytes())


def walk(value):
    if isinstance(value,dict):
        yield value
        for child in value.values():yield from walk(child)
    elif isinstance(value,list):
        for child in value:yield from walk(child)


def vector(raw):
    return [((raw>>shift)&15)-(16 if ((raw>>shift)&15)>=8 else 0) for shift in (48,52,56)]


def field(observation):
    raw=int(observation['raw'])
    return {'state':raw&0xffffffff,'s_reg':(raw>>32)&65535,
            'direction':vector(raw),'semantic':(raw>>60)&15}


def pure_z(reader):
    values=[]
    for observation in reader.get('panel',[]):
        state=field(observation)
        if state['state'] and state['semantic']==1 and state['direction'] in ([0,0,-1],[0,0,1]):
            values.append(state['direction'][2])
    return values[0] if len(values)==1 else None


def actuator(selection):
    candidates=[]
    for observation in selection['reader']['observations']:
        state=field(observation);v=state['direction'];sign=v[0]
        if state['state'] and state['semantic']==1 and sign in(-1,0,1) and v==[sign,1,0] and observation['site']==[(25+2*sign)%67,15,53]:
            candidates.append(sign)
    return candidates[0] if len(candidates)==1 else None


def current_comparison(reader):
    values=[]
    for observation in reader['observations']:
        state=field(observation);v=state['direction'];x,y,z=v
        if state['state'] and state['semantic']==1 and x in(-1,0,1) and y==1 and z in(0,-1) and observation['site']==[(15+2*x)%67,17,(15+2*z)%67]:
            values.append(x)
    return values[0] if len(values)==1 else None


def number(record):
    trial=record['native_trial'];tick=trial['datum_tick']-2
    frames=[frame for frame in trial['frames'] if frame['tick']==tick]
    if len(frames)!=1:return None
    row=frames[0]['fields']['C'];state=field(row)
    if row['site']!=[12,17,18] or row['tick']!=tick or not state['state'] or state['semantic']!=1 or state['direction']!=[1,-1,-1]:return None
    return state['s_reg'] if record['operation']=='suma' else state['s_reg']-32


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence',required=True,type=Path)
    parser.add_argument('--io-evidence',type=Path,
        help='Optional archived OS class8 observer directory, never live-system state')
    parser.add_argument('--quality-artifacts',type=Path,
        help='Optional archived APD02_FILES.json manifest and exact artifact payloads')
    parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args()
    if args.out.exists():raise FileExistsError('Preserve earlier recalc output; select a new revision name')
    paths=sorted((args.evidence/'EVENTOS').glob('*.json.gz'))
    if not paths:raise ValueError('No primary Main events supplied')
    events=[read(path) for path in paths];issues=[];checks=0;raw_count=0
    event_locations=[{'path':path,'locator':'EVENTOS/'+path.name} for path in paths]
    receipts={};rejected_details={};transport=Counter();counts=Counter();opportunities=[];panels=[];language=[];sources=[];artifacts={};generic_uses=[];lessons=[];quality_uses=[];assisted_compositions=[]
    quality_artifact_manifest=None;quality_file_payloads={}
    if args.quality_artifacts:
        manifest_path=args.quality_artifacts/'APD02_FILES.json';quality_artifact_manifest=read(manifest_path)
        for item in quality_artifact_manifest['files']:
            candidate=(args.quality_artifacts/item['file']).resolve()
            if not candidate.is_relative_to(args.quality_artifacts.resolve()):raise ValueError('Archive artifact path escapes its supplied evidence')
            data=candidate.read_bytes()
            if len(data)!=item['bytes'] or digest(data)!=item['sha256']:raise ValueError('Archived APD02 artifact does not match its manifest')
            quality_file_payloads[(item['relative_path'],item['sha256'])]=data

    def check(condition,detail):
        nonlocal checks
        checks+=1
        if not condition:issues.append(detail)

    # The ordinary second UI owns its own journal rather than the first
    # driver's EVENTOS directory. Import only new completed material IDs;
    # a pending request retrieved twice is never counted as two actions.
    ui_journal=args.evidence/'SESIONES_UI_NUEVAS.jsonl.gz'
    continuation_path=args.evidence/'CONTINUACION_OTRO_PROCESO.json.gz'
    ordinary_ui_added=[]
    seen_ids={event['id'] for event in events if event.get('kind')=='material'}
    continuation=read(continuation_path) if continuation_path.exists() else None
    if ui_journal.exists():
        journal=[json.loads(line) for line in gzip.decompress(ui_journal.read_bytes()).decode('utf8').splitlines() if line.strip()]
        for index,row in enumerate(journal):
            if row.get('event') not in ('literal_material_result','same_id_read_only_result'):continue
            transport_result=row.get('result') or {};request=transport_result.get('request') or transport_result
            if request.get('status')!='completed' or request.get('is_control') or not request.get('result'):continue
            request_id=request['id']
            if request_id in seen_ids:continue
            pending=(continuation or {}).get('same_queued_ID_result',{}).get('request',{})
            is_same_pending=request_id==pending.get('id')
            if is_same_pending:
                check(all(request.get(key)==pending.get(key) for key in ('id','payload','payload_sha','result','seq','arrived_utc','status')),
                    'Second UI journal and actual same-ID continuation receipt differ')
            decoded_result=json.loads(request['result']) if isinstance(request['result'],str) else request['result']
            event={'kind':'material','id':request_id,
                'tag':'continuation_same_queued_ID' if is_same_pending else 'ordinary_UI_final_panel',
                'transport_result':transport_result,'decoded_result':decoded_result,
                'source_journal_locator':'SESIONES_UI_NUEVAS.jsonl.gz#line'+str(index),
                'not_a_new_submission_when_retrieved':is_same_pending}
            events.append(event);event_locations.append({'path':ui_journal,'locator':event['source_journal_locator']})
            seen_ids.add(request_id);ordinary_ui_added.append({'id':request_id,'tag':event['tag'],'source':event['source_journal_locator']})

    # Index the original byte payloads preserved by the actual environment,
    # rather than accepting a verdict or recreating an expected file.
    for event in events:
        for row in walk(event.get('decoded_result')):
            if {'relative_path','content_base64','sha256','bytes'}<=set(row):
                payload=base64.b64decode(row['content_base64'],validate=True)
                check(len(payload)==row['bytes'] and digest(payload)==row['sha256'],'Embedded actual artifact bytes/hash differ: '+row['relative_path'])
                key=(row['relative_path'],row['sha256'])
                check(key not in artifacts or artifacts[key]==payload,'Same artifact identity has different bytes')
                artifacts[key]=payload

    for location,event in zip(event_locations,events):
        path=location['path']
        sources.append({'file':location['locator'],'bytes':path.stat().st_size,'sha256':sha(path)})
        if event['kind']!='material':continue
        counts['material_requests']+=1;tag=event['tag'];payload=event.get('decoded_result')
        receipt=event['transport_result'].get('request') or event['transport_result']
        transport[str(receipt.get('status'))]+=1
        check(receipt.get('id')==event['id'],'Transport returned a different request ID')
        if not isinstance(payload,dict):
            counts['material_without_decoded_result']+=1;continue
        check(payload['after_tick']>=payload['before_tick'],'Physical time decreased inside a request')
        body=payload.get('result') or {}

        for occurrence in walk(payload):
            if {'raw','clock','site','direction','state','s_reg','semantic'}<=set(occurrence):
                raw_count+=1;actual=field(occurrence)
                check(all(actual[key]==occurrence[key] for key in actual) and 0<=int(occurrence['clock'])<2**64,
                      'Exact RAW/clock decomposition differs at '+tag)
            incoming=occurrence.get('receipt')
            if isinstance(incoming,dict) and type(occurrence.get('id')) is int:
                key=(incoming.get('kind'),occurrence['id']);status=incoming.get('status');previous=receipts.get(key)
                if previous is None or previous=='scheduled':receipts[key]=status
                elif status!='scheduled':check(status==previous,'Conflicting terminal Native receipt '+str(key))
                if status=='rejected':rejected_details[key]={'transport_tag':tag,'request_id':occurrence['id'],'receipt':incoming}

        top_rows=body.get('rows',[])
        nested_quality=[child for parent in top_rows for child in walk(parent)
            if child is not parent and child.get('kind')=='APD02_quality_request']
        for row in top_rows+nested_quality:
            if row.get('kind')=='APD02_quality_request':
                word_sign=pure_z(row['word']['reader']);route_sign=actuator(row['route'])
                selected_operation='add' if word_sign==1 else 'sub' if word_sign==-1 else None
                selected_procedure='native' if route_sign==-1 else 'external' if route_sign in(0,1) else None
                check(word_sign==row['native_operator_command'] and selected_operation==row['selected_operation'], 'APD02 operator cue/selection differs at '+tag)
                check(route_sign==row['native_route_command'] and selected_procedure==row['selected_procedure'], 'APD02 route codec differs at '+tag)
                committed=row['committed_effect'];artifact=committed.get('artifact');actual=None;byte_verified=False
                if artifact:
                    data=quality_file_payloads.get((artifact['relative_path'],artifact['sha256']))
                    if data is not None:
                        check(len(data)==artifact['bytes'],'APD02 actual file size differs at '+tag)
                        actual=json.loads(data);byte_verified=True
                    else:
                        # A partial live audit may report the old verifier's
                        # observation, but never label it independent bytes.
                        actual=row['quality']['private_audit'].get('observed_artifact')
                operands=row['raw_operands'];required=OPERATIONS[row['literal_form']]
                expected=operands[0]+operands[1] if required=='add' else operands[0]-operands[1]
                file_correct=bool(actual and actual.get('operation')==required and actual.get('operands')==operands and
                    actual.get('value')==expected and actual.get('task_id')==committed['task_id'] and actual.get('procedure')==selected_procedure)
                limits_ok=(type(committed.get('price')) is int and 0<=committed['price']<=2 and
                    type(committed.get('delay_ticks')) is int and 0<=committed['delay_ticks']<=8)
                successful=file_correct and limits_ok and committed['state']=='committed'
                check(bool(successful)==bool(row['quality']['task_success']), 'Independent post-action APD02 file/resource quality differs at '+tag)
                check(row['feedback_to_participant']['category']==('SUCCESS' if successful else 'FAILURE'), 'APD02 feedback differs from post-commit quality at '+tag)
                check(committed['selected_operation']==selected_operation and committed['selected_procedure']==selected_procedure, 'APD02 committed actor choice differs at '+tag)
                expected_calls={'native':int(selected_procedure=='native'),'external':int(selected_procedure=='external')}
                if committed['state']=='committed':check(committed['provider_calls']==expected_calls,'APD02 fallback/extra provider call at '+tag)
                native_value=number(row['native_numeric']) if isinstance(row.get('native_numeric'),dict) else None
                if native_value is not None:
                    check(native_value==row['native_numeric']['numeric_reader']['numeric_result'] and
                        native_value==committed['raw_provider_response']['value'],'APD02 Native RAW number differs before environmental fault at '+tag)
                quality_uses.append({'tag':tag,'form':row['literal_form'],'operands':operands,
                    'scope_group':'assisted_composition_primitive' if row in nested_quality else 'three_two_provider_cases',
                    'word_sign':word_sign,'route_sign':route_sign,'selected_operation':selected_operation,
                    'selected_procedure':selected_procedure,'native_numeric_before_environmental_fault':native_value,
                    'reported_value':committed.get('reported_value'),'synthetic_fault':committed.get('synthetic_fault'),
                    'actual_file':actual,'actual_bytes_independently_verified':byte_verified,
                    'post_action_numeric_correct':file_correct,'resource_limits_met':limits_ok,
                    'success':successful,'feedback':row['feedback_to_participant'],
                    'native_query_tick':row['route']['query_tick'],
                    'scope':'Old APD02 two-provider contract, not the APD03 ACT/QUERY action codec. External arithmetic remains external.'})
            if row.get('kind')=='APD02_assisted_quality_sequence':
                parts=row['rows']
                handoffs=[{'previous_actual_value':previous['committed_effect'].get('used_value'),
                    'next_actual_first_operand':following['raw_operands'][0],
                    'unchanged':previous['committed_effect'].get('used_value')==following['raw_operands'][0]}
                    for previous,following in zip(parts,parts[1:])]
                check(all(item['unchanged'] for item in handoffs),'Prepared composition corrected/replaced an actual intermediate result at '+tag)
                check(not parts or row['result']==parts[-1]['committed_effect'].get('used_value'),'Composition final result differs from last committed actual result at '+tag)
                assisted_compositions.append({'tag':tag,'actual_instructions':row['actual_instructions'],
                    'handoffs':handoffs,'result':row['result'],'prepared_order_not_native_plan':True})
            if row.get('kind')=='explicit_generic_lesson':
                support=field(row['hub'])
                check(support['state']>0 and support['semantic']==1 and support['direction']==[0,0,row['teacher_sign']], 'Paired lesson hub does not show the declared native sign at '+tag)
                lessons.append({'tag':tag,'form':row['form'],'teacher_sign':row['teacher_sign'],
                    'input_tick':row['input_tick'],'hub':row['hub'],'host_supplied_lesson_not_spontaneous':True})
            if row.get('kind')=='APD03_generic_acquired_request':
                word_sign=pure_z(row['word']['reader']);interaction=row['interaction'];reader=interaction.get('reader') or {}
                check(word_sign==row['native_function_choice'],'Acquired function selection differs from physical cue at '+tag)
                response=pure_z(reader) if 'formed_native_command' in reader else current_comparison(reader) if 'observations' in reader else None
                recorded=reader.get('formed_native_command',reader.get('choice'))
                check(response==recorded,'Generic use native response decoder differs at '+tag)
                generic_uses.append({'tag':tag,'form':row['literal_form'],'word_sign':word_sign,
                    'word_read_tick':row['word']['read_tick'],'operator_context':row['operator_supplied_context'],
                    'public_datum':row['public_datum'],'interaction_kind':interaction['kind'],
                    'response_sign':response,'interaction_read_tick':interaction.get('read_tick'),
                    'scope':'Cue association selects a prepared native comparison or MA interaction; the operator still supplies opportunity/context.'})
            if row.get('kind')=='APD03_explicit_material_panel':
                forms=[{'form':item['form'],'sign':pure_z(item['result']['reader']),
                        'physical_read_tick':item['result']['read_tick']} for item in row['forms']]
                memories=[{'context':item['context'],'sign':pure_z(item['result']['reader']),
                        'physical_read_tick':item['result']['read_tick']} for item in row['memories']]
                for item in row['forms']+row['memories']:
                    check(pure_z(item['result']['reader'])==item['result']['reader']['formed_native_command'],'Panel common physical decoder differs at '+tag)
                panels.append({'tag':tag,'transport_id':event['id'],'before_tick':payload['before_tick'],
                    'after_tick':payload['after_tick'],'forms':forms,'memories':memories,
                    'material_queries_not_passive':True})

            for opportunity in row.get('opportunities',[]):
                if not {'native_selection','environment_effect','word'}<=set(opportunity):continue
                selected=actuator(opportunity['native_selection'])
                action='ACT' if selected==-1 else 'QUERY' if selected in (0,1) else None
                word=pure_z(opportunity['word']['reader']);effect=opportunity['environment_effect']
                public=opportunity['public_observation'];fact=int(public['second'] is None)
                check(selected==opportunity['native_selection']['reader']['choice'] and selected==effect['physical_action_sign'], 'Physical action differs at '+tag)
                check(action==effect['selected_action'],'Fixed original action codec differs at '+tag)
                check(word==opportunity['word']['reader']['formed_native_command'] and word==effect['physical_operation_sign'],'Physical learned-form sign differs at '+tag)
                check(fact==opportunity['raw_missing_fact_codec']['raw_value']==opportunity['native_selection']['raw_observed_fact'],'Missingness flag differs from public observation at '+tag)
                sensory=opportunity['native_selection']['sensory_requests']
                counts['sensor_requested']+=len(sensory)
                counts['sensor_applied']+=sum(item['receipt']['status']=='applied' for item in sensory)
                for item in sensory:
                    check(item['payload']==fact and item['tick']==opportunity['native_selection']['query_tick']+3,'Sensory transduction/phase differs at '+tag)
                native_values=[number(item) for item in opportunity['native_numeric']]
                for item,value in zip(opportunity['native_numeric'],native_values):
                    check(value==item['numeric_reader']['numeric_result'],'Native numeric RAW decoder differs at '+tag)
                check(len(native_values)==int(effect.get('native_provider_called',False)) and len(native_values)<=1,'Provider called twice or count mismatch at '+tag)
                if action!='ACT':check(not native_values,'Native arithmetic called without physical ACT at '+tag)
                actual_file=None;file_correct=False;committed=effect.get('committed_effect')
                if committed and committed.get('artifact'):
                    ref=committed['artifact'];key=(ref['relative_path'],ref['sha256'])
                    selected_operation='add' if word==1 else 'sub' if word==-1 else None
                    check(committed.get('selected_operation')==selected_operation,'Committed operator differs from the native learned cue at '+tag)
                    check(committed.get('selected_procedure')=='native' and committed.get('provider_calls')=={'native':1,'external':0},'Non-native fallback or extra provider call in a Native-only goal at '+tag)
                    actual_bytes=artifacts.get(key)
                    check(actual_bytes is not None,'Actual committed file bytes omitted: '+ref['relative_path'])
                    if actual_bytes is not None:
                        actual_file=json.loads(actual_bytes)
                        check(len(actual_bytes)==ref['bytes'],'Committed file size differs')
                        required=OPERATIONS[public['text']]
                        expected=public['left']+public['second'] if required=='add' else public['left']-public['second']
                        file_correct=(actual_file.get('operation')==required and actual_file.get('operands')==[public['left'],public['second']] and
                            actual_file.get('value')==expected and actual_file.get('procedure')=='native' and actual_file.get('task_id')==committed['task_id'])
                        check(actual_file.get('value')==committed['used_value'] and actual_file.get('operation')==selected_operation,'File differs from actual committed physical operation/response')
                        check(native_values==[committed['used_value']],'Committed result not backed by native numeric trace')
                        quality=effect.get('quality') or {}
                        limits_ok=(type(committed.get('price')) is int and 0<=committed['price']<=2 and
                            type(committed.get('delay_ticks')) is int and 0<=committed['delay_ticks']<=8)
                        check(bool(quality.get('task_success'))==bool(file_correct and limits_ok),'Recalculated actual-file correctness/resources differs at '+tag)
                        counts['actual_files']+=1;counts['correct_actual_files']+=int(file_correct and limits_ok)
                new_fact=action=='QUERY' and public['second'] is None and effect['public_after']['second'] is not None
                completed=bool(file_correct and committed and committed['state']=='committed')
                useful=new_fact or completed
                expected_feedback='SUCCESS' if useful else 'FAILURE'
                check(new_fact==effect['new_public_fact_revealed'],'New fact claim differs at '+tag)
                check(completed==effect['final_goal_file_completed'],'Goal completion not backed by actual file at '+tag)
                check(useful==effect['local_action_useful'] and effect['feedback']['category']==expected_feedback,'Post-action local usefulness differs at '+tag)
                returned=opportunity.get('common_return')
                if returned:
                    check(returned['category']==expected_feedback and returned['mode']==opportunity['return_mode'],'Actual common consequence differs at '+tag)
                counts['opportunities']+=1;counts[action or 'NO_ACTION']+=1
                counts['valid_actions']+=int(selected is not None);counts['new_facts']+=int(new_fact);counts['useful_actions']+=int(useful)
                opportunities.append({'tag':tag,'transport_id':event['id'],'opportunity':opportunity['opportunity'],
                    'query_tick':opportunity['native_selection']['query_tick'],'word_input_tick':opportunity['word']['input_tick'],
                    'word':public['text'],'context':public['context'],'second_visible_before':public['second'] is not None,
                    'raw_missing_fact':fact,'word_sign':word,'physical_action_sign':selected,'action':action,
                    'reference_s_reg':[field(item)['s_reg'] for item in opportunity['native_selection']['references']],
                    'new_fact':new_fact,'useful':useful,'file_completed':completed,'actual_file':actual_file,
                    'native_numeric_values':native_values,'feedback':expected_feedback,'return_mode':opportunity['return_mode']})

            # Keep every non-goal use with its independently decoded signs;
            # do not guess a target or turn unexplored row kinds into success.
            if not row.get('opportunities') and row.get('kind')!='APD03_explicit_material_panel':
                readers=[]
                for item in walk(row):
                    reader=item.get('reader')
                    if isinstance(reader,dict) and 'formed_native_command' in reader:
                        readers.append({'sign':pure_z(reader),'recorded_sign':reader['formed_native_command'],
                            'read_tick':item.get('read_tick'),'kind':item.get('kind')})
                        check(readers[-1]['sign']==readers[-1]['recorded_sign'],'Other-use physical decoder differs at '+tag)
                language.append({'tag':tag,'transport_id':event['id'],'kind':row.get('kind'),
                    'before_tick':payload['before_tick'],'after_tick':payload['after_tick'],'physical_readers':readers,
                    'scope':'Literal use/teaching record, not automatically a new learned or correct semantic function.'})

    initial_forms={item['form']:item['sign'] for item in panels[0]['forms']} if panels else {}
    initial_memories={item['context']:item['sign'] for item in panels[0]['memories']} if panels else {}
    for panel in panels:
        panel['old_forms_equal_initial']={item['form']:item['sign']==initial_forms[item['form']] for item in panel['forms'] if item['form'] in initial_forms}
        panel['memories_equal_initial']={item['context']:item['sign']==initial_memories[item['context']] for item in panel['memories'] if item['context'] in initial_memories}
        panel['new_forms_equal_explicit_teaching']={item['form']:item['sign']=={'luma':1,'nara':-1}[item['form']] for item in panel['forms'] if item['form'] in('luma','nara')}
    final_path=args.evidence/'REGISTROS_VENTANA.json.gz';final=read(final_path) if final_path.exists() else None
    archived_sources=[]
    if final is not None:
        check(final['events']==[read(path) for path in paths],'Final aggregate differs from its original incremental events')
        check(final['enabled_seconds']==final['window_end_monotonic']-final['window_start_monotonic'],'Evolving-window duration differs from its monotonic endpoints')
        for source in final['sources']:
            path=(args.evidence/source['file']).resolve()
            if not path.is_relative_to(args.evidence.resolve()):raise ValueError('Archived source path escapes evidence directory')
            measured=sha(path)
            check(measured==source['sha256']==source['actual_sha256'] and source['unchanged'], 'Exact captured source bytes/closing freeze differs: '+source['file'])
            archived_sources.append({'file':source['file'],'bytes':path.stat().st_size,'sha256':measured})
    io_evidence={'earlier_class9_IoInfo':'RESERVED / NO MEDIDO: earlier zero fields are not a zero-I/O result.',
        'native_owner_scope':'Not host energy or physical storage traffic; logical Windows transfer counts may include cached I/O.',
        'nested_cpu_or_memory_not_added':True}
    if args.io_evidence:
        correction_path=args.io_evidence/'ALCANCE_Y_CORRECCION.json'
        samples_path=args.io_evidence/'MUESTRAS_CLASS8.jsonl'
        correction=read(correction_path);sample_bytes=samples_path.read_bytes();io_rows=[]
        for line in sample_bytes.splitlines():
            if line.strip():io_rows.append(json.loads(line))
        by_job={}
        for row in io_rows:
            if 'io' not in row:continue
            check(all(type(value) is int and value>=0 for value in row['io'].values()),'Class8 OS I/O count is not an exact nonnegative integer')
            previous=by_job.get(row['job_name'],{}).get('last')
            if previous:
                check(all(row['io'][key]>=previous['io'][key] for key in row['io']),'Cumulative I/O decreased inside the same OS Job')
            by_job.setdefault(row['job_name'],{'first':row,'samples':0})['last']=row
            by_job[row['job_name']]['samples']+=1
        io_evidence.update({'correction':correction,'sample_source':{'file':'MUESTRAS_CLASS8.jsonl',
            'bytes':len(sample_bytes),'sha256':digest(sample_bytes)},'correction_sha256':sha(correction_path),
            'jobs':list(by_job.values()),'phase_boundaries_before_attachment_not_measured':True})
    body={'schema':'APD03.Main.archived_stdlib_recalculation.R01','checks':checks,'issues':issues,
        'complete_driver_result_present':final is not None,'events_available':len(events),'counts':dict(counts),
        'ordinary_UI_material_results_added_once':ordinary_ui_added,
        'transport_terminal_statuses':dict(transport),'unique_native_receipt_statuses':dict(Counter(receipts.values())),
        'unique_native_requested_observed':len(receipts),'rejected_native_details':list(rejected_details.values()),
        'exact_RAW_observation_occurrences':raw_count,'panels':panels,'opportunities':opportunities,
        'other_physical_uses':language,'new_generic_lessons':lessons,'new_generic_uses':generic_uses,
        'APD02_quality_uses':quality_uses,
        'assisted_compositions':assisted_compositions,
        'APD02_quality_actual_bytes_coverage':{'requests':len(quality_uses),
            'independently_byte_verified':sum(row['actual_bytes_independently_verified'] for row in quality_uses),
            'unverified_partial_verifier_observations':sum(not row['actual_bytes_independently_verified'] for row in quality_uses)},
        'actual_artifact_count':len(artifacts),'event_sources':sources,
        'exact_captured_sources_verified':archived_sources,
        'OS_resources_correction':io_evidence,
        'window':None if final is None else {**{key:final.get(key) for key in ('enabled_seconds','error','sources_unchanged','protected_originals_unchanged','driver_wall_seconds','driver_cpu_ns','energy')},
            'FIN_owner_observation_is_startup_cached_not_final_snapshot':True},
                'scope':'Archived bytes only, zero new ticks and no access to operational states. Counters are dependent uses within one trajectory, not independent learned individuals. Native receipt status is its last exported observation, not an assertion about the full current Native pending agenda. This verifies raw transduction/decoding and post-action file facts, not a general P2/R2 or hidden process guarantee.'}
    with args.out.open('x',encoding='utf8') as stream:json.dump(body,stream,ensure_ascii=False,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps({'events':len(events),'checks':checks,'issues':len(issues),'counts':dict(counts),
        'panels':len(panels),'complete':final is not None},ensure_ascii=False))
    return bool(issues)


if __name__=='__main__':raise SystemExit(main())
