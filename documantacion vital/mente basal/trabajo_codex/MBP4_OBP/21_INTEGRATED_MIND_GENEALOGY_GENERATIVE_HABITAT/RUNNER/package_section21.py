from __future__ import annotations

import hashlib
import json
import os
import tempfile
import zipfile
from pathlib import Path


SECTION = Path(__file__).resolve().parents[1]
WORK = SECTION.parent
ROOT = WORK.parents[1]
CANONICAL = ROOT / "MENTE_BASAL_4_ORGANIZACION_BASAL_PERSISTENTE_VALIDACION_RESULTADOS.zip"
EXPECTED_PARENT_SHA = "d39c260e20a5a3bfe9775afc7b31031a36293df095b9adec40518ad4d57aaab6"
WRAPPER = "MENTE_BASAL_4_ORGANIZACION_BASAL_PERSISTENTE_VALIDACION_RESULTADOS"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def data_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def section_files() -> list[Path]:
    files = []
    for path in SECTION.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(SECTION)
        if "__pycache__" in relative.parts or path.name == "HASHES.sha256":
            continue
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(SECTION).as_posix())


def write_hashes() -> None:
    rows = [
        f"{sha256(path)}  {path.relative_to(SECTION).as_posix()}"
        for path in section_files()
    ]
    (SECTION / "HASHES.sha256").write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> None:
    if sha256(CANONICAL) != EXPECTED_PARENT_SHA:
        raise RuntimeError("canonical parent ZIP does not match the frozen section-20 parent")
    write_hashes()
    files = section_files() + [SECTION / "HASHES.sha256"]
    temp: Path | None = None
    parent_content: dict[str, str] = {}
    parent_infos: list[zipfile.ZipInfo] = []
    with zipfile.ZipFile(CANONICAL, "r") as parent:
        parent_infos = parent.infolist()
        if any(f"/{SECTION.name}/" in info.filename for info in parent_infos):
            raise RuntimeError("parent already contains section 21")
        parent_content = {
            info.filename: data_sha256(parent.read(info))
            for info in parent_infos if not info.is_dir()
        }
        descriptor, temp_name = tempfile.mkstemp(
            prefix="mbp4_section21_", suffix=".zip", dir=str(WORK)
        )
        os.close(descriptor)
        temp = Path(temp_name)
        with zipfile.ZipFile(temp, "w", allowZip64=True) as output:
            for info in parent_infos:
                output.writestr(info, parent.read(info))
            for path in files:
                arcname = f"{WRAPPER}/{SECTION.name}/{path.relative_to(SECTION).as_posix()}"
                output.write(path, arcname, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    if temp is None:
        raise RuntimeError("temporary ZIP was not created")
    try:
        with zipfile.ZipFile(temp, "r") as check:
            bad = check.testzip()
            if bad is not None:
                raise RuntimeError(f"ZIP CRC failure at {bad}")
            inherited = {
                name: data_sha256(check.read(name))
                for name in parent_content
            }
            if inherited != parent_content:
                raise RuntimeError("an inherited entry in sections 00-20 changed")
            hash_name = f"{WRAPPER}/{SECTION.name}/HASHES.sha256"
            rows = check.read(hash_name).decode("utf-8").splitlines()
            for row in rows:
                digest, relative = row.split("  ", 1)
                name = f"{WRAPPER}/{SECTION.name}/{relative}"
                if data_sha256(check.read(name)) != digest:
                    raise RuntimeError(f"section hash mismatch in ZIP: {relative}")
        os.replace(temp, CANONICAL)
    finally:
        if temp.exists():
            temp.unlink()

    verification = {
        "schema": "mbp4.integrated-mind.package-verification.v1",
        "parent_zip_sha256": EXPECTED_PARENT_SHA,
        "final_zip": CANONICAL.name,
        "final_zip_sha256": sha256(CANONICAL),
        "inherited_file_entries_verified_byte_exact": len(parent_content),
        "section21_files_hashed": len(files) - 1,
        "crc_error": None,
        "section_hashes_verified": True,
    }
    path = WORK / "section21_package_verification.json"
    path.write_text(json.dumps(verification, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(verification, sort_keys=True))


if __name__ == "__main__":
    main()
