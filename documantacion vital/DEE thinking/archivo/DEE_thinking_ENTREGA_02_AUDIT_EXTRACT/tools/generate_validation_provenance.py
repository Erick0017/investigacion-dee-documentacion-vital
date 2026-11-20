#!/usr/bin/env python3
"""Bind one fresh Release build and its complete validation evidence to source."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path, PurePosixPath

from verify_delivery import (
    EXPECTED_RELEASE_FILES,
    EXPECTED_TESTS,
    MAX_EVIDENCE_BYTES,
    PROVENANCE_SOURCE_PREFIXES,
    VerificationError,
    existing_file_within_root,
    is_reparse_point,
    payload_name_allowed,
    release_flags_are_optimized,
    validate_build_log,
    validate_ctest_junit,
    validate_ctest_log,
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_bounded(path: Path, maximum: int = MAX_EVIDENCE_BYTES) -> bytes:
    try:
        with path.open("rb") as stream:
            blob = stream.read(maximum + 1)
    except OSError as exc:
        raise RuntimeError(f"cannot read evidence file {path}: {exc}") from exc
    if len(blob) > maximum:
        raise RuntimeError(f"evidence file exceeds {maximum} bytes: {path}")
    return blob


def hash_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def provenance_source_paths(root: Path) -> list[Path]:
    paths = [root / "CMakeLists.txt"]
    sections = sorted({prefix.split("/", 1)[0] for prefix in PROVENANCE_SOURCE_PREFIXES})
    for section in sections:
        section_root = root / section
        if not section_root.is_dir() or is_reparse_point(section_root):
            raise RuntimeError(f"missing or reparse-point provenance section: {section_root}")
        for candidate in section_root.rglob("*"):
            if is_reparse_point(candidate):
                raise RuntimeError(f"reparse points are forbidden in provenance source: {candidate}")
            if not candidate.is_file():
                continue
            relative = candidate.relative_to(root).as_posix()
            if payload_name_allowed(relative):
                paths.append(candidate)
    for path in paths:
        if not existing_file_within_root(path, root):
            raise RuntimeError(f"provenance source escapes its root: {path}")
    return sorted(paths, key=lambda item: item.relative_to(root).as_posix())


def source_tree_hash(root: Path, paths: list[Path]) -> str:
    hasher = hashlib.sha256()
    for path in paths:
        relative = path.relative_to(root).as_posix().encode("utf-8")
        blob = path.read_bytes()
        hasher.update(len(relative).to_bytes(4, "little"))
        hasher.update(relative)
        hasher.update(len(blob).to_bytes(8, "little"))
        hasher.update(blob)
    return hasher.hexdigest()


def cache_value(lines: list[str], key: str) -> str:
    prefix = key + ":"
    for line in lines:
        if line.startswith(prefix):
            return line.partition("=")[2]
    raise RuntimeError(f"missing CMake cache value: {key}")


def atomic_json(path: Path, value: dict[str, object]) -> None:
    blob = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(blob)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--build-root", type=Path, required=True)
    parser.add_argument("--junit", type=Path, required=True)
    parser.add_argument("--ctest-log", type=Path, required=True)
    parser.add_argument("--build-log", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    root = args.project_root.resolve(strict=True)
    build = args.build_root.resolve(strict=True)
    output = args.output_dir.resolve(strict=True)
    expected_output = (root / "validation").resolve(strict=True)
    if output != expected_output:
        raise RuntimeError(f"validation provenance must be written to {expected_output}")

    evidence_paths = {
        "junit": args.junit.resolve(strict=True),
        "ctest_log": args.ctest_log.resolve(strict=True),
        "build_log": args.build_log.resolve(strict=True),
    }
    expected_evidence = {
        "junit": output / "ctest.junit.xml",
        "ctest_log": output / "ctest.log",
        "build_log": output / "build_and_installed_consumer.log",
    }
    if evidence_paths != expected_evidence:
        raise RuntimeError(f"evidence paths must be the delivered validation files: {expected_evidence}")
    for path in evidence_paths.values():
        if not existing_file_within_root(path, output):
            raise RuntimeError(f"unsafe validation evidence path: {path}")

    cache = build / "CMakeCache.txt"
    if not existing_file_within_root(cache, build):
        raise RuntimeError(f"missing or unsafe CMake cache: {cache}")
    cache_lines = cache.read_text(encoding="utf-8").splitlines()
    configuration = cache_value(cache_lines, "CMAKE_BUILD_TYPE")
    flags = cache_value(cache_lines, "CMAKE_CXX_FLAGS_RELEASE")
    if configuration != "Release":
        raise RuntimeError(f"expected Release build, got {configuration}")
    if not release_flags_are_optimized(flags):
        raise RuntimeError(f"invalid effective Release flags: {flags!r}")

    junit_blob = read_bounded(evidence_paths["junit"])
    ctest_log_blob = read_bounded(evidence_paths["ctest_log"])
    build_log_blob = read_bounded(evidence_paths["build_log"])
    try:
        names = validate_ctest_junit(junit_blob)
        validate_ctest_log(ctest_log_blob)
        validate_build_log(build_log_blob)
    except VerificationError as exc:
        raise RuntimeError(str(exc)) from exc

    artifact_paths: dict[str, Path] = {
        name: build.joinpath(*PurePosixPath(name).parts[2:])
        for name in EXPECTED_RELEASE_FILES
    }
    for name, path in artifact_paths.items():
        if not existing_file_within_root(path, build):
            raise RuntimeError(f"missing, escaping, or reparse-point Release artifact {name}: {path}")

    source_paths = provenance_source_paths(root)
    latest_validated_input_ns = max(
        path.stat().st_mtime_ns for path in [*source_paths, *artifact_paths.values()])
    for label, path in evidence_paths.items():
        if path.stat().st_mtime_ns < latest_validated_input_ns:
            raise RuntimeError(f"stale {label} evidence predates source/artifacts: {path}")

    validation = {
        "schema": "dee-thinking-validation-summary-v2",
        "configuration": configuration,
        "all_passed": True,
        "test_count": len(names),
        "tests": sorted(names),
        "ctest_junit_sha256": digest(junit_blob),
        "ctest_log_sha256": digest(ctest_log_blob),
        "installed_relocated_consumer": True,
        "build_log_sha256": digest(build_log_blob),
    }
    provenance = {
        "schema": "dee-thinking-build-provenance-v1",
        "configuration": configuration,
        "cmake_generator": cache_value(cache_lines, "CMAKE_GENERATOR"),
        "cxx_flags_release": flags,
        "source_tree_sha256": source_tree_hash(root, source_paths),
        "source_file_count": len(source_paths),
        "release_artifact_sha256": {
            name: hash_file(path) for name, path in sorted(artifact_paths.items())
        },
        "ctest_junit_sha256": validation["ctest_junit_sha256"],
        "ctest_log_sha256": validation["ctest_log_sha256"],
        "build_log_sha256": validation["build_log_sha256"],
        "installed_relocated_consumer": True,
    }
    atomic_json(output / "VALIDATION_SUMMARY.json", validation)
    atomic_json(output / "BUILD_PROVENANCE.json", provenance)
    print(json.dumps({"generated": True, "tests": len(names), "artifacts": len(artifact_paths)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
