"""Single alternative architecture, explicitly new T0 life and raw teaching."""
from pathlib import Path
import argparse,gzip,json,os,sys,time
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'sistema'));sys.path.insert(0,str(HERE))
import dee_thinking as d
from app.lives import Store,WorldAdapter,now
from app.native_tools import digest_file,physical,atomic_json
from capacidades import arquitectura_distribuida_mi02_r8 as body
from capacidades import cierre_funcional_cf01 as cf
from capacidades import integracion_distribuida_mi02_r9 as native
from capacidades import ente_evolucion_02_core as core
import sensorial_r10 as sensor
from serie_cuatro_r05 import ram
LIFE='EO02_SENSORIAL_R10_T0'
DATA=[[1,3,1,1,0,1,0,1],[2,3,0,1,0,1,0,0],[1,2,1,2,0,1,1,2],[2,3,1,1,0,1,0,0]]
class Gate:
    def __init__(self,values,reference=4):self.values=values;self.reference=reference
    def act(self,*,formed,executed,posture,public,native_tick):
        L=sum(self.values[::2]);R=sum(self.values[1::2]);gate=1 if L+self.reference>=R else-1;okay=executed is not None and executed==gate
        before={'law':'R10.eight_component_gate.v1','raw_components':self.values,'reference':self.reference,'gate_not_injected':gate,'calculated_after_emission':True}
        observed={'tick':native_tick,'movement':executed is not None,'contact':executed is not None and not okay,'actuator_posture':posture,'job_completed':okay,'effect':'passed'if okay else'contact'if executed is not None else'no_movement'}
        return{'before':before,'after':{**before,'observed':observed},'observed':observed}
def create(store):
    if store.life_dir(LIFE).exists():raise FileExistsError('R10 life already exists; continuation only')
    recipe,g=sensor.design();a=WorldAdapter(d.OrganizationalWorld.create(recipe))
    rec={'schema':'DCS1.1.life.v1','life_id':LIFE,'world_id':LIFE,'profile':'fisica_directa','branch':'NEW_PREPARATION_T0','parent':None,'created_utc':now(),
       'parameters':{'N':26,'architecture':sensor.REVISION},'knowledge':'No trained EO01 state imported. Own11/11 and B61/19 are future declared raw experiences, not prepared answers.',
       'memberships':[{'id':LIFE,'role':'Full R10 shared Runtime with A/B; not duplicate matter per view'}]}
    with store.writer(LIFE):rec=store.commit(rec,a,{'kind':'R10_CREATE_EXTERNAL_ANATOMY_T0','geometry':g,'before_any_raw_experiences':physical(a.world)})
    result=store.mutate(LIFE,'R10_INITIAL_RAW_EXPERIENCES',lambda a:native.acquire(a,geometry=g,own=(11,11),private=(61,19)),details={'raw_scalar_samples':{'own':[11,11],'private_B':[61,19]},'new_life_not_continuity':True})
    return{'T0':{'physical':rec['physical'],'snapshot':rec['snapshot'],'snapshot_sha256':rec['snapshot_sha256']},'acquisition':result,'geometry':g}
def episodes(a,count):
    rows=[];old=core._sample
    sites={'targets':[(5,13,15),(7,13,15)],'heads':[(5,10,23),(7,16,23)],'turn1':[(5,10,21),(7,16,21)],'turn2':[(5,13,18),(7,13,18)]}
    def passive(a,p,detail):
        q=old(a,p,detail);q['r10']={k:[body.obs(a,s)for s in ss]for k,ss in sites.items()};return q
    core._sample=passive
    try:
        for values in DATA[:count]:
            inputs=sensor.submit(a,values)
            r=core.external_episode(a,public=[0,0],reference=4,actuator='closed',feedback='real',trace=True,environment=Gate(values))
            rows.append({'values':values,'inputs':inputs,'input_receipts':body.receipts(a,inputs['requests']),'native':r})
    finally:core._sample=old
    return{'rows':rows,'memory_after':cf.witness(a),'physical_after':physical(a.world,occupation=True),'no_reset_between_episodes':True}
def main():
    p=argparse.ArgumentParser();p.add_argument('--step',choices=['create','pilot'],required=True);p.add_argument('--count',type=int,default=2);args=p.parse_args()
    dest=ROOT/'evidencia/campanas/ENTE_DEE_EVOLUCION_02/capacidad'/('R10_'+args.step+'.json.gz')
    if dest.exists():raise FileExistsError(dest)
    archive=HERE/'revisiones/R10';archive.mkdir(parents=True,exist_ok=True)
    files=[Path(__file__),HERE/'sensorial_r10.py',ROOT/'sistema/capacidades/ente_evolucion_02_core.py']
    for f in files:
        target=archive/f.name
        if target.exists()and digest_file(target)!=digest_file(f):raise ValueError('Source bytes changed after closure')
        if not target.exists():target.write_bytes(f.read_bytes())
    store=Store();beg=time.monotonic()
    r=create(store)if args.step=='create'else store.mutate(LIFE,'R10_EIGHT_COMPONENT_PILOT',lambda a:episodes(a,args.count),details={'unseen_raw_inputs':DATA[:args.count],'environment_calibration':4})
    out={'step':args.step,'revision':sensor.REVISION,'life_id':LIFE,'sources':{str(f):digest_file(f)for f in files},'elapsed_seconds':time.monotonic()-beg,'ram':ram(),'result':r}
    with gzip.open(dest,'wt',encoding='utf8',compresslevel=6)as f:json.dump(out,f,ensure_ascii=False,allow_nan=False)
    rows=[]if args.step=='create'else[{'values':q['values'],'command':q['native']['formed_native_command'],'completed':q['native']['job_completed'],'inputs':[v['receipt']['status']for v in q['input_receipts']],
       'targets':next(f['r10']['targets']for f in q['native']['frames']if f['tick']==q['inputs']['target_tick']),
       'own_before':[v['s_reg']for v in q['native']['before']['own']],'own_after':[v['s_reg']for v in q['native']['after']['own']]}for q in r['result']['rows']]
    print(json.dumps({'path':str(dest),'step':args.step,'seconds':out['elapsed_seconds'],'ram':out['ram'],'rows':rows},ensure_ascii=False))
if __name__=='__main__':main()
