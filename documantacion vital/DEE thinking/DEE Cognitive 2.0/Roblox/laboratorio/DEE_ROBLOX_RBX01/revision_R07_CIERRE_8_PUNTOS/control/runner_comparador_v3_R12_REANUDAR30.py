"""Prepared SAME R09 Llama continuation31..46; Root executes, no import effects.

Delegates the byte-pinned R10 execution loop and unchanged R09 backend/policy.
Only World restoration is replaced. Never starts another trial or replays29/30.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,sys,time
ROOT=Path(__file__).resolve().parents[1]
def load(p,name):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def main():
    original=ROOT/'control/runner_comparador_v3_R10_RAM.py'
    if hashlib.sha256(original.read_bytes()).hexdigest()!='676ba83bcf05635adf5e2c865395435b0b6fb6f1abf851784acda8336409636d':raise ValueError('UNCHANGED_R10_LOOP_REQUIRED')
    runner=load(original,'_R12_same_R10_execution_loop')
    fixed=load(ROOT/'control/world_reabrir_llama30_R12.py','_R12_same_pair_world')
    if (runner.CUTOFF,runner.HARD_CLOSE,fixed.BASE.BASE.FINISH)!=(1794934800,1794938400,1794938400):raise ValueError('UNCHANGED17_18UTC_FINITE_WINDOWS')
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
    if time.time()>=runner.HARD_CLOSE:raise ValueError('HARD18UTC_REACHED')
    runner.CompressedWorld=fixed.ReopenedReferenceWorld
    return runner.execute(a)
if __name__=='__main__':main()
