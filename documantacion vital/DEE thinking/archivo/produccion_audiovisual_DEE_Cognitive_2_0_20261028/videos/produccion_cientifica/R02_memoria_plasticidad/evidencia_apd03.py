"""Extractos editoriales de APD03 existente. No ejecuta DEE ni escribe archivos.

extract() comprueba los bytes citados antes de interpretar los registros. Los
datos resultantes describen acontecimientos históricos de una sola vida; no
constituyen otra interfaz de Cognitive ni una traza completa por tick.
"""
from __future__ import annotations

import base64
import gzip
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile


_CLOSURE = (
    "archivo/DEE Cognitive System 1.1/laboratorio/campanas/"
    "APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION/main/exportacion/CIERRE_MAIN_APD03_R01"
)
_HASHES = {
    "002_material.json.gz": "9595d5d063625b1f90c8c5682aa8f15a185639910a1e0168b8d672761c60831d",
    "014_material.json.gz": "4c4b3caa99a199ead485cda5204d9d9d4c7be4b5a1ce95348313899d58a54cd8",
    "015_material.json.gz": "5e2a9f0c07f747f0b287fca59d7e6f2bf6a2b3f4ede8cb1a67b980bfebee3a61",
    "016_material.json.gz": "e0b82ee51de8a451c3c547292421091fceccc71cb54f31c7e88c8cc78223db15",
    "017_material.json.gz": "9eb067811c2092a35408cccfa400a3f2c83975abda0fb5ed943483d1192e8408",
    "022_material.json.gz": "6f333426443caa3ea5f6d6499638a80a107518d91bd8d9805267131a3f1c30c4",
    "024_material.json.gz": "3b884d930293fde263912f7441b28e07ea9e9094bdb5795e923438ed29010d6f",
    "047_material.json.gz": "eb19f9e068065ab5432d98d050e54ca81eb46e9fc9ff54e476fb4adec2edd64f",
}


def _root() -> Path:
    return next(p for p in Path(__file__).resolve().parents if p.name == "DEE thinking")


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _checked(root: Path, relative: str, expected: str) -> bytes:
    path = root / relative
    data = path.read_bytes()
    actual = _digest(data)
    if actual != expected:
        raise ValueError(f"Fuente APD03 con bytes distintos: {path}; SHA256 {actual}")
    return data


def _receipt(request: dict) -> dict:
    receipt = request["receipt"]
    return {k: receipt.get(k) for k in
            ("id", "channels", "requested_tick", "effective_tick", "status", "reason")}


def _panel(row: dict) -> dict:
    return {
        "before_tick": row["before"]["tick"],
        "after_tick": row["after"]["tick"],
        "forms": [{"form": x["form"], "tick": x["result"]["read_tick"],
                   "sign": x["result"]["reader"]["formed_native_command"]}
                  for x in row["forms"]],
        "memory_queries": [{"context": x["context"], "tick": x["result"]["read_tick"],
                            "sign": x["result"]["reader"]["formed_native_command"]}
                           for x in row["memories"]],
        "material_queries_not_passive": row["material_not_passive"],
    }


def extract() -> dict:
    """Devuelve evidencia mínima trazable; únicamente lectura de bytes archivados."""
    root = _root()
    sources = []
    loaded = {}
    for name, expected in _HASHES.items():
        relative = f"{_CLOSURE}/EVIDENCIA_MAIN/EVENTOS/{name}"
        data = _checked(root, relative, expected)
        event = json.loads(gzip.decompress(data).decode("utf-8"))
        assert event["decoded_result"]["committed_snapshot"]["life_id"] == "APD03_MAIN"
        loaded[name] = event
        sources.append({"path": str(root / relative), "relative_path": relative,
                        "sha256": expected, "pointer": "/decoded_result/result/rows/0",
                        "transport_id": event["id"]})

    def row(name):
        return loaded[name]["decoded_result"]["result"]["rows"][0]

    recalc_path = f"{_CLOSURE}/RESULTADOS/RECALCULO_MAIN_FINAL.json"
    recalc_sha = "2f4208e4d1fc4575772685672640ecff66e0b7092b6c9fd3e680feda24917ab8"
    recalc = json.loads(_checked(root, recalc_path, recalc_sha).decode("utf-8"))
    sources.append({"path": str(root / recalc_path), "relative_path": recalc_path,
                    "sha256": recalc_sha,
                    "pointer": "/new_generic_lessons; /new_generic_uses; /panels; /opportunities; /counts"})

    # El informe da genealogía y atribución; los valores de los planos se toman
    # de los primarios anteriores, no se copian de un veredicto automático.
    report_path = "archivo/DEE Cognitive System 1.1/entregas/DEE_APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION_ANALISIS.zip"
    report_zip_sha = "1cf0db455e60e7490c5fac59a4ca8a00e01cb0a44f9d4738137d44de14875109"
    _checked(root, report_path, report_zip_sha)
    member = "DEE_APD03_ANALISIS/INFORME_CIENTIFICO_APD03.md"
    member_sha = "9ae5bffc643e21fc64d63cd6bbb90c1124d17b95879028ee7cda0da7f8b1b408"
    with ZipFile(root / report_path) as archive:
        report = archive.read(member)
    assert _digest(report) == member_sha
    sources.append({"path": str(root / report_path), "relative_path": report_path,
                    "sha256": report_zip_sha, "member": member,
                    "member_sha256": member_sha,
                    "pointer": "Sujeto preparación y continuidad; V Dos asociaciones nuevas conservación y continuidad efectiva"})

    lessons = []
    first_uses = []
    for form, name, use_name in [
        ("luma", "014_material.json.gz", "016_material.json.gz"),
        ("nara", "015_material.json.gz", "017_material.json.gz"),
    ]:
        lesson = row(name)
        assert lesson["form"] == form and lesson["lesson_is_external"] is True
        assert len(lesson["requests"]) == 2
        assert all(x["receipt"]["status"] == "applied" for x in lesson["requests"])
        lessons.append({
            "form": form, "transport_id": loaded[name]["id"], "source": name,
            "pointer": "/decoded_result/result/rows/0",
            "input_tick": lesson["input_tick"], "result_tick": lesson["end_tick"],
            "teacher_sign": lesson["teacher_sign"],
            "acquired_hub": {k: lesson["hub"][k] for k in ("site", "direction", "s_reg", "tick")},
            "receipts": [_receipt(x) for x in lesson["requests"]],
        })
        use = row(use_name)
        interaction = use["interaction"]
        reader = interaction["reader"]
        first_uses.append({
            "form": form, "transport_id": loaded[use_name]["id"], "source": use_name,
            "pointer": "/decoded_result/result/rows/0",
            "word_tick": use["word"]["read_tick"],
            "word_sign": use["word"]["reader"]["formed_native_command"],
            "native_function_choice": use["native_function_choice"],
            "interaction_kind": interaction["kind"],
            "interaction_tick": interaction["read_tick"],
            "interaction_response_sign": reader.get("formed_native_command", reader.get("choice")),
            "operator_context": use["operator_supplied_context"],
            "public_datum": use["public_datum"],
        })
    assert [x["teacher_sign"] for x in lessons] == [1, -1]
    assert [x["word_sign"] for x in first_uses] == [1, -1]

    initial = _panel(row("002_material.json.gz"))
    retained = _panel(row("022_material.json.gz"))
    later = _panel(row("047_material.json.gz"))
    old_signs = {x["form"]: x["sign"] for x in initial["forms"]}
    old_ma = {x["context"]: x["sign"] for x in initial["memory_queries"]}
    assert len(old_signs) == 14 and len(old_ma) == 6
    for panel in (retained, later):
        forms = {x["form"]: x["sign"] for x in panel["forms"]}
        ma = {x["context"]: x["sign"] for x in panel["memory_queries"]}
        assert all(forms[k] == v for k, v in old_signs.items())
        assert ma == old_ma and forms["luma"] == 1 and forms["nara"] == -1
        panel["comparison_to_initial"] = {
            "old_forms_same_sign": {"matched": 14, "sampled": 14},
            "MA_queries_same_sign": {"matched": 6, "sampled": 6},
            "new_associations_match_teaching": {"matched": 2, "sampled": 2},
            "not_22_independent_faculties": True,
        }

    goal_row = row("024_material.json.gz")
    query, action = goal_row["opportunities"]
    query_effect = query["environment_effect"]
    action_effect = action["environment_effect"]
    assert query["public_observation"]["second"] is None
    assert query_effect["selected_action"] == "QUERY"
    assert query_effect["revealed_observation"] == {"second": 13}
    assert action["public_observation"]["second"] == 13
    assert action_effect["selected_action"] == "ACT"
    numeric = action["native_numeric"][0]["numeric_reader"]
    committed = action_effect["committed_effect"]
    assert numeric["numeric_result"] == committed["used_value"] == 15
    assert committed["provider_calls"] == {"external": 0, "native": 1}
    artifact = goal_row["operational_environment_state"]["base_state"]["artifacts"][0]
    content = base64.b64decode(artifact["content_base64"], validate=True)
    assert _digest(content) == artifact["sha256"] == committed["artifact"]["sha256"]
    actual_file = json.loads(content.decode("utf-8"))
    assert actual_file["operands"] == [28, 13] and actual_file["value"] == 15

    def opportunity_data(op, index):
        selection = op["native_selection"]
        return {
            "source": "024_material.json.gz", "transport_id": loaded["024_material.json.gz"]["id"],
            "pointer": f"/decoded_result/result/rows/0/opportunities/{index}",
            "public_observation": op["public_observation"],
            "word": op["word"]["form"], "word_tick": op["word"]["read_tick"],
            "word_sign": op["word"]["reader"]["formed_native_command"],
            "sensory_receipts": [_receipt(x) for x in selection["sensory_requests"]],
            "query_tick": selection["query_tick"],
            "selection_tick": selection["reader"]["tick"],
            "physical_action_sign": selection["reader"]["choice"],
            "selected_action": op["environment_effect"]["selected_action"],
            "effect": op["environment_effect"]["environment_effect"],
        }

    query_data = opportunity_data(query, 0)
    query_data["revealed_observation"] = {"second": 13}
    query_data["retention_of_operand_between_steps"] = "Environmental public observation; not proved native numerical memory."
    action_data = opportunity_data(action, 1)
    action_data.update({
        "native_numeric_tick": numeric["tick"], "native_numeric_result": 15,
        "native_numeric_observation": {k: numeric["observation"][k] for k in
                                       ("site", "direction", "s_reg", "tick")},
        "numeric_representation_bias": numeric["representation_bias"],
        "actual_file": actual_file, "actual_file_bytes": len(content),
        "actual_file_sha256": artifact["sha256"],
        "actual_file_relative_path": artifact["relative_path"],
        "provider_calls": committed["provider_calls"],
        "OS_file_writer": "External fixed executor; not DEE writing operating-system bytes.",
        "arithmetic": "Prepared native subtraction with fixed decoding; not a learned arithmetic algorithm.",
    })

    return {
        "schema": "DEE.video.R02.APD03.archived_extract.v1", "sources": sources,
        "life": "APD03_MAIN", "N": 67,
        "parent": {"life": "APD02_MAIN", "tick": 548407},
        "historical_final_tick": 604825,
        "visual_type": "Visualization of authentic archived event records; no invented Cognitive2.0 interface or complete per-tick reconstruction.",
        "events": [
            {"kind": "acquisition_and_first_use", "lessons": lessons, "first_uses": first_uses},
            {"kind": "retention_panel", "source": "022_material.json.gz",
             "transport_id": loaded["022_material.json.gz"]["id"],
             "pointer": "/decoded_result/result/rows/0", **retained},
            {"kind": "information_query", **query_data},
            {"kind": "use_received_information", **action_data},
        ],
        "later_retention": {"source": "047_material.json.gz",
                            "transport_id": loaded["047_material.json.gz"]["id"],
                            "pointer": "/decoded_result/result/rows/0", **later},
        "historical_denominators": recalc["counts"],
        "assistance": "Teaching, opportunities, contexts, routes, supplies, readers and file executor were prepared. Acquired signs select prepared functions; operator initiates opportunities.",
        "new_native_ticks": 0, "native_imported": False, "originals_written": False,
    }
