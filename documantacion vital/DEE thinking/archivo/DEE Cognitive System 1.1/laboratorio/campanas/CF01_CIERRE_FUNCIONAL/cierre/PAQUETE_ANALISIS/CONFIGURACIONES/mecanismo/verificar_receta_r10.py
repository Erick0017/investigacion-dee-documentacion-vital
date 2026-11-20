"""Structural recipe check only; no Runtime, world creation or DEE ticks."""
from pathlib import Path
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT/"sistema"))
from capacidades.geometria_distribuida_mi02_r9 import unified_recipe as baseline
from capacidades.geometria_cierre_funcional_cf01_r10 import unified_recipe as candidate


def main():
    _, old = baseline()
    _, new = candidate()
    a = {tuple(q["site"]): (q["load"], q["direction"]) for q in old["anchors"]}
    b = {tuple(q["site"]): (q["load"], q["direction"]) for q in new["anchors"]}
    changed = {p for p in set(a)|set(b) if a.get(p) != b.get(p)}
    expected = {(16,8,8),(16,7,7),(22,8,8),(22,7,7)}
    assert changed == expected
    assert old["N"] == new["N"] == 26
    assert old["A"] == new["A"] and old["B"] == new["B"]
    for key in ("pinned", "query", "social", "external_sensors"):
        assert old[key] == new[key], key
    sources_a = {q["id"]: q for q in old["prepared_sources"]}
    sources_b = {q["id"]: q for q in new["prepared_sources"]}
    assert set(sources_a) == set(sources_b)
    assert {k for k in sources_a if sources_a[k] != sources_b[k]} == {"B.-1.first", "B.1.first"}
    code = ROOT/"sistema/capacidades/geometria_cierre_funcional_cf01_r10.py"
    report = {"schema": "CF01.R10.recipe.structural_check.v1", "new_ticks": 0,
              "Runtime_instantiated": False, "scope": "Prepared recipe structure only, not native functional validation",
              "code_sha256": hashlib.sha256(code.read_bytes()).hexdigest(),
              "changed_anchors": [{"site": p, "R9": a.get(p), "R10": b.get(p)} for p in sorted(changed)],
              "source_changes": new["CF01_source_changes"],
              "pinned_query_social_and_external_interfaces_unchanged": True,
              "opened_added": sorted(set(map(tuple,new["opened"]))-set(map(tuple,old["opened"]))),
              "opened_removed": sorted(set(map(tuple,old["opened"]))-set(map(tuple,new["opened"])))}
    path = HERE/"R10_GEOMETRIA_COMPROBACION.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n", encoding="utf8")
    print(json.dumps({"output": str(path), "changed_anchors": len(changed), "new_ticks": 0,
                      "Runtime_instantiated": False, "code_sha256": report["code_sha256"]}))


if __name__ == "__main__":
    main()
