from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


REFERENCE_TICK = 193536
FINAL_TICK = 214872


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_reset(path: Path, parent: Path) -> None:
    resolved = path.resolve()
    if resolved.parent != parent.resolve() or not resolved.name.startswith("stage_"):
        raise RuntimeError(f"refusing to reset unsafe staging path: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)
    resolved.mkdir(parents=True)


def copy_one(source: Path, stage: Path, relative: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(source)
    destination = stage / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def copy_tree_files(source: Path, stage: Path, relative: Path, suffixes: set[str] | None = None) -> None:
    for item in sorted(source.rglob("*")):
        if not item.is_file() or "__pycache__" in item.parts or item.suffix == ".pyc":
            continue
        if suffixes is not None and item.suffix.lower() not in suffixes:
            continue
        copy_one(item, stage, relative / item.relative_to(source))


def descriptor_files(root: Path, descriptor: Path) -> Iterable[tuple[Path, Path]]:
    payload = json.loads(descriptor.read_text(encoding="utf-8"))
    yield descriptor, Path("history/collections") / descriptor.name
    for value in payload["immutable_files"]:
        relative = Path(value)
        yield root / relative, relative


def freeze_runtime_evidence(root: Path, area: Path, stage: Path) -> None:
    world_status = json.loads((root / "world/status.json").read_text(encoding="utf-8"))
    observer_status = json.loads((area / "observer_runtime/observer_status.json").read_text(encoding="utf-8"))
    validation = stage / "validation"
    validation.mkdir(parents=True, exist_ok=True)
    (validation / "main_status_after_cut.json").write_text(
        json.dumps(world_status, indent=2) + "\n", encoding="utf-8")
    (validation / "observer_status_after_cut.json").write_text(
        json.dumps(observer_status, indent=2) + "\n", encoding="utf-8")
    source_log = area / "observer_runtime/observer_samples.jsonl"
    selected = []
    for line in source_log.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if int(record["sample_tick"]) <= FINAL_TICK:
            selected.append(json.dumps(record, separators=(",", ":")))
    (validation / "observer_samples_through_final_cut.jsonl").write_text(
        "\n".join(selected) + ("\n" if selected else ""), encoding="utf-8")
    for name in ("observer.stdout.log", "observer.stderr.log"):
        source = area / "observer_runtime" / name
        if source.is_file():
            copy_one(source, stage, Path("validation") / name)
    operational = {
        "schema": "mente-basal.observation-coupling-003.operational-freeze.v1",
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "scientific_cut_tick": FINAL_TICK,
        "world_status_tick_at_freeze": world_status.get("tick"),
        "world_pid": world_status.get("pid"),
        "world_id": world_status.get("world_id"),
        "session_id": world_status.get("session_id"),
        "observer_pid": observer_status.get("pid"),
        "observer_state": observer_status.get("state"),
        "observer_last_sample_tick": observer_status.get("last_sample_tick"),
        "observer_samples_packaged_through_cut": len(selected),
        "note": "Operational evidence after the immutable scientific cut; not part of the T193536..T214872 trajectory.",
    }
    (validation / "OPERATIONAL_FREEZE.json").write_text(
        json.dumps(operational, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--area", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    area = args.area.resolve()
    output = args.output.resolve()
    package_dir = area / "package"
    package_dir.mkdir(parents=True, exist_ok=True)
    stage = package_dir / "stage_obs003"
    safe_reset(stage, package_dir)

    for name in ("README.md", "INFORME_INTEGRADO.md"):
        copy_one(area / name, stage, Path(name))
    copy_tree_files(area / "tools", stage, Path("tools"), {".py", ".ps1"})
    copy_tree_files(area / "analysis", stage, Path("analysis"), {".json", ".csv", ".md", ".jsonl"})
    copy_tree_files(area / "checkpoints", stage, Path("experiments/checkpoints"), {".json", ".deetsnap"})
    copy_tree_files(area / "validation", stage, Path("validation"), {".json", ".md", ".txt", ".log"})

    copy_one(root / "app/habitat.py", stage, Path("app/habitat.py"))
    copy_one(root / "config/habitat.template.json", stage, Path("config/habitat.template.json"))
    copy_one(root / "baseline/dee_thinking-2.2.0-cp313-cp313-win_amd64.whl", stage,
             Path("baseline/dee_thinking-2.2.0-cp313-cp313-win_amd64.whl"))
    copy_tree_files(root / "baseline/python_site", stage, Path("baseline/python_site"))

    checkpoint_names = (
        "tick_000000000064_collect_SESSION_001_REF_0853e180.deetsnap",
        "tick_000000134856_collect_CUT_002_762afc79.deetsnap",
        "tick_000000193536_collect_OBS_003_REF_e1c00e61.deetsnap",
        "tick_000000214872_collect_OBS_003_FINAL_3babbbcd.deetsnap",
    )
    for name in checkpoint_names:
        source = root / "world/checkpoints" / name
        copy_one(source, stage, Path("world/checkpoints") / name)
        copy_one(source.with_name(source.name + ".json"), stage,
                 Path("world/checkpoints") / (name + ".json"))

    descriptors = (
        root / "history/collections/cut_OBS_003_REF_t193536.json",
        root / "history/collections/cut_OBS_003_FINAL_t214872.json",
    )
    copied = set()
    for descriptor in descriptors:
        for source, relative in descriptor_files(root, descriptor):
            key = relative.as_posix().lower()
            if key not in copied:
                copy_one(source, stage, relative)
                copied.add(key)

    freeze_runtime_evidence(root, area, stage)

    payload_files = sorted(
        item for item in stage.rglob("*")
        if item.is_file() and item.name not in {"MANIFEST.json", "HASHES.sha256"}
    )
    entries = []
    for item in payload_files:
        entries.append({
            "path": item.relative_to(stage).as_posix(),
            "bytes": item.stat().st_size,
            "sha256": sha256(item),
        })
    manifest = {
        "schema": "mente-basal.observation-coupling-003.package.v1",
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "world_id": "MENTE-BASAL-001", "session_id": "SESSION-001-20261005T035032Z",
        "reference_tick": REFERENCE_TICK, "final_cut_tick": FINAL_TICK,
        "kernel": "DEE v27 frozen", "product": "DEE thinking 2.2.0",
        "hash_scope": "all payload files listed below; excludes MANIFEST.json and HASHES.sha256 to avoid circular identity",
        "files": entries,
    }
    (stage / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (stage / "HASHES.sha256").write_text(
        "".join(f"{entry['sha256']}  {entry['path']}\n" for entry in entries), encoding="utf-8")

    temporary = output.with_name(output.name + ".tmp")
    temporary.parent.mkdir(parents=True, exist_ok=True)
    if temporary.exists():
        temporary.unlink()
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for item in sorted(path for path in stage.rglob("*") if path.is_file()):
            archive.write(item, item.relative_to(stage).as_posix())
    with zipfile.ZipFile(temporary, "r") as archive:
        bad = archive.testzip()
        if bad is not None:
            raise RuntimeError(f"ZIP CRC failure: {bad}")
        names = archive.namelist()
        nested = [name for name in names if name.lower().endswith(".zip")]
        if nested:
            raise RuntimeError(f"unexpected nested ZIP: {nested}")
    os.replace(temporary, output)
    result = {
        "path": str(output), "bytes": output.stat().st_size,
        "sha256": sha256(output), "entries": len(zipfile.ZipFile(output).namelist()),
        "stage": str(stage),
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

