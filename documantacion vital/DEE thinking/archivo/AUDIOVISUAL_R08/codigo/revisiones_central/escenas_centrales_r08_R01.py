"""R08 S01-S04 source adapter: retained fields, reader panels and stage cuts.

No DEE imports, simulation, invented carriers or interpolated coordinates.
model(scene_id, shot_id, progress) returns the root-owned render_r08 contract.
"""
from __future__ import annotations
from copy import deepcopy
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CENTRAL = ROOT / "evidencia_central/CENTRAL_R08_DATOS_EXACTOS.json.gz"
ANCESTOR = ROOT / "evidencia_central/LECTOR_PREVIO_ALT_R08.json.gz"
SHOTLIST = ROOT / "guion_fuente/SHOTLIST_R08.json"
HUB = [44, 7, 47]
INPUT = [47, 7, 47]
LEX_READERS = [[43, 7, 46], [43, 7, 48]]
LEX_BOUNDS = [[40, 4, 43], [48, 10, 51]]
READER_BOUNDS = [[42.6, 6.6, 45.0], [43.4, 7.4, 49.0]]
HUB_BOUNDS = [[43, 6, 46], [45, 8, 48]]
MEMORY_BOUNDS = [[31, 30, 30], [40, 36, 36]]


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def _hash(value):
    return _sha(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode())


@lru_cache(maxsize=1)
def _data():
    return json.loads(gzip.decompress(CENTRAL.read_bytes()))


@lru_cache(maxsize=1)
def _ancestor():
    return json.loads(gzip.decompress(ANCESTOR.read_bytes()))


@lru_cache(maxsize=1)
def _shots():
    raw = json.loads(SHOTLIST.read_text(encoding="utf-8-sig"))
    return {shot["shot_id"]: dict(shot, scene_id=scene["scene_id"])
            for scene in raw["scenes"] for shot in scene["shots"]}


def _inside(site, bounds):
    return all(bounds[0][i] <= site[i] <= bounds[1][i] for i in range(3))


def _crop(points, bounds):
    # Cropping preserves each original integer coordinate and every retained
    # field, including RAW-nonzero/state0. It never moves a source point.
    return [deepcopy(p) for p in points if _inside(p["site"], bounds)]


def _source(path, sha, pointer, **extra):
    return dict(source_path=path, source_sha256=sha, pointer=pointer, **extra)


def _sign(value):
    if value not in (-1, 0, 1):
        raise ValueError("No qualified recorded reader output")
    return {1: "+", -1: "-", 0: "0"}[value]


def _snapshot(branch, tick, label, *, bounds=LEX_BOUNDS, difference=False, teaching=False, input_mark=False):
    key = branch + "_T" + str(tick)
    item = _data()["snapshot_panels"][key]
    panel = {"N": item["N"], "tick": item["tick"], "points": _crop(item["points"], bounds),
             "label": label, "case_id": item["life"], "branch_id": branch,
             "parent_id": "ECI02_ALT_CONSOLIDADA@719846", "evidence_type": "Visualización de registros",
             "source": _source(item["source_path"], item["source_sha256"], "/native_fields",
                               source_container=str(CENTRAL), container_pointer="/snapshot_panels/" + key,
                               RAW_sha256=item["summary"]["RAW_sha256"], clocks_sha256=item["summary"]["clocks_sha256"]),
             "bounds": bounds, "fields_shown": ["RAW nonzero glyph", "state0 wireframe", "direction annotation"],
             "coordinate_scope": "Unchanged source-world coordinates, explicit rectangular crop"}
    if difference:
        changed = [x["site"] for x in _data()["matched_RAW_differences"]["719851"]["points"]]
        panel["difference_sites"] = changed
        panel["direction_sites"] = changed
        for point in panel["points"]:
            if point["site"] in changed:
                point["role"] = "difference"
        panel["matched_comparison"] = {
            "tick": 719851, "EDAD_vs_MINUS_RAW_different_sites": len(changed), "clocks_different_sites": 0,
            "difference_source": str(CENTRAL), "pointer": "/matched_RAW_differences/719851",
            "scope": "Only the exact matched field difference is highlighted; not all temporal changes or a memory map."}
        panel["direction_field_source"] = panel["source"]["container_pointer"] + "/points/*/direction"
    if teaching:
        history = _data()["branches"]["MINUS"]["steps"]["HISTORIA"]
        applied = [r for r in history["row"]["requests"] if r["receipt"]["status"] == "applied"]
        if len(applied) != 3:
            raise ValueError("MINUS teaching admission contract changed")
        panel["teaching_sites"] = [r["site"] for r in applied]
        panel["input_receipts"] = applied
        panel["receipt_annotation_scope"] = "Actual admitted inputs at719848; outlines are annotations, not unretained moving matter."
    if input_mark:
        panel["input_site"] = INPUT
    return panel


def _reader(branch, phase, label, *, show_output=True):
    key = branch + "_" + phase
    item = _data()["reader_panels"][key]
    panel = {"N": item["N"], "tick": item["tick"], "points": _crop(item["points"], READER_BOUNDS),
             "label": label, "case_id": item["life"], "branch_id": branch,
             "parent_id": "ECI02_ALT_CONSOLIDADA@719846", "evidence_type": "Visualización de registros",
             "reader_sites": deepcopy(LEX_READERS), "direction_sites": deepcopy(item["reader_sites"]),
             "input_receipts": item["input_receipts"], "input_tick": item["input_tick"],
             "source": _source(item["source_path"], item["source_sha256"], item["pointer"]),
             "reader_evidence": dict(item["reader_contract"], source_path=item["source_path"],
                 source_sha256=item["source_sha256"], pointer=item["pointer"], recorded_output=item["output"]),
             "bounds": READER_BOUNDS, "fields_shown": ["retained local RAW/state/direction", "qualified reader output"],
             "scope": "All32original reader sites retained in source; visible crop contains the two luma positions. No target supplied."}
    for point in panel["points"]:
        if point["site"] in item["reader_sites"]:
            point["role"] = "reader"
    if show_output:
        panel["output_text"] = _sign(item["output"])
    return panel


def _prior(label, *, show_output=True, input_mark=False):
    item = _ancestor()
    bounds = LEX_BOUNDS if input_mark else READER_BOUNDS
    panel = {"N": item["N"], "tick": item["tick"], "points": _crop(item["points"], bounds),
             "label": label, "case_id": item["life"], "branch_id": "ALT_ANCESTOR",
             "evidence_type": "Visualización de registros", "reader_sites": deepcopy(LEX_READERS),
             "direction_sites": deepcopy(item["reader_sites"]), "bounds": bounds,
             "input_tick": item["input_tick"], "input_receipts": item["input_receipts"],
             "source": _source(item["source_path"], item["source_sha256"], item["pointer"] + "/reader"),
             "reader_evidence": dict(item["reader_contract"], source_path=item["source_path"],
                 source_sha256=item["source_sha256"], pointer=item["pointer"] + "/reader", recorded_output=item["output"]),
             "genealogy_scope": item["scope"], "fields_shown": ["retained earlier luma reader observations"]}
    for point in panel["points"]:
        if point["site"] in item["reader_sites"]:
            point["role"] = "reader"
    if show_output:
        panel["output_text"] = _sign(item["output"])
    if input_mark:
        panel["input_site"] = item["input_site"]
    return panel


def _native_interaction(branch, phase, label):
    step = _data()["branches"][branch]["steps"][phase]
    row = step["row"]["interaction"]
    reader = row["reader"]
    points = reader.get("panel", reader.get("observations"))
    output = reader.get("formed_native_command", reader.get("choice"))
    candidates = reader.get("candidates", [])
    sites = [c.get("site", c.get("observation", {}).get("site")) for c in candidates]
    is_memory = row["kind"] == "query"
    bounds = MEMORY_BOUNDS if is_memory else [[10, 11, 10], [20, 21, 20]]
    pointer = "/request/result/result/rows/0/interaction/reader"
    panel = {"N": 67, "tick": row["read_tick"], "points": _crop(points, bounds), "label": label,
             "case_id": step["row"].get("life", "ECI02_L_" + branch), "branch_id": branch,
             "evidence_type": "Visualización de registros", "reader_sites": sites, "direction_sites": sites,
             "source": _source(step["source_path"], step["source_sha256"], pointer),
             "reader_evidence": dict(source_path=step["source_path"], source_sha256=step["source_sha256"],
                 pointer=pointer, recorded_output=output, reader_contract=reader),
             "output_text": _sign(output), "bounds": bounds, "input_receipts": row["requests"],
             "scope": row.get("selection_scope", row.get("scope")),
             "fields_shown": ["actual selected native function's own local reader fields"]}
    return panel


def retention_panels():
    """Exact MINUS nara/MA readers for S06; these occurred before publication."""
    result = {}
    for name, phase in [("nara", "RET_NARA"), ("MA", "RET_MA")]:
        step = _data()["branches"]["MINUS"]["steps"][phase]
        row = step["row"]
        pointer = "/request/result/result/rows/0"
        if name == "MA":
            row = row["result"]["rows"][0]
            pointer += "/result/rows/0"
        reader = row["reader"]
        sites = [x["site"] for x in reader["candidates"]]
        bounds = MEMORY_BOUNDS if name == "MA" else [[44, 0, 44], [51, 7, 51]]
        result[name] = {"N": 67, "tick": row["read_tick"], "label": name,
            "points": _crop(reader["panel"], bounds), "reader_sites": sites, "direction_sites": sites,
            "output_text": _sign(reader["formed_native_command"]), "bounds": bounds,
            "case_id": "ECI02_L_MINUS", "branch_id": "MINUS", "evidence_type": "Visualización de registros",
            "source": _source(step["source_path"], step["source_sha256"], pointer + "/reader"),
            "reader_evidence": dict(source_path=step["source_path"], source_sha256=step["source_sha256"],
                pointer=pointer + "/reader", recorded_output=reader["formed_native_command"]),
            "input_receipts": row["requests"], "scope": "Retained MINUS use before export; not a post-reopening nara claim."}
    return result


def model(scene_id, shot_id, progress):
    progress = float(progress)
    if not 0 <= progress <= 1:
        raise ValueError("progress must be in0..1")
    shot = _shots()[shot_id]
    if shot["scene_id"] != scene_id or scene_id not in {"S01", "S02", "S03", "S04"}:
        raise ValueError("Only the literal S01-S04 shot IDs are supported")
    result = {"scene_id": scene_id, "shot_id": shot_id, "progress": progress,
              "labels_exact": shot["labels_exact"], "anchor_exact": shot["anchor_exact"],
              "evidence_type": "Visualización de registros", "panels": [],
              "replay_status": "No replay; retained exact snapshots, local panels and admitted-input receipts only",
              "source_shotlist": str(SHOTLIST), "source_shotlist_sha256": _sha(SHOTLIST.read_bytes()),
              "limitations": ["No inferred transport or interpolated physical field.",
                  "Camera/crop/contours/arrows/labels are editorial; arrows annotate a retained direction field."]}
    if shot_id == "S01_P01":
        result.update(title="MISMA SEÑAL: LUMA", bounds=READER_BOUNDS,
            panels=[_prior("ANTES +"), _reader("MINUS", "USO_COMUN", "DESPUÉS -")],
            editorial_teaser=True)
    elif shot_id == "S01_P02":
        tick = 719846 if progress < .5 else 719851
        result.update(title="ENTRE AMBOS: UNA EXPERIENCIA", bounds=LEX_BOUNDS,
            panels=[_snapshot("MINUS", tick, "", teaching=True)],
            evidence_type="Reconstrucción de etapas", stage_jump=True)
    elif shot_id == "S01_P03":
        tick = 719846 if progress < .5 else 719851
        result.update(title="DEE: MUNDO COMPUTACIONAL", bounds=HUB_BOUNDS,
            panels=[_snapshot("MINUS", tick, "QUÉ CAMBIÓ", bounds=HUB_BOUNDS, difference=True)],
            evidence_type="Reconstrucción de etapas", stage_jump=True)
    elif shot_id == "S02_P01":
        result.update(title="LUMA: SEÑAL DE PRUEBA", bounds=LEX_BOUNDS,
            panels=[_snapshot("MINUS", 719846, "ENTRADA PREPARADA", input_mark=True)])
    elif shot_id == "S02_P02":
        result.update(title="ENTRADA PREPARADA", bounds=LEX_BOUNDS,
            panels=[_prior("ESTADOS DEL MUNDO", show_output=progress >= .6, input_mark=True)])
    elif shot_id == "S02_P03":
        if progress < .4:
            result.update(title="NUEVA EXPERIENCIA", bounds=LEX_BOUNDS,
                panels=[_snapshot("MINUS", 719846, "", teaching=True)],
                evidence_type="Reconstrucción de etapas", stage_jump=True)
        else:
            result.update(title="NUEVA EXPERIENCIA", bounds=HUB_BOUNDS,
                panels=[_snapshot("MINUS", 719846, "ESTADO ANTERIOR", bounds=HUB_BOUNDS, difference=True),
                        _snapshot("MINUS", 719851, "ESTADO DESPUÉS", bounds=HUB_BOUNDS, difference=True)],
                evidence_type="Reconstrucción de etapas", stage_jump=True)
    elif shot_id == "S02_P04":
        if progress < .5:
            panel = _snapshot("MINUS", 719851, "MISMA SEÑAL", input_mark=True)
            panel["input_receipts"] = _data()["reader_panels"]["MINUS_USO_COMUN"]["input_receipts"]
            result.update(title="MISMA SEÑAL", panels=[panel], bounds=LEX_BOUNDS,
                evidence_type="Reconstrucción de etapas", stage_jump=True)
        else:
            result.update(title="MISMA SEÑAL", bounds=READER_BOUNDS,
                panels=[_reader("MINUS", "USO_COMUN", "OTRA RESPUESTA -")])
    elif shot_id == "S02_P05":
        result.update(title="DOS SALIDAS DISTINTAS", bounds=READER_BOUNDS,
            panels=[_prior("ANTES +"), _reader("MINUS", "USO_COMUN", "DESPUÉS -")])
    elif shot_id == "S03_P01":
        result.update(title="DOS COPIAS", bounds=HUB_BOUNDS,
            panels=[_snapshot(b, 719846, "MISMO ESTADO INICIAL", bounds=HUB_BOUNDS) for b in ["EDAD", "MINUS"]])
    elif shot_id == "S03_P02":
        tick = 719846 if progress < .5 else 719851
        result.update(title="DOS COPIAS", bounds=HUB_BOUNDS,
            panels=[_snapshot("EDAD", tick, "SIN NUEVA ENSEÑANZA", bounds=HUB_BOUNDS, difference=True),
                    _snapshot("MINUS", tick, "CON NUEVA ENSEÑANZA", bounds=HUB_BOUNDS, difference=True)],
            evidence_type="Reconstrucción de etapas", stage_jump=True)
    elif shot_id == "S03_P03":
        result.update(title="MISMA CONSULTA" if progress < .5 else "RESPUESTAS DISTINTAS", bounds=READER_BOUNDS,
            panels=[_reader("EDAD", "USO_COMUN", "SIN NUEVA ENSEÑANZA"),
                    _reader("MINUS", "USO_COMUN", "CON NUEVA ENSEÑANZA")])
    elif shot_id == "S03_P04":
        result.update(title="COMPROBACIÓN POSTERIOR", bounds=READER_BOUNDS,
            panels=[_reader("EDAD", "RESERVA", "SIN REPETIR LA ENSEÑANZA"),
                    _reader("MINUS", "RESERVA", "SIN REPETIR LA ENSEÑANZA")],
            evidence_type="Reconstrucción de etapas", stage_jump=True,
            temporal_scope={"EDAD_read_tick": 720053, "MINUS_read_tick": 720120,
                "idle_ticks_per_branch": 67, "same_absolute_tick_comparison": False,
                "reason": "Each reserved use follows its own67tick idle; selected native protocols have different durations."})
    elif shot_id == "S04_P01":
        result.update(title="ENLACE EXTERNO PREPARADO", bounds=READER_BOUNDS,
            panels=[_reader("MINUS", "USO_COMUN", "DENTRO DE DEE: RESPUESTA")],
            scheme={"kind": "bridge", "active": 1}, evidence_type="Registros y esquema")
    elif shot_id == "S04_P02":
        branch = "EDAD" if progress < .5 else "MINUS"
        panel = _reader(branch, "USO_COMUN", "DENTRO DE DEE: RESPUESTA")
        actual_output = panel["reader_evidence"]["recorded_output"]
        result.update(title="ENLACE PREPARADO", bounds=READER_BOUNDS, panels=[panel],
            scheme={"kind": "bridge", "active": 0 if actual_output == 1 else 1},
            evidence_type="Registros y esquema")
    elif shot_id == "S04_P03":
        panel = (_reader("MINUS", "USO_COMUN", "CAMBIÓ LA SALIDA") if progress < .5 else
                 _native_interaction("MINUS", "USO_COMUN", "SE UTILIZÓ OTRO ACCESO"))
        result.update(title="OTRO ACCESO", panels=[panel], bounds=panel["bounds"],
            scheme={"kind": "bridge", "active": 1}, evidence_type="Registros y esquema", stage_jump=True)
    elif shot_id == "S04_P04":
        result.update(title="DEE TRANSFORMA" if progress < .5 else "EL ENLACE UTILIZA", bounds=MEMORY_BOUNDS,
            panels=[_native_interaction("MINUS", "USO_COMUN", "")],
            scheme={"kind": "bridge", "active": 1}, evidence_type="Registros y esquema")
    else:
        raise KeyError(shot_id)
    if result.get("scheme", {}).get("kind") == "bridge":
        result["scheme"].update(evidence_type="Esquema explicativo", topology="fixed before the selected response",
            source=_data()["routing"], scope="Prepared external if/else, not a material link or acquired autonomous routing")
        result["zone_evidence"] = {"left": "A / retained reader", "right": "C / prepared external bridge"}
    result["source_refs"] = [p["source"] for p in result["panels"]]
    result["source_data_hash"] = _hash({"panels": result["panels"], "scheme": result.get("scheme"),
        "data_source_sha256": _sha(CENTRAL.read_bytes()), "ancestral_source_sha256": _sha(ANCESTOR.read_bytes())})
    return result
