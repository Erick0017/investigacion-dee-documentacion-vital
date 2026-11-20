"""Use incorporated P1 only on explicit Store evaluation forks."""
import argparse,gzip,hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];EV=ROOT/'evidencia/campanas/MENTE_ACUMULATIVA_R02/mecanismo_repetible';sys.path.insert(0,str(ROOT/'sistema'))
from app.lives import Store
from capacidades import selector_p1_ma02 as p1
def main():
    ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['fork_use','reload']);a=ap.parse_args();s=Store()
    out=EV/('MA02_P1_SYSTEM_'+a.phase.upper()+'.json.gz')
    if out.exists():raise FileExistsError(out)
    results=[]
    for suffix in('H1','H0'):
        src='MA02_SELECTOR_P1_'+suffix;target=src+'_EVALUACION_01'
        before=s.status(src)
        if a.phase=='fork_use':
            fork=s.fork(src,target,kind='EXACT_EVALUATION_FORK');result=s.mutate(target,'P1_FIRST_USE_INCORPORADO',lambda x:p1.use(x,detailed=True),{'domain':'certified one finite use, no re-teaching'})
            results.append({'source_life':src,'source_status_before':before,'fork':fork,'result':result,'source_status_after':s.status(src)})
        else:
            rec,ad=s.load(target);state=p1.state(ad);reject=None
            try:p1.use(ad);raise RuntimeError('Unexpected second-use admission')
            except ValueError as e:reject=str(e)
            results.append({'source_life':src,'source_status_before':before,'evaluation_life':target,'reloaded_record':rec,'state':state,'repeat_rejected':reject,'source_status_after':s.status(src)})
    value={'schema':'MA02.P1.system_operational_check.1','identifier':'MA02_P1_SYSTEM_'+a.phase.upper(),'phase':a.phase,'results':results,'adapter_sha256':hashlib.sha256((ROOT/'sistema/capacidades/selector_p1_ma02.py').read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'no_original_consumed':True,'same_manager_no_new_T0':True}
    out.write_bytes(gzip.compress(json.dumps(value,ensure_ascii=False,sort_keys=True).encode(),mtime=0));print(json.dumps({'phase':a.phase,'life_ticks':[(r['source_life'],r['source_status_after']['physical']['tick'])for r in results]},ensure_ascii=False))
if __name__=='__main__':main()
