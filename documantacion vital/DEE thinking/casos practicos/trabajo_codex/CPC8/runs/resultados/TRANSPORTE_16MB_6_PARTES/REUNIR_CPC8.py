"""Verifica y reune las partes binarias de CPC8 sin sobrescribir archivos."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile

BLOCK = 1024 * 1024


def safe_name(value):
    if (not isinstance(value, str) or not value or value in (".", "..")
            or Path(value).name != value or any(c in value for c in "/\\:")):
        raise ValueError("Nombre de transporte no valido")
    return value


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(BLOCK), b""):
            h.update(chunk)
    return h.hexdigest()


def reconstruct(manifest, output=None):
    manifest = Path(manifest).resolve()
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if data.get("schema") != 2 or not data.get("parts"):
        raise ValueError("Manifiesto de partes no valido")
    ordered = sorted(data["parts"], key=lambda p: p["order"])
    if [p["order"] for p in ordered] != list(range(1, len(ordered) + 1)):
        raise ValueError("Orden de partes no valido")
    names = [safe_name(p["name"]) for p in ordered]
    if len(set(names)) != len(names):
        raise ValueError("Partes repetidas")
    target_name = safe_name(data["zip"]["name"])
    output = Path(output).resolve() if output is not None else manifest.parent / target_name
    if output.exists():
        raise FileExistsError("Se protege el archivo existente: " + str(output))
    if not output.parent.is_dir():
        raise FileNotFoundError(output.parent)
    if sum(p["bytes"] for p in ordered) != data["zip"]["bytes"]:
        raise ValueError("La suma de tamanos no coincide")
    for part in ordered:
        path = manifest.parent / part["name"]
        if (not path.is_file() or path.stat().st_size != part["bytes"]
                or digest(path) != part["sha256"]):
            raise ValueError("Parte ausente, incompleta o corrupta: " + str(path))
    handle, temp_name = tempfile.mkstemp(prefix=".cpc8_reunion_", suffix=".pending", dir=output.parent)
    os.close(handle)
    temporary = Path(temp_name)
    combined = hashlib.sha256()
    size = 0
    try:
        with temporary.open("wb") as out:
            for part in ordered:
                part_hash = hashlib.sha256()
                part_size = 0
                with (manifest.parent / part["name"]).open("rb") as stream:
                    for chunk in iter(lambda: stream.read(BLOCK), b""):
                        out.write(chunk)
                        combined.update(chunk)
                        part_hash.update(chunk)
                        part_size += len(chunk)
                        size += len(chunk)
                if part_size != part["bytes"] or part_hash.hexdigest() != part["sha256"]:
                    raise ValueError("Una parte cambio durante la lectura")
            out.flush()
            os.fsync(out.fileno())
        if size != data["zip"]["bytes"] or combined.hexdigest() != data["zip"]["sha256"]:
            raise ValueError("El ZIP reunido no coincide con el original")
        # Creacion atomica que falla si ya existe el destino, incluso por concurrencia.
        os.link(temporary, output)
        temporary.unlink()
        return {"status": "RECONSTRUCTION_HASH_VERIFIED", "output": str(output),
                "bytes": size, "sha256": combined.hexdigest(), "parts": len(ordered)}
    finally:
        if temporary.exists():
            temporary.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path(__file__).with_name("PARTES.json"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    print(json.dumps(reconstruct(args.manifest, args.output), ensure_ascii=False))


if __name__ == "__main__":
    main()
