"""RP documentary entry point; preserved actual REAL18, never a new replay."""
from pathlib import Path
import argparse, importlib.util, json

def main(args):
    root=Path(args.root).resolve(strict=True); out=Path(args.out_dir).absolute()
    if out.exists(): raise ValueError('New external output directory required')
    spec=importlib.util.spec_from_file_location('preserved_B18_recalculation',root/'RECALCULAR_B_PI08_R01.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    result=module.calculate(root,'INDICE_B_PI08_R01.json')
    real=result['denominators'].get('real',{})
    if not(result['integrity_passed']and real.get('complete_closed_18')is True and real.get('opportunities')==18):
        raise ValueError('Actual complete REAL18 evidence required')
    out.mkdir(parents=True)
    (out/'RESULTADO_RECALCULO.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'integrity_passed':True,'REAL18':real,'B_new_CLI_replay_verified':False,'Native_executed':False},ensure_ascii=False))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',required=True);parser.add_argument('--out-dir',required=True);main(parser.parse_args())
