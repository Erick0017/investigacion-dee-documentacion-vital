from __future__ import annotations

import hashlib
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

TESTS = Path(r"D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests")
DV = TESTS / "documantacion vital"
WORK = DV / "mente basal" / "trabajo_codex" / "MBP4_OBP"
OUT_DOC = WORK / "provenance" / "documents"
OUT_HIST = WORK / "provenance" / "historical"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        xml = archive.read("word/document.xml")
    root = ET.fromstring(xml)
    ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    paragraphs: list[str] = []
    for para in root.iter(ns + "p"):
        text = "".join((node.text or "") for node in para.iter(ns + "t"))
        if text.strip():
            paragraphs.append(text)
    return "\n".join(paragraphs) + "\n"


documents = [
    DV / "DEE thinking" / "DEE_thinking_2_2_0_Libro_Blanco_y_Manual_Tecnico.docx",
    DV / "DEE thinking" / "DEE_thinking_2_2_0_Maestro_Arquitectura_Reconstruccion.docx",
    DV / "FISICA DEE Y PROCESAMIENTO NATIVO" / "Procesamiento_Nativo_DEE_Libro_Manual_v1.docx",
    DV / "FISICA DEE Y PROCESAMIENTO NATIVO" / "DEE_V4_0_1.docx",
    DV / "documentos necesarios para cada chat" / "por separado" / "FORMULAS_Y_CORRESPONDENCIAS_DEE_REINTERPRETACION_HDEE_20260912.docx",
    DV / "documentos necesarios para cada chat" / "por separado" / "DEE_RELACION_UNIVERSAL_Y_PRUEBA_CONSTRUCTIVA_DE_PUENTES_POST_V7_REINTERPRETADA_HDEE_20260912.docx",
]

zip_specs: list[tuple[Path, list[str]]] = [
    (
        DV / "ingenieria" / "INGENIERIA_01_DEE_V27_MEMORIA_APRENDIZAJE_PLASTICIDAD_Y_PROCESAMIENTO_RESULTADOS.zip",
        [
            r"DEE_(CLOSED_LOOP_ADAPTATION|REUSABLE_FEEDBACK_LOOP|POLICY_REGENERATION)\.json$",
            r"REWRITE_WORK/(FREEZE/R0?4|FREEZE/R14|HOLDOUT/R0?4|HOLDOUT/R14|RUNNERS/(reset_apparatus_v1|feedback_apparatus_v1|run_r14_feedback_holdout|run_r04_reset_corrected_holdout))",
            r"RUNNERS/(ing01_apparatus|ing01_common|run_ing01_d05_closed_pipeline)\.py$",
        ],
    ),
    (
        DV / "ingenieria" / "INGENIERIA_02_DEE_V27_PROCESAMIENTO_INTEGRADO_ADAPTACION_Y_AUTONOMIA_RESULTADOS.zip",
        [r"DISCOVERY/ING02_D06_RELATIVE_MEMORY\.json$", r"RUNNERS/run_d06_relative_memory\.py$", r"ING02_(DISTRIBUTED_MEMORY|PLASTICITY_STABILITY_MAP|TEMPORAL_HISTORY_MEMORY)\.json$"],
    ),
    (
        DV / "ingenieria" / "INGENIERIA_05_DEE_V27_INTEGRADA_RESULTADOS.zip",
        [r"SCIENTIFIC_REPORT\.md$", r"NRD06_RECURRENT_PILOT\.json$"],
    ),
    (
        DV / "ingenieria" / "INGENIERIA_06_DEE_V27_CAPACIDAD_ADAPTATIVA_Y_FRONTERA_L4_RESULTADOS.zip",
        [r"(MASTER|SCIENTIFIC|FINAL).*\.(md|json)$", r"FULL.*\.json$", r"OMISSION.*\.json$"],
    ),
    (
        DV / "cores" / "DEE_V27_MASTER_REVALIDATION_CORE01_TO_14_ANTI_OVERFIT_RESULTADOS.zip",
        [r"(MASTER|SUMMARY|FINAL).*\.(md|json)$"],
    ),
    (
        DV / "cores" / "17_DEE_V27_REALITY_UNIFICATION_CROSS_SCALE_PHYSICS_AND_CAPABILITIES_RESULTADOS.zip",
        [r"(MASTER|SUMMARY|FINAL|SCIENTIFIC).*\.(md|json)$"],
    ),
    (
        DV / "procesos" / "PROCESOS_01_DEE_V27_CONTINUIDAD_ENDOGENA_ATLAS_MULTIOBSERVADOR_RESULTADOS.zip",
        [r"(MASTER|SCIENTIFIC|FINAL).*\.(md|json)$"],
    ),
    (
        DV / "procesos" / "PROCESOS_02_DEE_V27_CONTINUIDAD_CAUSAL_POST_TRANSICION_RESULTADOS.zip",
        [r"(MASTER|SCIENTIFIC|FINAL).*\.(md|json)$"],
    ),
]


def main() -> None:
    OUT_DOC.mkdir(parents=True, exist_ok=True)
    OUT_HIST.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, object] = {"schema": "mbp4.directed-source-extraction.v1", "documents": [], "archives": [], "missing": []}
    for path in documents:
        if not path.exists():
            manifest["missing"].append(str(path))
            continue
        target = OUT_DOC / f"{path.stem}.txt"
        target.write_text(docx_text(path), encoding="utf-8")
        manifest["documents"].append({"source": str(path), "source_sha256": sha256(path), "text": target.relative_to(WORK).as_posix(), "characters": target.stat().st_size})
    master = next(TESTS.rglob("ORGANIZACION_BASAL_PERSISTENTE_DOCUMENTO_MAESTRO_V1.docx"), None)
    if master is None:
        manifest["missing"].append("ORGANIZACION_BASAL_PERSISTENTE_DOCUMENTO_MAESTRO_V1.docx")
    else:
        target = OUT_DOC / f"{master.stem}.txt"
        target.write_text(docx_text(master), encoding="utf-8")
        manifest["documents"].append({"source": str(master), "source_sha256": sha256(master), "text": target.relative_to(WORK).as_posix(), "characters": target.stat().st_size})
    for archive_path, patterns in zip_specs:
        if not archive_path.exists():
            manifest["missing"].append(str(archive_path))
            continue
        selected: list[dict[str, object]] = []
        out_root = OUT_HIST / archive_path.stem
        with zipfile.ZipFile(archive_path) as archive:
            for name in archive.namelist():
                if name.endswith("/") or not any(re.search(pattern, name, re.I) for pattern in patterns):
                    continue
                # Bound generic report selection while preserving exact core mechanisms.
                if len(selected) >= 40 and "INGENIERIA_01" not in archive_path.name:
                    break
                data = archive.read(name)
                target = out_root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                selected.append({"member": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
        manifest["archives"].append({"source": str(archive_path), "source_sha256": sha256(archive_path), "selected": selected})
    (WORK / "01_PROVENANCE" / "DIRECTED_SOURCE_MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"documents": len(manifest["documents"]), "archives": len(manifest["archives"]), "missing": manifest["missing"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
