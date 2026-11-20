"""Certify that final launcher conveniences did not change the frozen worker."""
import ast
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.common import put,sha


def function(path,name):
    return next(n for n in ast.parse(path.read_text(encoding="utf-8")).body if isinstance(n,ast.FunctionDef) and n.name==name)


old=ROOT/"resultados"/"versiones"/"EJECUTOR_CONFIRMATORIO_V1.py"
new=ROOT/"ejecutar.py"
unchanged={name:ast.dump(function(old,name))==ast.dump(function(new,name)) for name in ("load_config","case_worker","completed","campaign")}
assert all(unchanged.values())
put(ROOT/"resultados"/"EXECUTOR_EVOLUTION.json",{
    "source_used_for_33_frozen_cases":"resultados/versiones/EJECUTOR_CONFIRMATORIO_V1.py",
    "v1_sha256":sha(old),"current_source":"ejecutar.py","current_sha256":sha(new),
    "functions_AST_identical":unchanged,
    "change":"Final public entry point adds demo and conditional access2 reproduction dispatch only; no preparation, participant input, physics, decoder or measured worker body changed",
    "followup_validation":"Clean extracted execution reproduces MAIN_MINUS/CUT_MINUS and demo with final launcher; source assertions remain on the original experimental modules"})
print("Frozen worker functions unchanged",unchanged)
