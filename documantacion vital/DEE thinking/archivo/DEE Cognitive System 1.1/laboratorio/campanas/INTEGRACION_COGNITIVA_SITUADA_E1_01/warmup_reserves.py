from pathlib import Path
import sys,time,json
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
sys.path[:0]=[str(ROOT/'sistema'),str(LAB)]
from app.lives import Store
from app.native_tools import physical,atomic_json,digest_file
from app.process_control import protect_current
import ic_native_core as ic
protect_current();s=Store();deadline=json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']
name='WARMUP_FIXED_56';life='IC01_'+name
if not(EV/(name+'.json')).exists():
    s.fork('IC01_CANDIDATE_R2',life,kind='DIAGNOSTIC_COPY',checkpoint='estado/checkpoints/IC01_CANDIDATE_R2.T3312.f57d7d352bce.deetsnap.gz')
    r=s.mutate(life,'IC01_EXPLICIT_TWO_OPPORTUNITY_WARMUP',lambda a:ic.situated(a,name=name,availability=(1,1),mode='intact',trace=False,compact=True,gap=0,stream=True,shunt='a_only'),{'code':digest_file(LAB/'ic_native_core.py'),'reason_before':'Initial opposite reserve failed. Test a new declared curriculum with two prior successful opportunities; this does not retroactively turn the failed reserve positive.'});atomic_json(EV/(name+'.json'),r)
contexts=(-1,-1,-1,1,1,-1,1,1,1,-1,-1,1,-1,-1,-1,1,1,1,1,-1,-1,1,1,-1,-1,-1,1,-1,1,1,-1,-1)
for name,shunt,mode in [('WARM_RESERVE_57','a_only','intact'),('WARM_SHAM_58','sham','intact'),('WARM_RETURN_OMIT_59','a_only','omit_return')]:
    if time.monotonic()>deadline:raise TimeoutError('Deadline')
    out=EV/(name+'.json');target='IC01_'+name
    if out.exists():continue
    s.fork(life,target,kind='DIAGNOSTIC_COPY')
    def run(a):
        pre=physical(a.world,occupation=True);rows=ic.situated(a,name=name,availability=contexts,mode=mode,trace=False,compact=True,gap=0,stream=True,shunt=shunt)
        return{'initial':pre,'contexts_fixed_before':[int(v)for v in contexts],'native':rows,'final':physical(a.world,occupation=True),'scope':'Reserve after a declared two-opportunity curriculum, NOT success of the earlier cold-start reserve'}
    r=s.mutate(target,'IC01_RESERVED_AFTER_FIXED_WARMUP',run,{'shunt':shunt,'mode':mode,'source_sha256':digest_file(LAB/'ic_native_core.py'),'shared_exact_warm_prefix':s.record(life)['snapshot_sha256']});atomic_json(out,r);print(name+' '+str(r['INSTRUMENTO']['tick']),flush=True)
