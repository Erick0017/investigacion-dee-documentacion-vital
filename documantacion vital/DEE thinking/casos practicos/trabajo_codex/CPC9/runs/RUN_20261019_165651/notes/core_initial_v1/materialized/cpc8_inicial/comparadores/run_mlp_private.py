"""Disclosed constructor-only isolation; reuse the exact frozen common evaluator.

The evaluator's scenario seed is discarded by this bootstrap and never reaches
the participant. Model/optimizer/replay/decoder and experience streams do not
change. models.py imports no curriculum, targets or campaign configuration.
"""
from pathlib import Path
import hashlib,json,sys
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
import run_comparison as evaluator
from models import ReplayMLP

PRIVATE_INITIALIZATION_SEED=17890331

def construct_private(*,count,seed,**parameters):
    del seed  # evaluator identifier is explicitly not participant information
    return ReplayMLP(count=count,seed=PRIVATE_INITIALIZATION_SEED,**parameters)

def main():
    config=json.loads((BASE/"PRIVATE_RNG_PROTOCOL.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==config["source_sha256"]
    assert config["private_seed"]==PRIVATE_INITIALIZATION_SEED
    if "--method" not in sys.argv or sys.argv[sys.argv.index("--method")+1]!="B2":
        raise ValueError("This bootstrap is only the isolated B2 comparator")
    if "--output" not in sys.argv:raise ValueError("Separate output required: preserve original shared-seed attempts")
    evaluator.ReplayMLP=construct_private
    evaluator.main()

if __name__=="__main__":main()
