"""Replay the exact CPC7 candidate in a fresh offline environment, outside source.

The immutable plan comes from inside that candidate. Expected-state comparisons
belong to explicit later auditor commands, never to the participant's runtime.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import zipfile

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE));sys.path.insert(0,str(HERE.parent))
from bundle import ROOT,WHL,WHL_SHA,PYD_SHA,put,sha,safe_name,verify
from supervisor import OwnedJob,remaining

ENGINE_CHECK=r'''
import hashlib,json,pathlib,sys
import dee_thinking as d
assert sys.version_info[:2]==(3,13) and sys.maxsize>2**32
assert d.__version__=='4.0.0' and d.kernel_identity()['kernel_version']==27
module=pathlib.Path(d.__file__).resolve()
assert module.is_relative_to(pathlib.Path(sys.prefix).resolve()/'Lib'/'site-packages')
assert hashlib.sha256(pathlib.Path(d._native.__file__).read_bytes()).hexdigest()==sys.argv[1]
assert not any(name.startswith(('dee_universe','CPC3','SEM01')) for name in sys.modules)
pathlib.Path(sys.argv[2]).write_text(json.dumps({'version':d.__version__,'kernel':d.kernel_identity(),
 'module':str(module),'python':sys.executable,'native_sha256':sys.argv[1]},indent=2),encoding='utf-8')
'''

def run_command(argv,cwd,directory,label,timeout,deadline):
    allowed=min(float(timeout),max(0,deadline-time.monotonic()))
    if allowed<=0:raise TimeoutError('Original campaign/task deadline reached')
    env=dict(os.environ,PYTHONNOUSERSITE='1',PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
    env.pop('PYTHONPATH',None);env.pop('PYTHONHOME',None)
    started=time.monotonic();job=None;status='START_ERROR';process=None;error=None
    with (directory/(label+'.stdout.log')).open('wb') as stdout,(directory/(label+'.stderr.log')).open('wb') as stderr:
        try:
            process=subprocess.Popen([str(value) for value in argv],cwd=str(cwd),env=env,stdout=stdout,stderr=stderr,
                                     creationflags=subprocess.CREATE_NO_WINDOW)
            job=OwnedJob(process);status='COMPLETED'
            try:process.wait(timeout=allowed)
            except subprocess.TimeoutExpired:status='TIMEOUT';job.terminate();process.wait(timeout=30)
        except BaseException as exc:
            error=repr(exc)
            if process is not None and process.poll() is None:
                if job:job.terminate()
                else:process.kill()
                process.wait(timeout=30)
        finally:
            if job:job.close()
    result={'label':label,'argv':[str(value) for value in argv],'cwd':str(cwd),'elapsed_seconds':time.monotonic()-started,
            'timeout_seconds':allowed,'status':status,'exit_code':process.returncode if process else None,'error':error,
            'owned_worker_waited':process is not None and process.poll() is not None,
            'owned_job_closed':job is not None and job.handle is None}
    put(directory/(label+'.COMMAND.json'),result)
    return result

def pointer(data,path):
    if path=='':return data
    assert path.startswith('/'),'JSON assertion paths use JSON Pointer'
    for part in path[1:].split('/'):
        part=part.replace('~1','/').replace('~0','~')
        data=data[int(part)] if isinstance(data,list) else data[part]
    return data

def validate_plan(plan):
    assert plan['schema']=='CPC7.clean-plan.v1'
    assert plan['commands'] and plan['assertions'],'Actual native replay and posttrajectory assertions are mandatory'
    ids=[row['id'] for row in plan['commands']]
    assert len(ids)==len(set(ids))
    for identifier in ids:assert identifier and all(c.isalnum() or c in '_-' for c in identifier)
    for row in plan['commands']:
        assert row['argv'][0]=='{python}','Use only the fresh isolated interpreter'
        assert isinstance(row.get('timeout_seconds',300),(int,float)) and 0<row.get('timeout_seconds',300)<=1200
    for row in plan['assertions']:
        safe_name(row['path']);assert row['equals']
        assert all(key=='' or key.startswith('/') for key in row['equals'])

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate',type=Path,required=True);p.add_argument('--destination',type=Path,required=True)
    p.add_argument('--plan-member',default='configuraciones/CLEAN_PLAN.json')
    p.add_argument('--report',type=Path,required=True);p.add_argument('--timeout',type=int,default=1800)
    p.add_argument('--respect-budget',action='store_true');a=p.parse_args()
    start=time.monotonic();deadline=start+a.timeout
    if a.respect_budget:deadline=min(deadline,start+remaining())
    commands=[];assertions=[];container=None;error=None;status='ERROR';directory=a.destination.resolve();plan_sha=None
    try:
        assert not directory.is_relative_to(ROOT.resolve()),'Clean extraction must be outside CPC7 source'
        assert len(str(directory))<190,'Choose an explicit short Windows staging path'
        if directory.exists():raise FileExistsError(directory)
        safe_name(a.plan_member)
        container=verify(a.candidate)
        with zipfile.ZipFile(a.candidate) as archive:
            plan_raw=archive.read('CPC7/'+a.plan_member)
            plan=json.loads(plan_raw);validate_plan(plan)
            import hashlib
            plan_sha=hashlib.sha256(plan_raw).hexdigest()
            directory.mkdir(parents=True,exist_ok=False)
            extraction=directory/'extracted';extraction.mkdir();archive.extractall(extraction)
        root=extraction/'CPC7';assert sha(root/'runtime'/WHL)==WHL_SHA
        output=directory/'generated';output.mkdir()
        envdir=directory/'isolated_env';python=envdir/'Scripts/python.exe'
        automatic=[('00_venv',[sys.executable,'-I','-m','venv',str(envdir)],90),
          ('01_offline_install',[str(python),'-I','-m','pip','install','--no-index','--no-deps',str(root/'runtime'/WHL)],90),
          ('02_engine_identity',[str(python),'-I','-c',ENGINE_CHECK,PYD_SHA,str(directory/'ENGINE_IDENTITY.json')],90)]
        for label,argv,timeout in automatic:
            result=run_command(argv,directory,directory,label,timeout,deadline);commands.append(result)
            if result['exit_code']!=0 or result['status']!='COMPLETED':raise RuntimeError('Clean command failed: '+label)
        mapping={'{python}':str(python),'{root}':str(root),'{out}':str(output),'{work}':str(directory)}
        for i,row in enumerate(plan['commands']):
            argv=[]
            for argument in row['argv']:
                for key,value in mapping.items():argument=argument.replace(key,value)
                argv.append(argument)
            label=f'{i+3:02d}_'+row['id']
            result=run_command(argv,directory,directory,label,row.get('timeout_seconds',300),deadline);commands.append(result)
            if result['exit_code']!=0 or result['status']!='COMPLETED':raise RuntimeError('Clean command failed: '+label)
        for name in plan.get('required_outputs',[]):
            safe_name(name);path=output/name;assert path.is_file() and path.stat().st_size
        for row in plan['assertions']:
            path=output/row['path'];data=json.loads(path.read_text(encoding='utf-8-sig'))
            comparisons={key:pointer(data,key)==expected for key,expected in row['equals'].items()}
            assertions.append({'path':row['path'],'sha256':sha(path),'checks':comparisons,'observations':data})
            assert all(comparisons.values()),('Posttrajectory assertion failed',row['path'],comparisons)
        assert assertions and all(x['owned_worker_waited'] and x['owned_job_closed'] for x in commands)
        status='VERIFIED'
    except BaseException as exc:error=repr(exc)
    report={'schema':'CPC7.exact-clean-reproduction.v1','status':status,
      'candidate_sha256':container['sha256'] if container else sha(a.candidate) if a.candidate.exists() else None,
      'candidate_bytes':container['bytes'] if container else None,'plan_member':a.plan_member,'plan_sha256':plan_sha,
      'container_verification':container,'commands':commands,'posttrajectory_assertions':assertions,
      'error':error,'directory':str(directory),'elapsed_seconds':time.monotonic()-start,
      'completed_utc':datetime.now(timezone.utc).isoformat(),
      'engine_identity':json.loads((directory/'ENGINE_IDENTITY.json').read_text(encoding='utf-8')) if (directory/'ENGINE_IDENTITY.json').is_file() else None,
      'scope':'Exact candidate; plan read from inside that ZIP. Fresh noneditable offline wheel installation; each native task isolated under an owned JobObject. Audit assertions occur after completed trajectories.'}
    put(a.report,report);print(json.dumps({'status':status,'commands':len(commands),'assertions':len(assertions),'error':error,'elapsed_seconds':report['elapsed_seconds']},ensure_ascii=False,indent=2))
    if status!='VERIFIED':raise SystemExit(1)

if __name__=='__main__':main()
