"""Copy closed CF01 analysis evidence; content deduplication, no native ticks.

Only the five assigned staging components are written. This is not a ZIP sealer
and never reads/writes the engine, active life or native Runtime state.
"""
from pathlib import Path
from collections import Counter
import argparse
import ast
import gzip
import hashlib
import json
import shutil

HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE.parent
ROOT = HERE.parents[3]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf8")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", type=Path, default=CAMPAIGN / "cierre/PAQUETE_ANALISIS")
    args = ap.parse_args()
    stage = args.stage.resolve()
    evidence = ROOT / "evidencia/campanas/CF01_CIERRE_FUNCIONAL"
    stage.mkdir(parents=True, exist_ok=True)
    exported = []
    def copy(source, relative, category):
        target = stage / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        data = source.read_bytes()
        if target.exists() and target.read_bytes() != data:
            raise FileExistsError("Staging member has other bytes: " + str(target))
        if not target.exists():
            shutil.copyfile(source, target)
        exported.append({"category": category, "original": str(source), "bytes": len(data),
                         "sha256": sha(source), "export_relative_path": target.relative_to(stage).as_posix(),
                         "export_sha256": sha(target), "transformation": "exact byte copy"})

    primary_paths = sorted(evidence.glob("*.json.gz"))
    for path in primary_paths:
        # Gzip CRC, UTF8 and JSON are checked. Never discard process failures.
        json.loads(gzip.decompress(path.read_bytes()).decode("utf8"))
        copy(path, Path("EVIDENCIA_CAUSAL") / path.name, "primary")

    archived = evidence / "codigo_ejecutado"
    files = sorted(p for p in archived.rglob("*") if p.is_file())
    members = []; unique = {}
    for path in files:
        digest = sha(path)
        if path.suffix == ".py":
            ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        elif path.suffix == ".json":
            json.loads(path.read_text(encoding="utf-8-sig"))
        blob_rel = Path("CODIGO_EJECUTADO/blobs") / digest
        if digest not in unique:
            copy(path, blob_rel, "archived_source_unique_blob")
            unique[digest] = path.stat().st_size
        else:
            exported.append({"category": "archived_source_deduplicated_reference", "original": str(path),
                             "bytes": path.stat().st_size, "sha256": digest,
                             "export_relative_path": blob_rel.as_posix(), "export_sha256": digest,
                             "transformation": "identical bytes shared by content hash; exact original path recoverable from source index"})
        members.append({"archive_relative_path": path.relative_to(archived).as_posix(), "original": str(path),
                        "sha256": digest, "bytes": path.stat().st_size})
    write_json(stage / "CODIGO_EJECUTADO/INDICE_CONTENIDOS.json",
               {"schema": "CF01.executed_source.content_addressed.v1", "members": members,
                "original_members": len(files), "original_bytes": sum(p.stat().st_size for p in files),
                "unique_blobs": len(unique), "unique_bytes": sum(unique.values()),
                "restoration": "python RECALCULO/materializar_codigo_cf01.py --index CODIGO_EJECUTADO/INDICE_CONTENIDOS.json --out DIRECTORIO_NUEVO",
                "scope": "Exact captured Python/configuration source revisions, no binary engine or WHL."})

    scripts = ("recalcular_todo.py", "materializar_codigo_cf01.py", "recalcular_primarios_cf01.py",
               "recalcular_tarea_cf01.py", "recalcular_contexto_cf01.py", "recalcular_compuesto_cf01.py",
               "recalcular_servicio_v3_cf01.py", "recalcular_post_cal8_cf01.py",
               "recalcular_lectura_cf01.py", "observador_snapshot_existente.py")
    for name in scripts:
        copy(HERE / name, Path("RECALCULO") / name, "recalculation_source")
    references = ("RECALCULO_TAREA_CF01.json", "RECALCULO_CONTEXTO_CF01.json",
                  "RECALCULO_COMPUESTO_ORIGINAL_CF01.json", "RECALCULO_SERVICIO_V3_CF01.json",
                  "RECALCULO_POST_CAL8_CF01.json")
    for name in references:
        source = HERE / name
        target = stage / "RECALCULO/REFERENCIAS_LOCALES" / (name + ".gz")
        target.parent.mkdir(parents=True, exist_ok=True)
        data = source.read_bytes()
        target.write_bytes(gzip.compress(data, compresslevel=9, mtime=0))
        assert gzip.decompress(target.read_bytes()) == data
        exported.append({"category": "local_recalculation_reference", "original": str(source),
                         "bytes": len(data), "sha256": sha(source),
                         "export_relative_path": target.relative_to(stage).as_posix(),
                         "export_bytes": target.stat().st_size, "export_sha256": sha(target),
                         "transformation": "lossless gzip with mtime0; exact decoded original bytes verified",
                         "scope": "May contain previously verified local snapshot details; reduced package recalculation does not pretend to repeat omitted-snapshot checks."})
    full_local = HERE / "LECTURA_PRIMARIOS_CF01_R2.json"
    d = json.loads(full_local.read_text(encoding="utf8"))
    write_json(stage / "RECALCULO/REFERENCIAS_LOCALES/COMPARACION_LOCAL_SNAPSHOTS_CAL36_CAL52.json",
               {"source": str(full_local), "source_sha256": sha(full_local),
                "extraction": {"snapshot_comparisons": d["snapshot_comparisons"]},
                "scope": "Exact JSON subtree of existing local read-only full-snapshot comparison. Raw snapshot bytes omitted; not independently repeatable from this reduced package alone."})

    for path in sorted(CAMPAIGN.iterdir()):
        if path.is_file() and path.suffix in (".json", ".py"):
            copy(path, Path("CONFIGURACIONES") / path.name, "fixed_protocol_or_supervisor")
    notes = ("R9_ANALISIS_ESTADO_Y_RUTAS.json", "FASE_ADMISION_Y_CONTROLES_R9.json",
             "R10_DECISION_PROSPECTIVA.json", "R10_GEOMETRIA_COMPROBACION.json",
             "geometria_cierre_funcional_cf01_r10_codigo_fijado.py", "verificar_receta_r10.py",
             "SINTESIS_MECANISMO_CF01.md", "preparar_staging_analisis_cf01.py")
    for name in notes:
        copy(HERE / name, Path("CONFIGURACIONES/mecanismo") / name, "mechanism_analysis_or_unused_candidate")

    omitted = []
    checkpoints = ROOT / "sistema/estado/checkpoints"
    for path in sorted(checkpoints.glob("CF01*.deetsnap.gz")):
        omitted.append({"category": "complete_operational_snapshot", "original": str(path),
                        "bytes": path.stat().st_size, "sha256": sha(path),
                        "reason": "Retained locally and in operational distribution as selected; analysis ZIP intentionally contains no complete snapshots.",
                        "consequence": "Cannot continue that native life or repeat its complete-state checks from this analysis package alone."})
    for name in ("LECTURA_PRIMARIOS_CF01.json", "LECTURA_PRIMARIOS_CF01_R2.json", "LECTURA_CONTEXTO_CF01.json",
                 "RECALCULO_TAREA_CF01_PY312.json", "RECALCULO_SERVICIO_V3_CF01_PY313.json", "RECALCULO_POST_CAL8_CF01_PY313.json"):
        path = HERE / name
        if path.is_file():
            omitted.append({"category": "redundant_or_deep_recalculation", "original": str(path),
                            "bytes": path.stat().st_size, "sha256": sha(path),
                            "reason": "Deep expanded views or independently identical recalculation. Primary source data and necessary source scripts retained; selected local snapshot comparison exported separately.",
                            "consequence": "No unique primary trial dropped; full-snapshot-only facts remain local-check records, explicitly labelled."})
    index = {"schema": "CF01.analysis.sources_and_omissions.v1", "new_native_ticks": 0,
      "exported_originals": exported, "omitted_local_files": omitted,
      "volumes": {"primary_files": len(primary_paths), "primary_gzip_bytes": sum(p.stat().st_size for p in primary_paths),
                  "primary_expanded_json_bytes": sum(len(gzip.decompress(p.read_bytes())) for p in primary_paths),
                  "archived_code_original_members": len(files), "archived_code_original_bytes": sum(p.stat().st_size for p in files),
                  "archived_code_unique_members": len(unique), "archived_code_unique_bytes": sum(unique.values()),
                  "archived_code_duplicate_bytes_not_repeated": sum(p.stat().st_size for p in files) - sum(unique.values()),
                  "omitted_operational_snapshots": sum(q["category"] == "complete_operational_snapshot" for q in omitted),
                  "omitted_snapshot_encoded_bytes": sum(q["bytes"] for q in omitted if q["category"] == "complete_operational_snapshot")},
      "scope": ["All closed CF01 evidence-root *.json.gz primaries copied byte-for-byte, including failures, silence and rejected inputs.",
                "Exact executed Python sources deduplicated without deleting revision membership; materializer restores every captured source byte.",
                "This essential scientific package is not the operational system and cannot continue omitted snapshots.",
                "No motor, WHL, historical ZIP corpus or duplicate independent-runtime recalculation copies included.",
                "Source-path strings are localizers/provenance only, never import dependencies of the exported recalculation."]}
    write_json(stage / "INDICE_FUENTES_Y_OMISIONES.json", index)
    readme = stage / "RECALCULO/LEER_RECALCULO.md"
    readme.write_text("# Recálculo CF01 sin motor\n\nDesde la raíz extraída, con CPython 3.12 o3.13 y sólo su biblioteca estándar:\n\n`python RECALCULO/recalcular_todo.py --evidence EVIDENCIA_CAUSAL --out SALIDA_RECALCULO`\n\nVerifica hashes de primarios, materializa temporalmente los códigos exactos deduplicados, recalcula inventario, campos RAW, recibos, reservas, controles sociales, panel antiguo, servicio y CAL8. No importa DEE, no genera ticks ni necesita rutas históricas. No ejecuta los códigos nativos archivados; sólo los localiza y verifica.\n\nLas referencias locales comprimidas preservan recálculos anteriores con comprobaciones de snapshots completos. Estos snapshots no viajan: el recálculo exportado no repite ni finge esas comprobaciones. El paquete reducido no permite continuar vidas. El índice identifica todos los snapshots CF01 omitidos y sus hashes.\n\n`materializar_codigo_cf01.py` puede reconstruir las versiones fuente archivadas en un directorio nuevo. R10 es una receta prospectiva NO EJECUTADA; no tiene Runtime, vida ni resultados físicos.\n", encoding="utf8")
    print(json.dumps({"stage": str(stage), "volumes": index["volumes"],
                      "staged_files_now": sum(p.is_file() for p in stage.rglob("*")),
                      "staged_bytes_now": sum(p.stat().st_size for p in stage.rglob("*") if p.is_file()),
                      "new_native_ticks": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
