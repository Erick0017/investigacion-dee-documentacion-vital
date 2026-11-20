"""Recalculate R03 native choices, original requests, actual files and feedback.

Only stdlib and the archived post-commit evaluator are imported. It cannot
restore a native world, start an owner, choose an action or teach an individual.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path


def read(path):
    data=Path(path).read_bytes()
    return json.loads(gzip.decompress(data) if str(path).endswith('.gz') else data)


def fingerprint(path):
    data=Path(path).read_bytes()
    return {'path':str(path),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}


def walk(value):
    if isinstance(value,dict):
        yield value
        for child in value.values():yield from walk(child)
    elif isinstance(value,list):
        for child in value:yield from walk(child)


def direction(raw):
    return [((raw>>shift)&15)-(16 if ((raw>>shift)&15)>=8 else 0) for shift in(48,52,56)]


def numeric_from_native(record):
    trial=record['native_trial'];at=trial['datum_tick']-2
    frames=[frame for frame in trial['frames'] if frame['tick']==at]
    if len(frames)!=1:return None
    row=frames[0]['fields']['C'];raw=int(row['raw'])
    valid=row['site']==[12,17,18] and row['tick']==at and bool(raw&0xffffffff) and ((raw>>60)&15)==1 and direction(raw)==[1,-1,-1]
    if not valid:return None
    payload=(raw>>32)&65535
    return payload if record['operation']=='suma' else payload-32


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args()
    result=read(args.evidence/'RESULTADOS.json')
    evaluator_path=args.evidence/'CODIGO_EJECUTADO/08_evaluador_calidad_apd02.py'
    spec=importlib.util.spec_from_file_location('apd03_archived_post_commit_only',evaluator_path)
    quality=importlib.util.module_from_spec(spec);spec.loader.exec_module(quality)
    issues=[];checks=0;raw_count=0;arms=[];event_sources=[];all_native=Counter()
    policy={'max_operand':32,'max_artifact_bytes':4096,'max_price':2,'max_delay_ticks':8,'resource_limits_required_for_success':True}
    for arm in result['arms']:
        counters=Counter();rows=[];requests={}
        for row in arm['rows']:
            task=row['task'];opportunity=row['opportunity_index']
            path=args.evidence/arm['id']/task['id']/('OPORTUNIDAD_'+str(opportunity)+'.json.gz')
            original=read(path);event_sources.append(fingerprint(path));checks+=1
            if row!=original:issues.append(arm['id']+': aggregate differs from original event')
            word=row['word']['reader'];word_candidates=[]
            for observation in word['panel']:
                if observation['state']>0 and observation['semantic']==1 and observation['direction'] in([0,0,-1],[0,0,1]):
                    word_candidates.append(observation['direction'][2])
            command=word_candidates[0] if len(word_candidates)==1 else None
            checks+=1
            if command!=row['native_operation_sign'] or command!=word['formed_native_command']:
                issues.append(arm['id']+': learned operator decode differs')
            action_candidates=[]
            for observation in row['native_selection']['reader']['observations']:
                vector=observation['direction'];sign=vector[0]
                if observation['state']>0 and observation['semantic']==1 and vector==[sign,1,0] and sign in(-1,0,1) and observation['site']==[(25+2*sign)%67,15,53]:
                    action_candidates.append(sign)
            physical_action=action_candidates[0] if len(action_candidates)==1 else None
            decoded_action='ACT' if physical_action==-1 else 'QUERY' if physical_action in(0,1) else None
            effect=row['environment_effect'];public=row['public_before']
            checks+=1
            if physical_action!=row['native_action_sign'] or decoded_action!=effect['selected_action']:
                issues.append(arm['id']+': native actuator/codec differs')
            fact=int(public['second'] is None);checks+=1
            if fact!=row['raw_interface_missingness_fact'] or fact!=row['native_selection']['raw_observed_fact']:
                issues.append(arm['id']+': raw interface fact changed')
            sensory=row['native_selection']['sensory_requests']
            counters['sensor_requested']+=len(sensory)
            counters['sensor_applied']+=sum(request['receipt']['status']=='applied' for request in sensory)
            for request in sensory:
                checks+=1
                if request['payload']!=fact or request['tick']!=row['native_selection']['query_tick']+3:
                    issues.append(arm['id']+': sensory transduction/phase changed')
            for native in row['native_numeric']:
                decoded=numeric_from_native(native);checks+=1
                if decoded!=native['numeric_reader']['numeric_result']:
                    issues.append(arm['id']+': native numeric decoder differs')
            calls=len(row['native_numeric']);checks+=1
            if calls!=int(effect['native_provider_called']) or calls>1:
                issues.append(arm['id']+': provider call count differs or fallback exists')
            if decoded_action!='ACT' and calls:
                issues.append(arm['id']+': arithmetic called without native ACT')
            counters['native_calls']+=calls
            committed=effect['committed_effect'];recalculated_quality=None
            if committed is not None:
                request={'task_id':committed['task_id'],'text':task['text'],'operands':[public['left'],public['second']]}
                recalculated_quality=quality.evaluate_literal_committed(request,committed,
                    sandbox_root=args.evidence/arm['id']/task['id']/'artifacts',policy=policy)
                checks+=1
                for key in('feedback','axes','valid_solution_before_resource_ranking','resource_acceptable','task_success','completed_task','completed_under_declared_limits','private_audit'):
                    if recalculated_quality[key]!=effect['quality'][key]:
                        issues.append(arm['id']+': actual file/original request quality differs at '+key)
                artifact=committed.get('artifact')
                if artifact:
                    file=args.evidence/arm['id']/task['id']/'artifacts'/artifact['relative_path']
                    actual=fingerprint(file);counters['files']+=1
                    if actual['bytes']!=artifact['bytes'] or actual['sha256']!=artifact['sha256']:
                        issues.append(arm['id']+': committed file bytes/hash differ')
                    counters['correct_files']+=int(recalculated_quality['task_success'])
            new_fact=(decoded_action=='QUERY' and public['second'] is None and effect['public_after']['second'] is not None)
            complete=bool(effect['progress_after']['verified_file_goal_completed'])
            useful=new_fact or complete
            expected_feedback={'category':'SUCCESS' if useful else 'FAILURE'}
            checks+=1
            if useful!=effect['local_action_useful'] or new_fact!=effect['new_public_fact_revealed'] or expected_feedback!=effect['feedback']:
                issues.append(arm['id']+': local consequence calculation differs')
            returned=row['common_return'];checks+=1
            if returned['category']!=expected_feedback['category'] or returned['mode']!=row['feedback_mode']:
                issues.append(arm['id']+': common return differs from post-action consequence')
            counters['opportunities']+=1;counters['valid_actions']+=int(physical_action is not None)
            counters['local_useful']+=int(useful);counters['new_facts']+=int(new_fact)
            counters['ACT']+=int(decoded_action=='ACT');counters['QUERY']+=int(decoded_action=='QUERY')
            counters['NO_ACTION']+=int(decoded_action is None)
            counters['post_experience_useful']+=int(useful and task['phase']!='acquisition_experience')
            counters['post_experience_opportunities']+=int(task['phase']!='acquisition_experience')
            for observation in walk(row):
                if {'raw','clock','site','direction','state','s_reg','semantic'}<=set(observation):
                    raw=int(observation['raw']);clock=int(observation['clock']);raw_count+=1;checks+=1
                    if (raw&0xffffffff)!=observation['state'] or ((raw>>32)&65535)!=observation['s_reg'] or direction(raw)!=observation['direction'] or ((raw>>60)&15)!=observation['semantic'] or not 0<=clock<2**64:
                        issues.append(arm['id']+': exact raw/clock field mismatch')
                if isinstance(observation.get('receipt'),dict) and type(observation.get('id')) is int:
                    rid=observation['id'];status=observation['receipt'].get('status');old=requests.get(rid)
                    if old is None or old=='scheduled':requests[rid]=status
                    elif status!='scheduled' and old!=status:issues.append(arm['id']+': inconsistent terminal receipt')
            rows.append({'task':task['id'],'phase':task['phase'],'opportunity':opportunity,
                'word_input_tick':row['word']['input_tick'],'query_tick':row['native_selection']['query_tick'],
                'before_tick':row['before']['tick'],'after_tick':row['after']['tick'],
                'raw_missingness_fact':fact,'native_action_sign':physical_action,'action':decoded_action,
                'local_useful':useful,'new_public_fact':new_fact,'file_completed':complete,
                'actual_numeric_values':[numeric_from_native(record) for record in row['native_numeric']],
                'feedback':expected_feedback,'feedback_mode':row['feedback_mode']})
        statuses=Counter(requests.values());all_native.update(statuses)
        arms.append({'id':arm['id'],'counts':dict(counters),'unique_native_terminal_statuses':dict(statuses),
            'rows':rows,'initial':arm.get('initial'),'final':arm.get('final'),'error':arm.get('error')})
    paired=[]
    if len(arms)==2:
        for task_id in('experience_full','reserve_full'):
            left=next(row for row in arms[0]['rows'] if row['task']==task_id)
            right=next(row for row in arms[1]['rows'] if row['task']==task_id)
            equal={key:left[key]==right[key] for key in('word_input_tick','query_tick','before_tick','after_tick')}
            checks+=1
            if not all(equal.values()):issues.append('Initial decisive contrast is not age/calendar matched: '+task_id)
            paired.append({'task':task_id,'calendar_equality':equal,'real_action':left['action'],
                'omit_action':right['action'],'real_useful':left['local_useful'],'omit_useful':right['local_useful'],
                'scope':'Shared exact prefix then declared consequence intervention. Subsequent interactive futures are not forcibly identical.'})
    body={'schema':'APD03.contextual_application.stdlib_recalculation.v1',
        'primary':fingerprint(args.evidence/'RESULTADOS.json'),'archived_evaluator':fingerprint(evaluator_path),
        'checks':checks,'exact_RAW_observation_occurrences':raw_count,'issues':issues,
        'arms':arms,'decisive_age_matched_contrasts':paired,
        'unique_native_requests_by_world_terminal_status':dict(all_native),
        'event_sources':event_sources,'performed_action_opportunities':result['performed_action_opportunities'],
        'scope':'No native execution. Native prepared sensor plus acquired reference/action association; private quality arithmetic only after action. Not general missing-data semantics, planning or R2.'}
    with args.out.open('x',encoding='utf8') as stream:
        json.dump(body,stream,ensure_ascii=False,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps({'checks':checks,'issues':len(issues),'opportunities':result['performed_action_opportunities'],
        'arms':[{'id':arm['id'],'counts':arm['counts'],'native':arm['unique_native_terminal_statuses']} for arm in arms]}))
    return 1 if issues else 0


if __name__=='__main__':raise SystemExit(main())
