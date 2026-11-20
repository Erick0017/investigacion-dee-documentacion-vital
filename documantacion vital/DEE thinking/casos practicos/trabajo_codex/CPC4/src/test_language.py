"""Non-native parser/catalogue contracts, not physical capability tests."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.language import InterfaceAliases, catalogue_view, parse, render


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    checks = {}
    checks["spanish_command_only"] = parse("consulta B bruma").arguments == ("B", "bruma")
    checks["quoted_windows_path_preserved"] = parse('cargar "C:\\Mis datos\\ente.deetsnap"').arguments == ("C:\\Mis datos\\ente.deetsnap",)
    checks["seed_is_argument_not_answer"] = parse("crear semilla 23").arguments == ("23",)
    checks["accent_commands"] = parse("catálogo").operation == "catalogue"
    aliases = InterfaceAliases(("A", "B"))
    aliases.add("bruma", "B")
    checks["alias_is_interface_identity_only"] = aliases.resolve("bruma") == "B"
    try:
        aliases.add("A", "B")
        checks["alias_cannot_usurp_physical_id"] = False
    except ValueError:
        checks["alias_cannot_usurp_physical_id"] = True
    for text, name in (("crear semilla -1", "bad_seed"), ("avanzar 10001", "bounded_advance"), ("resuelve toda la mente", "unknown_command")):
        try:
            parse(text)
            checks[name] = False
        except ValueError:
            checks[name] = True
    catalog = json.loads((ROOT / "NSM65_CATALOGO.json").read_text(encoding="utf-8"))
    checks["sixty_five_stable_ids"] = len(catalog["entries"]) == len({x["id"] for x in catalog["entries"]}) == 65
    checks["seven_independent_dimensions"] = all(len(x["dimensiones_independientes"]) == 7 for x in catalog["entries"])
    checks["other_sixty_three_only_documentary"] = all(x["dimensiones_independientes"]["asociacion_entrenada"]["estado"] == "NO_COMPROBADO_EN_DEE" for x in catalog["entries"] if x["id"] not in ("NSM65.THERE_IS","NSM65.NOT"))
    checks["no_full_NSM_semantics_claim"] = all(x.get("full_NSM_semantics") is not True for x in catalog["entries"])
    checks["single_form_teaching_command"] = parse("enseñar HAY").arguments == ("HAY",)
    checks["diagnostic_is_explicit_command"] = parse("diagnóstico").operation == "diagnose"
    checks["observe_again_only_passive_operation"] = parse("vuelve a observar").operation == "observe"
    checks["catalogue_is_explicitly_documentary"] = catalogue_view(ROOT / "NSM65_CATALOGO.json", "antes")["attribution"] == "EXPLICACION_DOCUMENTAL"
    checks["render_reports_actual_raw_not_a_label_solution"] = "RAW=123" in render({"attribution": "ENTE", "physical_output": {"tick": 8, "raw": 123, "direction": [-1, 1, 0], "s_reg": 21}})
    value = {"verified": all(checks.values()), "checks": checks, "count": len(checks), "native_executions": 0,
             "scope": "Parser, external aliases and documentary inventory only; no native capability adjudication"}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"verified": value["verified"], "checks": len(checks)}))
    assert value["verified"]


if __name__ == "__main__":
    main()
