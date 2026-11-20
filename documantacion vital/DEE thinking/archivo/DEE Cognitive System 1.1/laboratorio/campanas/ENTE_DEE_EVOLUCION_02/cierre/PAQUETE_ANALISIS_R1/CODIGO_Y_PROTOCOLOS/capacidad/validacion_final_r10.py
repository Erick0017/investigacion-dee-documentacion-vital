"""Second prospective evaluation after naturally acquired boundary alignment.

No16 empty repetitions. The prior planned2-input use produced the missing
boundary experience. Older3/6,6/6,6/6 and1/2 remain unchanged.
"""
from pathlib import Path
import argparse,gzip,json,os,sys,time
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'sistema'));sys.path.insert(0,str(HERE))
from app.lives import Store
from app.native_tools import digest_file,physical,atomic_json
from capacidades import arquitectura_distribuida_mi02_r8 as body
from capacidades import cierre_funcional_cf01 as cf
from capacidades import ente_evolucion_02_core as core
from piloto_sensorial_r10 import Gate,LIFE
from serie_cuatro_r05 import ram
import sensorial_r10 as sensor
BASE='AUX_EO02_CAP_R10_ALINEADA'
BASIS={'M0':[0,7,0,0,0,0,0,0], 'P0':[5,3,0,0,0,0,0,0]}
for k in range(4):
    a=list(BASIS['M0']);a[2*k]=6;BASIS['ML'+str(k)]=a
    b=list(BASIS['P0']);b[2*k+1]+=8;BASIS['PR'+str(k)]=b
TIGHT={}
for seq in(1,2,3):
    frames=[]
    for j in range(6):
        L=[(seq*3+j+2*k)%6+1 for k in range(4)]
        R=[L[k]+(2 if j%2 and k==0 else 1)for k in range(4)]
        frames.append([v for pair in zip(L,R)for v in pair])
    TIGHT['FRONTERA'+str(seq)]=frames
PLAN={'revision':'R10.prospective_boundary.v2','aligned_from':'Planned two-input test first failed and learned delta6->7; no retrospectively inserted content',
      'basis':BASIS,'reserves':TIGHT,'world_calibration':4,'decoder':'same2fixednativecontactticks',
      'criterion':'Report each complete6-opportunity reserve; per-component relevance requires one raw component alone to change command.',
      'joint_arity':8,'serial_capacity_windows':{'16':2,'32':4},'windows_are_not_independent_trials':True}
def seal(store):
    seal=HERE/'PROTOCOLO_R10_FRONTERA_V2.json'
    if seal.exists():raise FileExistsError(seal)
    record=store.record(LIFE);atomic_json(seal,{**PLAN,'source_life':LIFE,'source_tick':record['physical']['tick'],'source_snapshot_sha256':record['snapshot_sha256']})
    return store.fork(LIFE,BASE,kind='R10_BOUNDARY_ALIGNED_EXACT_FORK')
def run(a,frames,feedback):
    before=physical(a.world);rows=[];old=core._sample
    def passive(a,p,d):
        q=old(a,p,d);q['r10']={'targets':[body.obs(a,p)for p in[(5,13,15),(7,13,15)]],
          'heads':[body.obs(a,p)for p in[(5,10,23),(7,16,23)]],'turns':[body.obs(a,p)for p in[(5,10,21),(7,16,21),(5,13,18),(7,13,18)]]};return q
    core._sample=passive
    try:
        for values in frames:
            inputs=sensor.submit(a,values)
            r=core.external_episode(a,public=[0,0],reference=4,actuator='closed'if feedback=='real'else'nulled',feedback=feedback,trace=True,environment=Gate(values))
            rows.append({'values':values,'inputs':inputs,'input_receipts':body.receipts(a,inputs['requests']),'native':r})
    finally:core._sample=old
    return{'rows':rows,'physical_before':before,'physical_after':physical(a.world,occupation=True),'memory_after':cf.witness(a),'architecture':sensor.REVISION,'feedback':feedback}
def main():
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=['seal','basis','reserve'],required=True);p.add_argument('--case');args=p.parse_args();store=Store()
    if args.mode=='seal':print(json.dumps({'base':seal(store)['life_id'],'plan':PLAN},ensure_ascii=False));return
    if not(HERE/'PROTOCOLO_R10_FRONTERA_V2.json').exists():raise RuntimeError('Prospective protocol not frozen')
    if args.mode=='basis':
        if args.case not in BASIS:raise ValueError('Unfrozen case')
        life='AUX_EO02_CAP_R10_V2_'+args.case;fork=store.fork(BASE,life,kind='R10_COMPONENT_CAUSAL_CONTRAST');frames=[BASIS[args.case]];feedback='omit'
    else:
        if args.case not in TIGHT:raise ValueError('Unfrozen reserve')
        life=LIFE;fork=None;frames=TIGHT[args.case];feedback='real'
    name='R10_V2_'+args.mode+'_'+args.case;dest=ROOT/'evidencia/campanas/ENTE_DEE_EVOLUCION_02/capacidad'/(name+'.json.gz')
    if dest.exists():raise FileExistsError(dest)
    files=[Path(__file__),HERE/'sensorial_r10.py',HERE/'piloto_sensorial_r10.py',ROOT/'sistema/capacidades/ente_evolucion_02_core.py'];archive=HERE/'revisiones/R10_V2';archive.mkdir(parents=True,exist_ok=True)
    for f in files:
        t=archive/f.name
        if t.exists()and digest_file(t)!=digest_file(f):raise ValueError('Frozen source differs')
        if not t.exists():t.write_bytes(f.read_bytes())
    beg=time.monotonic();r=store.mutate(life,name,lambda a:run(a,frames,feedback),details={'frozen_inputs':frames,'feedback':feedback,'case':args.case})
    rec=store.record(life);out={'case':args.case,'mode':args.mode,'life_id':life,'parent':None if fork is None else fork['parent'],'sources':{str(f):digest_file(f)for f in files},
       'protocol_sha256':digest_file(HERE/'PROTOCOLO_R10_FRONTERA_V2.json'),'elapsed_seconds':time.monotonic()-beg,'ram':ram(),'snapshot':rec['snapshot'],'snapshot_sha256':rec['snapshot_sha256'],'snapshot_bytes':rec['storage']['encoded_bytes'],'result':r}
    with gzip.open(dest,'wt',encoding='utf8',compresslevel=6)as f:json.dump(out,f,ensure_ascii=False,allow_nan=False)
    print(json.dumps({'case':args.case,'mode':args.mode,'tick':rec['physical']['tick'],'rows':[{'values':q['values'],'cmd':q['native']['formed_native_command'],'ok':q['native']['job_completed'],
       'sum_actual':[v['s_reg']for v in next(f['r10']['targets']for f in q['native']['frames']if f['tick']==q['inputs']['target_tick'])],
       'own':[v['s_reg']for v in q['native']['after']['own']],'statuses':[v['receipt']['status']for v in q['input_receipts']]}for q in r['result']['rows']]},ensure_ascii=False))
if __name__=='__main__':main()
