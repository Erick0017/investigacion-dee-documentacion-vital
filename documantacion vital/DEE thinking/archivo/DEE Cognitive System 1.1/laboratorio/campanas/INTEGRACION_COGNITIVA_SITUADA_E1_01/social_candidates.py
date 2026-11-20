from pathlib import Path
import sys,json,time
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
sys.path[:0]=[str(ROOT/'sistema'),str(LAB)]
from app.lives import Store
from app.native_tools import physical,atomic_json,digest_file
from app.process_control import protect_current
import ic_body as body,ic_social as social
protect_current();s=Store();deadline=json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']
for name,value,mode in [('SOCIAL_ALIGNED_V2_32',45,'full'),('SOCIAL_OPPOSED_33',18,'full'),('SOCIAL_NO_PARTNER_34',45,'no_partner'),('SOCIAL_CUT_35',45,'cut'),('SOCIAL_SHAM_36',45,'sham')]:
    if time.monotonic()>deadline:raise TimeoutError('Deadline')
    out=EV/(name+'.json');life='IC01_'+name
    if out.exists():continue
    s.fork('IC01_CANDIDATE_R2',life,kind='DIAGNOSTIC_COPY',checkpoint='estado/checkpoints/IC01_CANDIDATE_R2.T3312.f57d7d352bce.deetsnap.gz')
    def run(a):
        before=physical(a.world,occupation=True);armed=body.arm(a,name=name,contexts=(1,1),guards='none');p=social.plan(a,name=name,value=value,mode=mode);h=body.attach(a)
        try:
            result=social.execute(a,p);a.run_until(h['state']['end_tick'])
        finally:h['detach']()
        return{'initial':before,'body_preparation':armed,'social':result,'native_frames':h['frames'],'body_requests':[body.ic.receipts(a,rr)for rr in h['state']['requests']],'final':physical(a.world,occupation=True)}
    result=s.mutate(life,'IC01_SOCIAL_COUPLED',run,{'private_value':value,'mode':mode,'sources':{p.name:digest_file(p)for p in[LAB/'ic_body.py',LAB/'ic_native_core.py',LAB/'ic_social.py']}})
    atomic_json(out,result);print(name+' '+str(result['INSTRUMENTO']['tick']),flush=True)
