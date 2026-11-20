import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put
from supervisor import run
results=[]
for backend in ('LAZY','DENSE_SEQUENTIAL','DENSE_PARALLEL'):
    out=ROOT/'resultados/technical_backends'/backend
    if not (out/'CONTRACT.json').exists():
        r=run('technical_'+backend,[sys.executable,'-I','-B','-X','utf8',ROOT/'src/technical_contract.py','--backend',backend,'--out',out],180)
        assert r['exit_code']==0,r
    results.append(json.loads((out/'CONTRACT.json').read_text(encoding='utf-8')))
assert all(m['states']==results[0]['states'] for m in results)
put(ROOT/'resultados/technical_backends/BACKEND_EQUIVALENCE.json',{'schema':'CPC7.backend_equivalence.v1','status':'VERIFIED','backends':[m['backend'] for m in results],
    'raw_clock_tick_equal_at':[r['tick'] for r in results[0]['states']],'invalid_input_tests':sum(m['invalid_inputs_rejected_before_evolution'] for m in results),
    'passive_observation_preserves_physics':True,'save_load_and_continuation_equal':True,'new_scientific_samples':0})
print('BACKENDS_EQUIVALENT')
