from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'sistema'))
from app.legacy import run_families
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--families');p.add_argument('--seconds',type=int,default=3600);p.add_argument('--workers',type=int,default=1);a=p.parse_args()
    result=run_families(ROOT/'sistema',a.out,families=a.families.split(',')if a.families else None,total_seconds=a.seconds,max_workers=a.workers)
    print(json.dumps({'status':result['status'],'counts':result['counts'],'seconds':result['elapsed_seconds']}))
if __name__=='__main__':main()
