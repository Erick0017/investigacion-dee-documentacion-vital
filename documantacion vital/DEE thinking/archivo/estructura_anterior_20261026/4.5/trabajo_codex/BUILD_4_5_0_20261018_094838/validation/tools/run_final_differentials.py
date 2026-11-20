"""Repeat candidate validation against fixed original4.0 data, never rebuild it.

Exactly two independent native worker trees at most. Each tree has its own
Windows JobObject/timeouts under the original campaign supervisor. Every
Runtime still has a single mutable writer. Inputs/configs are unchanged.
"""
from __future__ import annotations
import argparse,concurrent.futures,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from neutral_differential import put,sha
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from supervisor import run

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--python',type=Path,required=True);parser.add_argument('--reference-python',type=Path,default=ROOT/'.venv40/Scripts/python.exe');parser.add_argument('--candidate',required=True);a=parser.parse_args()
    if not a.python.is_file():raise FileNotFoundError(a.python)
    if not a.candidate.isidentifier():raise ValueError('Use an explicit unique artifact identifier')
    v=ROOT/'validation';tools=v/'tools';py=str(a.python.resolve());candidate=a.candidate
    neutral=v/('differential_4_5_'+candidate);cpc=v/('cpc_ports_4_5_'+candidate);revision=v/('finite_revision_4_5_'+candidate)
    if not a.reference_python.is_file():raise FileNotFoundError(a.reference_python)
    original_py=str(a.reference_python.resolve());cross=v/('cross_process_'+candidate);reports=[]
    def task(label,script,args,timeout=600,executable=py):
        argv=[str(executable),'-I','-B',str(tools/script),*[str(x) for x in args]];name=candidate+'_'+label
        command=ROOT/'jobs'/name/'COMMAND.json'
        if command.exists():
            old=json.loads(command.read_text(encoding='utf8'))
            if old['argv']!=argv or old['status']!='COMPLETED' or old['exit_code']!=0:raise RuntimeError('Existing job is not a matching successful completion: '+name)
            reports.append({'label':label,'command':'jobs/'+name+'/COMMAND.json','resumed_existing_success':True});return old
        result=run(name,argv,timeout=timeout)
        reports.append({'label':label,'command':'jobs/'+name+'/COMMAND.json','resumed_existing_success':False})
        if result['exit_code']!=0:raise RuntimeError('Validation worker failed: '+name)
        return result
    put(v/('FINAL_PLAN_'+candidate+'.json'),{'schema':'DEE45.final_differential_plan.v1','candidate':candidate,'interpreter':py,'configuration_sha256':{name:sha(tools/name) for name in ('neutral_config.json','port_config.json','revision_port_config.json','regulation_port_config.json')},'source_sha256':sha(__file__),'max_simultaneous_native_workers':2,'baseline_reprepared':False,'baseline_paths':['differential_4_0','cpc_ports_4_0','finite_revision_4_0','experimental_regulation_4_0'],'expected_version':'4.5.0','scope':'Same frozen cases, new installed native binary. No new scientific cases, no changed decoder, no historical reset.'})
    def ports():
        task('cpc_ports','cpc_port.py',['suite','--out',cpc,'--expected-version','4.5.0'],1500)
        task('finite_revision','revision_port.py',['suite','--out',revision,'--expected-version','4.5.0'],900)
        task('experimental_regulation','regulation_port.py',['suite','--out',v/('experimental_regulation_4_5_'+candidate),'--expected-version','4.5.0'],900)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(task,'neutral','neutral_batch.py',['--config',tools/'neutral_config.json','--out',neutral,'--expected-version','4.5.0'],2400),pool.submit(ports)]
        for future in futures:future.result()
    task('backend_comparison','neutral_checks.py',['backends','--suite',neutral,'--out',v/(candidate.upper()+'_BACKEND_EQUIVALENCE.json')])
    task('neutral_comparison','neutral_checks.py',['versions','--before',v/'differential_4_0','--after',neutral,'--out',v/('NEUTRAL_DIFF_'+candidate+'.json')])
    for label,before,after,target in [('cpc',v/'cpc_ports_4_0',cpc,'CPC_PORT_DIFF_'),('revision',v/'finite_revision_4_0',revision,'FINITE_REVISION_DIFF_')]:
        task(label+'_comparison','cpc_port_compare.py',['--before',before,'--after',after,'--out',v/(target+candidate+'.json')])
    task('experimental_regulation_comparison','cpc_port_compare.py',['--before',v/'experimental_regulation_4_0','--after',v/('experimental_regulation_4_5_'+candidate),'--out',v/('EXPERIMENTAL_REGULATION_DIFF_'+candidate+'.json')])
    for direction,engine,source,version in [('old',py,v/'differential_4_0','4.5.0'),('new',original_py,neutral,'4.0.0')]:
        for kind,case,tick in [('runtime','R11_ADMISSION_QUEUE_LAZY',12),('recipe','P00_MOBILE_PAIR_LAZY',16)]:
            label=direction+'_'+kind+('_on_45' if direction=='old' else '_on_40');target=cross/label
            task('snapshot_'+label,'neutral_checks.py',['resume','--snapshot',source/case/'PENDING.deetsnap','--kind',kind,'--expected-version',version,'--target-tick',tick,'--out',target],300,engine)
            task('snapshot_check_'+label,'neutral_checks.py',['resume-check','--resumed',target,'--reference',source/case,'--out',cross/(label+'_CHECK.json')])
    task('api_inventory','api_surface.py',['inventory','--expected-version','4.5.0','--out',v/('api45_'+candidate+'.json')],120)
    task('api_comparison','api_surface.py',['compare','--before',v/'api40.json','--after',v/('api45_'+candidate+'.json'),'--out',v/('API_DIFF_'+candidate+'.json')],120)
    task('summary','validation_summary.py',['--validation',v,'--candidate',candidate,'--out',v/('TECHNICAL_DIFFERENTIAL_SUMMARY_'+candidate+'.json')],120)
    put(v/('FINAL_RUN_'+candidate+'.json'),{'schema':'DEE45.final_differential_run.v1','candidate':candidate,'status':'PASS','configuration_sha256':sha(v/('FINAL_PLAN_'+candidate+'.json')),'jobs':reports,'baseline_new_preparations':0,'native_world_paths':48+10+6+4,'cross_version_cross_process_continuations':4,'scientific_replication_claim':False})
    print(json.dumps({'candidate':candidate,'status':'PASS','physical_paths':68,'cross_version_continuations':4}),flush=True)
if __name__=='__main__':main()
