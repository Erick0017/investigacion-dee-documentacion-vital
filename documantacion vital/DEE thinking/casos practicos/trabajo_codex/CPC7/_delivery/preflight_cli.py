"""Finite CLI startup preflight. --help is not scientific reproduction."""
import argparse,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src/packaging'));sys.path.insert(0,str(ROOT/'src'))
from bundle import put,sha
from clean import run_command,validate_plan
from supervisor import remaining

p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,required=True);a=p.parse_args()
directory=a.directory.resolve();assert directory.is_relative_to(ROOT/'_delivery')
directory.mkdir(parents=True,exist_ok=False)
plan_path=ROOT/'configuraciones/CLEAN_PLAN.json';plan=json.loads(plan_path.read_text(encoding='utf-8'));validate_plan(plan)
started=time.monotonic();deadline=started+min(180,remaining());commands=[];sources={}
for index,row in enumerate(plan['commands']):
    script=next(value for value in row['argv'] if value.endswith('.py')).replace('{root}',str(ROOT))
    sources[str(Path(script).relative_to(ROOT))]=sha(Path(script))
    argv=[sys.executable,'-I','-B','-X','utf8',script,'--help']
    result=run_command(argv,ROOT,directory,f'{index:02d}_'+row['id'],30,deadline);commands.append(result)
    if result['status']!='COMPLETED' or result['exit_code']!=0:break
result={'schema':'CPC7.cli-preflight.v1','classification':'STARTUP_ONLY_NOT_SCIENTIFIC_REPLAY',
        'status':'VERIFIED' if len(commands)==len(plan['commands']) and all(x['status']=='COMPLETED' and x['exit_code']==0 for x in commands) else 'ERROR',
        'commands':commands,'script_sources':sources,'plan_sha256':sha(plan_path),'source_sha256':sha(Path(__file__)),
        'elapsed_seconds':time.monotonic()-started,'native_experiment_requested':False,
        'scope':'Actual scientific tasks and posttrajectory comparisons remain mandatory for the exact candidate ZIP.'}
put(directory/'PREFLIGHT_REPORT.json',result)
print(json.dumps({'status':result['status'],'commands':len(commands),'seconds':result['elapsed_seconds']},indent=2))
if result['status']!='VERIFIED':raise SystemExit(1)
