"""External-only actuator references. Never controls or teaches a DEE life."""
from pathlib import Path
import sys,json,random,time
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
sys.path[:0]=[str(ROOT/'sistema')]
from capacidades.habitat_externo_01 import _Worker
from app.native_tools import atomic_json,digest_file
out=EV/'EXTERNAL_REFERENCES_93.json'
if out.exists():raise FileExistsError('No overwrite')
if time.monotonic()>json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']:raise TimeoutError('Deadline')
trials=[];w=_Worker()
try:
    for seed in(81017,81031):
        for mode in('neutral','constant_positive','auditor_random'):
            reset=w.call('reset',seed=seed,g=10.0);initial=w.call('snapshot')['snapshot'];rng=random.Random(90111);rows=[]
            for i in range(64):
                torque=0 if mode=='neutral'else 2 if mode=='constant_positive'else rng.uniform(-2,2);response=w.call('step',torque=torque);rows.append({'index':i,'torque':torque,'response':response})
            trials.append({'seed':seed,'mode':mode,'reset':reset,'initial_environment':initial,'rows':rows,'final_environment':w.call('snapshot')['snapshot']})
finally:w.close()
atomic_json(out,{'source_sha256':digest_file(__file__),'trials':trials,'native_ticks':0,'DEE_life':None,'scope':'Separate environment references, no native participant, no cross-run outputs fed to E1 and no competence claim from aggregate reward alone.'});print('EXTERNAL_REFERENCES_93 '+str(len(trials)),flush=True)
