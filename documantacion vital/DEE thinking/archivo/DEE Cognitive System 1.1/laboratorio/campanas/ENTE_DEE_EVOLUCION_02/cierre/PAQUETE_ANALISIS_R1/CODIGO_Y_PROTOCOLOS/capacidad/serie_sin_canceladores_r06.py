"""R06: remove the two center cancel supplies, not acquired matter.

The recipe is fixed prospectively on a new exact fork. Residual side directions
are allowed, but their effect is measured rather than assumed equivalent.
"""
from pathlib import Path
import gzip,json,os,sys,time
from types import SimpleNamespace
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'sistema'));sys.path.insert(0,str(HERE))
from app.lives import Store
from app.native_tools import digest_file
from capacidades import arquitectura_distribuida_mi02_r8 as body
from capacidades import ente_operativo_01_core as core
import serie_cuatro_r05 as runner

def submit_extra(a,values):
    t=core._plan(a)['critical_tick']-18
    rows=[body.send(a,'EO02.fanin4nocancel.'+name,site,v,t,values[index])for name,site,v,index in
       [('left',(4,13,16),(1,0,-1),2),('right',(8,13,16),(-1,0,-1),3)]]
    return{'revision':'EO02.fanin4.no_center_cancel.r06','tick':t,'requests':rows,'expected_arrival':t+1,
       'sums_not_supplied':True,'prepared_zero_resources':0,'central_positions_not_injected':True}
def main():
    dest=ROOT/'evidencia/campanas/ENTE_DEE_EVOLUCION_02/capacidad/SERIE_R06_CUATRO_SIN_CENTROS.json.gz'
    if dest.exists():raise FileExistsError(dest)
    files=[Path(__file__),HERE/'serie_cuatro_r05.py'];archive=HERE/'revisiones/R06';archive.mkdir(parents=True,exist_ok=True)
    for f in files:
        out=archive/f.name
        if out.exists()and digest_file(out)!=digest_file(f):raise ValueError('Archive conflict')
        if not out.exists():out.write_bytes(f.read_bytes())
    runner.fanin=SimpleNamespace(submit_extra=submit_extra)
    store=Store();life='AUX_EO02_CAP_R06_NO_CENTER';fork=store.fork('EO01_MAIN',life,kind='EO02_CAPACITY_DIAGNOSTIC_EXACT_FORK');start=time.monotonic()
    r=store.mutate(life,'EO02_CAPACITY4_R06',lambda a:runner.experiment(a,runner.FRAMES[:4]),details={'new_preparation':'No central cancel supplies; no state edits','frames':runner.FRAMES[:4]})
    out={'revision':'EO02.fanin4.no_center_cancel.r06','life_id':life,'parent':fork['parent'],'sources':{str(f):digest_file(f)for f in files},'elapsed_seconds':time.monotonic()-start,'ram':runner.ram(),'result':r}
    with gzip.open(dest,'wt',encoding='utf8',compresslevel=6)as f:json.dump(out,f,ensure_ascii=False,allow_nan=False)
    print(json.dumps({'path':str(dest),'rows':[q['auditor_only']for q in r['result']['rows']],'receipts':[v['receipt']['status']for q in r['result']['rows']for v in q['extra_receipts']],'ram':out['ram']},ensure_ascii=False))
if __name__=='__main__':main()
