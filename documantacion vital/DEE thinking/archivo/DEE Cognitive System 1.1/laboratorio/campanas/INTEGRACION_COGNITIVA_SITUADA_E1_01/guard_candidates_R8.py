from pathlib import Path
import sys,time,json
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
sys.path[:0]=[str(ROOT/'sistema'),str(LAB)]
from app.lives import Store
from app.native_tools import physical,atomic_json,digest_file
from app.process_control import protect_current
import ic_native as ic
protect_current();s=Store();deadline=json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']
for name,guard in [('GUARDED_R8_27','on'),('GUARD_SHAM_R8_28','sham')]:
    if time.monotonic()>deadline:raise TimeoutError('Deadline')
    out=EV/(name+'.json');life='IC01_'+name
    if out.exists():continue
    s.fork('IC01_CANDIDATE_R2',life,kind='DIAGNOSTIC_COPY',checkpoint='estado/checkpoints/IC01_CANDIDATE_R2.T3312.f57d7d352bce.deetsnap.gz')
    def run(a):
        initial=physical(a.world,occupation=True);rows=ic.situated(a,name=name,availability=(1,1,-1,-1,1,1,-1,-1,1,1),mode='intact',trace=False,compact=True,gap=0,stream=True,guards=guard)
        return{'initial':initial,'native':rows,'final':physical(a.world,occupation=True)}
    result=s.mutate(life,'IC01_GUARD_CANDIDATE',run,{'guards':guard,'code_sha256':digest_file(LAB/'ic_native.py'),'no_independent_replicate_claim':True})
    atomic_json(out,result);print(name+' '+str(result['INSTRUMENTO']['tick']),flush=True)
