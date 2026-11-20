#!/usr/bin/env python3
"""Stage, build and verify the DEE thinking 2.2.0 definitive ZIP.

The legacy Entrega 02 packagers are deliberately not imported.  This tool
builds a candidate with the final basename in a temporary directory, calls the
definitive verifier, and only then atomically publishes to ``--output``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Iterable


ARCHIVE_NAME = "DEE_thinking_ENTREGA_02_DEFINITIVA_RESULTADOS.zip"
PRODUCT_VERSION = "2.2.0"
WHEEL_NAME = "dee_thinking-2.2.0-cp313-cp313-win_amd64.whl"
TOP_FILES = (
    "CMakeLists.txt",
    "PROJECT_METADATA.json",
    "README.md",
    "THIRD_PARTY_NOTICES.md",
    "pyproject.toml",
    "setup.py",
)
SOURCE_TREES = (
    "benchmarks",
    "bindings",
    "cmake",
    "examples",
    "fixtures",
    "include",
    "python",
    "src",
    "tests",
)
DOC_FILES = (
    "API_CONTRACT.md",
    "ARCHITECTURE_AND_BUILD.md",
    "BUILD_INSTALL_AND_SNAPSHOT.md",
    "CAPABILITY_CONTRACTS.md",
    "CHANGELOG.md",
    "CLOSURE_AND_FRONTIER_REPORT.md",
    "CORE05_PHASE_MEMORY.md",
    "DEFINITIVE_INTEGRATION_REPORT.md",
    "DIRECTED_SOURCE_REVIEW.md",
    "KERNEL_PROVENANCE.md",
    "MICROSCOPIC_BRANCH_AUDIT.md",
    "ORGANIZATION_CATALOG.md",
    "PREINTEGRATION_REPORT.md",
    "REPRODUCIBILITY.md",
    "SCIENTIFIC_SCOPE.md",
    "TECHNICAL_REPORT.md",
    "TEST_MATRIX_DEFINITIVE.md",
)
TOOL_FILES = (
    "build_definitive.ps1",
    "package_definitive.py",
    "verify_definitive_delivery.py",
)
EVIDENCE_TREE = "evidence/laboratory_final"
FORBIDDEN_PARTS = {
    ".git",
    ".vs",
    ".vscode",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "venv",
    ".venv",
}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo", ".obj", ".o", ".ilk", ".tmp", ".zip"}
NATIVE_ARTIFACT_SUFFIXES = {".exe", ".lib", ".dll", ".pyd"}


class PackagingError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _is_reparse_or_link(path: Path) -> bool:
    if path.is_symlink():
        return True
    attributes = getattr(path.lstat(), "st_file_attributes", 0)
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return bool(flag and attributes & flag)


def _allowed_source(path: Path) -> bool:
    parts = {part.casefold() for part in path.parts}
    if parts & {part.casefold() for part in FORBIDDEN_PARTS}:
        return False
    if any(part.casefold().endswith(".egg-info") for part in path.parts):
        return False
    return path.suffix.casefold() not in FORBIDDEN_SUFFIXES


def _tree_files(root: Path) -> Iterable[Path]:
    if not root.is_dir():
        raise PackagingError(f"required directory is missing: {root}")
    if _is_reparse_or_link(root):
        raise PackagingError(f"linked/reparse source root is forbidden: {root}")
    for path in sorted(root.rglob("*"), key=lambda value: value.as_posix().casefold()):
        if path.is_dir():
            if _is_reparse_or_link(path):
                raise PackagingError(f"linked/reparse directory is forbidden: {path}")
            continue
        if _is_reparse_or_link(path):
            raise PackagingError(f"linked/reparse file is forbidden: {path}")
        relative = path.relative_to(root)
        if _allowed_source(relative):
            yield path


def _add_file(mapping: dict[str, Path], archive_name: str, source: Path) -> None:
    name = PurePosixPath(archive_name).as_posix()
    if name.startswith("/") or ".." in PurePosixPath(name).parts:
        raise PackagingError(f"unsafe staged name: {name}")
    if name.casefold() in {item.casefold() for item in mapping}:
        raise PackagingError(f"duplicate or case-colliding staged name: {name}")
    if not source.is_file() or _is_reparse_or_link(source):
        raise PackagingError(f"staged source is missing or linked: {source}")
    mapping[name] = source


def _collect(
    project: Path,
    wheel: Path,
    build_root: Path,
    install_root: Path,
    validation_root: Path,
) -> dict[str, Path]:
    if _is_reparse_or_link(project):
        raise PackagingError(f"linked/reparse project root is forbidden: {project}")
    files: dict[str, Path] = {}
    for name in TOP_FILES:
        _add_file(files, name, project / name)
    for tree_name in SOURCE_TREES:
        tree = project / tree_name
        for path in _tree_files(tree):
            _add_file(files, path.relative_to(project).as_posix(), path)
    for name in DOC_FILES:
        _add_file(files, f"docs/{name}", project / "docs" / name)
    for name in TOOL_FILES:
        _add_file(files, f"tools/{name}", project / "tools" / name)
    evidence = project / EVIDENCE_TREE
    for path in _tree_files(evidence):
        _add_file(files, path.relative_to(project).as_posix(), path)

    for path in _tree_files(validation_root):
        _add_file(
            files,
            (PurePosixPath("validation") / path.relative_to(validation_root).as_posix()).as_posix(),
            path,
        )
    for path in _tree_files(install_root):
        _add_file(
            files,
            (PurePosixPath("install") / path.relative_to(install_root).as_posix()).as_posix(),
            path,
        )

    artifact_count = 0
    for path in _tree_files(build_root):
        if path.suffix.casefold() not in NATIVE_ARTIFACT_SUFFIXES:
            continue
        relative = path.relative_to(build_root)
        # Preserve only the meaningful bin/lib tail, not generator internals.
        parts = list(relative.parts)
        try:
            anchor = next(i for i, part in enumerate(parts) if part.casefold() in {"bin", "lib"})
        except StopIteration:
            continue
        tail = PurePosixPath(*parts[anchor:]).as_posix()
        _add_file(files, f"artifacts/native/{tail}", path)
        artifact_count += 1
    if artifact_count == 0:
        raise PackagingError(f"no native .exe/.lib/.dll artifacts found under {build_root}")

    _add_file(files, f"wheel/{wheel.name}", wheel)
    return files


def _copy_stage(files: dict[str, Path], stage: Path) -> None:
    for name, source in sorted(files.items()):
        target = stage.joinpath(*PurePosixPath(name).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def _write_metadata(stage: Path, wheel_name: str) -> None:
    payload: list[dict[str, object]] = []
    for path in sorted(stage.rglob("*"), key=lambda value: value.relative_to(stage).as_posix()):
        if not path.is_file():
            continue
        name = path.relative_to(stage).as_posix()
        data = path.read_bytes()
        payload.append({"path": name, "size": len(data), "sha256": sha256_bytes(data)})
    wheel_path = f"wheel/{wheel_name}"
    wheel_record = next((record for record in payload if record["path"] == wheel_path), None)
    if wheel_record is None:
        raise PackagingError("internal wheel was not staged")
    manifest = {
        "schema": "dee-thinking-definitive-manifest-v1",
        "archive_name": ARCHIVE_NAME,
        "product": "DEE thinking",
        "product_version": PRODUCT_VERSION,
        "kernel_version": 27,
        "wheel": {
            "path": wheel_path,
            "sha256": wheel_record["sha256"],
            "size": wheel_record["size"],
        },
        "payload": payload,
    }
    manifest_path = stage / "MANIFEST.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    hash_records = payload + [
        {
            "path": "MANIFEST.json",
            "size": manifest_path.stat().st_size,
            "sha256": sha256_bytes(manifest_path.read_bytes()),
        }
    ]
    (stage / "HASHES.sha256").write_text(
        "".join(f"{record['sha256']}  {record['path']}\n" for record in hash_records),
        encoding="utf-8",
        newline="\n",
    )


def _zip_stage(stage: Path, output: Path) -> None:
    fixed_time = (1980, 1, 1, 0, 0, 0)
    with zipfile.ZipFile(
        output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9, allowZip64=True
    ) as package:
        for path in sorted(stage.rglob("*"), key=lambda value: value.relative_to(stage).as_posix()):
            if not path.is_file():
                continue
            name = path.relative_to(stage).as_posix()
            info = zipfile.ZipInfo(name, date_time=fixed_time)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (0o100644 & 0xFFFF) << 16
            package.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    default_project = Path(__file__).resolve().parents[1]
    parser.add_argument("--project-root", type=Path, default=default_project)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--build-root", type=Path)
    parser.add_argument("--install-root", type=Path)
    parser.add_argument("--validation-root", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args(argv)

    project = args.project_root.resolve()
    wheel = args.wheel.resolve()
    build_root = (args.build_root or project / "build-definitive").resolve()
    install_root = (args.install_root or project / "install-definitive").resolve()
    validation_root = (args.validation_root or project / "validation").resolve()
    if wheel.name != WHEEL_NAME:
        raise SystemExit(f"wheel must be named {WHEEL_NAME}")
    if not wheel.is_file():
        raise SystemExit(f"wheel does not exist: {wheel}")
    if args.output is None:
        candidate_directory = Path(tempfile.mkdtemp(prefix="dee-thinking-definitive-"))
        output = candidate_directory / ARCHIVE_NAME
    else:
        output = args.output.resolve()
        if output.name != ARCHIVE_NAME:
            raise SystemExit(f"output must be named {ARCHIVE_NAME}")
        output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and not args.replace:
        raise SystemExit(f"output already exists (use --replace): {output}")

    verifier = project / "tools" / "verify_definitive_delivery.py"
    try:
        files = _collect(project, wheel, build_root, install_root, validation_root)
        with tempfile.TemporaryDirectory(prefix="dee-thinking-definitive-stage-") as temp:
            temporary = Path(temp)
            stage = temporary / "stage"
            stage.mkdir()
            _copy_stage(files, stage)
            _write_metadata(stage, wheel.name)
            candidate = temporary / ARCHIVE_NAME
            _zip_stage(stage, candidate)
            subprocess.run(
                [
                    sys.executable,
                    str(verifier),
                    "--archive",
                    str(candidate),
                    "--external-wheel",
                    str(wheel),
                ],
                check=True,
            )
            publish_tmp = output.with_name(output.name + ".publishing")
            shutil.copy2(candidate, publish_tmp)
            os.replace(publish_tmp, output)
    except (OSError, PackagingError, subprocess.CalledProcessError) as exc:
        print(f"DEFINITIVE_PACKAGE_CREATED=false error={exc}", file=sys.stderr)
        return 1

    print(f"DEFINITIVE_PACKAGE_CREATED=true path={output}")
    print(f"archive_sha256={sha256_bytes(output.read_bytes())}")
    print(f"wheel_sha256={sha256_bytes(wheel.read_bytes())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
