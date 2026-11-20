"""Conventional APD03 references; no DEE imports and no feedback to a life.

Only public observations/explicit teaching and binary post-action outcomes
reach a policy. Route names preserve the environment contract, not the
implementation of arithmetic: both callbacks here are classical references.
"""
from __future__ import annotations
import argparse
import copy
import ctypes
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import statistics
import sys
import time

SCHEMA = 'DEE.APD03.executed_conventional_comparator.R01'
ROUTES = ('native', 'external')
PUBLIC_KEYS = {'text', 'left', 'second', 'context', 'public_resources'}
POLICY = {'max_operand':32,'max_artifact_bytes':4096,'max_price':2,
          'max_delay_ticks':8,'resource_limits_required_for_success':True}


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(',', ':'))+'\n').encode('utf8')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def save(path, value):
    data = canonical(value)
    with Path(path).open('xb') as stream:
        stream.write(data)
    return {'path':Path(path).name,'bytes':len(data),'sha256':digest(data)}


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def process_resources():
    """OS counters for this one process, no inferred energy or host totals."""
    result = {'wall_monotonic_ns':time.perf_counter_ns(),
              'cpu_process_ns':time.process_time_ns(),
              'working_set_bytes':None,'peak_working_set_bytes':None,
              'io_read_bytes':None,'io_write_bytes':None,
              'io_read_operations':None,'io_write_operations':None,
              'energy_joules':'NO MEDIDA'}
    if os.name != 'nt':
        result['counter_scope'] = 'Process CPU/wall only; Windows counters unavailable'
        return result
    from ctypes import wintypes
    class Memory(ctypes.Structure):
        _fields_ = [('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD),
          ('PeakWorkingSetSize',ctypes.c_size_t),('WorkingSetSize',ctypes.c_size_t),
          ('QuotaPeakPagedPoolUsage',ctypes.c_size_t),('QuotaPagedPoolUsage',ctypes.c_size_t),
          ('QuotaPeakNonPagedPoolUsage',ctypes.c_size_t),('QuotaNonPagedPoolUsage',ctypes.c_size_t),
          ('PagefileUsage',ctypes.c_size_t),('PeakPagefileUsage',ctypes.c_size_t)]
    class Io(ctypes.Structure):
        _fields_ = [(name,ctypes.c_ulonglong) for name in
          ('ReadOperationCount','WriteOperationCount','OtherOperationCount',
           'ReadTransferCount','WriteTransferCount','OtherTransferCount')]
    kernel = ctypes.WinDLL('kernel32',use_last_error=True)
    psapi = ctypes.WinDLL('psapi',use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE,ctypes.c_void_p,wintypes.DWORD]
    psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
    kernel.GetProcessIoCounters.argtypes = [wintypes.HANDLE,ctypes.c_void_p]
    kernel.GetProcessIoCounters.restype = wintypes.BOOL
    handle = kernel.GetCurrentProcess()
    mem = Memory();mem.cb = ctypes.sizeof(mem)
    io = Io()
    if not psapi.GetProcessMemoryInfo(handle,ctypes.byref(mem),mem.cb):
        raise ctypes.WinError(ctypes.get_last_error())
    if not kernel.GetProcessIoCounters(handle,ctypes.byref(io)):
        raise ctypes.WinError(ctypes.get_last_error())
    result.update(working_set_bytes=int(mem.WorkingSetSize),
        peak_working_set_bytes=int(mem.PeakWorkingSetSize),
        io_read_bytes=int(io.ReadTransferCount),io_write_bytes=int(io.WriteTransferCount),
        io_read_operations=int(io.ReadOperationCount),io_write_operations=int(io.WriteOperationCount),
        counter_scope='Windows current process only; no worker processes')
    return result


def resource_delta(before, after):
    out = {'wall_ns':after['wall_monotonic_ns']-before['wall_monotonic_ns'],
           'cpu_ns':after['cpu_process_ns']-before['cpu_process_ns'],
           'peak_working_set_bytes_process_to_date':after['peak_working_set_bytes'],
           'working_set_bytes_after':after['working_set_bytes']}
    for key in ('io_read_bytes','io_write_bytes','io_read_operations','io_write_operations'):
        out[key] = None if before[key] is None else after[key]-before[key]
    return out


class CommonPolicy:
    def __init__(self):
        self.lexicon = {}
        self.queries = 0
    def teach(self, public_teaching):
        if set(public_teaching) != {'text','operation'}:
            raise ValueError('Exact common explicit teaching required')
        if public_teaching['operation'] not in ('add','sub'):
            raise ValueError('Bounded add/sub teaching only')
        self.lexicon[public_teaching['text']] = public_teaching['operation']
    def begin_task(self):
        self.queries = 0
    def choose_route(self, observation):
        return 'native'
    def choose(self, observation):
        # This is a conventional baseline policy, never called by a DEE actor.
        if set(observation) != PUBLIC_KEYS:
            raise ValueError('Policy must receive precisely the public projection')
        if observation['second'] is None:
            self.queries += 1
            return {'kind':'QUERY'}
        operation = self.lexicon.get(observation['text'])
        if operation is None:
            return {'kind':'NO_OUTPUT'}
        return {'kind':'ACT','operation':operation,
                'procedure':self.choose_route(observation)}
    def feedback(self, observation, action, public_return):
        if set(public_return) != {'category'} or public_return['category'] not in ('SUCCESS','FAILURE'):
            raise ValueError('Only the common binary consequence is admitted')
    def state(self):
        return {'lexicon':dict(self.lexicon)}


class Fixed(CommonPolicy):
    name = 'fijo'
    def choose(self, observation):
        if self.queries == 0:
            self.queries += 1
            return {'kind':'QUERY'}
        return super().choose(observation)


class ContextTable(CommonPolicy):
    name = 'tabla_contextual'
    def __init__(self):
        super().__init__();self.table = {}
    def choose_route(self, observation):
        key = str(observation['context'])
        row = self.table.setdefault(key,{route:[0,0] for route in ROUTES})
        allowed=observation['public_resources'].get('allowed_procedures',ROUTES)
        for route in allowed:
            if row[route][1] == 0:
                return route
        return max(allowed,key=lambda route:row[route][0]/row[route][1])
    def feedback(self, observation, action, public_return):
        super().feedback(observation,action,public_return)
        if action['kind']=='ACT':
            row = self.table.setdefault(str(observation['context']),{route:[0,0] for route in ROUTES})
            row[action['procedure']][1] += 1
            row[action['procedure']][0] += int(public_return['category']=='SUCCESS')
    def state(self):
        return {**super().state(),'counts_successes_attempts':copy.deepcopy(self.table)}


class WinStayLoseShift(CommonPolicy):
    name = 'wsls'
    def __init__(self):
        super().__init__();self.route = 'native'
    def choose_route(self, observation):
        allowed=observation['public_resources'].get('allowed_procedures',ROUTES)
        return self.route if self.route in allowed else allowed[0]
    def feedback(self, observation, action, public_return):
        super().feedback(observation,action,public_return)
        if action['kind']=='ACT' and public_return['category']=='FAILURE':
            self.route = 'external' if self.route=='native' else 'native'
    def state(self):
        return {**super().state(),'last_route':self.route}


POLICIES = {p.name:p for p in (Fixed,ContextTable,WinStayLoseShift)}


def public_observation(task, second):
    return {'text':task['text'],'left':task['left'],'second':second,
            'context':copy.deepcopy(task['context']),
            'public_resources':copy.deepcopy(task['public_resources'])}


def check_program(program):
    if program.get('schema') != 'DEE.APD03.common_task_program.R01':
        raise ValueError('A prospective common program is required')
    if not isinstance(program.get('events'),list) or len(program['events'])>2048:
        raise ValueError('Ordered common events required')
    if program.get('feedback_mode','local_useful') not in ('local_useful','file_only'):
        raise ValueError('A frozen local-usefulness or file-only consequence mode is required')
    ids = set()
    for event in program['events']:
        if event['kind']=='teach':
            if set(event['teaching']) != {'text','operation'}:
                raise ValueError('Bad explicit teaching')
            continue
        if event['kind']!='task':
            raise ValueError('No unbounded/action-setting event is admitted')
        task = event['task'];tid=task['task_id']
        if tid in ids:
            raise ValueError('Unique task IDs required')
        ids.add(tid)
        if type(task['left']) is not int or type(task['second']) is not int:
            raise ValueError('Exact integer world facts required')
        if not 0<=task['left']<=32 or not 0<=task['second']<=32:
            raise ValueError('Operand outside shared 0..32 domain')
        if type(task['second_initially_public']) is not bool:
            raise ValueError('Explicit visible/missing distinction required')
        if task['required_operation'] not in ('add','sub'):
            raise ValueError('Evaluator-private operation required')
        if set(task['laws']) != set(ROUTES) or set(task['faults']) != set(ROUTES):
            raise ValueError('Both fixed route laws/faults must be declared privately')
        query_price=task['public_resources'].get('query_price',0)
        if type(query_price) is not int or query_price<0:
            raise ValueError('Optional public query price must be a nonnegative integer')
        allowed=task['public_resources'].get('allowed_procedures',list(ROUTES))
        if not isinstance(allowed,list) or not allowed or len(set(allowed))!=len(allowed) or any(r not in ROUTES for r in allowed):
            raise ValueError('A nonempty public list of admitted tool interfaces is required')
        if not 1<=task.get('max_opportunities',4)<=4:
            raise ValueError('Shared bounded opportunities1..4 required')
    return True


def arithmetic(operation, operands):
    return operands[0]+operands[1] if operation=='add' else operands[0]-operands[1]


def run(program_path, output, policy_name):
    overall_before = process_resources()
    source = Path(__file__).resolve()
    here = source.parent
    program_bytes = Path(program_path).read_bytes()
    program = json.loads(program_bytes)
    check_program(program)
    output = Path(output).resolve();output.mkdir(parents=True,exist_ok=False)
    artifacts=output/'artifacts';artifacts.mkdir()
    quality=load_module(here/'vendor'/'evaluador_calidad_apd02.py','quality_reference')
    effects=load_module(here/'vendor'/'proveedores_prueba_apd02.py','effects_reference')
    policy=POLICIES[policy_name]()
    loaded=process_resources()
    rows=[];phases=[{'phase':'startup_load','resources':resource_delta(overall_before,loaded)}]
    with (output/'eventos_primarios.jsonl').open('xb') as stream:
        for seq,event in enumerate(program['events']):
            before=process_resources()
            if event['kind']=='teach':
                policy.teach(copy.deepcopy(event['teaching']))
                row={'sequence':seq,'kind':'teach','public_teaching':event['teaching'],
                     'policy_state_after':policy.state()}
                row['resources']=resource_delta(before,process_resources())
                phases.append({'phase':'explicit_learning','sequence':seq,'resources':row['resources']})
                stream.write(canonical(row));rows.append(row)
                continue
            task=event['task'];second=task['second'] if task['second_initially_public'] else None
            policy.begin_task();completed=False
            for opportunity in range(1,task.get('max_opportunities',4)+1):
                observation=public_observation(task,second)
                decision_before=process_resources()
                state_before=policy.state()
                action=policy.choose(copy.deepcopy(observation))
                decision_after=process_resources()
                row={'sequence':seq,'kind':'opportunity','task_id':task['task_id'],
                     'purpose_auditor_only':task.get('purpose','unspecified'),
                     'opportunity':opportunity,'public_observation':observation,
                     'policy_state_before':state_before,'committed_action':action,
                     'decision_resources':resource_delta(decision_before,decision_after),
                     'requested':1,'admitted_by_conventional_executor':1,
                     'provider_scope':'Conventional arithmetic on both nominal routes; no DEE ticks'}
                effect_before=process_resources()
                if action['kind']=='QUERY':
                    new_fact=second is None
                    second=task['second']
                    row.update(environment_effect='SECOND_OPERAND_OBSERVED',
                        public_revealed={'second':second},
                        public_return={'category':'SUCCESS'if new_fact and program.get('feedback_mode','local_useful')=='local_useful'else'FAILURE'},
                        local_action_useful=new_fact,new_public_fact_revealed=new_fact,
                        answered=1,correct=0,abstention=0,no_response=0,
                        synthetic_query_price=task['public_resources'].get('query_price',0))
                elif action['kind']=='NO_OUTPUT':
                    row.update(environment_effect='NO_OUTPUT',public_return={'category':'FAILURE'},
                        answered=0,correct=0,abstention=0,no_response=1)
                elif action['kind']=='ACT':
                    if second is None:
                        row.update(environment_effect='ACT_FAILED_MISSING_OBSERVATION',
                            public_return={'category':'FAILURE'},answered=1,correct=0,
                            abstention=0,no_response=0)
                    else:
                        route=action['procedure'];effect_id=task['task_id']+'_attempt'+str(opportunity)
                        public={'task_id':effect_id,'text':task['text'],'operands':[task['left'],second]}
                        committed=effects.execute_selected(public,
                            {'operation':action['operation'],'procedure':route},sandbox_root=artifacts,
                            native_value_reader=arithmetic,external_calculator=arithmetic,
                            law=task['laws'][route],fault=task['faults'][route],synthetic_fixture=True)
                        if committed['state']=='uncertain':
                            row.update(committed_effect=committed,public_return=None,
                                environment_effect='UNCERTAIN_FILE_EFFECT',
                                answered=1,correct=0,abstention=0,no_response=0,
                                stop_task_for_explicit_reconciliation=True)
                        else:
                            evaluation_before=process_resources()
                            report=quality.evaluate_committed({**public,'required_operation':task['required_operation']},
                                committed,sandbox_root=artifacts,policy=program.get('quality_policy',POLICY))
                            evaluation_after=process_resources()
                            row.update(committed_effect=committed,quality_private_after_commit=report,
                                public_return=quality.actor_feedback(report,binary=True),
                                environment_effect='VERIFIED_GOAL_FILE' if report['task_success'] else 'TERMINAL_TASK_NOT_VERIFIED',
                                answered=1,correct=int(report['task_success']),abstention=0,no_response=0,
                                verification_resources=resource_delta(evaluation_before,evaluation_after))
                            completed=bool(report['task_success'])
                else:
                    raise ValueError('Policy emitted an unknown action')
                row['execution_and_verification_resources']=resource_delta(effect_before,process_resources())
                if row['public_return'] is not None:
                    policy.feedback(copy.deepcopy(observation),copy.deepcopy(action),copy.deepcopy(row['public_return']))
                row['policy_state_after']=policy.state()
                row['task_completed']=completed
                row['final_goal_file_completed']=completed
                if action['kind']!='QUERY':row['local_action_useful']=completed
                row['feedback_mode']=program.get('feedback_mode','local_useful')
                # Private environment is logged after the effect only and never
                # passed to a policy. This is sufficient to audit/recalculate it.
                row['private_environment_after_commit']={key:copy.deepcopy(task[key]) for key in
                    ('required_operation','laws','faults','second')}
                log_start=time.perf_counter_ns();stream.write(canonical(row));stream.flush()
                row['logging_wall_ns_not_in_archived_row']=time.perf_counter_ns()-log_start
                rows.append(row)
                if completed or row.get('stop_task_for_explicit_reconciliation'):break
            phases.append({'phase':'task_total_with_logging','sequence':seq,
                           'resources':resource_delta(before,process_resources())})
    run_end=process_resources()
    summary=recalculate_rows(rows,program)
    summary.update(schema=SCHEMA,policy=policy_name,program_sha256=digest(program_bytes),
        feedback_mode=program.get('feedback_mode','local_useful'),
        source_sha256=digest(source.read_bytes()),python=sys.version,executable=sys.executable,
        phases=phases,process_total=resource_delta(overall_before,run_end),
        total_before_final_summary_write=True,
        policy_state_final=policy.state(),energy='NO MEDIDA',
        architecture='Separate conventional comparator; no Native Runtime, no shared actor state',
        route_caveat='Both nominal route callbacks are conventional arithmetic; route laws/quality identical, not v27 CPU equivalents',
        eventlog_sha256=digest((output/'eventos_primarios.jsonl').read_bytes()))
    save(output/'resumen.json',summary)
    save(output/'programa_ejecutado.json',program)
    manifest=[]
    for file in sorted(output.rglob('*')):
        if file.is_file():
            data=file.read_bytes();manifest.append({'path':file.relative_to(output).as_posix(),
                'bytes':len(data),'sha256':digest(data)})
    save(output/'MANIFIESTO.json',{'members':manifest,'excludes_own_hash':True})
    return summary


def recalculate_rows(rows,program):
    opportunity=[r for r in rows if r['kind']=='opportunity']
    task_ids=[e['task']['task_id'] for e in program['events'] if e['kind']=='task']
    bytask={tid:[r for r in opportunity if r['task_id']==tid] for tid in task_ids}
    tasks=[]
    for tid, rr in bytask.items():
        acts=[r for r in rr if r['committed_action']['kind']=='ACT']
        completed=any(r['task_completed'] for r in rr)
        totalwall=sum(r['decision_resources']['wall_ns']+r['execution_and_verification_resources']['wall_ns'] for r in rr)
        tasks.append({'task_id':tid,'opportunities':len(rr),'queries':sum(r['committed_action']['kind']=='QUERY' for r in rr),
            'acts':len(acts),'completed':completed,'first_opportunity_completed':bool(rr and rr[0]['task_completed']),
            'wrong_or_unusable_acts':sum(not bool(r['correct']) for r in acts),
            'no_response':sum(r['no_response'] for r in rr),'measured_decision_effect_wall_ns':totalwall,
            'uncertain_effects':sum(bool(r.get('stop_task_for_explicit_reconciliation')) for r in rr),
            'synthetic_price':sum(r.get('committed_effect',{}).get('price',0)+r.get('synthetic_query_price',0) for r in rr),
            'query_price':sum(r.get('synthetic_query_price',0) for r in rr)})
    latencies=[r['decision_resources']['wall_ns'] for r in opportunity]
    correct=sum(t['completed'] for t in tasks)
    return {'tasks':tasks,'task_count':len(tasks),'tasks_completed':correct,
        'tasks_not_completed':len(tasks)-correct,'opportunities_requested':len(opportunity),
        'opportunities_admitted_conventional_executor':sum(r['admitted_by_conventional_executor'] for r in opportunity),
        'responses':sum(r['answered'] for r in opportunity),'correct_completed_effects':sum(r['correct'] for r in opportunity),
        'incorrect_or_unusable_acts':sum(t['wrong_or_unusable_acts'] for t in tasks),
        'queries':sum(t['queries'] for t in tasks),'no_response':sum(t['no_response'] for t in tasks),
        'abstentions':sum(r['abstention'] for r in opportunity),'rejected_by_conventional_executor':0,
        'uncertain_effects':sum(t['uncertain_effects'] for t in tasks),
        'synthetic_total_price_including_failures':sum(t['synthetic_price'] for t in tasks),
        'decision_latency_samples':len(latencies),
        'decision_latency_ns':{'min':min(latencies,default=None),'median':statistics.median(latencies) if latencies else None,'max':max(latencies,default=None)},
        'decision_effect_wall_ns_per_completed_task':sum(t['measured_decision_effect_wall_ns'] for t in tasks)/correct if correct else None,
        'not_independent_samples':'One trajectory per output; opportunities are repeated interactions, not independent learners'}


def validate_archived(directory):
    """Recompute quality from actual files and replay only the classical policy.

    This is archived-evidence recalculation, not a new task, provider call or
    Native reproduction. Report timing fields are intentionally not compared.
    """
    directory=Path(directory)
    program=json.loads((directory/'programa_ejecutado.json').read_text(encoding='utf8'))
    summary=json.loads((directory/'resumen.json').read_text(encoding='utf8'))
    rows=[json.loads(line) for line in (directory/'eventos_primarios.jsonl').read_text(encoding='utf8').splitlines()]
    quality=load_module(Path(__file__).parent/'vendor'/'evaluador_calidad_apd02.py','quality_recalculation')
    policy=POLICIES[summary['policy']]();last_sequence=None;checks=0;files=0
    for row in rows:
        event=program['events'][row['sequence']]
        if row['kind']=='teach':
            if row['public_teaching']!=event['teaching']:raise ValueError('Archived teaching differs')
            policy.teach(copy.deepcopy(row['public_teaching']));checks+=1;continue
        task=event['task']
        if row['sequence']!=last_sequence:policy.begin_task();last_sequence=row['sequence']
        observation=row['public_observation']
        if set(observation)!=PUBLIC_KEYS:raise ValueError('Archived public projection contains extra fields')
        if policy.choose(copy.deepcopy(observation))!=row['committed_action']:
            raise ValueError('Archived classical decision is not reproducible from public history')
        checks+=1;action=row['committed_action']
        if action['kind']=='QUERY':
            revealed=row['public_revealed']['second']
            if revealed!=task['second']:raise ValueError('Query did not reveal the actual environment fact')
            new_fact=observation['second']is None
            expected_category='SUCCESS'if new_fact and program.get('feedback_mode','local_useful')=='local_useful'else'FAILURE'
            if row['public_return']!={'category':expected_category} or row['task_completed']:
                raise ValueError('Query feedback or final-file status invalid')
            checks+=1
        if row.get('quality_private_after_commit'):
            committed=row['committed_effect']
            public={'task_id':committed['task_id'],'text':observation['text'],
                    'operands':[observation['left'],observation['second']]}
            report=quality.evaluate_committed({**public,'required_operation':task['required_operation']},
                committed,sandbox_root=directory/'artifacts',policy=program.get('quality_policy',POLICY))
            before=copy.deepcopy(row['quality_private_after_commit']);before.pop('evaluation_resources',None)
            after=copy.deepcopy(report);after.pop('evaluation_resources',None)
            if before!=after:raise ValueError('Quality cannot be recalculated from actual archived artifact')
            if row['correct']!=int(report['task_success']):raise ValueError('Completion count differs from recalculated quality')
            calls=committed['provider_calls']
            if sum(calls.values())not in(0,1)or calls.get('native',0)+calls.get('external',0)!=sum(calls.values()):
                raise ValueError('Dual provider call or unknown provider')
            checks+=1;files+=int(bool(committed.get('artifact')))
        if row['public_return']is not None:
            policy.feedback(copy.deepcopy(observation),copy.deepcopy(action),copy.deepcopy(row['public_return']))
        if policy.state()!=row['policy_state_after']:raise ValueError('Policy state differs after archived return')
        checks+=1
    return {'schema':'DEE.APD03.comparator_archive_recalculation.R01','checks':checks,
            'artifact_quality_recomputed':files,'issues':0,'new_provider_calls':0,'new_native_ticks':0,
            'excludes_original_nondeterministic_timings':True}


def recalculate(directory):
    directory=Path(directory)
    validate_archived(directory)
    program=json.loads((directory/'programa_ejecutado.json').read_text(encoding='utf8'))
    rows=[json.loads(line) for line in (directory/'eventos_primarios.jsonl').read_text(encoding='utf8').splitlines()]
    return recalculate_rows(rows,program)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--program');parser.add_argument('--output')
    parser.add_argument('--policy',choices=tuple(POLICIES))
    parser.add_argument('--recalculate')
    parser.add_argument('--validate')
    args=parser.parse_args()
    if args.validate:
        result=validate_archived(args.validate)
    elif args.recalculate:
        result=recalculate(args.recalculate)
    else:
        if not all((args.program,args.output,args.policy)):
            parser.error('--program --output --policy are required for execution')
        result=run(args.program,args.output,args.policy)
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
