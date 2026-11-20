from __future__ import annotations

import argparse
import hashlib
import json
import os
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


FINAL_ROOT = "MENTE_BASAL_CORTE_FINAL_1000"


def digest_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def digest_member(archive: zipfile.ZipFile, name: str) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with archive.open(name, "r") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
            size += len(block)
    return digest.hexdigest(), size


def find_member(names: list[str], suffix: str) -> str:
    matches = [name for name in names if name.endswith(suffix)]
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one ZIP member ending in {suffix!r}, found {matches}")
    return matches[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--descriptor", required=True, type=Path)
    parser.add_argument("--world-status", required=True, type=Path)
    args = parser.parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    descriptor_path = args.descriptor.resolve()
    status_path = args.world_status.resolve()
    descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
    status = json.loads(status_path.read_text(encoding="utf-8"))
    if descriptor.get("world_id") != "MENTE-BASAL-001":
        raise RuntimeError("unexpected world_id in collection descriptor")
    if not descriptor.get("stop_after"):
        raise RuntimeError("collection is not a collect-stop cut")
    end_tick = int(descriptor["end_tick"])
    if status.get("state") not in {"STOPPED", "STOPPED_SAFE"} or int(status.get("tick", -1)) != end_tick:
        raise RuntimeError(f"worker is not safely stopped at T{end_tick}: {status.get('state')} T{status.get('tick')}")

    source_sha = digest_path(source)
    with zipfile.ZipFile(source, "r") as archive:
        bad = archive.testzip()
        if bad is not None:
            raise RuntimeError(f"source collection CRC failure: {bad}")
        names = archive.namelist()
        checkpoint_suffix = "/" + str(descriptor["end_checkpoint"]).replace("\\", "/")
        checkpoint_member = find_member(names, checkpoint_suffix)
        sidecar_member = find_member(names, checkpoint_suffix + ".json")
        descriptor_member = find_member(names, "/history/collections/" + descriptor_path.name)
        archived_descriptor = json.loads(archive.read(descriptor_member).decode("utf-8"))
        if archived_descriptor != descriptor:
            raise RuntimeError("descriptor in source ZIP differs from published descriptor")
        sidecar = json.loads(archive.read(sidecar_member).decode("utf-8"))
        checkpoint_sha, checkpoint_bytes = digest_member(archive, checkpoint_member)
        if checkpoint_sha != sidecar.get("sha256") or checkpoint_bytes != int(sidecar.get("bytes", -1)):
            raise RuntimeError("checkpoint sidecar hash/size mismatch")
        if int(sidecar.get("tick", -1)) != end_tick or sidecar.get("world_id") != "MENTE-BASAL-001":
            raise RuntimeError("checkpoint identity mismatch")
        source_prefix = PurePosixPath(names[0]).parts[0]
        for relative in descriptor["immutable_files"]:
            expected = source_prefix + "/" + str(relative).replace("\\", "/")
            if expected not in names:
                raise RuntimeError(f"immutable collection member missing: {relative}")

    validation = {
        "schema": "mente-basal.final-cut-1000.validation.v1",
        "validated_utc": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "world_id": "MENTE-BASAL-001",
        "session_id": descriptor.get("session_id"),
        "request_id": descriptor.get("request_id"),
        "end_tick": end_tick,
        "created_utc": descriptor.get("created_utc"),
        "created_local": descriptor.get("created_local"),
        "stop_after": True,
        "worker_state": status.get("state"),
        "source_collection": source.name,
        "source_collection_sha256": source_sha,
        "checkpoint": descriptor["end_checkpoint"],
        "checkpoint_sha256": checkpoint_sha,
        "checkpoint_bytes": checkpoint_bytes,
        "source_zip_crc_ok": True,
        "checkpoint_identity_ok": True,
        "history_and_telemetry_closed": True,
        "recovery_note": "The scheduled collect-stop succeeded. Final publication was recovered without a second cut after accepting the habitat's terminal state name STOPPED_SAFE.",
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".tmp")
    if temporary.exists():
        temporary.unlink()
    hashes: list[tuple[str, str]] = []
    with zipfile.ZipFile(source, "r") as input_zip, zipfile.ZipFile(
        temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6
    ) as final_zip:
        source_prefix = PurePosixPath(input_zip.namelist()[0]).parts[0]
        for info in input_zip.infolist():
            if info.is_dir():
                continue
            relative = PurePosixPath(info.filename).relative_to(source_prefix).as_posix()
            destination = f"{FINAL_ROOT}/{relative}"
            digest = hashlib.sha256()
            with input_zip.open(info, "r") as source_stream, final_zip.open(destination, "w") as output_stream:
                for block in iter(lambda: source_stream.read(1024 * 1024), b""):
                    digest.update(block)
                    output_stream.write(block)
            hashes.append((destination, digest.hexdigest()))
        for tool in (Path(__file__).resolve(), Path(__file__).with_name("final_cut_1000.ps1")):
            tool_bytes = tool.read_bytes()
            tool_name = f"{FINAL_ROOT}/finalization_tools/{tool.name}"
            final_zip.writestr(tool_name, tool_bytes)
            hashes.append((tool_name, hashlib.sha256(tool_bytes).hexdigest()))
        validation_name = f"{FINAL_ROOT}/FINAL_VALIDATION.json"
        validation_bytes = (json.dumps(validation, indent=2) + "\n").encode("utf-8")
        final_zip.writestr(validation_name, validation_bytes)
        hashes.append((validation_name, hashlib.sha256(validation_bytes).hexdigest()))
        hash_text = "".join(f"{digest}  {name}\n" for name, digest in sorted(hashes))
        final_zip.writestr(f"{FINAL_ROOT}/HASHES.sha256", hash_text.encode("utf-8"))

    with zipfile.ZipFile(temporary, "r") as archive:
        bad = archive.testzip()
        if bad is not None:
            raise RuntimeError(f"final ZIP CRC failure: {bad}")
        if f"{FINAL_ROOT}/FINAL_VALIDATION.json" not in archive.namelist():
            raise RuntimeError("final validation record missing")
        entries = len(archive.namelist())
    os.replace(temporary, output)
    print(json.dumps({
        "path": str(output), "bytes": output.stat().st_size,
        "sha256": digest_path(output), "entries": entries,
        "end_tick": end_tick, "checkpoint_sha256": checkpoint_sha,
        "worker_state": status.get("state"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
