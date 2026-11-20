from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
import zipfile
from pathlib import Path


INCLUDE_PATHS = (
    "CMakeLists.txt",
    "README.md",
    "src",
    "configs",
    "docs",
    "tools",
    "baseline/dee_thinking_2_2_0",
    "bin",
    "validation",
    "results/baseline_2_2_0.txt",
    "results/panel_final",
    "results/panel_v2",
    "results/panel_v3",
    "results/checkpoint_reference.csv",
    "results/checkpoint_new_process_resume.csv",
    "checkpoints/learned_dose4_t40.deetsnap",
    "checkpoints/learned_dose4_holdout_reference_t60.deetsnap",
    "checkpoints/learned_dose4_holdout_resumed_t60.deetsnap",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing archive: {output}")

    with tempfile.TemporaryDirectory(prefix="dee-e3-stage-") as temporary:
        stage = Path(temporary) / "DEE_thinking_ENTREGA_03_APRENDIZAJE_NATIVO"
        stage.mkdir()
        for relative in INCLUDE_PATHS:
            source = root / relative
            if not source.exists():
                raise FileNotFoundError(source)
            target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir():
                shutil.copytree(source, target)
            else:
                shutil.copy2(source, target)

        files = sorted(path for path in stage.rglob("*") if path.is_file())
        manifest = {
            "campaign": "entrega03.native_learning.v1",
            "baseline": "DEE thinking 2.2.0",
            "kernel": "DEE v27 (unchanged)",
            "entry_count_without_manifest": len(files),
            "files": [
                {
                    "path": path.relative_to(stage).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
                for path in files
            ],
        }
        (stage / "MANIFEST.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        output.parent.mkdir(parents=True, exist_ok=True)
        candidate = Path(temporary) / output.name
        with zipfile.ZipFile(candidate, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for path in sorted(p for p in stage.rglob("*") if p.is_file()):
                archive.write(path, path.relative_to(stage).as_posix())

        with zipfile.ZipFile(candidate) as archive:
            bad = archive.testzip()
            names = archive.namelist()
            if bad is not None:
                raise RuntimeError(f"corrupt archive member: {bad}")
            if any(name.lower().endswith(".zip") for name in names):
                raise RuntimeError("nested ZIP detected")
            if any("__pycache__" in name or name.endswith((".pyc", ".obj", ".pdb"))
                   for name in names):
                raise RuntimeError("development artifact detected")
            required = {
                "src/native_environment_learning.cpp",
                "bin/dee_entrega03_native_learning.exe",
                "results/panel_final/case_summary.csv",
                "checkpoints/learned_dose4_t40.deetsnap",
                "docs/SCIENTIFIC_REPORT.md",
                "validation/VALIDATION_SUMMARY.json",
            }
            missing = required.difference(names)
            if missing:
                raise RuntimeError(f"missing required members: {sorted(missing)}")
        shutil.copy2(candidate, output)

    print(f"archive={output}")
    print(f"sha256={sha256(output)}")
    with zipfile.ZipFile(output) as archive:
        print(f"entries={len(archive.namelist())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

