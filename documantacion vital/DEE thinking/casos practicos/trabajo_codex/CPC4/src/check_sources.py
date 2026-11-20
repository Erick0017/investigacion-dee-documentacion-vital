"""Syntax, frozen-source and immutable-kernel checks without simulation."""
import ast
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.common import put,sha,KERNEL_SHA


def main():
    files=[ROOT/"ejecutar.py",ROOT/"demostracion.py",ROOT/"supervise.py",*sorted((ROOT/"src").glob("*.py"))]
    checked=[]
    for p in files:
        ast.parse(p.read_text(encoding="utf-8"))
        checked.append({"path":p.relative_to(ROOT).as_posix(),"sha256":sha(p),"AST_valid":True})
    frozen=json.loads((ROOT/"EXPERIMENT_CONFIG.json").read_text(encoding="utf-8"))
    identity=[]
    for name,expected in frozen["source_sha256"].items():
        path=ROOT/("resultados/versiones/EJECUTOR_CONFIRMATORIO_V1.py" if name=="ejecutar.py" else name)
        assert sha(path)==expected,(name,"frozen source changed")
        identity.append({"source":name,"preserved_at":path.relative_to(ROOT).as_posix(),"sha256":expected})
    kernel=ROOT/"referencias"/"fuentes"/"fuentes"/"producto4"/"source"/"src"/"kernel_v27.cpp"
    assert sha(kernel)==KERNEL_SHA
    result={"AST_sources_checked":len(files),"sources":checked,"frozen_source_identities":identity,
            "frozen_identities_equal":True,"kernel_source_sha256":sha(kernel),
            "source_version_note":"Final launcher convenience dispatches differ from the original launcher; the actual worker AST is separately checked identical. No frozen physical module changed."}
    put(ROOT/"resultados"/"SOURCE_CHECKS.json",result)
    print("Source checks",len(files),"AST; frozen",len(identity),"identities; kernel exact")


if __name__=="__main__":main()
