"""Final, conditionally-authorized CPC7 delivery coordinator; no participant logic."""
import ctypes
from datetime import datetime,timezone
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
assert ROOT.name=='CPC7'
WORKSPACE=ROOT.parents[4];assert WORKSPACE.name=='tests'
CASES=ROOT.parents[1]
DELIVERY=ROOT/'_delivery'
PYTHON=ROOT/'.venv/Scripts/python.exe'
sys.path.insert(0,str(ROOT/'src/packaging'))
from bundle import NAME,put,sha
from clean import run_command
from supervisor import remaining

commands=[];stage_name='NOT_STARTED'
def clock():
    budget=json.loads((ROOT/'BUDGET.json').read_text(encoding='utf-8'))
    current=ctypes.c_longlong();assert ctypes.windll.kernel32.QueryPerformanceCounter(ctypes.byref(current))
    elapsed=(current.value-budget['start_qpc'])/budget['qpc_frequency']
    return {'start_utc':budget['start_utc'],'deadline_utc':budget['deadline_utc'],
            'budget_seconds':budget['budget_seconds'],'start_qpc':str(budget['start_qpc']),
            'end_qpc':str(current.value),'qpc_frequency':budget['qpc_frequency'],
            'elapsed_seconds':elapsed,'within_original_budget':elapsed<=budget['budget_seconds'],
            'reported_utc':datetime.now(timezone.utc).isoformat()}

def step(label,argv,timeout):
    directory=DELIVERY/('final_'+label);directory.mkdir(exist_ok=False)
    result=run_command(argv,ROOT,directory,label,timeout,time.monotonic()+min(timeout,remaining()))
    commands.append(result);put(directory/'COMMAND.json',result)
    assert result['status']=='COMPLETED' and result['exit_code']==0,(label,result)
    return result

try:
    candidate=DELIVERY/'FINAL01.candidate.zip';container_path=DELIVERY/'FINAL01_CONTAINER.json'
    final_directory=CASES/'CPC7_VERIFICACION'
    verification_path=final_directory/'VERIFICACION_FINAL_EXTERNA.json'
    publication_path=final_directory/'PUBLICACION.json'
    assert not verification_path.exists() and not publication_path.exists()
    stage_name='BUILD'
    step('build',[str(PYTHON),'-I','-B','-X','utf8',str(ROOT/'src/packaging/bundle.py'),
      'build','--stage',str(DELIVERY/'stage_pre01'),'--candidate',str(candidate),'--report',str(container_path)],900)
    container=json.loads(container_path.read_text(encoding='utf-8'))
    assert container['status']=='VERIFIED' and container['encoded_snapshots']==757
    stage_name='EXACT_FINAL_CLEAN'
    step('clean',[str(PYTHON),'-I','-B','-X','utf8',str(ROOT/'src/packaging/clean.py'),
      '--candidate',str(candidate),'--destination',str(WORKSPACE/'c7_verify_final01'),
      '--plan-member','configuraciones/CLEAN_PLAN.json','--report',str(verification_path),
      '--timeout','1800','--respect-budget'],1800)
    proof=json.loads(verification_path.read_text(encoding='utf-8'))
    assert proof['status']=='VERIFIED' and proof['candidate_sha256']==container['sha256']==sha(candidate)
    assert len(proof['commands'])==17 and len(proof['posttrajectory_assertions'])==13
    assert proof['error'] is None and all(row['status']=='COMPLETED' and row['exit_code']==0 for row in proof['commands'])
    assert all(all(row['checks'].values()) for row in proof['posttrajectory_assertions'])
    assert all(row['owned_worker_waited'] and row['owned_job_closed'] for row in proof['commands'])
    verification_sha=sha(verification_path)
    stage_name='AUTHORIZED_CONDITIONAL_PUBLICATION'
    step('publish',[str(PYTHON),'-I','-B','-X','utf8',str(ROOT/'src/packaging/bundle.py'),
      'publish','--candidate',str(candidate),'--destination',str(CASES),
      '--clean-report',str(verification_path),'--report',str(publication_path)],600)
    stage_name='POSTPUBLICATION_INTEGRITY'
    post_path=DELIVERY/'POSTPUBLICACION_CONTAINER.json'
    step('postverify',[str(PYTHON),'-I','-B','-X','utf8',str(ROOT/'src/packaging/bundle.py'),
      'verify','--candidate',str(CASES/NAME),'--report',str(post_path)],600)
    post=json.loads(post_path.read_text(encoding='utf-8'))
    publication=json.loads(publication_path.read_text(encoding='utf-8'))
    assert post['status']=='VERIFIED' and post['sha256']==publication['sha256']==container['sha256']
    assert sha(verification_path)==verification_sha
    publication['external_final_verification']={'path':str(verification_path),'sha256':verification_sha,
      'status':proof['status'],'commands':17,'posttrajectory_assertion_groups':13}
    publication['postpublication_container_verification']=post
    publication['campaign_clock']=clock()
    publication['delivery_pipeline_commands']=commands
    publication['owned_workers_closed']={
      'value':all(row['owned_worker_waited'] and row['owned_job_closed'] for row in commands),
      'basis':'All four supervised pipeline workers waited; every clean worker waited; owned KILL_ON_JOB_CLOSE handles closed. No global process termination.'}
    publication['coordinator']={'path':str(Path(__file__)),'sha256':sha(Path(__file__)),
      'scope':'External engineering coordinator only; does not compute or repair participant responses.'}
    publication['verification_report_immutable_after_clean']=True
    publication['zip_not_modified_after_exact_final_clean']=True
    publication['publication_pipeline_status']='COMPLETE'
    put(publication_path,publication)
    put(DELIVERY/'FINAL_PIPELINE_COMMANDS.json',commands)
    stage_name='COMPLETE'
    print(json.dumps({'status':'COMPLETE','canonical':publication['canonical'],'sha256':publication['sha256'],
      'bytes':publication['bytes'],'expanded_bytes':publication['expanded_bytes'],
      'logical_snapshot_bytes':publication['logical_snapshot_bytes'],'transport':publication['transport'],
      'verification_report':str(verification_path),'verification_report_sha256':verification_sha,
      'publication_report':str(publication_path),'publication_report_sha256':sha(publication_path),
      'clock':publication['campaign_clock'],'owned_workers_closed':publication['owned_workers_closed']['value']},ensure_ascii=False,indent=2))
except BaseException as error:
    put(DELIVERY/'FINAL01_PIPELINE_ERROR.json',{'stage':stage_name,'error':repr(error),
       'commands':commands,'clock':clock(),'coordinator_sha256':sha(Path(__file__)),
       'scope':'Preserve candidate, data and errors. No automatic criterion/physics repair.'})
    raise
