"""Last algebraically directed refinement of the same vector family, 3 runs."""
from datetime import datetime,timezone
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/"src"))
from red import recipe_v3 as r
import supervision


def main():
    folder=ROOT/"resultados/red/v3_discovery01"
    sources=("recipe_v3.py","session_v3.py","run_roles_v3.py","common_helpers.py","run_v3_discovery.py")
    config={"frozen_utc":datetime.now(timezone.utc).isoformat(),"architecture_family":1,
            "reason":"V2 unpaired controls preserved utility because uncued teacher components reached the useful routes. V3 query axes distinguish these actual sources.",
            "source_sha256":{name:r.sha(Path(__file__).with_name(name)) for name in sources},
            "cases":[json.loads((folder/(name+".json")).read_text(encoding="utf-8")) for name in ("FULL","C_UNPAIRED","D_UNPAIRED")],
            "D_query_panel_frozen":[{"input_tick":158,"direction":[1,0,0]},{"input_tick":225,"direction":[-1,0,0]}],
            "scope":"Alternating fixed two-probe panel, not identical indefinitely renewable input. Last refinement of this family; preserve any limitation rather than tuning another shortcut away."}
    r.put(folder/"EXPERIMENT_CONFIG.json",config)
    frozen=folder/"EXECUTED_SOURCE";frozen.mkdir(exist_ok=True)
    for name in sources:(frozen/name).write_bytes(Path(__file__).with_name(name).read_bytes())
    rows=[]
    for name in ("FULL","C_UNPAIRED","D_UNPAIRED"):
        argv=[str(r.BASE/".venv/Scripts/python.exe"),"-I","-B",str(Path(__file__).with_name("run_roles_v3.py")),
              "--case",str(folder/(name+".json")),"--output",str(folder/name)]
        row=supervision.run(ROOT,"red_v3_discovery_"+name,argv,180,str(ROOT));rows.append(row)
        r.put(folder/"EXECUTION_INDEX.json",rows);print(json.dumps(row),flush=True)


if __name__=="__main__":main()
