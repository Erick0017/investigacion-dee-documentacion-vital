"""Fresh independent extraction and replay of a cumulative candidate.

The final report is external to its exact ZIP and never changes that archive.
Expected values are read only by explicit post-trajectory audit commands.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import zipfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from package_extension import EXT, PREFIX, WHL, WHL_SHA, PYD_SHA, put, sha, verify
from supervisor import module as frozen_supervisor
OwnedJob = frozen_supervisor.OwnedJob

ENGINE_CHECK = r'''
import hashlib,json,pathlib,sys
import dee_thinking as d
assert sys.version_info[:2]==(3,13) and sys.maxsize>2**32
assert d.__version__=='4.0.0' and d.kernel_identity()['kernel_version']==27
module=pathlib.Path(d.__file__).resolve()
assert module.is_relative_to(pathlib.Path(sys.prefix).resolve())
native=pathlib.Path(d._native.__file__)
assert hashlib.sha256(native.read_bytes()).hexdigest()==sys.argv[1]
snapshots=[]
for item in sys.argv[3:]:
 w=d.OrganizationalWorld.load_snapshot(item)
 assert len(w.runtime.raw_copy())==w.runtime.dimension**3
 assert len(w.runtime.clock_copy())==w.runtime.dimension**3
 snapshots.append({'path':item,'tick':w.runtime.current_tick,'N':w.runtime.dimension,
                   'channels':list(w.runtime.channel_names),'receipts':len(w.runtime.receipts),
                   'protocols':len(w.protocols)})
assert not any(n.startswith(('dee_universe','CPC3','SEM01')) for n in sys.modules)
pathlib.Path(sys.argv[2]).write_text(json.dumps({'version':d.__version__,
 'kernel':d.kernel_identity(),'python':sys.executable,'module':str(module),
 'native_sha256':sys.argv[1],'snapshots':snapshots},ensure_ascii=False,indent=2),encoding='utf-8')
'''


def run(argv, cwd, destination, label, timeout, deadline):
    allowed = min(timeout, max(0, deadline-time.monotonic()))
    if allowed <= 0: raise TimeoutError('Clean replay deadline exhausted')
    env = dict(os.environ, PYTHONNOUSERSITE='1', PYTHONDONTWRITEBYTECODE='1',
               PYTHONUTF8='1', OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1')
    env.pop('PYTHONPATH', None); env.pop('PYTHONHOME', None)
    started = time.monotonic(); job = None
    with (destination/(label+'.stdout.log')).open('w',encoding='utf-8') as stdout, \
         (destination/(label+'.stderr.log')).open('w',encoding='utf-8') as stderr:
        process = subprocess.Popen(argv,cwd=cwd,env=env,stdout=stdout,stderr=stderr,
                                   creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        try:
            if os.name=='nt': job=OwnedJob(process)
            status='COMPLETED'
            try: process.wait(timeout=allowed)
            except subprocess.TimeoutExpired:
                status='TIMEOUT'
                if job: job.terminate()
                else: process.kill()
                process.wait(timeout=30)
        except BaseException:
            if process.poll() is None:
                if job: job.terminate()
                else: process.kill()
                process.wait(timeout=30)
            raise
        finally:
            if job: job.close()
    result={'label':label,'argv':argv,'elapsed_seconds':time.monotonic()-started,
            'exit_code':process.returncode,'status':status,'timeout_seconds':allowed}
    put(destination/(label+'.COMMAND.json'),result)
    if process.returncode: raise RuntimeError('Clean command failed: '+label)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--destination',type=Path,required=True)
    p.add_argument('--plan',type=Path,required=True)
    p.add_argument('--report',type=Path,required=True)
    p.add_argument('--timeout',type=int,default=1200)
    p.add_argument('--respect-campaign-deadline',action='store_true')
    args=p.parse_args()
    started=time.monotonic(); deadline=started+args.timeout
    if args.respect_campaign_deadline:
        budget=json.loads((EXT/'BUDGET.json').read_text(encoding='utf-8'))
        remaining=(datetime.fromisoformat(budget['deadline_utc'])-datetime.now(timezone.utc)).total_seconds()
        deadline=min(deadline,started+max(0,remaining))
        if deadline<=started: raise TimeoutError('Original campaign deadline exhausted')
    plan=json.loads(args.plan.read_text(encoding='utf-8'))
    assert plan['schema']=='CPC5.extension.clean-reproduction-plan.v1'
    container=verify(args.candidate)
    destination=args.destination.resolve(); destination.mkdir(parents=True,exist_ok=False)
    commands=[]; explicit=[]; error=None; status='ERROR'
    try:
        extraction=destination/'extracted'; extraction.mkdir()
        with zipfile.ZipFile(args.candidate) as z: z.extractall(extraction)
        root=extraction/'CPC5'
        extension=root/'ampliaciones'/EXT.name
        assert sha(root/'runtime'/WHL)==WHL_SHA
        envdir=destination/'isolated_env'
        commands.append(run([sys.executable,'-I','-m','venv',str(envdir)],destination,destination,'00_venv',90,deadline))
        python=envdir/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
        commands.append(run([str(python),'-I','-m','pip','install','--no-index','--no-deps',str(root/'runtime'/WHL)],
                            destination,destination,'01_offline_install',90,deadline))
        checkpoints=[]
        for name in plan.get('checkpoints',[]):
            path=(root/name).resolve(); assert path.is_relative_to(root) and path.is_file()
            checkpoints.append(str(path))
        commands.append(run([str(python),'-I','-c',ENGINE_CHECK,PYD_SHA,str(destination/'ENGINE_IDENTITY.json'),*checkpoints],
                            destination,destination,'02_engine_identity',180,deadline))
        output=destination/'generated'; output.mkdir()
        mapping={'{python}':str(python),'{root}':str(root),'{extension}':str(extension),'{out}':str(output)}
        for i, test in enumerate(plan['commands']):
            argv=[]
            for argument in test['argv']:
                for key,value in mapping.items(): argument=argument.replace(key,value)
                argv.append(argument)
            commands.append(run(argv,destination,destination,f'{i+3:02d}_{test["id"]}',
                                test.get('timeout_seconds',300),deadline))
        for name in plan['required_outputs']:
            path=(output/name).resolve(); assert path.is_relative_to(output) and path.is_file() and path.stat().st_size
        for assertion in plan['asserted_json_outputs']:
            path=(output/assertion['path']).resolve(); assert path.is_relative_to(output)
            data=json.loads(path.read_text(encoding='utf-8'))
            comparisons={key:data.get(key)==value for key,value in assertion['field_equals'].items()}
            assert comparisons and all(comparisons.values()),(assertion,comparisons)
            explicit.append({'path':assertion['path'],'sha256':sha(path),'assertions':comparisons,'observations':data})
        assert explicit and all(r['exit_code']==0 and r['status']=='COMPLETED' for r in commands)
        status='VERIFIED'
    except BaseException as exc: error=repr(exc)
    result={'schema':'CPC5.extension.clean-reproduction.v1','status':status,
            'candidate_sha256':container['sha256'],'candidate_bytes':container['bytes'],
            'plan_sha256':sha(args.plan),'commands':commands,'explicit_posttrajectory_verification':explicit,
            'engine_identity':json.loads((destination/'ENGINE_IDENTITY.json').read_text(encoding='utf-8'))
                if (destination/'ENGINE_IDENTITY.json').is_file() else None,
            'error':error,'elapsed_seconds':time.monotonic()-started,'directory':str(destination),
            'completed_utc':datetime.now(timezone.utc).isoformat()}
    put(args.report,result); print(json.dumps(result,ensure_ascii=False,indent=2))
    if status!='VERIFIED': raise SystemExit(1)


if __name__=='__main__': main()
