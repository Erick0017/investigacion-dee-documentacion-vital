from __future__ import annotations

import hashlib
import json
import os
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import dee_thinking as dee


SECTION = Path(__file__).resolve().parents[1]
WORK = SECTION.parent
ROOT = WORK.parents[1]
CANONICAL = ROOT / "MENTE_BASAL_4_ORGANIZACION_BASAL_PERSISTENTE_VALIDACION_RESULTADOS.zip"
WRAPPER = "MENTE_BASAL_4_ORGANIZACION_BASAL_PERSISTENTE_VALIDACION_RESULTADOS"
SECTION_PREFIX = f"{WRAPPER}/19_SHARED_PLASTIC_LANDSCAPE_MULTI_ENTITY/"
PARENT_SHA = "dfb25c87b14eeadb63a754583d3c9ced9d031a14098c8f5a5fa95f9ab8c025ee"
BACKUP_DIR = ROOT / "archivo" / "MBP4_TRABAJO_CERRADO" / "parent_packages"
BACKUP = BACKUP_DIR / f"{CANONICAL.name}.parent_{PARENT_SHA[:16]}"
TEMP = WORK / f".{CANONICAL.name}.section19.tmp"


def utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def payload_files() -> list[Path]:
    excluded = {"MANIFEST_APPEND.json", "HASHES.sha256", "ZIP_VERIFICATION.json"}
    return sorted(
        (p for p in SECTION.rglob("*") if p.is_file() and p.name not in excluded),
        key=lambda p: p.relative_to(SECTION).as_posix(),
    )


def entry_digest(path: Path) -> dict[str, object]:
    return {"path": path.relative_to(SECTION).as_posix(), "bytes": path.stat().st_size,
            "sha256": sha256(path)}


def zip_payload_digest(path: Path, include_section19: bool) -> tuple[str, dict[str, str]]:
    rows: dict[str, str] = {}
    with zipfile.ZipFile(path, "r") as zf:
        for info in zf.infolist():
            name = info.filename
            if info.is_dir():
                continue
            is_section19 = name.startswith(SECTION_PREFIX)
            if is_section19 != include_section19:
                continue
            rows[name] = sha256_bytes(zf.read(name))
    h = hashlib.sha256()
    for name in sorted(rows):
        h.update(name.encode("utf-8"))
        h.update(b"\0")
        h.update(rows[name].encode("ascii"))
        h.update(b"\n")
    return h.hexdigest(), rows


def copy_parent_entry(dst: zipfile.ZipFile, src: zipfile.ZipFile, info: zipfile.ZipInfo) -> None:
    clone = zipfile.ZipInfo(info.filename, info.date_time)
    clone.compress_type = info.compress_type
    clone.comment = info.comment
    clone.extra = info.extra
    clone.internal_attr = info.internal_attr
    clone.external_attr = info.external_attr
    clone.create_system = info.create_system
    clone.flag_bits = info.flag_bits
    if info.is_dir():
        dst.writestr(clone, b"")
    else:
        dst.writestr(clone, src.read(info.filename))


def verify_snapshots() -> list[dict[str, object]]:
    required = [
        "FRESH_SHARED_T0.deetsnap", "FRESH_SHARED_VALIDATED.deetsnap",
        "POST_ACQUISITION.deetsnap", "POST_INTERFERENCE.deetsnap",
        "POST_RELEARNING.deetsnap", "B1_B2_PRE_CONTACT.deetsnap",
        "B1_B2_POST_CONTACT.deetsnap", "MAIN_FINAL.deetsnap",
    ]
    rows = []
    for name in required:
        path = SECTION / "CHECKPOINTS" / name
        runtime = dee.Runtime.load_snapshot(str(path))
        rows.append({"path": f"CHECKPOINTS/{name}", "tick": int(runtime.current_tick),
                     "dimension": int(runtime.dimension), "sha256": sha256(path),
                     "load_pass": True})
    return rows


def main() -> None:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    if not BACKUP.exists() and sha256(CANONICAL) == PARENT_SHA:
        shutil.copy2(CANONICAL, BACKUP)
    if sha256(BACKUP) != PARENT_SHA:
        raise RuntimeError("parent backup hash mismatch")

    snapshots = verify_snapshots()
    files = payload_files()
    manifest_dir = SECTION / "MANIFEST_APPEND"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema": "mbp4.sp.manifest-append.v1", "generated_utc": utc(),
        "parent_package": {"name": CANONICAL.name, "sha256": PARENT_SHA},
        "section": "19_SHARED_PLASTIC_LANDSCAPE_MULTI_ENTITY",
        "files": [entry_digest(p) for p in files],
        "required_snapshots": snapshots,
        "highest_gate": "MBP4-SP9", "sp10": "FAIL_NON_ADDITIVE_FUTURE_NOT_DEMONSTRATED",
        "self_hash_policy": "manifest/hash/verification files are excluded from their own recursive digest",
    }
    write_json(manifest_dir / "MANIFEST_APPEND.json", manifest)

    hash_files = payload_files() + [manifest_dir / "MANIFEST_APPEND.json"]
    hashes = "".join(f"{sha256(p)}  {p.relative_to(SECTION).as_posix()}\n" for p in sorted(hash_files))
    (manifest_dir / "HASHES.sha256").write_text(hashes, encoding="utf-8")
    parent_payload_digest, parent_entries = zip_payload_digest(BACKUP, False)
    verification = {
        "schema": "mbp4.sp.zip-verification.v1", "verified_utc": utc(),
        "parent_zip_sha256": PARENT_SHA, "parent_non_section19_entries": len(parent_entries),
        "parent_payload_digest": parent_payload_digest,
        "required_snapshots": snapshots, "snapshot_restore_pass": all(x["load_pass"] for x in snapshots),
        "publication_protocol": "build temporary ZIP, close, CRC-test, compare sections 00-18 by entry content, atomic replace, reopen and CRC-test",
        "final_zip_sha256_policy": "reported externally after closure; cannot be embedded self-referentially",
    }
    write_json(manifest_dir / "ZIP_VERIFICATION.json", verification)

    if TEMP.exists():
        TEMP.unlink()
    with zipfile.ZipFile(BACKUP, "r") as src, zipfile.ZipFile(TEMP, "w", allowZip64=True) as dst:
        for info in src.infolist():
            if info.filename.startswith(SECTION_PREFIX):
                raise RuntimeError("parent unexpectedly contains section 19")
            copy_parent_entry(dst, src, info)
        for path in sorted((p for p in SECTION.rglob("*") if p.is_file()),
                           key=lambda p: p.relative_to(SECTION).as_posix()):
            arc = SECTION_PREFIX + path.relative_to(SECTION).as_posix()
            dst.write(path, arc, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

    with zipfile.ZipFile(TEMP, "r") as zf:
        crc_error = zf.testzip()
        names = set(zf.namelist())
    if crc_error is not None:
        raise RuntimeError(f"temporary ZIP CRC failure: {crc_error}")
    required_entries = {
        SECTION_PREFIX + "MASTER_REPORT.md",
        SECTION_PREFIX + "CHECKPOINTS/MAIN_FINAL.deetsnap",
        SECTION_PREFIX + "MANIFEST_APPEND/MANIFEST_APPEND.json",
        SECTION_PREFIX + "MANIFEST_APPEND/HASHES.sha256",
        SECTION_PREFIX + "MANIFEST_APPEND/ZIP_VERIFICATION.json",
    }
    missing = sorted(required_entries - names)
    if missing:
        raise RuntimeError(f"temporary ZIP missing required entries: {missing}")
    temp_parent_digest, temp_parent_entries = zip_payload_digest(TEMP, False)
    if temp_parent_digest != parent_payload_digest or temp_parent_entries != parent_entries:
        raise RuntimeError("sections 00-18 changed by content")

    os.replace(TEMP, CANONICAL)
    with zipfile.ZipFile(CANONICAL, "r") as zf:
        final_crc_error = zf.testzip()
        final_entries = len(zf.infolist())
    final_parent_digest, _ = zip_payload_digest(CANONICAL, False)
    if final_crc_error is not None or final_parent_digest != parent_payload_digest:
        raise RuntimeError("published package verification failed")
    final_sha = sha256(CANONICAL)
    print(json.dumps({
        "status": "PUBLISHED_VERIFIED", "path": str(CANONICAL), "sha256": final_sha,
        "bytes": CANONICAL.stat().st_size, "entries": final_entries, "crc_error": final_crc_error,
        "sections_00_18_payload_digest": final_parent_digest,
        "parent_backup": str(BACKUP), "parent_backup_sha256": sha256(BACKUP),
        "main_checkpoint": snapshots[-1],
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
