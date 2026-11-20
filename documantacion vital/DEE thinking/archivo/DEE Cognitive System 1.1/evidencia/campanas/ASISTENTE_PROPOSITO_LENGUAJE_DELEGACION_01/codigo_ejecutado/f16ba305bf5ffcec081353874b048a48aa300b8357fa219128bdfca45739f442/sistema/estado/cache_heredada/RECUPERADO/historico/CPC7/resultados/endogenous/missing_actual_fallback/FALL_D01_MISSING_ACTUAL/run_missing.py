"""Select the explicit v2 physical adapter; reuse passive runner, not results."""
from pathlib import Path
import argparse,json,shutil,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.path.insert(0,str(Path(__file__).resolve().parent))
import run_need
import comparison_need_v2
from common import put,sha,ROOT


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    # This chooses the declared apparatus before creation, never a branch or
    # result during evolution. v1 code and earlier primary files stay intact.
    run_need.apparatus=comparison_need_v2
    a.out.mkdir(parents=True,exist_ok=True);index=[]
    for case in json.loads(a.config.read_text(encoding='utf-8-sig'))['cases']:
        out=a.out/case['id']
        r=json.loads((out/'MEASUREMENTS.json').read_text(encoding='utf-8')) if (out/'MEASUREMENTS.json').exists() else run_need.run(case,out)
        for name in ('comparison_need_v2.py','run_missing.py'):shutil.copyfile(Path(__file__).parent/name,out/name)
        put(out/'ADAPTER_IDENTITY.json',{'adapter':'comparison_need_v2','source_sha256':sha(Path(__file__).parent/'comparison_need_v2.py'),
            'selector_sha256':sha(__file__),'selection_modality':'PreT0 declared recipe selection, not runtime decision from targets'})
        index.append({'id':case['id'],'questions':r['native_questions'],'information':r['received_information'],'use':r['later_physical_use'],
                      'evidence':(out/'MEASUREMENTS.json').resolve().relative_to(ROOT).as_posix(),'sha256':sha(out/'MEASUREMENTS.json')})
        put(a.out/'INDEX.json',{'cases':index})

if __name__=='__main__':main()
