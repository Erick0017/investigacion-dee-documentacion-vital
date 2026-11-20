"""R10 finite prospective continuation, all phases share the same lived world."""
from pathlib import Path
import argparse,gzip,json,os,sys,time
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'sistema'));sys.path.insert(0,str(HERE))
from app.lives import Store
from app.native_tools import digest_file,physical
from capacidades import arquitectura_distribuida_mi02_r8 as body
from capacidades import cierre_funcional_cf01 as cf
from capacidades import ente_evolucion_02_core as core
from piloto_sensorial_r10 import Gate,LIFE
from serie_cuatro_r05 import ram
import sensorial_r10 as sensor
PLAN={
 'TRAIN_REST':[[1,2,1,2,0,1,1,2],[2,3,1,1,0,1,0,0]],
 'RESERVA1':[[1,2,1,2,1,2,1,2],[1,3,1,3,1,2,1,2],[2,3,2,3,1,1,1,2],[2,3,1,4,2,3,1,2],[3,1,2,3,1,4,2,3],[1,4,3,5,2,2,2,2]],
 'RESERVA2':[[4,3,1,2,2,4,1,2],[3,5,2,4,2,3,1,2],[5,6,1,2,1,2,2,2],[1,4,2,3,3,5,2,2],[2,3,4,2,1,3,3,5],[5,6,1,4,1,3,2,2]],
 'RESERVA3':[[6,7,1,2,2,2,1,2],[2,6,3,5,1,2,3,2],[4,5,3,2,2,4,2,3],[5,8,2,3,1,3,2,2],[3,6,4,2,1,3,4,4],[6,8,1,3,2,3,1,2]],
 'REUSO2':[[11,15],[5,10]]}
def run(a,phase):
    old=core._sample;rows=[];before=physical(a.world)
    def passive(a,p,detail):
        q=old(a,p,detail);q['r10']={'targets':[body.obs(a,p)for p in[(5,13,15),(7,13,15)]],
          'heads':[body.obs(a,p)for p in[(5,10,23),(7,16,23)]],
          'turns':[body.obs(a,p)for p in[(5,10,21),(7,16,21),(5,13,18),(7,13,18)]]};return q
    core._sample=passive
    try:
        for values in PLAN[phase]:
            inputs=None if phase=='REUSO2'else sensor.submit(a,values)
            r=core.external_episode(a,public=values if phase=='REUSO2'else[0,0],reference=4,actuator='closed',feedback='real',trace=True,environment=None if phase=='REUSO2'else Gate(values))
            rows.append({'values':values,'inputs':inputs,'input_receipts':[]if inputs is None else body.receipts(a,inputs['requests']),'native':r})
    finally:core._sample=old
    return{'phase':phase,'architecture':sensor.REVISION,'rows':rows,'physical_before':before,'physical_after':physical(a.world,occupation=True),'memory_after':cf.witness(a),'same_life_no_native_reset':True}
def main():
    p=argparse.ArgumentParser();p.add_argument('--phase',choices=PLAN,required=True);args=p.parse_args()
    dest=ROOT/'evidencia/campanas/ENTE_DEE_EVOLUCION_02/capacidad'/('R10_CONT_'+args.phase+'.json.gz')
    if dest.exists():raise FileExistsError(dest)
    files=[Path(__file__),HERE/'sensorial_r10.py',HERE/'piloto_sensorial_r10.py',ROOT/'sistema/capacidades/ente_evolucion_02_core.py']
    archive=HERE/'revisiones/R10_CONT';archive.mkdir(parents=True,exist_ok=True)
    for f in files:
        t=archive/f.name
        if t.exists()and digest_file(t)!=digest_file(f):raise ValueError('Source conflict')
        if not t.exists():t.write_bytes(f.read_bytes())
    store=Store();beg=time.monotonic();result=store.mutate(LIFE,'R10_'+args.phase,lambda a:run(a,args.phase),details={'frozen_phase':args.phase,'inputs':PLAN[args.phase],'plasticity_stays_active':True})
    rec=store.record(LIFE);out={'life_id':LIFE,'phase':args.phase,'sources':{str(f):digest_file(f)for f in files},'elapsed_seconds':time.monotonic()-beg,'ram':ram(),'snapshot':rec['snapshot'],'snapshot_sha256':rec['snapshot_sha256'],'snapshot_bytes':rec['storage']['encoded_bytes'],'result':result}
    if args.phase=='TRAIN_REST':out['control_base']=store.fork(LIFE,'AUX_EO02_CAP_R10_TRAINED_BASE',kind='EO02_R10_TRAINED_EXACT_FORK')
    with gzip.open(dest,'wt',encoding='utf8',compresslevel=6)as f:json.dump(out,f,ensure_ascii=False,allow_nan=False)
    print(json.dumps({'phase':args.phase,'path':str(dest),'tick':rec['physical']['tick'],'rows':[{'v':q['values'],'cmd':q['native']['formed_native_command'],'ok':q['native']['job_completed'],
      'own_after':[v['s_reg']for v in q['native']['after']['own']],'receipts':[v['receipt']['status']for v in q['input_receipts']]}for q in result['result']['rows']]},ensure_ascii=False))
if __name__=='__main__':main()
