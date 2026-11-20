"""Portable one-case replay from an inherited physical+operative checkpoint."""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.continuidad.common import PARENT,load,sha,put
from src.continuidad.temporal_access import run

def main():
    p=argparse.ArgumentParser();p.add_argument('--case',type=Path,required=True);p.add_argument('--id');p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    case=json.loads(a.case.read_text(encoding='utf-8-sig'))
    if 'cases' in case:
        if not a.id:raise ValueError('A multi-case configuration requires --id')
        case=next(x for x in case['cases'] if x['id']==a.id)
    parent=PARENT/case['parent']
    if sha(parent)!=case['parent_sha256']:raise ValueError('Inherited checkpoint identity mismatch')
    if a.output.exists():raise FileExistsError('Use a new reproduction output directory')
    w,spec,neutral=load(parent);_,r=run(w,spec,case,a.output)
    put(a.output/'REPRODUCTION.json',{'case':case,'physical_final':r['final'],'forms':r['emitted_forms'],'parent_verified':True})
    print(json.dumps({'forms':r['emitted_forms'],'tick':w.runtime.current_tick}))

if __name__=='__main__':main()
