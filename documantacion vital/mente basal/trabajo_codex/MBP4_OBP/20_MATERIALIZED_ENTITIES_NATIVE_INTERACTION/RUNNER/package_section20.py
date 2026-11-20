from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import zipfile
from pathlib import Path


SECTION = Path(__file__).resolve().parents[1]
WORK = SECTION.parent
ROOT = WORK.parents[1]
CANONICAL = ROOT / "MENTE_BASAL_4_ORGANIZACION_BASAL_PERSISTENTE_VALIDACION_RESULTADOS.zip"
EXPECTED_PARENT_SHA = "da23fcb06ac3c26ca16ab443762a49e38d2303c015a69d9d70afe23daafd0c4f"
WRAPPER = "MENTE_BASAL_4_ORGANIZACION_BASAL_PERSISTENTE_VALIDACION_RESULTADOS"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def data_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def section_files() -> list[Path]:
    rows = []
    for path in SECTION.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(SECTION)
        if "__pycache__" in relative.parts or path.name == "HASHES.sha256":
            continue
        rows.append(path)
    return sorted(rows, key=lambda p: p.relative_to(SECTION).as_posix())


def write_hashes() -> None:
    lines = [f"{sha256(path)}  {path.relative_to(SECTION).as_posix()}" for path in section_files()]
    (SECTION / "HASHES.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if sha256(CANONICAL) != EXPECTED_PARENT_SHA:
        raise RuntimeError("canonical parent ZIP changed before packaging")
    write_hashes()
    files = section_files() + [SECTION / "HASHES.sha256"]
    temp: Path | None = None
    with zipfile.ZipFile(CANONICAL, "r") as parent:
        parent_infos = parent.infolist()
        if any(f"/{SECTION.name}/" in info.filename for info in parent_infos):
            raise RuntimeError("parent already contains section 20")
        parent_content = {
            info.filename: data_sha256(parent.read(info))
            for info in parent_infos if not info.is_dir()
        }
        fd, temp_name = tempfile.mkstemp(prefix="mbp4_section20_", suffix=".zip", dir=str(WORK))
        os.close(fd)
        temp = Path(temp_name)
        with zipfile.ZipFile(temp, "w", allowZip64=True) as out:
            for info in parent_infos:
                out.writestr(info, parent.read(info))
            for path in files:
                arcname = f"{WRAPPER}/{SECTION.name}/{path.relative_to(SECTION).as_posix()}"
                out.write(path, arcname, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    if temp is None:
        raise RuntimeError("temporary ZIP was not created")
    try:
        with zipfile.ZipFile(temp, "r") as check:
            bad = check.testzip()
            if bad is not None:
                raise RuntimeError(f"ZIP CRC failure at {bad}")
            new_content = {
                name: data_sha256(check.read(name))
                for name in parent_content
            }
            if new_content != parent_content:
                raise RuntimeError("an entry in sections 00-19 changed")
            hashes = {}
            for line in check.read(f"{WRAPPER}/{SECTION.name}/HASHES.sha256").decode("utf-8").splitlines():
                digest, relative = line.split("  ", 1)
                hashes[relative] = digest
            for relative, expected in hashes.items():
                name = f"{WRAPPER}/{SECTION.name}/{relative}"
                if data_sha256(check.read(name)) != expected:
                    raise RuntimeError(f"section hash mismatch in ZIP: {relative}")
        os.replace(temp, CANONICAL)
    finally:
        if temp.exists():
            temp.unlink()

    verification = {
        "schema": "mbp4.materialized-entities.package-verification.v1",
        "parent_zip_sha256": EXPECTED_PARENT_SHA,
        "final_zip": CANONICAL.name,
        "final_zip_sha256": sha256(CANONICAL),
        "old_file_entries_verified_byte_exact": len(parent_content),
        "section20_files_hashed": len(files) - 1,
        "crc_error": None,
        "section_hashes_verified": True,
    }
    verification_path = WORK / "section20_package_verification.json"
    verification_path.write_text(json.dumps(verification, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(verification, sort_keys=True))


if __name__ == "__main__":
    main()
