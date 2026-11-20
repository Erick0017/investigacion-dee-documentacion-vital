"""Finite paired pilot on exact forks; all native consequences omitted.

The EO01 environment is a legacy unused fixture here; the four-component law
is calculated only AFTER its emitted physical command has been recorded.
No utility/contact/learning claim is made from that old two-variable fixture.
"""
from pathlib import Path
import argparse,gzip,hashlib,json,os,sys,time
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'sistema'));sys.path.insert(0,str(HERE))
from app.lives import Store
from capacidades import arquitectura_distribuida_mi02_r8 as body
from capacidades import cierre_funcional_cf01 as cf
from capacidades import ente_operativo_01_core as core
from app.native_tools import physical,atomic_json,digest_file
import fanin_r01 as fanin
CASES={'M0':[3,18,0,0],'M_LBASE':[9,18,0,0],'M_RBASE':[3,12,0,0],
       'M_LEXTRA':[3,18,6,0],'P0':[6,15,0,0],'P_REXTRA':[6,15,0,6]}

def experiment(a,values):
    pre=physical(a.world);extra=fanin.submit_extra(a,values)
    result=core.external_episode(a,public=values[:2],reference=12,actuator='nulled',feedback='omit',trace=True)
    # AUDITOR ONLY, after emission. No aggregate or desired sign entered DEE.
    totalL=values[0]+values[2];totalR=values[1]+values[3]
    target=1 if totalL+12>=totalR else-1
    sensor_frames=[]
    for f in result['frames']:
        if abs(f['tick']-extra['expected_arrival'])<=2:
            sensor_frames.append({'tick':f['tick'],'frame':f})
    return{'revision':fanin.REVISION,'values':values,'physical_before':pre,'extra':extra,
      'extra_receipts':body.receipts(a,extra['requests']),'native':result,
      'auditor_only':{'left_total':totalL,'right_total':totalR,'calibration':12,'target':target,
        'command':result['formed_native_command'],'matches':result['formed_native_command']==target},
      'scope':'Material joint-use pilot; old external fixture was actuator-nulled and feedback-omitted. Not an acquisition/utility trial.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--case',choices=CASES,required=True);args=p.parse_args()
    path=ROOT/'evidencia/campanas/ENTE_DEE_EVOLUCION_02/capacidad'/('PILOTO_R01_'+args.case+'.json.gz')
    if path.exists():raise FileExistsError(path)
    store=Store();life='AUX_EO02_CAP_R01_'+args.case
    fork=store.fork('EO01_MAIN',life,kind='EO02_CAPACITY_DIAGNOSTIC_EXACT_FORK')
    start=time.monotonic()
    try:r=store.mutate(life,'EO02_FANIN4_R01',lambda a:experiment(a,CASES[args.case]),details={'role':'pilot','values':CASES[args.case],'no_native_reteaching':True})
    except Exception as e:
        atomic_json(path.with_suffix('.ERROR.json'),{'case':args.case,'error':repr(e),'life':life});raise
    output={'case':args.case,'life_id':life,'parent':fork['parent'],'sources':{str(f):digest_file(f)for f in(HERE/'fanin_r01.py',Path(__file__))},'elapsed_seconds':time.monotonic()-start,'result':r}
    path.parent.mkdir(parents=True,exist_ok=True)
    with gzip.open(path,'wt',encoding='utf8',compresslevel=6)as f:json.dump(output,f,ensure_ascii=False,allow_nan=False)
    q=r['result'];print(json.dumps({'case':args.case,'primary':str(path),'elapsed_seconds':output['elapsed_seconds'],'tick':r['INSTRUMENTO']['tick'],'audit':q['auditor_only'],'extra_receipts':q['extra_receipts']},ensure_ascii=False))
if __name__=='__main__':main()
