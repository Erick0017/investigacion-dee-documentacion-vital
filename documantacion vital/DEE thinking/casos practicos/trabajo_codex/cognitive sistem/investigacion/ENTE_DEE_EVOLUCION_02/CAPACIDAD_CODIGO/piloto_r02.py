"""Same physical fan-in R01, deeper passive sensory witness.
No change to the instrument/actuator reader, sources, geometry or native law.
"""
from pathlib import Path
import argparse,gzip,json,os,sys,time
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'sistema'));sys.path.insert(0,str(HERE))
from app.lives import Store
from capacidades import arquitectura_distribuida_mi02_r8 as body
from capacidades import ente_operativo_01_core as core
from app.native_tools import digest_file,atomic_json,physical
import fanin_r01 as fanin
CASES={'M0':[3,18,0,0],'M_LBASE':[9,18,0,0],'M_RBASE':[3,12,0,0],
       'M_LEXTRA':[3,18,6,0],'P0':[6,15,0,0],'P_REXTRA':[6,15,0,6]}
SITES={'targets':[(5,13,15),(7,13,15)],'bases':[(5,13,16),(7,13,16)],
       'extra':[(4,13,16),(8,13,16)],'generic':[(6,13,15),(6,13,16)]}

def experiment(a,values):
    before=physical(a.world);extra=fanin.submit_extra(a,values)
    original=core._sample
    def passive(a,plan,detailed):
        row=original(a,plan,detailed)
        row['fanin']={name:[body.obs(a,p)for p in sites]for name,sites in SITES.items()}
        return row
    core._sample=passive
    try:result=core.external_episode(a,public=values[:2],reference=12,actuator='nulled',feedback='omit',trace=True)
    finally:core._sample=original
    L=values[0]+values[2];R=values[1]+values[3];target=1 if L+12>=R else-1
    f=next(f for f in result['frames']if f['tick']==extra['expected_arrival'])
    return{'revision':'EO02.fanin4.passive_witness.r02','values':values,'physical_before':before,'extra':extra,
      'extra_receipts':body.receipts(a,extra['requests']),'native':result,
      'auditor_only':{'left_total':L,'right_total':R,'calibration':12,'target':target,
        'command':result['formed_native_command'],'matches':result['formed_native_command']==target,
        'targets_at_arrival':f['fanin']['targets'],'sum_loads_materially_observed':[q['s_reg']for q in f['fanin']['targets']]==[L,R]},
      'scope':'No feedback, no learning claim. Target computation is auditor-only after the material action.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--case',choices=CASES,required=True);a=p.parse_args()
    path=ROOT/'evidencia/campanas/ENTE_DEE_EVOLUCION_02/capacidad'/('PILOTO_R02_'+a.case+'.json.gz')
    if path.exists():raise FileExistsError(path)
    store=Store();life='AUX_EO02_CAP_R02_'+a.case;fork=store.fork('EO01_MAIN',life,kind='EO02_CAPACITY_DIAGNOSTIC_EXACT_FORK')
    sources={str(f):digest_file(f)for f in(HERE/'fanin_r01.py',Path(__file__))}
    archive=HERE/'revisiones'/'R02';archive.mkdir(parents=True,exist_ok=True)
    for f in(HERE/'fanin_r01.py',Path(__file__)):
        dest=archive/f.name
        if dest.exists()and digest_file(dest)!=digest_file(f):raise ValueError('Executed source archive conflicts')
        if not dest.exists():dest.write_bytes(f.read_bytes())
    start=time.monotonic();r=store.mutate(life,'EO02_FANIN4_R02',lambda x:experiment(x,CASES[a.case]),details={'values':CASES[a.case],'observation_only_revision':True})
    output={'case':a.case,'life_id':life,'parent':fork['parent'],'sources':sources,'elapsed_seconds':time.monotonic()-start,'result':r}
    path.parent.mkdir(parents=True,exist_ok=True)
    with gzip.open(path,'wt',encoding='utf8',compresslevel=6)as f:json.dump(output,f,ensure_ascii=False,allow_nan=False)
    print(json.dumps({'case':a.case,'primary':str(path),'elapsed_seconds':output['elapsed_seconds'],'tick':r['INSTRUMENTO']['tick'],'audit':r['result']['auditor_only']},ensure_ascii=False))
if __name__=='__main__':main()
