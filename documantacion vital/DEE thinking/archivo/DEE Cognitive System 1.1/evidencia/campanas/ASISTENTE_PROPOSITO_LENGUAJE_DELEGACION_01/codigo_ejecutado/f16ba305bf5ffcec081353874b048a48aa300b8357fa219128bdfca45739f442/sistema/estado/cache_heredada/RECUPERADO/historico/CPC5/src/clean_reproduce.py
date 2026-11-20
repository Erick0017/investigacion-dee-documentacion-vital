"""Independent extraction, offline wheel installation and bounded replay.

The report is external to the candidate ZIP whose exact identity it proves.
The plan is a frozen JSON list of commands; no scientific answer is supplied
to participants. Each command must produce its own observations from v27.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from package_delivery import verify, put, sha, WHL, WHL_SHA, PYD_SHA

ENGINE_CHECK = r'''
import hashlib, json, pathlib, sys
import dee_thinking as d
assert sys.version_info[:2] == (3,13) and sys.maxsize > 2**32
assert d.__version__ == '4.0.0'
assert d.kernel_identity()['kernel_version'] == 27
p=pathlib.Path(d.__file__).resolve()
assert p.is_relative_to(pathlib.Path(sys.prefix).resolve())
assert hashlib.sha256(pathlib.Path(d._native.__file__).read_bytes()).hexdigest() == sys.argv[1]
rows=[]
for checkpoint in sys.argv[3:]:
    w=d.OrganizationalWorld.load_snapshot(checkpoint)
    assert w.runtime.dimension > 0 and w.runtime.current_tick >= 0
    assert len(w.runtime.raw_copy()) == w.runtime.dimension**3
    assert len(w.runtime.clock_copy()) == w.runtime.dimension**3
    rows.append({'path':checkpoint,'tick':w.runtime.current_tick,'N':w.runtime.dimension,
                 'channels':list(w.runtime.channel_names),'receipts':len(w.runtime.receipts),
                 'protocols':len(w.protocols)})
assert not any(x.startswith(('CPC3','SEM01','dee_universe')) for x in sys.modules)
pathlib.Path(sys.argv[2]).write_text(json.dumps({'version':d.__version__,'kernel':d.kernel_identity(),
    'module':str(p),'python':sys.executable,'checkpoints_loaded':rows},ensure_ascii=False,indent=2),encoding='utf-8')
'''


def run(command, cwd, destination, label, timeout, deadline):
    allowed = min(float(timeout), max(0, deadline - time.monotonic()))
    if allowed <= 0: raise TimeoutError('Clean reproduction deadline')
    env = dict(os.environ, PYTHONNOUSERSITE='1', PYTHONDONTWRITEBYTECODE='1',
               PYTHONUTF8='1', OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1')
    env.pop('PYTHONPATH', None)
    env.pop('PYTHONHOME', None)
    started = time.monotonic()
    with (destination/(label+'.stdout.log')).open('w',encoding='utf-8') as stdout, \
         (destination/(label+'.stderr.log')).open('w',encoding='utf-8') as stderr:
        process = subprocess.Popen(command,cwd=cwd,env=env,stdout=stdout,stderr=stderr,
                                   creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        # Same campaign-owned job mechanism as scientific tasks; no global kill.
        job = None
        if os.name == 'nt':
            from supervisor import OwnedJob
            try: job=OwnedJob(process)
            except BaseException:
                process.kill();process.wait(timeout=15);raise
        status='COMPLETED'
        try: process.wait(timeout=allowed)
        except subprocess.TimeoutExpired:
            status='TIMEOUT'
            if job:job.terminate()
            else:process.kill()
            process.wait(timeout=30)
        finally:
            if job:job.close()
    row={'label':label,'argv':command,'elapsed_seconds':time.monotonic()-started,
         'exit_code':process.returncode,'status':status,'timeout_seconds':allowed}
    put(destination/(label+'.COMMAND.json'),row)
    if process.returncode:raise RuntimeError('Clean command failed: '+label)
    return row


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--destination',type=Path,required=True)
    p.add_argument('--plan',type=Path,required=True)
    p.add_argument('--timeout',type=int,default=900)
    p.add_argument('--respect-campaign-deadline',action='store_true',
                   help='For this authorized campaign only; future explicitly requested reproductions use their own bounded timeout')
    p.add_argument('--report',type=Path,required=True)
    args=p.parse_args()
    started=time.monotonic();deadline=started+args.timeout
    # BUDGET remains immutable. Current campaign opts into its original limit;
    # a later user-authorized reproduction is a new bounded operation, not a
    # silently resumed scientific campaign and not a reset of this budget.
    if args.respect_campaign_deadline:
        budget=json.loads((Path(__file__).resolve().parents[1]/'BUDGET.json').read_text(encoding='utf-8'))
        wall_remaining=(datetime.fromisoformat(budget['deadline_utc'])-datetime.now(timezone.utc)).total_seconds()
        deadline=min(deadline,started+max(0,wall_remaining))
        if deadline<=started:raise TimeoutError('Original campaign deadline exhausted')
    container=verify(args.candidate)
    plan=json.loads(args.plan.read_text(encoding='utf-8'))
    assert plan.get('schema')=='CPC5.clean-reproduction-plan.v1'
    destination=args.destination.resolve()
    destination.mkdir(parents=True,exist_ok=False)
    extraction=destination/'extracted'
    extraction.mkdir()
    with zipfile.ZipFile(args.candidate) as z:z.extractall(extraction)
    root=extraction/'CPC5'
    assert sha(root/'runtime'/WHL)==WHL_SHA
    envdir=destination/'isolated_env'
    commands=[]
    try:
        commands.append(run([sys.executable,'-I','-m','venv',str(envdir)],destination,destination,'00_venv',90,deadline))
        python=envdir/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
        commands.append(run([str(python),'-I','-m','pip','install','--no-index','--no-deps',str(root/'runtime'/WHL)],
                            destination,destination,'01_offline_install',90,deadline))
        checkpoints=[]
        for name in plan.get('checkpoints',[]):
            path=(root/name).resolve()
            assert path.is_relative_to(root) and path.is_file()
            checkpoints.append(str(path))
        commands.append(run([str(python),'-I','-c',ENGINE_CHECK,PYD_SHA,str(destination/'ENGINE_IDENTITY.json'),*checkpoints],
                            destination,destination,'02_engine_and_snapshots',180,deadline))
        output=destination/'generated'
        output.mkdir()
        mapping={'{python}':str(python),'{root}':str(root),'{out}':str(output)}
        for index,test in enumerate(plan['commands']):
            argv=[]
            for arg in test['argv']:
                for key,value in mapping.items():arg=arg.replace(key,value)
                argv.append(arg)
            commands.append(run(argv,destination,destination,f'{index+3:02d}_{test["id"]}',
                                test.get('timeout_seconds',300),deadline))
        required=plan.get('required_outputs',[])
        assert required, 'Frozen plan must identify actual replay outputs'
        for name in required:
            path=(output/name).resolve()
            assert path.is_relative_to(output) and path.is_file() and path.stat().st_size>0
        explicit_checks=[]
        for item in plan.get('asserted_json_outputs',[]):
            path=(output/item['path']).resolve()
            assert path.is_relative_to(output)
            observed=json.loads(path.read_text(encoding='utf-8'))
            comparisons={key:observed.get(key)==expected for key,expected in item['field_equals'].items()}
            assert comparisons and all(comparisons.values()),(item,comparisons)
            explicit_checks.append({'path':item['path'],'sha256':sha(path),'assertions':comparisons,'observations':observed})
        assert explicit_checks, 'Frozen plan must require explicit post-trajectory verification, not only return codes'
        assert all(x['exit_code']==0 and x['status']=='COMPLETED' for x in commands)
        status='VERIFIED'
        error=None
    except BaseException as exc:
        status='ERROR';error=repr(exc)
    result={'schema':'CPC5.clean-reproduction.v1','status':status,'candidate_sha256':container['sha256'],
            'candidate_bytes':container['bytes'],'plan_sha256':sha(args.plan),'commands':commands,
            'error':error,'elapsed_seconds':time.monotonic()-started,'directory':str(destination),
            'explicit_posttrajectory_verification':explicit_checks if status=='VERIFIED' else [],
            'engine_identity':json.loads((destination/'ENGINE_IDENTITY.json').read_text(encoding='utf-8'))
                if (destination/'ENGINE_IDENTITY.json').is_file() else None,
            'completed_utc':datetime.now(timezone.utc).isoformat()}
    put(args.report,result)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if status!='VERIFIED':raise SystemExit(1)


if __name__=='__main__':main()
