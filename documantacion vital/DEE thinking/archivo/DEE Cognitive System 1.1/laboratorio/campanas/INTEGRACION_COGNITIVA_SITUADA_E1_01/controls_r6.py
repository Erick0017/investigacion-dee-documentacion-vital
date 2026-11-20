from pathlib import Path
import sys,time,json
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
sys.path[:0]=[str(ROOT/'sistema'),str(LAB)]
from app.lives import Store
from app.native_tools import physical,atomic_json,digest_file
from app.process_control import protect_current
import ic_native as ic
protect_current();store=Store();deadline=json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']
prefix='estado/checkpoints/IC01_CANDIDATE_R2.T3312.f57d7d352bce.deetsnap.gz'
cases=[('RETURN_OMITTED_17','omit_return'),('NO_ACTION_18','no_action'),('RETURN_UNPAIRED_19','unpaired'),('RETURN_SHAM_20','sham')]
for name,mode in cases:
    if time.monotonic()>deadline:raise TimeoutError('Original deadline')
    out=EV/(name+'.json');life='IC01_'+name
    if out.exists():print('ALREADY_DONE '+name,flush=True);continue
    store.fork('IC01_CANDIDATE_R2',life,kind='DIAGNOSTIC_COPY',checkpoint=prefix)
    def run(a):
        pre=physical(a.world,occupation=True);rows=ic.situated(a,name=name,availability=(1,1,-1,-1,1,1),mode=mode,trace=False,compact=True,gap=0)
        return{'initial':pre,'native':rows,'final':physical(a.world,occupation=True)}
    result=store.mutate(life,'IC01_CONTROL_R6',run,{'mode':mode,'source_sha256':digest_file(LAB/'ic_native.py'),'shared_prefix_not_independent_replicates':True})
    atomic_json(out,result);print(name+' '+str(result['INSTRUMENTO']['tick']),flush=True)
