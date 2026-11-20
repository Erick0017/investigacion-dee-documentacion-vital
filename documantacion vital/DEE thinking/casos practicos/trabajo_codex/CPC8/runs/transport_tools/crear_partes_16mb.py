"""Genera un transporte adicional limitado a 16 MB, preservando CPC8 original."""
from __future__ import annotations

import datetime
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import tempfile
import time
import zipfile

EXPECTED = "4cf266a0ab968e26986a9935317ba146a8f769fc5717092470c4bead8983b8ed"
NAME = "CPC8_ORGANIZACION_COGNITIVA_NATIVA_APRENDIZAJE65_RESULTADOS.zip"
BLOCK = 1024 * 1024
MAX_BYTES = 16_000_000


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(BLOCK), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    start = time.monotonic()
    source_dir = Path(sys.argv[1]).resolve()
    source = source_dir / NAME
    outdir = source_dir / "TRANSPORTE_16MB_6_PARTES"
    if not source.is_file() or digest(source) != EXPECTED:
        raise ValueError("La identidad del ZIP original no coincide")
    if not outdir.is_dir():
        raise FileNotFoundError(outdir)
    count = math.ceil(source.stat().st_size / MAX_BYTES)
    size_base, remainder = divmod(source.stat().st_size, count)
    target_paths = [outdir / (NAME + f".{i:03d}") for i in range(1, count + 1)]
    if any(p.exists() for p in target_paths) or (outdir / "PARTES.json").exists():
        raise FileExistsError("Se protegen las partes ya existentes")
    parts = []
    with source.open("rb") as stream:
        for i, path in enumerate(target_paths):
            expected_size = size_base + (1 if i < remainder else 0)
            remaining = expected_size
            h = hashlib.sha256()
            with path.open("xb") as output:
                while remaining:
                    chunk = stream.read(min(BLOCK, remaining))
                    if not chunk:
                        raise EOFError("El ZIP original termino antes de lo previsto")
                    output.write(chunk)
                    h.update(chunk)
                    remaining -= len(chunk)
            if path.stat().st_size != expected_size or expected_size > MAX_BYTES:
                raise ValueError("Tamano de parte incorrecto")
            parts.append({"order": i + 1, "name": path.name, "bytes": expected_size,
                          "sha256": h.hexdigest()})
        if stream.read(1):
            raise ValueError("El ZIP cambio de tamano")
    manifest = {"schema": 2, "kind": "Sequential binary parts, not independent ZIP archives",
                "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "max_part_bytes": MAX_BYTES, "part_count": count,
                "zip": {"name": source.name, "bytes": source.stat().st_size, "sha256": EXPECTED},
                "parts": parts}
    write_json(outdir / "PARTES.json", manifest)
    spec = importlib.util.spec_from_file_location("cpc8_reunir", outdir / "REUNIR_CPC8.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Reconstruccion real temporal, comparacion byte por byte y CRC de todos los miembros.
    with tempfile.TemporaryDirectory(prefix="verificacion_real_", dir=outdir) as temp_dir:
        rebuilt = Path(temp_dir) / NAME
        result = module.reconstruct(outdir / "PARTES.json", rebuilt)
        compared = 0
        with source.open("rb") as a, rebuilt.open("rb") as b:
            while True:
                chunk_a, chunk_b = a.read(BLOCK), b.read(BLOCK)
                if chunk_a != chunk_b:
                    raise ValueError("La reconstruccion difiere byte por byte")
                if not chunk_a:
                    break
                compared += len(chunk_a)
        with zipfile.ZipFile(rebuilt) as archive:
            bad = archive.testzip()
            if bad is not None:
                raise ValueError("CRC ZIP incorrecto: " + bad)
            member_count = len(archive.infolist())
        try:
            module.reconstruct(outdir / "PARTES.json", rebuilt)
        except FileExistsError:
            overwrite_protection = True
        else:
            raise AssertionError("La proteccion contra sobrescritura fallo")
    unchanged = digest(source) == EXPECTED
    if not unchanged:
        raise ValueError("El ZIP canonico cambio")
    report = {"status": "VERIFIED", "verified_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "zip": manifest["zip"], "part_count": count,
              "max_part_bytes": max(p["bytes"] for p in parts),
              "all_parts_under_16000000_bytes": all(p["bytes"] <= MAX_BYTES for p in parts),
              "actual_reconstruction": result, "byte_by_byte_compared": compared,
              "zip_crc_all_members": "PASS", "zip_members": member_count,
              "existing_output_protected": overwrite_protection,
              "canonical_zip_unchanged": unchanged, "elapsed_seconds": time.monotonic() - start}
    write_json(outdir / "VERIFICACION_TRANSPORTE.json", report)
    hash_lines = []
    for path in sorted(outdir.iterdir()):
        if path.is_file():
            hash_lines.append(digest(path) + "  " + path.name)
    with (outdir / "HASHES.sha256").open("x", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(hash_lines) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
