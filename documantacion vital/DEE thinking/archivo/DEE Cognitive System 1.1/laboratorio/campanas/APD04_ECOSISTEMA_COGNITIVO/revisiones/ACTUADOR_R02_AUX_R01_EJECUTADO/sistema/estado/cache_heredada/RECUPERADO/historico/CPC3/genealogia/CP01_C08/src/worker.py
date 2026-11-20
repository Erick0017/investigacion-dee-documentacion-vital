import argparse
from pathlib import Path
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from fronts import FIELDS
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--field',required=True);a=p.parse_args();root=Path(a.root)
    cfg=json.loads((root/'casos/EXPERIMENT_CONFIG.json').read_text())[a.field]
    result=FIELDS[a.field](root,cfg);print(json.dumps({'field':a.field,'status':result['status'],'duration_seconds':result['duration_seconds']},indent=2))
