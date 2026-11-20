from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = HERE.parent
CONT = WORK / "18_NATIVE_PERSISTENT_LEARNING"
ROOT = WORK.parents[1]
OFFICIAL_NAME = "MENTE_BASAL_4_ORGANIZACION_BASAL_PERSISTENTE_VALIDACION_RESULTADOS.zip"
OFFICIAL = ROOT / OFFICIAL_NAME
PREFIX = "MENTE_BASAL_4_ORGANIZACION_BASAL_PERSISTENTE_VALIDACION_RESULTADOS"
PARENT_SHA = "b0fad297af0ffeeb9718a70714eaa3dd3203768d81c322508968fd73af2f1691"
BACKUP = ROOT / "archivo" / "MBP4_TRABAJO_CERRADO" / "parent_packages" / f"{OFFICIAL_NAME}.parent_{PARENT_SHA[:16]}"
STAGING = WORK / "staging" / "continuation"
PREFLIGHT = STAGING / "MBP4_CONTINUATION_PREFLIGHT.zip"
TEMP_FINAL = STAGING / (OFFICIAL_NAME + ".tmp")


def utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def bytes_sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def section_files(include_verification: bool = True) -> list[Path]:
    files = []
    for path in CONT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(CONT).as_posix()
        if rel == "MANIFEST_APPEND/HASHES.sha256":
            continue
        if not include_verification and rel == "MANIFEST_APPEND/ZIP_VERIFICATION.json":
            continue
        files.append(path)
    return sorted(files, key=lambda p: p.relative_to(CONT).as_posix())


def build_section_manifests() -> None:
    manifest_path = CONT / "MANIFEST_APPEND" / "MANIFEST.json"
    hashes_path = CONT / "MANIFEST_APPEND" / "HASHES.sha256"
    verification_path = CONT / "MANIFEST_APPEND" / "ZIP_VERIFICATION.json"
    for path in (manifest_path, hashes_path, verification_path):
        path.unlink(missing_ok=True)

    entries = []
    for path in section_files(include_verification=False):
        entries.append({"path": path.relative_to(CONT).as_posix(),
                        "bytes": path.stat().st_size, "sha256": sha(path)})
    write_json(manifest_path, {
        "schema": "mbp4.native-learning-manifest.v1", "created_utc": utc(),
        "parent_package_sha256": PARENT_SHA, "section": "18_NATIVE_PERSISTENT_LEARNING",
        "file_count_before_hash_and_verification": len(entries), "files": entries})
    hash_lines = []
    for path in section_files(include_verification=False):
        rel = path.relative_to(CONT).as_posix()
        hash_lines.append(f"{sha(path)}  {rel}")
    hashes_path.write_text("\n".join(hash_lines) + "\n", encoding="ascii")
    write_json(verification_path, {
        "schema": "mbp4.continuation-zip-verification.v1", "created_utc": utc(),
        "pass": None, "phase": "preflight pending", "parent_sha256": PARENT_SHA,
        "checks": ["CRC", "parent entry byte identity", "section HASHES.sha256", "final checkpoint SHA-256"]})


def choose_parent() -> Path:
    if OFFICIAL.exists() and sha(OFFICIAL) == PARENT_SHA:
        BACKUP.parent.mkdir(parents=True, exist_ok=True)
        if not BACKUP.exists():
            shutil.copy2(OFFICIAL, BACKUP)
        if sha(BACKUP) != PARENT_SHA:
            raise RuntimeError("archived parent copy hash mismatch")
        return BACKUP
    if BACKUP.exists() and sha(BACKUP) == PARENT_SHA:
        return BACKUP
    raise RuntimeError("verified MBP4 parent package unavailable")


def build_zip(parent: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.unlink(missing_ok=True)
    with zipfile.ZipFile(parent, "r") as zin, zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zout:
        for info in zin.infolist():
            if info.filename.startswith(PREFIX + "/18_NATIVE_PERSISTENT_LEARNING/"):
                continue
            data = zin.read(info.filename)
            cloned = zipfile.ZipInfo(info.filename, info.date_time)
            cloned.comment = info.comment
            cloned.extra = info.extra
            cloned.internal_attr = info.internal_attr
            cloned.external_attr = info.external_attr
            cloned.create_system = info.create_system
            cloned.flag_bits = info.flag_bits
            cloned.compress_type = zipfile.ZIP_DEFLATED
            zout.writestr(cloned, data)
        for path in section_files(include_verification=True):
            arc = f"{PREFIX}/18_NATIVE_PERSISTENT_LEARNING/{path.relative_to(CONT).as_posix()}"
            zout.write(path, arcname=arc)


def parse_hashes() -> dict[str, str]:
    result = {}
    for line in (CONT / "MANIFEST_APPEND" / "HASHES.sha256").read_text(encoding="ascii").splitlines():
        digest, rel = line.split("  ", 1)
        result[rel] = digest
    return result


def verify_zip(parent: Path, package: Path) -> dict:
    expected = parse_hashes()
    mismatches = []
    parent_mismatches = []
    with zipfile.ZipFile(parent, "r") as pz, zipfile.ZipFile(package, "r") as zf:
        bad_crc = zf.testzip()
        parent_names = [x.filename for x in pz.infolist() if not x.filename.startswith(PREFIX + "/18_NATIVE_PERSISTENT_LEARNING/")]
        for name in parent_names:
            if bytes_sha(pz.read(name)) != bytes_sha(zf.read(name)):
                parent_mismatches.append(name)
        for rel, digest in expected.items():
            name = f"{PREFIX}/18_NATIVE_PERSISTENT_LEARNING/{rel}"
            if name not in zf.namelist() or bytes_sha(zf.read(name)) != digest:
                mismatches.append(rel)
        final_name = f"{PREFIX}/18_NATIVE_PERSISTENT_LEARNING/CHECKPOINTS/MBP4_NATIVE_MAIN_FINAL.deetsnap"
        final_sha = bytes_sha(zf.read(final_name))
        return {"pass": bad_crc is None and not parent_mismatches and not mismatches and
                        final_sha == "cba13f5fa58b2fef02a1cf4c170ab1555efde4467341ba4a99dc6f2046cd7cee",
                "crc_bad_member": bad_crc, "entries": len(zf.infolist()),
                "parent_entries_checked": len(parent_names), "parent_mismatches": parent_mismatches,
                "section_hashes_checked": len(expected), "section_hash_mismatches": mismatches,
                "final_checkpoint_sha256": final_sha}


def main() -> None:
    parent = choose_parent()
    build_section_manifests()
    build_zip(parent, PREFLIGHT)
    preflight = verify_zip(parent, PREFLIGHT)
    if not preflight["pass"]:
        raise RuntimeError(json.dumps(preflight, sort_keys=True))
    write_json(CONT / "MANIFEST_APPEND" / "ZIP_VERIFICATION.json", {
        "schema": "mbp4.continuation-zip-verification.v1", "created_utc": utc(),
        "pass": True, "phase": "preflight sealed file set",
        "preflight_zip_sha256": sha(PREFLIGHT), "parent_sha256": PARENT_SHA,
        "result": preflight,
        "note": "The official package is rebuilt from the same parent and section file set, then verified again externally."})
    build_zip(parent, TEMP_FINAL)
    final_check = verify_zip(parent, TEMP_FINAL)
    if not final_check["pass"]:
        raise RuntimeError(json.dumps(final_check, sort_keys=True))
    os.replace(TEMP_FINAL, OFFICIAL)
    published_check = verify_zip(parent, OFFICIAL)
    if not published_check["pass"]:
        raise RuntimeError(json.dumps(published_check, sort_keys=True))
    result = {
        "schema": "mbp4.continuation-publication.v1", "created_utc": utc(),
        "parent_backup": str(BACKUP), "parent_sha256": sha(parent),
        "official": str(OFFICIAL), "official_sha256": sha(OFFICIAL),
        "bytes": OFFICIAL.stat().st_size, "verification": published_check,
    }
    write_json(WORK / "analysis" / "CONTINUATION_PUBLICATION_RESULT.json", result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
