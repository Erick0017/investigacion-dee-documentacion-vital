"""Explicit preT0factory adapter; no observation-based input or answer choice."""
import argparse
import json
from pathlib import Path
import shutil
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from integracion import run_pair
from integracion.relational_pair_v2 import PairV2


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case-id',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    # run_pair.main owns one finite process and reads the frozen configuration.
    adapter={'modality':'EXPLICIT_PRET0_REPRESENTATION2_FACTORY_NOT_TARGET_SELECTION','factory':'integracion.relational_pair_v2.PairV2',
        'source_sha256':{p.name:run_pair.sha(p)for p in(Path(__file__),ROOT/'src/integracion/relational_pair_v2.py')}}
    original=run_pair.put
    def put(path,value):
        if Path(path).name=='MEASUREMENTS.json':value={**value,'factory_adapter':adapter}
        return original(path,value)
    run_pair.PairSession=PairV2;run_pair.put=put
    sys.argv=[sys.argv[0],'--config',str(a.config),'--case-id',a.case_id,'--out',str(a.out)];run_pair.main()
    for path in(Path(__file__),ROOT/'src/integracion/relational_pair_v2.py'):shutil.copyfile(path,a.out/'executed_source'/path.name)


if __name__=='__main__':main()
