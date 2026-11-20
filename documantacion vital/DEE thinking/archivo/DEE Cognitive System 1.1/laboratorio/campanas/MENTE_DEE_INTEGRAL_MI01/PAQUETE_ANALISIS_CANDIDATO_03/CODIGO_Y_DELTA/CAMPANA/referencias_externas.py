"""External controls only. No DEE Runtime, no policy acts for evaluated E1."""
import sys,random,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades.habitat_externo_01 import _Worker
initial=json.loads((E/'MI01_411_MAIN_RESERVA_1.json').read_bytes())['result']['result']['initial_environment'];rows=[]
cases=[('neutral',None),('constant_plus2',None),('random',246001),('random',246002),('random',246003)]
atomic_json(E/'REFERENCIAS_EXTERNAS_PROTOCOLO_480.json',{'cases':cases,'steps':47,'same_environment_initial':initial,'scope':'Reference policies never control E1; published Pendulum is restored, not a random data generator. Different actions imply legitimately different environmental futures. No native learning is attributed to these references.'})
for kind,seed in cases:
    w=_Worker();trajectory=[];rng=random.Random(seed)
    try:
        obs=w.call('restore',snapshot=initial)['observation']
        for i in range(47):
            torque=0 if kind=='neutral'else 2 if kind=='constant_plus2'else rng.choice([-2,0,2]);v=w.call('step',torque=torque);trajectory.append({'index':i,'observation_before':obs,'executed_torque':torque,'response':v});obs=v['observation']
        rows.append({'kind':kind,'seed':seed,'trajectory':trajectory,'reward_sum':math.fsum(v['response']['reward']for v in trajectory),'final_environment':w.call('snapshot')['snapshot']})
    finally:w.close()
atomic_json(E/'COMPARACION_EXTERNA_REFERENCIAS_480.json',{'native_ticks':0,'initial_environment':initial,'references':rows,'not_claimed':'No inference of broad competence from five trajectories sharing one environment prefix. These are reference controllers external to, and never substituted for, E1.'});print([(r['kind'],r['seed'],r['reward_sum'])for r in rows])
