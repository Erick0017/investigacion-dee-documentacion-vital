"""N0 real-file unit fixtures. No native organization or learned policy."""
import argparse,importlib.util,json,hashlib,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parent
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():raise FileExistsError('No overwrite')
    a.out.mkdir(parents=True)
    envmod=load('goal_environment',HERE/'entorno_objetivo_aclaracion_r01.py')
    q=load('quality_fixture',LAB/'calidad/evaluador_calidad_apd02.py');effects=load('effects_fixture',LAB/'calidad/proveedores_prueba_apd02.py')
    rows=[];issues=[]
    # These explicit action sequences are unit-test inputs, never a runner
    # for DEE. They test actuator laws, not how any policy selects an action.
    cases=[('complete',True,[(-1,1)],11),('missing_then_observed',False,[(-1,1),(0,1),(-1,1)],11),
        ('no_emission',False,[(None,1)],None),('wrong_operation',True,[(-1,-1)],3),
        ('no_operator',True,[(-1,None)],None),('query_when_already_public',True,[(1,1)],None)]
    for name,public,signs,fixture_value in cases:
        goal=envmod.GoalEnvironment(task_id=name,text='suma',left=7,second=4,second_initially_public=public,directory=a.out/name,quality=q,effects=effects)
        calls=[];events=[]
        def fixture(op,values):
            calls.append({'op':op,'values':list(values),'test_fixture_only_not_native':True});return fixture_value
        for action,operation in signs:events.append(goal.commit_selected(action,operation,native_value_reader=fixture,synthetic_fixture=True))
        if name=='complete'and not goal.progress()['verified_file_goal_completed']:issues.append([name,'Expected real valid file'])
        if name=='missing_then_observed':
            if events[0]['native_provider_called']or events[0]['public_after']['second']is not None:issues.append([name,'ACT manufactured data or invoked provider without datum'])
            if events[1]['feedback']!={'category':'FAILURE'}or events[1]['public_after']['second']!=4 or events[1]['progress_after']['verified_file_goal_completed']:issues.append([name,'QUERY must reveal only the real raw operand and remain incomplete'])
            if len(calls)!=1 or not goal.progress()['verified_file_goal_completed']:issues.append([name,'Expected sole ACT with visible data to complete'])
        if name in('no_emission','no_operator')and(calls or goal.progress()['filesystem_artifacts']):issues.append([name,'Invalid/silent emission must not produce work'])
        if name=='no_emission'and goal.observation()['second']is not None:issues.append([name,'Silence silently became QUERY'])
        if name=='wrong_operation'and(events[0]['quality']['feedback']['category']!='SEMANTIC_ERROR'or goal.progress()['verified_file_goal_completed']):issues.append([name,'Correct wrong-operator arithmetic must not complete original SUM goal'])
        if name=='query_when_already_public'and(calls or goal.progress()['verified_file_goal_completed']):issues.append([name,'QUERY substituted ACT'])
        goal.checkpoint(a.out/(name+'_ENV.json'))
        rows.append({'case':name,'input_action_signs':[x[0]for x in signs],'effects':[e['environment_effect']for e in events],
            'feedback':[e['feedback']for e in events],'provider_calls':calls,'progress':goal.progress(),
            'file_receipts':[e['committed_effect']['artifact']for e in events if e['committed_effect']],
            'scope':'Explicit synthetic unit fixtures, no Runtime/ticks or DEE action-selection test'})
    result={'schema':'APD02.goal_environment.pure_fixture.R01','new_native_ticks':0,'engine_imported':False,
        'cases':rows,'issues':issues,'sources':{str(f):sha(f)for f in(HERE/'entorno_objetivo_aclaracion_r01.py',
            HERE/'aparato_objetivo_aclaracion_r01.py',Path(__file__),LAB/'calidad/evaluador_calidad_apd02.py',LAB/'calidad/proveedores_prueba_apd02.py')},
        'no_native_or_learning_claim':True}
    with(a.out/'RESULTADO.json').open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps({'cases':len(rows),'issues':issues,'native_ticks':0,'output':str(a.out)},ensure_ascii=False))
    if issues:raise SystemExit(1)
if __name__=='__main__':main()
