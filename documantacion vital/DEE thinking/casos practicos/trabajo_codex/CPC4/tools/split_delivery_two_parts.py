"""Split the published delivery byte-for-byte without modifying the original."""
import hashlib
import json
from pathlib import Path


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def main():
    folder = Path(__file__).resolve().parents[3]
    source = folder / "CPC4_COMUNICACION_NATIVA_Y_META_ROSETTA_RESULTADOS.zip"
    expected = "4a14a81f913a434a8e54e47c0c700d7ee54418bb16913aedded8bf49a3294723"
    original_size = source.stat().st_size
    if sha256(source) != expected:
        raise RuntimeError("The original ZIP does not match the verified delivery.")
    first_size = (original_size + 1) // 2
    sizes = (first_size, original_size - first_size)
    targets = [Path(str(source) + suffix) for suffix in (".001", ".002")]
    if any(target.exists() for target in targets):
        raise FileExistsError("A split part already exists; nothing was overwritten.")
    pending = [Path(str(target) + ".tmp") for target in targets]
    if any(target.exists() for target in pending):
        raise FileExistsError("A pending split part already exists; nothing was overwritten.")
    with source.open("rb") as reader:
        for target, size in zip(pending, sizes):
            remaining = size
            with target.open("xb") as writer:
                while remaining:
                    block = reader.read(min(1024 * 1024, remaining))
                    if not block:
                        raise EOFError("Unexpected end of the original ZIP.")
                    writer.write(block)
                    remaining -= len(block)
        if reader.read(1):
            raise RuntimeError("The original ZIP grew during splitting.")
    combined = hashlib.sha256()
    for target in pending:
        with target.open("rb") as stream:
            while block := stream.read(1024 * 1024):
                combined.update(block)
    if combined.hexdigest() != expected or sha256(source) != expected:
        raise RuntimeError("Split reconstruction did not match the unchanged original.")
    for temporary, target in zip(pending, targets):
        temporary.rename(target)
    print(json.dumps({
        "original": str(source),
        "original_bytes": original_size,
        "original_preserved": True,
        "parts": [{"path": str(target), "bytes": target.stat().st_size,
                   "sha256": sha256(target)} for target in targets],
        "recombined_sha256": combined.hexdigest(),
        "byte_exact_reconstruction_verified": True,
    }, indent=2))


if __name__ == "__main__":
    main()
