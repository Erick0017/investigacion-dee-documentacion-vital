"""Archived fourth-reference verification; no Native or provider calls."""
import argparse,importlib.util,json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--evidence',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path);args=parser.parse_args()
    source=args.evidence/'CODIGO_EJECUTADO/comparadores_apd03_wsls_estandar_r03.py'
    spec=importlib.util.spec_from_file_location('standard_wsls_closed',source)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    result=module.recalculate(args.evidence/'wsls_estandar')
    with args.out.open('x',encoding='utf8')as stream:
        json.dump(result,stream,sort_keys=True,ensure_ascii=False,indent=2);stream.write('\n')


if __name__=='__main__':main()
