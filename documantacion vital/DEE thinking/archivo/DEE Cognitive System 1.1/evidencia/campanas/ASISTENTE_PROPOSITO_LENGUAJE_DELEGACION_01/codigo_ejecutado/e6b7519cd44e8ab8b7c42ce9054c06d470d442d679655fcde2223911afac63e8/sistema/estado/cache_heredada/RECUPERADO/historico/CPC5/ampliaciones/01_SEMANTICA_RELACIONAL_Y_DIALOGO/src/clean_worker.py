"""Finite technical replay coordinator; no terminal records or targets read.

Calls the scientific native constructor/evolution directly. This avoids a
research screen's workspace-relative index requirement for external output.
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--case',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    from dialogue import run_case
    config=json.loads(a.case.read_text(encoding='utf-8'))
    case=config['case'];root=a.output
    if root.exists():raise FileExistsError(root)
    root.mkdir(parents=True)
    run_case(case,root/case['id'])


if __name__=='__main__':main()
