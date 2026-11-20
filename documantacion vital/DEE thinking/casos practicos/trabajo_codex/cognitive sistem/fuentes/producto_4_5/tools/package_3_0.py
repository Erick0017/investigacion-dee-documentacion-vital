#!/usr/bin/env python3
"""Build and atomically publish the DEE thinking 3.0.0 final delivery.

The caller supplies already-built wheel, installed C++ tree, validation
evidence and scientific evidence.  This tool stages a curated clean source
tree, emits MANIFEST.json and HASHES.sha256, creates a deterministic ZIP,
verifies the candidate with ``verify_delivery_3_0.py``, and only then replaces
the official output path.
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
import uuid
import zipfile
from pathlib import Path, PurePosixPath
from typing import Iterable


ARCHIVE_NAME = "DEE_thinking_3_0_0_ENTREGA_FINAL_RESULTADOS.zip"
PRODUCT_VERSION = "3.0.0"
WHEEL_NAME = "dee_thinking-3.0.0-cp313-cp313-win_amd64.whl"
KERNEL_SHA256 = "fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31"
MANIFEST_SCHEMA = "dee-thinking-3.0.0-delivery-manifest-v1"

ROOT_FILES = (
    "README.md",
    "PRODUCT_CONTRACT.json",
    "PROJECT_METADATA.json",
    "THIRD_PARTY_NOTICES.md",
)
SOURCE_TOP_FILES = (
    "CMakeLists.txt",
    "PRODUCT_CONTRACT.json",
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
    "tools",
)
DOC_FILES = (
    "API_AND_SCOPE.md",
    "BUILD_AND_RECONSTRUCTION.md",
    "MIGRATION_2_2_TO_3_0.md",
)

SKIP_PARTS = {
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
    "build",
    "dist",
    "_skbuild",
}
SOURCE_FORBIDDEN_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".obj",
    ".o",
    ".ilk",
    ".tmp",
    ".zip",
    ".whl",
    ".pyd",
    ".dll",
    ".lib",
    ".exe",
}
SENSITIVE_NAMES = {".env", "id_rsa", "id_ed25519", "credentials", "credentials.json"}
SENSITIVE_SUFFIXES = {".pem", ".key", ".pfx", ".p12"}


class PackagingError(RuntimeError):
    """Raised for an invalid or incomplete package input."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _is_link_or_reparse(path: Path) -> bool:
    if path.is_symlink():
        return True
    attributes = getattr(path.lstat(), "st_file_attributes", 0)
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return bool(flag and attributes & flag)


def _unsafe_credentials(relative: Path) -> bool:
    return (
        relative.name.casefold() in SENSITIVE_NAMES
        or relative.suffix.casefold() in SENSITIVE_SUFFIXES
    )


def _tree_files(root: Path, *, source_mode: bool = False) -> Iterable[Path]:
    if not root.is_dir():
        raise PackagingError(f"required directory is missing: {root}")
    if _is_link_or_reparse(root):
        raise PackagingError(f"linked/reparse input root is forbidden: {root}")
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix().casefold()):
        relative = path.relative_to(root)
        parts = {part.casefold() for part in relative.parts}
        if path.is_dir():
            if _is_link_or_reparse(path):
                raise PackagingError(f"linked/reparse directory is forbidden: {path}")
            continue
        if _is_link_or_reparse(path):
            raise PackagingError(f"linked/reparse file is forbidden: {path}")
        if parts & SKIP_PARTS or any(part.casefold().endswith(".egg-info") for part in relative.parts):
            continue
        if _unsafe_credentials(relative):
            raise PackagingError(f"credential-like file is forbidden: {path}")
        if source_mode and relative.suffix.casefold() in SOURCE_FORBIDDEN_SUFFIXES:
            continue
        yield path


def _add_file(
    mapping: dict[str, Path],
    folded_names: set[str],
    archive_name: str,
    source: Path,
) -> None:
    name = PurePosixPath(archive_name).as_posix()
    pure = PurePosixPath(name)
    if pure.is_absolute() or not name or any(part in {"", ".", ".."} for part in pure.parts):
        raise PackagingError(f"unsafe staged path: {archive_name}")
    if name.casefold() in folded_names:
        raise PackagingError(f"duplicate/case-colliding staged path: {name}")
    if not source.is_file() or _is_link_or_reparse(source):
        raise PackagingError(f"staged input is missing or linked: {source}")
    mapping[name] = source
    folded_names.add(name.casefold())


def _add_tree(
    mapping: dict[str, Path],
    folded_names: set[str],
    source_root: Path,
    archive_root: str,
    *,
    source_mode: bool = False,
) -> int:
    count = 0
    for path in _tree_files(source_root, source_mode=source_mode):
        name = (PurePosixPath(archive_root) / path.relative_to(source_root).as_posix()).as_posix()
        _add_file(mapping, folded_names, name, path)
        count += 1
    return count


def _collect(
    project: Path,
    wheel: Path,
    install_root: Path,
    validation_root: Path,
    evidence_root: Path,
) -> dict[str, Path]:
    if not project.is_dir() or _is_link_or_reparse(project):
        raise PackagingError(f"invalid project root: {project}")
    mapping: dict[str, Path] = {}
    folded_names: set[str] = set()

    for name in ROOT_FILES:
        _add_file(mapping, folded_names, name, project / name)
    for name in SOURCE_TOP_FILES:
        _add_file(mapping, folded_names, f"source/{name}", project / name)
    for tree_name in SOURCE_TREES:
        _add_tree(
            mapping,
            folded_names,
            project / tree_name,
            f"source/{tree_name}",
            source_mode=True,
        )

    docs_count = 0
    for name in DOC_FILES:
        _add_file(mapping, folded_names, f"docs/{name}", project / "docs" / name)
        docs_count += 1
    install_count = _add_tree(mapping, folded_names, install_root, "install")
    validation_count = _add_tree(mapping, folded_names, validation_root, "validation")
    evidence_count = _add_tree(mapping, folded_names, evidence_root, "evidence")
    for label, count in (
        ("docs", docs_count),
        ("install", install_count),
        ("validation", validation_count),
        ("evidence", evidence_count),
    ):
        if count == 0:
            raise PackagingError(f"required {label} payload is empty")

    _add_file(mapping, folded_names, f"wheel/{wheel.name}", wheel)
    return mapping


def _copy_stage(mapping: dict[str, Path], stage: Path) -> None:
    for name, source in sorted(mapping.items(), key=lambda item: item[0].casefold()):
        target = stage.joinpath(*PurePosixPath(name).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def _write_metadata(stage: Path) -> None:
    payload: list[dict[str, object]] = []
    section_counts: dict[str, int] = {}
    for path in sorted(stage.rglob("*"), key=lambda item: item.relative_to(stage).as_posix().casefold()):
        if not path.is_file():
            continue
        name = path.relative_to(stage).as_posix()
        data = path.read_bytes()
        payload.append({"path": name, "size": len(data), "sha256": sha256_bytes(data)})
        section = name.split("/", 1)[0] if "/" in name else "root"
        section_counts[section] = section_counts.get(section, 0) + 1

    wheel_path = f"wheel/{WHEEL_NAME}"
    wheel_record = next((record for record in payload if record["path"] == wheel_path), None)
    if wheel_record is None:
        raise PackagingError("wheel was not staged")
    kernel_path = "source/src/kernel_v27.cpp"
    kernel_record = next((record for record in payload if record["path"] == kernel_path), None)
    if kernel_record is None:
        raise PackagingError("frozen kernel source was not staged")
    if kernel_record["sha256"] != KERNEL_SHA256:
        raise PackagingError(
            f"kernel source digest changed: {kernel_record['sha256']}, expected {KERNEL_SHA256}"
        )

    manifest = {
        "schema": MANIFEST_SCHEMA,
        "archive_name": ARCHIVE_NAME,
        "product": "DEE thinking",
        "product_version": PRODUCT_VERSION,
        "kernel_version": 27,
        "kernel": {
            "path": kernel_path,
            "sha256": kernel_record["sha256"],
            "size": kernel_record["size"],
            "status": "frozen-byte-exact",
        },
        "wheel": {
            "path": wheel_path,
            "sha256": wheel_record["sha256"],
            "size": wheel_record["size"],
            "tag": "cp313-cp313-win_amd64",
        },
        "section_file_counts": dict(sorted(section_counts.items())),
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


def _zip_stage(stage: Path, target: Path) -> None:
    fixed_time = (1980, 1, 1, 0, 0, 0)
    with zipfile.ZipFile(
        target,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        allowZip64=True,
    ) as package:
        for path in sorted(stage.rglob("*"), key=lambda item: item.relative_to(stage).as_posix().casefold()):
            if not path.is_file():
                continue
            name = path.relative_to(stage).as_posix()
            info = zipfile.ZipInfo(name, date_time=fixed_time)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (0o100644 & 0xFFFF) << 16
            package.writestr(
                info,
                path.read_bytes(),
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )


def _run_verifier(
    verifier: Path,
    archive: Path,
    *,
    allow_noncanonical_name: bool,
    report: Path | None = None,
) -> None:
    command = [sys.executable, str(verifier), "--archive", str(archive)]
    if allow_noncanonical_name:
        command.append("--allow-noncanonical-name")
    if report is not None:
        command.extend(("--report", str(report)))
    completed = subprocess.run(command, check=False)
    if completed.returncode != 0:
        raise PackagingError(f"delivery verifier failed with exit code {completed.returncode}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    default_project = Path(__file__).resolve().parents[1]
    parser.add_argument("--project-root", type=Path, default=default_project)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--install-root", type=Path, required=True)
    parser.add_argument("--validation-root", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--staging-parent", type=Path)
    parser.add_argument("--verification-report", type=Path)
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--keep-stage", action="store_true")
    args = parser.parse_args(argv)

    project = args.project_root.resolve()
    wheel = args.wheel.resolve()
    install_root = args.install_root.resolve()
    validation_root = args.validation_root.resolve()
    evidence_root = args.evidence_root.resolve()
    output = args.output.resolve()
    if wheel.name != WHEEL_NAME:
        raise SystemExit(f"wheel must be named {WHEEL_NAME}")
    if not wheel.is_file():
        raise SystemExit(f"wheel does not exist: {wheel}")
    if output.name != ARCHIVE_NAME:
        raise SystemExit(f"output must be named {ARCHIVE_NAME}")
    if output.exists() and not args.replace:
        raise SystemExit(f"output exists; pass --replace to publish atomically: {output}")

    verifier = project / "tools" / "verify_delivery_3_0.py"
    if not verifier.is_file():
        raise SystemExit(f"verifier is missing: {verifier}")
    output.parent.mkdir(parents=True, exist_ok=True)
    staging_parent = (args.staging_parent.resolve() if args.staging_parent else project / ".package-stage")
    staging_parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="dee-thinking-3.0.0-", dir=staging_parent))
    candidate = output.parent / f".{output.name}.{uuid.uuid4().hex}.tmp"
    published = False
    try:
        mapping = _collect(project, wheel, install_root, validation_root, evidence_root)
        _copy_stage(mapping, stage)
        _write_metadata(stage)
        _zip_stage(stage, candidate)
        _run_verifier(verifier, candidate, allow_noncanonical_name=True)
        os.replace(candidate, output)
        published = True
        _run_verifier(
            verifier,
            output,
            allow_noncanonical_name=False,
            report=args.verification_report.resolve() if args.verification_report else None,
        )
        print(
            json.dumps(
                {
                    "archive": str(output),
                    "archive_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
                    "archive_size": output.stat().st_size,
                    "stage": str(stage) if args.keep_stage else None,
                    "status": "PUBLISHED_VERIFIED",
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    except (OSError, PackagingError, zipfile.BadZipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    finally:
        if candidate.exists():
            candidate.unlink()
        if not args.keep_stage:
            # ``stage`` is the unique child created by mkdtemp, never the supplied parent.
            shutil.rmtree(stage, ignore_errors=True)
        if published and output.exists() and output.name != ARCHIVE_NAME:
            raise AssertionError("unexpected published archive name")


if __name__ == "__main__":
    raise SystemExit("Legacy 3.0 publisher disabled in the 3.5 source copy. Use package_3_5.py; the original 3.0 artifact is immutable.")
