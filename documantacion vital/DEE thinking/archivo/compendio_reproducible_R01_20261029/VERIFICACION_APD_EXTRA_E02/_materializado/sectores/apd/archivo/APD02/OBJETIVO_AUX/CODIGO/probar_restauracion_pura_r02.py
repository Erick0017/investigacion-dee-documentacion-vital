"""Pure external-state continuity; two processes, no DEE imports or ticks."""
import argparse,hashlib,importlib.util,json,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parent
def load(name,path):
    sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sys.modules[name]=m;sp.loader.exec_module(m);return m
def modules():
    return(load('goal_r02',HERE/'entorno_objetivo_aclaracion_r02.py'),load('goal_driver_r02',HERE/'aparato_objetivo_aclaracion_r02.py'),
        load('post_quality',LAB/'calidad/evaluador_calidad_apd02.py'),load('file_effects',LAB/'calidad/proveedores_prueba_apd02.py'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,value):
    with p.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2)
def child(statefile,dest,result):
    env,driver,q,e=modules();state=json.loads(statefile.read_bytes());goal=env.restore_operational(state,directory=dest,quality=q,effects=e)
    before=goal.operational_state();calls=[];row=None
    if not goal.terminal():
        # A fixture receipt, not an action policy or a native learner.
        def fixture(op,values):calls.append({'op':op,'operands':list(values),'synthetic_fixture_only':True});return 11
        row=goal.commit_selected(-1,1,native_value_reader=fixture,synthetic_fixture=True)
    after=goal.operational_state();write(result,{'before':before,'after':after,'effect':row,'calls':calls,'native_ticks':0,'engine_imported':False})
def main(out):
    if out.exists():raise FileExistsError('Preserve all executed fixtures')
    out.mkdir(parents=True);env,driver,q,e=modules();files=[Path(__file__),HERE/'entorno_objetivo_aclaracion_r02.py',HERE/'aparato_objetivo_aclaracion_r02.py',LAB/'calidad/evaluador_calidad_apd02.py',LAB/'calidad/proveedores_prueba_apd02.py']
    (out/'FUENTES').mkdir()
    for p in files:(out/'FUENTES'/p.name).write_bytes(p.read_bytes())
    issues=[];rows=[]
    for case in('after_query','after_wrong_act','uncertain','completed','exhausted'):
        goal=env.GoalEnvironment(task_id=case,text='suma',left=7,second=4,second_initially_public=case!='after_query',directory=out/(case+'_original'),quality=q,effects=e)
        if case=='after_query':goal.commit_selected(0,1,native_value_reader=lambda *_:11,synthetic_fixture=True)
        elif case=='after_wrong_act':goal.commit_selected(-1,-1,native_value_reader=lambda *_:3,synthetic_fixture=True)
        elif case=='completed':goal.commit_selected(-1,1,native_value_reader=lambda *_:11,synthetic_fixture=True)
        elif case=='exhausted':
            for _ in range(4):goal.commit_selected(None,None,native_value_reader=lambda *_:11,synthetic_fixture=True)
        else:
            class FaultEffects:
                @staticmethod
                def execute_selected(*args,**kwargs):return e.execute_selected(*args,**kwargs,fault={'fail_after_write':True})
            goal._effects=FaultEffects
            goal.commit_selected(-1,1,native_value_reader=lambda *_:11,synthetic_fixture=True)
        state=goal.operational_state();statefile=out/(case+'_STATE.json');goal.checkpoint(statefile)
        # No original absolute directory or event-based answer table is in
        # the transferable world facts. Private b remains environmental.
        if str(goal._directory)in statefile.read_text(encoding='utf8')or'events'in state:issues.append([case,'Original path/history leaked into operational state'])
        result=out/(case+'_CHILD.json')
        with tempfile.TemporaryDirectory(prefix='apd02_goal_n0_')as tmp:
            proc=subprocess.run([sys.executable,'-I','-B','-X','utf8',str(Path(__file__).resolve()),'--child',str(statefile.resolve()),'--destination',str((out/(case+'_restored')).resolve()),'--result',str(result.resolve())],cwd=tmp,capture_output=True,text=True,encoding='utf8',timeout=30)
        if proc.returncode:issues.append([case,'Child error',proc.returncode,proc.stderr]);continue
        data=json.loads(result.read_bytes())
        if data['before']!=state:issues.append([case,'Restore changed facts/counter/artifact bytes'])
        if case in('after_query','after_wrong_act')and(not data['after']['progress']['verified_file_goal_completed']or data['after']['progress']['opportunities_used']!=2 or len(data['calls'])!=1):issues.append([case,'Expected one post-reload ACT, no cursor reset'])
        if case in('uncertain','completed','exhausted')and(data['calls']or data['before']!=data['after']):issues.append([case,'Terminal/uncertain state was silently retried or changed'])
        if case=='after_wrong_act'and len(data['after']['artifacts'])!=2:issues.append([case,'Old wrong-file evidence was not preserved'])
        rows.append({'case':case,'initial_cursor':state['progress']['opportunities_used'],'after_cursor':data['after']['progress']['opportunities_used'],
            'completed':data['after']['progress']['verified_file_goal_completed'],'uncertain':data['after']['progress']['uncertain_effect']is not None,
            'artifact_count':len(data['after']['artifacts']),'state_sha256':sha(statefile),'child_sha256':sha(result),'state_equal_before_next_step':data['before']==state,
            'separate_child_process':True,'native_ticks':0})
    # Driver unit fixture: maximum=1 does not silently execute a second action.
    goal=env.GoalEnvironment(task_id='single_step',text='suma',left=7,second=4,second_initially_public=False,directory=out/'single_step_original',quality=q,effects=e)
    class WordsFixture:
        @staticmethod
        def query(*args,**kwargs):return{'reader':{'formed_native_command':1},'synthetic_fixture':True}
    class LearnerFixture:
        calls=[]
        @classmethod
        def use(cls,*args):cls.calls.append('use');return{'reader':{'choice':0},'synthetic_fixture':True}
        @classmethod
        def consequence(cls,a,category,mode):cls.calls.append({'category':category,'mode':mode});return{'synthetic_fixture':True}
    class ArithmeticFixture:
        @staticmethod
        def native_pair(*args,**kwargs):raise AssertionError('QUERY may not call arithmetic')
    result=driver.run_opportunities(None,goal,LearnerFixture,words=WordsFixture,arithmetic=ArithmeticFixture,maximum=1)
    if len(result['opportunities'])!=1 or goal.progress()['opportunities_used']!=1 or LearnerFixture.calls!=['use',{'category':'FAILURE','mode':'real'}]:issues.append(['driver','Maximum1 or category-only consequence violated'])
    write(out/'RESULTADO.json',{'schema':'APD02.goal_operational_restore.pure.R02','cases':rows,'driver_one_step_fixture':result,
        'issues':issues,'new_native_ticks':0,'engine_imported':False,'fixture_actions_are_not_a_DEE_policy':True,
        'sources':{str(p):sha(p)for p in files},'scope':'Pure environment persistence and actuator tests. Does not demonstrate native selection, learning, a complete paired Cognitive restart or a native response.'})
    print(json.dumps({'cases':len(rows),'driver_one_step':len(result['opportunities']),'issues':issues,'native_ticks':0},ensure_ascii=False))
    if issues:raise SystemExit(1)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path);p.add_argument('--child',type=Path);p.add_argument('--destination',type=Path);p.add_argument('--result',type=Path);a=p.parse_args()
    if a.child:child(a.child,a.destination,a.result)
    elif a.out:main(a.out)
    else:p.error('Use --out for pure fixtures, or explicit child restoration arguments')
