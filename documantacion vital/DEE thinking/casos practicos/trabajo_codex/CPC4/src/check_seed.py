"""External full-state comparison for the user-seeded common translation."""
import argparse
import json
from pathlib import Path
import random
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.common import digest


def run(reference,actual,seed):
    import dee_thinking as d
    left=d.OrganizationalWorld.load_snapshot(str(reference))
    right=d.OrganizationalWorld.load_snapshot(str(actual))
    n=67;shift=tuple(random.Random(seed+j).randrange(n) for j in range(3))
    assert left.runtime.dimension==right.runtime.dimension==n
    for field in ("raw_copy","clock_copy"):
        a=getattr(left.runtime,field)();b=getattr(right.runtime,field)()
        assert all(a[(x*n+y)*n+z]==b[(((x+shift[0])%n)*n+(y+shift[1])%n)*n+(z+shift[2])%n]
                   for x in range(n) for y in range(n) for z in range(n)),field
    assert left.runtime.current_tick==right.runtime.current_tick==267
    return {"translation":shift,"complete_RAW_clock_translation_equivalence":True,"final":digest(right)}


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--reference",type=Path,required=True);p.add_argument("--actual",type=Path,required=True);p.add_argument("--seed",type=int,required=True);a=p.parse_args()
    print(json.dumps(run(a.reference,a.actual,a.seed)))
