"""AUX only: does a raw scalar event at an existing message head revise context?

Three histories share exact EO01 MAIN, same age and later raw comparison.
This is teaching through declared physical interfaces, not a RAW edit.
The taught scalar is not a correct motor response. No context or reader is
selected by expected success during the common later evaluation.
"""
from pathlib import Path
import argparse,gzip,hashlib,json,os,sys,time
from datetime import datetime,timezone

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'sistema'))
from app.lives import Store
from capacidades import cierre_funcional_cf01 as cf
from capacidades import arquitectura_distribuida_mi02_r8 as body
from capacidades import ente_operativo_01_core as core
EV=ROOT/'evidencia/campanas/ENTE_DEE_EVOLUCION_02/contexto'

def experiment(a,arm):
    start=int(a.tick);before=cf.witness(a);requests=[];frames=[]
    if arm!='none':
        sign=-1 if arm=='minus'else 1
        requests.append(body.send(a,'EO02.context.raw.'+arm,[6,16,12],[sign,-1,1],start+4,9))
    for t in range(start+1,start+25):
        a.run_until(t);frames.append({'witness':cf.witness(a),'head':body.obs(a,[6,16,12])})
    after_teaching=cf.witness(a)
    common=core.external_episode(a,public=[10,22],reference=12,feedback='omit',trace=True)
    return {'arm':arm,'before':before,'after_teaching':after_teaching,'frames':frames,'requests':body.receipts(a,requests),'common':common,'after':cf.witness(a)}

def main():
    p=argparse.ArgumentParser();p.add_argument('--arm',choices=['none','minus','plus'],required=True);args=p.parse_args()
    budget=json.loads((HERE.parent/'PRESUPUESTO.json').read_bytes())
    if time.monotonic()>=budget['deadline_monotonic']:raise TimeoutError('Original EO02 deadline')
    life='AUX_EO02_CTX_R01_'+args.arm
    out=EV/(life+'.json.gz')
    if out.exists():raise FileExistsError(out)
    store=Store(ROOT/'sistema');fork=store.fork('EO01_MAIN',life,kind='DIAGNOSTIC_EXACT_FORK')
    result=store.mutate(life,'EO02_CONTEXT_RAW_R01',lambda a:experiment(a,args.arm),details={'arm':args.arm,'raw_scalar':9,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    row={'source':str(Path(__file__).resolve()),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'parent':fork,'result':result,'new_ticks_only_on_auxiliary':True}
    EV.mkdir(parents=True,exist_ok=True)
    with gzip.open(out,'wt',encoding='utf8')as f:json.dump(row,f,ensure_ascii=False,allow_nan=False)
    r=result['result'];print(json.dumps({'life':life,'tick':r['after']['tick'],'context_before':[x['s_reg']for x in r['before']['context_A']],'context_after_teaching':[x['s_reg']for x in r['after_teaching']['context_A']],'context_after':[x['s_reg']for x in r['after']['context_A']],'common_command':r['common']['formed_native_command'],'own_after':[x['s_reg']for x in r['after']['own']],'requests':r['requests'],'primary':str(out)},ensure_ascii=False))
if __name__=='__main__':main()
