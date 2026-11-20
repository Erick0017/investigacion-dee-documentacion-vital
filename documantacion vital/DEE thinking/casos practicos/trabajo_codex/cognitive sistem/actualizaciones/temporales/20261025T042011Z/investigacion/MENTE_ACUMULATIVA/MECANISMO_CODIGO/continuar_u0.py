"""Fifth experience, retention first-use, and continuation in another process."""
import argparse,gzip,hashlib,json,time
from pathlib import Path
import dee_thinking as d
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
OUT=ROOT/'evidencia/campanas/MENTE_ACUMULATIVA/mecanismo'
def put(p,x):
    if p.exists():raise FileExistsError(p)
    p.write_bytes(gzip.compress(json.dumps(x,ensure_ascii=False,sort_keys=True).encode(),mtime=0))
def snap(s,p):
    proof=s.save_snapshot(p,compress=True)
    return{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'proof':str(proof)}
def main(stage):
    if stage==1:
        source=OUT/'MA_U0_SEL_BA_PLUS.T472.deetsnap.gz';s=d.IntegratedSession.load_snapshot(source)
        before=s.observe();before_n=len(s.receipts());s.acquire('L07',-1,536);s.run_until(539)
        acquisition=s.observe();query=s.query(['L07','L03','L06','L05','L04'],603)
        saved=snap(s,OUT/'MA_U0_SEL_BA_PLUS.T606.deetsnap.gz')
        result={'schema':'MA.U0.continuation.1','stage':1,'life':s.identifier,'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'tick_initial':before['tick'],'tick_final':s.tick,'before':before,'acquisition':acquisition,'first_retention_after_fifth':query,'receipts_new':s.receipts()[before_n:],'snapshot':saved,'same_physical_life':True,'new_experience':{'form':'L07','current_consequence':-1,'tick':536},'old_forms_not_retaught':True,'source_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    else:
        source=OUT/'MA_U0_SEL_BA_PLUS.T606.deetsnap.gz';s=d.IntegratedSession.load_snapshot(source)
        before=s.observe();before_n=len(s.receipts());query=s.query(['L04','L06','L07','L03','L05'],670)
        saved=snap(s,OUT/'MA_U0_SEL_BA_PLUS.T673.deetsnap.gz')
        result={'schema':'MA.U0.continuation.1','stage':2,'life':s.identifier,'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'tick_initial':before['tick'],'tick_final':s.tick,'before':before,'first_query_other_process':query,'receipts_new':s.receipts()[before_n:],'snapshot':saved,'same_physical_life':True,'new_experience':None,'old_forms_not_retaught':True,'source_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    put(OUT/('CONTINUACION_U0_PROCESO_'+str(stage)+'.json.gz'),result)
    print(json.dumps({'stage':stage,'life':s.identifier,'tick':s.tick,'responses':[(r['form'],r['value'],r['status'])for r in query['responses']],'snapshot':saved},ensure_ascii=False),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stage',type=int,choices=[1,2],required=True);args=p.parse_args();main(args.stage)
