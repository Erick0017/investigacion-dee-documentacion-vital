"""Explicit runtime budget lease, same R09 history31..46 and R12 World guard.

Files/policy pins remain exact; two runtime admission constants change visibly.
No connection or inference on import. Hard18UTC remains unchanged everywhere.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,sys,time
ROOT=Path(__file__).resolve().parents[1]
OLD=1794934800;NEW=1794936600;FINISH_CALLS=1794937500;HARD=1794938400
def load(p,name):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def configure_budget(runner,client):
    before={'loop_admission':runner.CUTOFF,'client_admission':client.STOP_NEW_CALLS,'hard_close':runner.HARD_CLOSE}
    if before!={'loop_admission':OLD,'client_admission':OLD,'hard_close':HARD}:raise ValueError('EXACT_OLD_RUNTIME_BUDGET_REQUIRED')
    runner.CUTOFF=NEW
    client.STOP_NEW_CALLS=FINISH_CALLS
    after={'loop_admission':runner.CUTOFF,'client_admission':client.STOP_NEW_CALLS,'hard_close':runner.HARD_CLOSE}
    if after!={'loop_admission':NEW,'client_admission':FINISH_CALLS,'hard_close':HARD}:raise ValueError('ONLY_TWO_ADMISSION_FIELDS_CHANGED')
    return {'before':before,'after':after,'changed':['loop_admission','client_admission'],'unchanged':['hard_close'],
      'Native_calls':0,'model_calls':0,'policy_or_history_changed':False}
def main():
    original=ROOT/'control/runner_comparador_v3_R10_RAM.py'
    if hashlib.sha256(original.read_bytes()).hexdigest()!='676ba83bcf05635adf5e2c865395435b0b6fb6f1abf851784acda8336409636d':raise ValueError('UNCHANGED_R10_LOOP_REQUIRED')
    runner=load(original,'_R15_same_R10_execution_loop')
    fixed=load(ROOT/'control/world_reabrir_llama30_R12.py','_R15_unchanged_R12_same_pair_world')
    if (runner.CUTOFF,runner.HARD_CLOSE,fixed.BASE.BASE.FINISH)!=(OLD,HARD,HARD):raise ValueError('UNCHANGED_OLD_AND_HARD_WINDOWS_REQUIRED')
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--execute-root-only',action='store_true');p.add_argument('--participant',required=True,choices=('CONVENTIONAL_AI',))
    p.add_argument('--destination',type=Path,required=True);p.add_argument('--world',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--studio-id',required=True)
    p.add_argument('--expected-place',default='VISUAL_R10.rbxlx');p.add_argument('--stop-cycle',type=int,required=True)
    p.add_argument('--session',required=True);p.add_argument('--resume',action='store_true');p.add_argument('--min-start-free-bytes',type=int,required=True)
    a=p.parse_args()
    if not a.resume or a.session!=fixed.SID:raise ValueError('ONLY_EXPLICIT_SAME_SID_RESUME')
    if a.destination.resolve()!=ROOT/'comparadores/CONVENTIONAL_AI_R09_HISTORIA_01':raise ValueError('EXACT_EXISTING_R09_HISTORY_ONLY')
    if hashlib.sha256(a.world.read_bytes()).hexdigest()!=fixed.SOURCE_SHA:raise ValueError('EXACT_CLOSED_EPISODE30_WORLD_ONLY')
    if time.time()>=HARD:raise ValueError('HARD18UTC_REACHED')
    lease_path=ROOT/'control/LEASE_LLM_ADMISSION_R15.json';lease=json.loads(lease_path.read_text('utf8'))
    if (lease['previous_last_new_epoch'],lease['effective_last_new_epoch'],lease['hard_close_epoch'])!=(OLD,NEW,HARD)or lease['session']!=a.session:raise ValueError('EXACT_PROSPECTIVE_LEASE_ONLY')
    # This is the real imported client used by the existing R09 backend, not
    # a fresh unused module loaded under another name.
    client=sys.modules[runner.create_backend.__globals__['LocalPolicy'].__module__]
    if Path(client.__file__).resolve()!=ROOT/'comparadores/cliente_modelo_v3_R09.py':raise ValueError('ACTUAL_R09_CLIENT_REQUIRED')
    proof=configure_budget(runner,client)
    proof.update(schema='DEE.R07.actual_runtime_admission_override.R15',lease_sha256=hashlib.sha256(lease_path.read_bytes()).hexdigest(),
      client_file=str(client.__file__),client_file_sha256=hashlib.sha256(Path(client.__file__).read_bytes()).hexdigest(),
      wrapper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),history=str(a.destination),session=a.session,
      effective_before_any_World_or_backend_open=True,server_START_metadata_is_not_rewritten=True)
    proof_path=ROOT/'control'/('RUNTIME_ADMISSION_R15_'+a.output.name+'.json')
    with proof_path.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
    runner.CompressedWorld=fixed.ReopenedReferenceWorld
    return runner.execute(a)
if __name__=='__main__':main()
