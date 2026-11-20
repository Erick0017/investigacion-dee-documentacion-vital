import argparse,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from core.revisable_selection import run,revalidate_r14
def main(root,case):
    config=json.loads((root/'experimentos/seleccion_revisable/EXPERIMENT_CONFIG.json').read_text());p=root/'experimentos/seleccion_revisable'
    if case=='r14':
        rows=revalidate_r14(p/'R14_REVALIDATION.json');print(json.dumps(rows,ensure_ascii=True));return
    spec=next(c for c in config['cases'] if c['id']==case);args={k:v for k,v in spec.items() if k not in ('id','kind')};t=time.monotonic();result=run(args,p/'casos'/case);print(json.dumps({'case':case,'seconds':time.monotonic()-t,'measurements':result['measurements'],'receipts':result['receipts']},ensure_ascii=True),flush=True)
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--root',type=Path,default=ROOT);a.add_argument('--case',required=True);x=a.parse_args();main(x.root,x.case)
