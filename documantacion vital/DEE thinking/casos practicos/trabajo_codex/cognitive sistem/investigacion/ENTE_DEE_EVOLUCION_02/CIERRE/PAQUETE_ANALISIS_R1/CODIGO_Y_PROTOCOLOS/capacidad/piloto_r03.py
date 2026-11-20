"""Eight-variable material-joint-use finite exploratory pilot, not training."""
from pathlib import Path
import argparse,gzip,json,os,sys,time
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'sistema'));sys.path.insert(0,str(HERE))
from app.lives import Store
from capacidades import arquitectura_distribuida_mi02_r8 as body
from capacidades import ente_operativo_01_core as core
from app.native_tools import digest_file,physical
import fanin_r03 as fanin
CASES={'M0':[3,18,0,0,0,0,0,0],
       'ML0':[9,18,0,0,0,0,0,0], 'MR0':[3,12,0,0,0,0,0,0],
       'ML1':[3,18,6,0,0,0,0,0],'ML2':[3,18,0,0,6,0,0,0],'ML3':[3,18,0,0,0,0,6,0],
       'P0':[6,15,0,0,0,0,0,0],
       'PR1':[6,15,0,6,0,0,0,0],'PR2':[6,15,0,0,0,6,0,0],'PR3':[6,15,0,0,0,0,0,6]}
SITES={'targets':[(5,13,15),(7,13,15)],'bases':[(5,13,16),(7,13,16)],
       'sources':[list(row[1])for row in fanin.SPECS]}
def experiment(a,values):
    before=physical(a.world);extra=fanin.submit_extra(a,values);original=core._sample
    def passive(a,plan,detailed):
        row=original(a,plan,detailed);row['fanin']={name:[body.obs(a,p)for p in sites]for name,sites in SITES.items()};return row
    core._sample=passive
    try:result=core.external_episode(a,public=values[:2],reference=12,actuator='nulled',feedback='omit',trace=True)
    finally:core._sample=original
    L=sum(values[::2]);R=sum(values[1::2]);target=1 if L+12>=R else-1
    f=next(f for f in result['frames']if f['tick']==extra['expected_arrival'])
    return{'revision':fanin.REVISION,'values':values,'physical_before':before,'extra':extra,
      'extra_receipts':body.receipts(a,extra['requests']),'native':result,
      'auditor_only':{'left_total':L,'right_total':R,'calibration':12,'target':target,
        'command':result['formed_native_command'],'matches':result['formed_native_command']==target,
        'targets_at_arrival':f['fanin']['targets'],'sum_loads_materially_observed':[q['s_reg']for q in f['fanin']['targets']]==[L,R]},
      'scope':'Joint-use pilot only. Feedback omitted and external actuator nulled; host sums only after emission for audit.'}
def main():
    p=argparse.ArgumentParser();p.add_argument('--case',choices=CASES,required=True);args=p.parse_args()
    dest=ROOT/'evidencia/campanas/ENTE_DEE_EVOLUCION_02/capacidad'/('PILOTO_R03_'+args.case+'.json.gz')
    if dest.exists():raise FileExistsError(dest)
    sources={str(f):digest_file(f)for f in(HERE/'fanin_r03.py',Path(__file__))};archive=HERE/'revisiones/R03';archive.mkdir(parents=True,exist_ok=True)
    for f in(HERE/'fanin_r03.py',Path(__file__)):
        d=archive/f.name
        if d.exists()and digest_file(d)!=digest_file(f):raise ValueError('Source bytes changed')
        if not d.exists():d.write_bytes(f.read_bytes())
    store=Store();life='AUX_EO02_CAP_R03_'+args.case;fork=store.fork('EO01_MAIN',life,kind='EO02_CAPACITY_DIAGNOSTIC_EXACT_FORK');start=time.monotonic()
    result=store.mutate(life,'EO02_FANIN8_R03',lambda a:experiment(a,CASES[args.case]),details={'values':CASES[args.case],'pilot_not_confirmatory':True})
    out={'case':args.case,'life_id':life,'parent':fork['parent'],'sources':sources,'elapsed_seconds':time.monotonic()-start,'result':result}
    with gzip.open(dest,'wt',encoding='utf8',compresslevel=6)as f:json.dump(out,f,ensure_ascii=False,allow_nan=False)
    print(json.dumps({'case':args.case,'primary':str(dest),'elapsed_seconds':out['elapsed_seconds'],'tick':result['INSTRUMENTO']['tick'],'audit':result['result']['auditor_only']},ensure_ascii=False))
if __name__=='__main__':main()
