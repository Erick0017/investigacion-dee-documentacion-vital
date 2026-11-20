from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path


PREFIX = "MENTE_BASAL_RECOLECCION_CUT_002_RESULTADOS"


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output.resolve()
    if output.exists():
        raise RuntimeError(f"refusing to overwrite official package: {output}")

    previous_rel = Path("history/collections/cut_SESSION_001_REF_t64.json")
    current_rel = Path("history/collections/cut_CUT_002_t134856.json")
    previous = load_json(root / previous_rel)
    current = load_json(root / current_rel)
    if (previous["world_id"] != current["world_id"] or
            previous["session_id"] != current["session_id"] or
            int(previous["end_tick"]) != int(current["start_tick"]) or
            previous["end_checkpoint"].replace("\\", "/") !=
            current["start_checkpoint"].replace("\\", "/")):
        raise RuntimeError("CUT_002 descriptor does not continue the T64 cut exactly")

    relative: set[Path] = {previous_rel, current_rel}
    for value in current["immutable_files"]:
        relative.add(Path(value.replace("\\", "/")))
    start = Path(current["start_checkpoint"].replace("\\", "/"))
    end = Path(current["end_checkpoint"].replace("\\", "/"))
    relative.update((start, Path(str(start) + ".json"), end, Path(str(end) + ".json")))

    # This periodic boundary makes a short exact replay of the closing window
    # feasible without replaying the complete 134792-tick interval.
    tail = Path("world/checkpoints/tick_000000134088_periodic_d5caa929.deetsnap")
    relative.update((tail, Path(str(tail) + ".json")))

    static = [
        "app/habitat.py", "app/launch_worker.py",
        "tools/habitat.ps1", "tools/panel.py", "tools/run_diagnostic_controls.py",
        "tools/analyze_cut_interval.py", "tools/replay_emergent_window.py",
        "tools/package_cut_002_scientific.py",
        "config/habitat.json", "config/habitat.template.json",
        "docs/OPERATIONS.md", "docs/SCIENTIFIC_SCOPE.md",
        "world/instance.json",
        "baseline/dee_thinking-2.2.0-cp313-cp313-win_amd64.whl",
        "validation/VALIDATION_SUMMARY.md",
    ]
    analysis = [
        "analysis/CUT_002_pre_status_observations.json",
        "analysis/CUT_002_status_after_collection.json",
        "analysis/CUT_002_interval_analysis.json",
        "analysis/CUT_002_emergent_replay_t64_t900.json",
        "analysis/CUT_002_eval_T64.json",
        "analysis/CUT_002_eval_Tcollect.json",
        "analysis/CUT_002_replay_validation.json",
        "analysis/CUT_002_INFORME_INTEGRADO.md",
    ]
    relative.update(Path(item) for item in static + analysis)

    missing = sorted(str(item) for item in relative if not (root / item).is_file())
    if missing:
        raise FileNotFoundError(f"missing package inputs: {missing}")

    # Frozen cut controls are installed at the canonical paths used by replay.
    aliases = {
        Path("world/controller.json"): Path(current["controller_snapshot"].replace("\\", "/")),
        Path("world/status.json"): Path(current["status_snapshot"].replace("\\", "/")),
        Path("world/latest_checkpoint.txt"): Path(current["latest_pointer_snapshot"].replace("\\", "/")),
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="mente-basal-cut002-") as temporary:
        temporary_root = Path(temporary)
        staged = temporary_root / PREFIX
        staged.mkdir()
        for item in sorted(relative, key=lambda value: value.as_posix()):
            destination = staged / item
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / item, destination)
        for destination_rel, source_rel in aliases.items():
            destination = staged / destination_rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / source_rel, destination)

        staged_files = sorted(
            (item for item in staged.rglob("*") if item.is_file()),
            key=lambda value: value.relative_to(staged).as_posix())
        file_rows = [{
            "path": item.relative_to(staged).as_posix(),
            "bytes": item.stat().st_size,
            "sha256": digest(item),
        } for item in staged_files]
        manifest = {
            "schema": "mente-basal.scientific-collection-package.v1",
            "created_utc": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "world_id": current["world_id"],
            "session_id": current["session_id"],
            "request_id": current["request_id"],
            "start_tick": int(current["start_tick"]),
            "end_tick": int(current["end_tick"]),
            "start_checkpoint": start.as_posix(),
            "end_checkpoint": end.as_posix(),
            "short_replay_checkpoint": tail.as_posix(),
            "canonical_control_sources": {
                destination.as_posix(): source.as_posix()
                for destination, source in aliases.items()
            },
            "post_cut_tools": [
                "tools/analyze_cut_interval.py",
                "tools/replay_emergent_window.py",
                "tools/package_cut_002_scientific.py",
            ],
            "files": file_rows,
        }
        manifest_path = staged / "MANIFEST.json"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

        hash_targets = staged_files + [manifest_path]
        hashes_path = staged / "HASHES.sha256"
        hashes_path.write_text("".join(
            f"{digest(item)}  {item.relative_to(staged).as_posix()}\n"
            for item in sorted(hash_targets,
                               key=lambda value: value.relative_to(staged).as_posix())),
            encoding="utf-8")

        candidate = temporary_root / output.name
        with zipfile.ZipFile(candidate, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for item in sorted(staged.rglob("*")):
                if item.is_file():
                    archive.write(item, item.relative_to(temporary_root).as_posix())
        with zipfile.ZipFile(candidate) as archive:
            bad = archive.testzip()
            if bad is not None:
                raise RuntimeError(f"corrupt archive member: {bad}")
            names = archive.namelist()
            if any(name.lower().endswith(".zip") for name in names):
                raise RuntimeError("nested ZIP detected")
            if any("__pycache__/" in name or "python_site/" in name for name in names):
                raise RuntimeError("cache or installed environment leaked into package")

        # Verify a clean extraction, every packaged hash, and both boundary snapshots.
        extraction = temporary_root / "clean-extraction"
        with zipfile.ZipFile(candidate) as archive:
            archive.extractall(extraction)
        extracted = extraction / PREFIX
        for line in (extracted / "HASHES.sha256").read_text(encoding="utf-8").splitlines():
            expected, path_text = line.split("  ", 1)
            if digest(extracted / Path(path_text)) != expected:
                raise RuntimeError(f"hash mismatch after extraction: {path_text}")
        import dee_thinking as dee
        start_runtime = dee.Runtime.load_snapshot(str(extracted / start))
        end_runtime = dee.Runtime.load_snapshot(str(extracted / end))
        if int(start_runtime.current_tick) != 64 or int(end_runtime.current_tick) != 134856:
            raise RuntimeError("extracted checkpoint tick mismatch")

        sibling = output.with_name(f".{output.name}.{uuid.uuid4().hex}.tmp")
        try:
            with candidate.open("rb") as source_stream, sibling.open("xb") as target_stream:
                shutil.copyfileobj(source_stream, target_stream, 1024 * 1024)
                target_stream.flush()
                os.fsync(target_stream.fileno())
            with zipfile.ZipFile(sibling) as archive:
                if archive.testzip() is not None:
                    raise RuntimeError("published candidate failed CRC verification")
            os.replace(sibling, output)
        finally:
            sibling.unlink(missing_ok=True)

    result = {
        "path": str(output),
        "bytes": output.stat().st_size,
        "sha256": digest(output),
        "start_tick": 64,
        "end_tick": 134856,
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
