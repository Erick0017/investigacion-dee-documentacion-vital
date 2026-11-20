"""Executed conventional references to the frozen MAIN-derived APD03 program.

No Runtime, no actor import, no Native ticks. Only a projected presence bit,
old mathematical cue and fixed tool interfaces reach selection. Arithmetic
values are supplied to the selected conventional executor after commitment.
"""
from __future__ import annotations
import argparse,copy,importlib.util,json,sys,time
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('comparison_n0_r01',HERE/'comparadores_apd03.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
SCHEMA='DEE.APD03.executed_conventional_comparator.R02.blind_context_presence_only'


class Fixed(base.Fixed):
    def choose(self,observation):
        # Same public action interfaces; quality windows do not offer QUERY.
        if 'QUERY'not in observation['public_resources']['allowed_actions']:
            return base.CommonPolicy.choose(self,observation)
        return super().choose(observation)


POLICIES={p.name:p for p in(Fixed,base.ContextTable,base.WinStayLoseShift)}


def projection(task,second):
    return {'text':task['text'],'left':None,'second':None if second is None else 0,
        'context':0,'public_resources':copy.deepcopy(task['public_resources'])}


def raw_observation(task,second):
    return {'text':task['text'],'left':task['left'],'second':second,
        'context':task['context'],'public_resources':copy.deepcopy(task['public_resources'])}


def check_program(program):
    if program['schema']!='DEE.APD03.common_task_program.R01':raise ValueError('Wrong program')
    if not program.get('derived_without_Main_outcomes'):raise ValueError('Prospective derivation required')
    normalized={'schema':program['schema'],'events':[],'feedback_mode':'local_useful'}
    for event in program['events']:
        if event['kind']=='environment_law':continue
        if event['kind']!='task':raise ValueError('Unknown event')
        task=copy.deepcopy(event);task.pop('kind')
        if task['feedback']not in('real','omit'):raise ValueError('Unknown feedback')
        if task['feedback_mode']not in('local_useful','file_quality'):raise ValueError('Unknown mode')
        if sum(task['opportunity_invocations'])!=task['max_opportunities']:raise ValueError('Opportunity mismatch')
        allowed=task['public_resources']['allowed_actions']
        if not allowed or any(a not in('ACT','QUERY')for a in allowed):raise ValueError('Unknown action')
        normalized['events'].append({'kind':'task','task':task})
    base.check_program(normalized)
    return True


def fault_config(label):
    table={'none':{},'wrong_value':{'wrong_value_delta':1},
        'filesystem':{'fail_before_write':True},'invalid_json':{'corrupt_json':True}}
    if label not in table:raise ValueError('Unsupported declared fault')
    return copy.deepcopy(table[label])


def restore_policy(name,state):
    policy=POLICIES[name]();policy.lexicon=dict(state['lexicon']);policy.queries=state['queries']
    if name=='tabla_contextual':policy.table=copy.deepcopy(state['counts_successes_attempts'])
    if name=='wsls':policy.route=state['last_route']
    return policy


def state(policy):return {**policy.state(),'queries':policy.queries}


def task_mode(task):return 'local_useful'if task['feedback_mode']=='local_useful'else'file_only'


def run(program_path,out,name):
    guard=base.load_module(HERE/'vendor/process_control.py','reference_owned_job')
    guard.protect_current(output=False,memory_limit=256*1024*1024)
    start=base.process_resources();program_bytes=Path(program_path).read_bytes();program=json.loads(program_bytes)
    check_program(program);out=Path(out).resolve();out.mkdir(parents=True,exist_ok=False)
    artifacts=out/'artifacts';artifacts.mkdir()
    quality=base.load_module(HERE/'vendor/evaluador_calidad_apd02.py','quality_r02')
    effects=base.load_module(HERE/'vendor/proveedores_prueba_apd02.py','effects_r02')
    policy=POLICIES[name]();rows=[];phases=[]
    with(out/'eventos_primarios.jsonl').open('xb')as stream:
        def record(row):
            stream.write(base.canonical(row));stream.flush();rows.append(row)
        for index,lesson in enumerate(program['preparation']['prior_knowledge']):
            before=base.process_resources();teaching={k:lesson[k]for k in('text','operation')}
            policy.teach(teaching)
            record({'kind':'preparation','preparation_index':index,'public_teaching':teaching,
                'policy_state_after':state(policy),'scope':'Supplied past association, not new APD03 acquisition',
                'resources':base.resource_delta(before,base.process_resources())})
        phases.append({'phase':'load_prior_and_environment','resources':base.resource_delta(start,base.process_resources())})
        for seq,event in enumerate(program['events']):
            if event['kind']=='environment_law':
                # Auditor-only environmental change. The policy receives no
                # event, route health, law config, task identity or schedule.
                record({'sequence':seq,'kind':'environment_law','auditor_event':event,'delivered_to_policy':False})
                continue
            task=event;second=task['second']if task['second_initially_public']else None
            policy.begin_task();completed=False;before_task=base.process_resources()
            invocation_ends=[];cumulative=0
            for n in task['opportunity_invocations']:
                cumulative+=n;invocation_ends.append(cumulative)
            for opportunity in range(1,task['max_opportunities']+1):
                obs=projection(task,second);before=base.process_resources();old_state=state(policy)
                action=policy.choose(copy.deepcopy(obs));after=base.process_resources()
                if action['kind']not in task['public_resources']['allowed_actions']and action['kind']!='NO_OUTPUT':
                    raise ValueError('Policy exceeded public interface')
                row={'kind':'opportunity','sequence':seq,'task_id':task['task_id'],'origin_block':task['origin_block'],
                    'scheduled_enabled_seconds_auditor':task['scheduled_enabled_seconds'],
                    'opportunity':opportunity,'public_observation':obs,'raw_observation_auditor':raw_observation(task,second),
                    'policy_state_before':old_state,'committed_action':action,
                    'decision_resources':base.resource_delta(before,after),'requested':1,'admitted_conventional':1}
                effect_start=base.process_resources();category='FAILURE';new_fact=False
                if action['kind']=='QUERY':
                    new_fact=second is None;second=task['second']
                    category='SUCCESS'if new_fact and task_mode(task)=='local_useful'else'FAILURE'
                    row.update(environment_effect='SECOND_OPERAND_OBSERVED',new_public_fact_revealed=new_fact,
                        public_revealed={'second':second},local_action_useful=new_fact,
                        answered=1,correct=0,no_response=0,query_price=task['public_resources'].get('query_price',0))
                elif action['kind']=='NO_OUTPUT':
                    row.update(environment_effect='NO_OUTPUT',answered=0,correct=0,no_response=1,local_action_useful=False)
                elif second is None:
                    row.update(environment_effect='ACT_FAILED_MISSING_OBSERVATION',answered=1,correct=0,no_response=0,local_action_useful=False)
                else:
                    route=action['procedure'];effect_id=task['task_id']+'_attempt'+str(opportunity)
                    public={'task_id':effect_id,'text':task['text'],'operands':[task['left'],second]}
                    committed=effects.execute_selected(public,{'operation':action['operation'],'procedure':route},
                        sandbox_root=artifacts,native_value_reader=base.arithmetic,external_calculator=base.arithmetic,
                        law=task['laws'][route],fault=fault_config(task['faults'][route]),synthetic_fixture=True)
                    row['committed_effect']=committed
                    if committed['state']=='uncertain':
                        row.update(environment_effect='UNCERTAIN_EFFECT',answered=1,correct=0,no_response=0,
                            local_action_useful=False,stop_task_for_explicit_reconciliation=True)
                    else:
                        report=quality.evaluate_committed({**public,'required_operation':task['required_operation']},
                            committed,sandbox_root=artifacts,policy=base.POLICY)
                        category=quality.actor_feedback(report,binary=True)['category'];completed=bool(report['task_success'])
                        row.update(quality_private_after_commit=report,environment_effect='VERIFIED_GOAL_FILE'if completed else'TERMINAL_TASK_NOT_VERIFIED',
                            answered=1,correct=int(completed),no_response=0,local_action_useful=completed)
                row['effect_resources']=base.resource_delta(effect_start,base.process_resources())
                row['computed_return_auditor']={'category':category}
                delivered=task['feedback']=='real'and not row.get('stop_task_for_explicit_reconciliation')
                row['return_delivered']=delivered;row['public_return']={'category':category}if delivered else None
                if delivered:policy.feedback(copy.deepcopy(obs),copy.deepcopy(action),row['public_return'])
                row.update(policy_state_after=state(policy),final_goal_file_completed=completed,
                    feedback_mode=task_mode(task),feedback_transduction=task['feedback'],
                    private_environment_after_commit={key:copy.deepcopy(task[key])for key in('required_operation','laws','faults','second')})
                record(row)
                if opportunity in invocation_ends[:-1]and not completed:
                    # Preserve pending environment and policy between specified
                    # invocations; this is an in-process serialization test,
                    # not the Native UI/process-continuation experiment.
                    checkpoint={'policy':state(policy),'second':second,'task_id':task['task_id'],'next_opportunity':opportunity+1}
                    data=base.canonical(checkpoint);decoded=json.loads(data)
                    policy=restore_policy(name,decoded['policy']);second=decoded['second']
                    record({'kind':'invocation_boundary','sequence':seq,'task_id':task['task_id'],
                        'checkpoint':checkpoint,'sha256':base.digest(data),'same_process':True})
                if completed or row.get('stop_task_for_explicit_reconciliation'):break
            phases.append({'phase':'task_with_logging','sequence':seq,'task_id':task['task_id'],
                'resources':base.resource_delta(before_task,base.process_resources())})
    end=base.process_resources();summary=metrics(rows,program)
    summary.update(schema=SCHEMA,policy=name,program_sha256=base.digest(program_bytes),
        source_sha256=base.digest(Path(__file__).read_bytes()),base_source_sha256=base.digest((HERE/'comparadores_apd03.py').read_bytes()),
        owned_job_resources=guard.current_resources(),
        policy_state_final=state(policy),phases=phases,process_total=base.resource_delta(start,end),
        process_scope='One conventional process; counters exclude launcher and final summary write',energy='NO MEDIDA',
        schedule='Logical event order and opportunity budgets; no artificial 3600s sleep, no Native basal evolution equivalence',
        scope='8 native-only goals and 3 quality/availability tasks; not lexical/MA/composition or full MAIN equivalence',
        arithmetic='Both nominal callbacks conventional, not measured DEE/v27 cost',
        information_fence='context constant0; no operand magnitude before selection; second0/None is presence only; private laws never policy inputs',
        eventlog_sha256=base.digest((out/'eventos_primarios.jsonl').read_bytes()),python=sys.version)
    base.save(out/'programa_ejecutado.json',program);base.save(out/'resumen.json',summary)
    base.save(out/'MANIFIESTO.json',{'members':[{'path':p.relative_to(out).as_posix(),'bytes':p.stat().st_size,
        'sha256':base.digest(p.read_bytes())}for p in sorted(out.rglob('*'))if p.is_file()],'excludes_own_hash':True})
    return summary


def metrics(rows,program):
    opportunities=[r for r in rows if r['kind']=='opportunity'];tasks=[]
    for task in(e for e in program['events']if e['kind']=='task'):
        rr=[r for r in opportunities if r['task_id']==task['task_id']];acts=[r for r in rr if r['committed_action']['kind']=='ACT']
        tasks.append({'task_id':task['task_id'],'domain':'two_provider_quality'if len(task['allowed_procedures'])==2 else'native_only_goal',
            'opportunities':len(rr),'queries':sum(r['committed_action']['kind']=='QUERY'for r in rr),'acts':len(acts),
            'completed':any(r['final_goal_file_completed']for r in rr),'correct_effects':sum(r['correct']for r in acts),
            'wrong_or_unusable_acts':sum(not r['correct']for r in acts),'no_output':sum(r['no_response']for r in rr),
            'local_useful_actions':sum(r['local_action_useful']for r in rr),
            'feedback_delivered':sum(r['return_delivered']for r in rr),
            'synthetic_price':sum(r.get('committed_effect',{}).get('price',0)+r.get('query_price',0)for r in rr)})
    return {'tasks':tasks,'task_count':len(tasks),'tasks_completed':sum(t['completed']for t in tasks),
        'native_only_completed':sum(t['completed']for t in tasks if t['domain']=='native_only_goal'),
        'native_only_total':sum(t['domain']=='native_only_goal'for t in tasks),
        'quality_completed':sum(t['completed']for t in tasks if t['domain']=='two_provider_quality'),
        'quality_total':sum(t['domain']=='two_provider_quality'for t in tasks),
        'opportunities_requested':len(opportunities),'admitted_conventional':sum(r['admitted_conventional']for r in opportunities),
        'answered':sum(r['answered']for r in opportunities),'correct_files':sum(r['correct']for r in opportunities),
        'wrong_or_unusable_acts':sum(t['wrong_or_unusable_acts']for t in tasks),
        'queries':sum(t['queries']for t in tasks),'no_output':sum(t['no_output']for t in tasks),
        'feedback_omitted':sum(not r['return_delivered']for r in opportunities),
        'uncertain_effects':sum(bool(r.get('stop_task_for_explicit_reconciliation'))for r in opportunities),
        'synthetic_price_total':sum(t['synthetic_price']for t in tasks),
        'sample_unit':'One continuous policy trajectory, not one independent sample per opportunity'}


def recalculate(directory):
    directory=Path(directory);program=json.loads((directory/'programa_ejecutado.json').read_bytes())
    summary=json.loads((directory/'resumen.json').read_bytes());check_program(program)
    rows=[json.loads(line)for line in(directory/'eventos_primarios.jsonl').read_bytes().splitlines()]
    policy=POLICIES[summary['policy']]();quality=base.load_module(HERE/'vendor/evaluador_calidad_apd02.py','quality_recalc_r02')
    checks=0;artifacts=0;lastseq=None;second=None
    for row in rows:
        if row['kind']=='preparation':
            expected=program['preparation']['prior_knowledge'][row['preparation_index']]
            teaching={k:expected[k]for k in('text','operation')}
            if row['public_teaching']!=teaching:raise ValueError('Prior history differs')
            policy.teach(teaching)
            if state(policy)!=row['policy_state_after']:raise ValueError('Prior policy state differs')
            checks+=2;continue
        event=program['events'][row['sequence']]
        if row['kind']=='environment_law':
            if event!=row['auditor_event']or row['delivered_to_policy']:raise ValueError('Law leaked')
            checks+=1;continue
        if row['kind']=='invocation_boundary':
            checkpoint=row['checkpoint']
            if checkpoint['policy']!=state(policy)or checkpoint['second']!=second:raise ValueError('Continuation differs')
            if base.digest(base.canonical(checkpoint))!=row['sha256']:raise ValueError('Continuation hash differs')
            policy=restore_policy(summary['policy'],json.loads(base.canonical(checkpoint))['policy']);checks+=2;continue
        task=event
        if lastseq!=row['sequence']:
            policy.begin_task();lastseq=row['sequence'];second=task['second']if task['second_initially_public']else None
        if row['public_observation']!=projection(task,second)or row['raw_observation_auditor']!=raw_observation(task,second):raise ValueError('Observation fence differs')
        if row['policy_state_before']!=state(policy):raise ValueError('Predecision policy differs')
        action=policy.choose(copy.deepcopy(row['public_observation']))
        if action!=row['committed_action']:raise ValueError('Decision not reproducible from public past')
        checks+=3;expected_category='FAILURE';complete=False
        if action['kind']=='QUERY':
            expected_category='SUCCESS'if second is None and task_mode(task)=='local_useful'else'FAILURE'
            second=task['second']
            if row['public_revealed']!={'second':second}:raise ValueError('False revealed fact')
            checks+=1
        elif row.get('quality_private_after_commit'):
            committed=row['committed_effect'];request={'task_id':committed['task_id'],'text':task['text'],'operands':[task['left'],second]}
            report=quality.evaluate_committed({**request,'required_operation':task['required_operation']},committed,
                sandbox_root=directory/'artifacts',policy=base.POLICY)
            old=copy.deepcopy(row['quality_private_after_commit']);old.pop('evaluation_resources',None)
            actual=copy.deepcopy(report);actual.pop('evaluation_resources',None)
            if old!=actual:raise ValueError('Archived artifact quality differs')
            expected_category=quality.actor_feedback(report,binary=True)['category'];complete=bool(report['task_success'])
            if sum(committed['provider_calls'].values())not in(0,1):raise ValueError('Dual provider call')
            artifacts+=int(bool(committed.get('artifact')));checks+=2
        delivered=task['feedback']=='real'and not row.get('stop_task_for_explicit_reconciliation')
        expected_return={'category':expected_category}if delivered else None
        if row['public_return']!=expected_return or row['computed_return_auditor']!={'category':expected_category}:raise ValueError('Binary return differs')
        if row['return_delivered']!=delivered or row['final_goal_file_completed']!=complete or row['correct']!=int(complete):raise ValueError('Denominators differ')
        if delivered:policy.feedback(copy.deepcopy(row['public_observation']),copy.deepcopy(action),expected_return)
        if state(policy)!=row['policy_state_after']:raise ValueError('Postfeedback state differs')
        checks+=3
    result=metrics(rows,program)
    for key,value in result.items():
        if summary[key]!=value:raise ValueError('Summary differs: '+key)
    return {'schema':'DEE.APD03.reference_recalculation.R02','policy':summary['policy'],'checks':checks,
        'issues':0,'actual_artifacts_rechecked':artifacts,'new_provider_calls':0,'new_native_ticks':0,
        'metrics':result,'resource_counters_not_regenerated':True}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--program');parser.add_argument('--out')
    parser.add_argument('--policy',choices=tuple(POLICIES));parser.add_argument('--recalculate');args=parser.parse_args()
    result=recalculate(args.recalculate)if args.recalculate else run(args.program,args.out,args.policy)
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
