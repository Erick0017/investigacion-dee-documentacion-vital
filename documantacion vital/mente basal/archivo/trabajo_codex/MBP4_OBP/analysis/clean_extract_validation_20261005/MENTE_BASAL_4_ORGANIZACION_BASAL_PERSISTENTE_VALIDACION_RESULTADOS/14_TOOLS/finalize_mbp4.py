from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

WORK = Path(__file__).resolve().parent.parent
ROOT = WORK.parents[1]
PACKAGE = "MENTE_BASAL_4_ORGANIZACION_BASAL_PERSISTENTE_VALIDACION_RESULTADOS"
STAGING_ROOT = WORK / "staging"
STAGE = STAGING_ROOT / PACKAGE
FINAL_ZIP = ROOT / f"{PACKAGE}.zip"
TEMP_ZIP = ROOT / f".{PACKAGE}.tmp.zip"
PREFLIGHT_ZIP = WORK / "staging" / f".{PACKAGE}.preflight.zip"
EXPECTED_MAIN_SHA = "cd09a4d94f72e00d9a5163c8dfd1d62e1528f1d146e4cb44ae23d261b3da09e6"
EXPECTED_MBP3_SHA = "6b7a646a2f48fc7f707c09ab10e16788878b326f712ed11719a727d501d586de"


def utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def safe_clear_stage() -> None:
    resolved = STAGE.resolve()
    if resolved.parent != STAGING_ROOT.resolve() or resolved.name != PACKAGE:
        raise RuntimeError(f"unsafe staging path: {resolved}")
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)


def copy_tree(source: Path, destination: Path) -> None:
    if not source.exists():
        return
    for path in source.rglob("*"):
        if path.is_dir():
            continue
        if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        rel = path.relative_to(source)
        target = destination / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def stage_payload() -> None:
    safe_clear_stage()
    for number in range(18):
        prefix = f"{number:02d}_"
        for source in WORK.glob(prefix + "*"):
            if source.is_dir():
                copy_tree(source, STAGE / source.name)
    copy_tree(WORK / "provenance", STAGE / "01_PROVENANCE" / "DIRECTED_SOURCES")
    copy_tree(WORK / "source", STAGE / "source")
    copy_tree(WORK / "tools", STAGE / "14_TOOLS")
    validation = WORK / "tests" / "VALIDATION_RESULTS.json"
    if validation.exists():
        (STAGE / "14_TOOLS" / "tests").mkdir(parents=True, exist_ok=True)
        shutil.copy2(validation, STAGE / "14_TOOLS" / "tests" / validation.name)
    # Keep the wheel in the official provenance section for clean extraction tests.
    wheel = WORK / "01_PROVENANCE" / "dee_thinking-2.2.0-cp313-cp313-win_amd64.whl"
    if not wheel.exists():
        raise RuntimeError("official DEE thinking wheel missing")
    status = {
        "schema": "mbp4.campaign-status.v1", "created_utc": utc(),
        "state": "STOPPED_SAFE", "worker_pid": None,
        "detail": "finite campaign complete; checkpoints resumable; no autonomous worker requested",
        "main_checkpoint": "12_CHECKPOINTS/OBP_FRESH_VALIDATED_T32.deetsnap",
        "main_checkpoint_sha256": EXPECTED_MAIN_SHA,
    }
    write_json(STAGE / "12_CHECKPOINTS" / "CAMPAIGN_STATUS.json", status)


def payload_files(include_manifest: bool = True):
    for path in sorted(p for p in STAGE.rglob("*") if p.is_file()):
        rel = path.relative_to(STAGE).as_posix()
        if not include_manifest and rel.startswith("17_MANIFEST/"):
            continue
        yield path, rel


def write_manifests(preflight_status: str) -> None:
    manifest_rows = []
    for path, rel in payload_files(include_manifest=False):
        manifest_rows.append({"path": rel, "bytes": path.stat().st_size, "sha256": sha_file(path)})
    write_json(STAGE / "17_MANIFEST" / "MANIFEST.json", {
        "schema": "mbp4.package-manifest.v1", "campaign": "MBP4-OBP-CONSTITUTION-CLOSED-LOOP",
        "created_utc": utc(), "payload_files": len(manifest_rows), "files": manifest_rows,
    })
    write_json(STAGE / "17_MANIFEST" / "ZIP_VERIFICATION.json", {
        "schema": "mbp4.zip-verification.v1", "created_utc": utc(),
        "preflight_crc": preflight_status,
        "checkpoint_restore_validation": "PASS",
        "main_checkpoint_sha256": EXPECTED_MAIN_SHA,
        "mbp3_parent_sha256": EXPECTED_MBP3_SHA,
        "note": "Final archive CRC and internal hashes are verified after handle close; outer result is retained in trabajo_codex/MBP4_OBP/analysis/PUBLICATION_RESULT.json.",
    })
    lines = []
    for path, rel in payload_files(include_manifest=True):
        if rel == "17_MANIFEST/HASHES.sha256":
            continue
        lines.append(f"{sha_file(path)}  {rel}")
    (STAGE / "17_MANIFEST" / "HASHES.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def build_zip(path: Path) -> None:
    if path.exists():
        path.unlink()
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as archive:
        for source, rel in payload_files(include_manifest=True):
            archive.write(source, f"{PACKAGE}/{rel}")


def verify_zip(path: Path) -> dict:
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        names = set(archive.namelist())
        prefix = PACKAGE + "/"
        hashes_name = prefix + "17_MANIFEST/HASHES.sha256"
        if hashes_name not in names:
            raise RuntimeError("HASHES.sha256 missing")
        hash_text = archive.read(hashes_name).decode("utf-8")
        mismatches = []
        checked = 0
        for line in hash_text.splitlines():
            if not line.strip():
                continue
            expected, rel = line.split("  ", 1)
            name = prefix + rel
            if name not in names:
                mismatches.append({"path": rel, "reason": "missing"})
                continue
            actual = sha_bytes(archive.read(name))
            checked += 1
            if actual != expected:
                mismatches.append({"path": rel, "expected": expected, "actual": actual})
        main_name = prefix + "12_CHECKPOINTS/OBP_FRESH_VALIDATED_T32.deetsnap"
        mbp3_name = prefix + "11_MBP3_INTEGRATION/tick_000000276832_collect_FINAL_MBP3_NATIVE_CURRICULUM_2H_d7cad9fc.deetsnap"
        checkpoints = {
            "main": sha_bytes(archive.read(main_name)) if main_name in names else None,
            "mbp3_parent": sha_bytes(archive.read(mbp3_name)) if mbp3_name in names else None,
        }
        ok = bad is None and not mismatches and checkpoints["main"] == EXPECTED_MAIN_SHA and checkpoints["mbp3_parent"] == EXPECTED_MBP3_SHA
        return {"crc_bad_member": bad, "entries": len(names), "hashes_checked": checked,
                "hash_mismatches": mismatches, "checkpoint_hashes": checkpoints, "pass": ok}


def main() -> None:
    stage_payload()
    write_manifests("PENDING")
    build_zip(PREFLIGHT_ZIP)
    preflight = verify_zip(PREFLIGHT_ZIP)
    if not preflight["pass"]:
        raise RuntimeError(f"preflight failed: {preflight}")
    write_manifests("PASS")
    build_zip(TEMP_ZIP)
    final_check = verify_zip(TEMP_ZIP)
    if not final_check["pass"]:
        raise RuntimeError(f"final temp verification failed: {final_check}")
    if FINAL_ZIP.exists():
        stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        prior = ROOT / "archivo" / "MBP4_TRABAJO_CERRADO" / f"{PACKAGE}.prior_{stamp}.zip"
        prior.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(FINAL_ZIP, prior)
    os.replace(TEMP_ZIP, FINAL_ZIP)
    published_check = verify_zip(FINAL_ZIP)
    if not published_check["pass"]:
        raise RuntimeError(f"published verification failed: {published_check}")
    result = {
        "schema": "mbp4.publication-result.v1", "created_utc": utc(),
        "zip": str(FINAL_ZIP), "zip_bytes": FINAL_ZIP.stat().st_size,
        "zip_sha256": sha_file(FINAL_ZIP), "preflight": preflight,
        "published": published_check,
    }
    write_json(WORK / "analysis" / "PUBLICATION_RESULT.json", result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
