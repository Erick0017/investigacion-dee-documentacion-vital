from pathlib import Path
import json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'sistema'))
from app.process_control import spawn_owned,job_resources,terminate_job,close_job
from app.native_tools import atomic_json,digest_file,physical
from app.lives import Store
import argparse
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--compare-only',action='store_true');args=parser.parse_args()
    out=ROOT/'evidencia/verificaciones/E1_T0_884_RECONSTRUCCION';out.mkdir(parents=True,exist_ok=args.compare_only);events=ROOT/'sistema/documentacion/ejemplos/e1_nueva_reproduccion.eventos';argv=[sys.executable,'-I','-B','-X','utf8',str(ROOT/'sistema/gestionar.py'),'eventos',str(events)];start=time.perf_counter()
    if not args.compare_only:
        with(out/'EVENTOS.stdout.json').open('w',encoding='utf8')as stdout,(out/'EVENTOS.stderr.log').open('w',encoding='utf8')as stderr:
            proc,job,name=spawn_owned(argv,cwd=out,stdout=stdout,stderr=stderr)
            try:code=proc.wait(timeout=900)
            except BaseException:terminate_job(job);proc.wait();raise
            finally:resources=job_resources(job);close_job(job)
        result={'schema':'DCS1.1.new_T0.reference_reconstruction.v1','event_file_sha256':digest_file(events),'argv':argv,'exit_code':code,'seconds':time.perf_counter()-start,'resources':resources,'owned_job':name,'new_life_not_imported_past':True};atomic_json(out/'EJECUCION.json',result)
    else:
        code=0;result={'schema':'DCS1.1.new_T0.reference_reconstruction.v1','event_file_sha256':digest_file(events),'argv_original':argv,'mode':'PASSIVE_COMPARISON_AFTER_COMPLETED_NEW_LIFE','execution_not_repeated':True,'resource_coverage_gap':'Original command completed successfully, but first comparison reporter raised KeyError on historicalrecordmetadata. Do not invent its lost elapsed/RAM accounting. Original stdout and learned life remain intact.','new_life_not_imported_past':True}
    if code==0:
        store=Store();old,a=store.load('E1_CPC9_884');new,b=store.load('E1_RECONSTRUIDO_11');result.update(reference_checkpoint_sha256=digest_file(store.snapshot(old)),new_checkpoint_sha256=new['snapshot_sha256'],reference_physical=physical(a.world),new_physical=physical(b.world),full_RAW_clocks_tick_equal=physical(a.world)==physical(b.world),reference_receipts=len(a.world.runtime.receipts),new_receipts=len(b.world.runtime.receipts),new_interfaces=len(b.world.interfaces),reference_interfaces=len(a.world.interfaces))
    atomic_json(out/'COMPARACION.json',result);print(json.dumps(result))
if __name__=='__main__':main()
