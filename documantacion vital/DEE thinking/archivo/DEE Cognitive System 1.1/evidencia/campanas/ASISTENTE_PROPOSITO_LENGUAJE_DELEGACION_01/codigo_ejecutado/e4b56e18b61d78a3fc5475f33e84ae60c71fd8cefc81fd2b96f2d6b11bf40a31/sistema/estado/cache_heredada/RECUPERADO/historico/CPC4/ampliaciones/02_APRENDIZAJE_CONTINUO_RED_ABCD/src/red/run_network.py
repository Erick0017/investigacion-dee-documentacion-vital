"""Explicit worker/reproducer for the bounded ABCD01 physical network."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"src"))
from red.recipe import run


def main():
    p=argparse.ArgumentParser();p.add_argument("--case",type=Path,required=True);p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();case=json.loads(a.case.read_text(encoding="utf-8"))
    world,spec,r=run(case,a.output)
    print(json.dumps({"id":case["id"],"tick":world.runtime.current_tick,"profile":r["task_profile"],
                      "D_first":r["D_first_read"],"D_reused":r["D_reused_read"]}))


if __name__=="__main__":main()
