"""Continue archived64-step environmental references; no DEE participant."""
from pathlib import Path
import sys,json,random,time
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01';sys.path.insert(0,str(ROOT/'sistema'))
from capacidades.habitat_externo_01 import _Worker
from app.native_tools import atomic_json,digest_file
from app.process_control import protect_current
protect_current();source=EV/'EXTERNAL_REFERENCES_93.json';out=EV/'EXTERNAL_REFERENCES_EXTEND193_168.json'
if out.exists():raise FileExistsError('No overwrite')
if time.monotonic()>json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']-2400:raise TimeoutError('Close reserve')
trials=[];w=_Worker()
try:
    for old in json.loads(source.read_text())['trials']:
        w.call('restore',snapshot=old['final_environment']);rng=random.Random(90111)
        if old['mode']=='auditor_random':
            for _ in range(64):rng.uniform(-2,2)
        rows=[]
        for i in range(64,193):
            torque=0 if old['mode']=='neutral'else 2 if old['mode']=='constant_positive'else rng.uniform(-2,2);response=w.call('step',torque=torque);rows.append({'index':i,'torque':torque,'response':response})
        trials.append({'seed':old['seed'],'mode':old['mode'],'initial_restored_environment':old['final_environment'],'rows':rows,'final_environment':w.call('snapshot')['snapshot']})
finally:w.close()
atomic_json(out,{'source_sha256':digest_file(__file__),'previous_primary':source.name,'previous_sha256':digest_file(source),'trials':trials,'native_ticks':0,'DEE_life':None,'scope':'129 genuinely new environment steps per reference from its archived64-step endpoint, no repeated native trajectory, no reference output ever supplied to E1. Performance references, not hidden controllers.'});print('EXTERNAL_REFERENCES193 '+str(len(trials)),flush=True)
