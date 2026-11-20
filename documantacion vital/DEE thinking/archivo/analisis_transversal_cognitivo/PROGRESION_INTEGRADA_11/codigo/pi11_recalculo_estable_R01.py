"""Stable RP documentary interface: --root MATERIAL --out-dir NEW.

Material contains primarios/, CIERRE_DOCUMENTAL.json and the exact preserved
recalcular_PI11_R01.py. No campaign path, selected life or DEE import is used.
"""
from pathlib import Path
import argparse,importlib.util,json

def run(root,out_dir):
    root=Path(root).resolve(strict=True)
    source=root/'recalcular_PI11_R01.py'
    sp=importlib.util.spec_from_file_location('PI11_closed_documentary_material',source)
    module=importlib.util.module_from_spec(sp);sp.loader.exec_module(module)
    result=module.recalculate(root/'primarios',out_dir,root/'CIERRE_DOCUMENTAL.json')
    return {'Native_executed':False,'DEE_imported':False,'lives':list(result['by_life']),
            'output':str(Path(out_dir).absolute()),'not_Native_reproduction':True}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',required=True);parser.add_argument('--out-dir',required=True)
    args=parser.parse_args();print(json.dumps(run(args.root,args.out_dir),ensure_ascii=False))
