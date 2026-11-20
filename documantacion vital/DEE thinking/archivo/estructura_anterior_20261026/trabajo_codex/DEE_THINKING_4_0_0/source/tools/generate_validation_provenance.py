#!/usr/bin/env python3
"""Bind one fresh Release build and its complete validation evidence to source."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath

from verify_delivery import (
    MAX_EVIDENCE_BYTES,
    existing_file_within_root,
    is_reparse_point,
    release_flags_are_optimized,
)


EXPECTED_TESTS = {
    "kernel_whl_differential", "runtime_contract", "reference_organizations",
    "integration_persistence", "execution_backends", "composition_catalog",
    "composition_snapshot_restore", "core05_phase_memory",
    "cross_process_persistence", "integrated_protocols",
    "basal_product_contract", "independent_consumer_e2e", "examples_smoke",
    "composition_a_e2e", "composition_b_e2e", "catalog_transport_e2e",
    "composition_c6_later_query_e2e", "integrated_protocols_e2e",
    "basal_product_e2e",
}

EXPECTED_RELEASE_FILES = {
    "build/Release/lib/dee_thinking.lib",
    *{
        f"build/Release/bin/{name}.exe"
        for name in (
            "dee_backend_benchmark", "dee_thinking_demo", "dee_thinking_consumer",
            "dee_composition_a", "dee_composition_b", "dee_catalog_transport",
            "dee_composition_c6_later_query", "dee_core05_phase_memory",
            "dee_integrated_protocols", "dee_basal_product",
            "dee_kernel_fixture_tests", "dee_runtime_tests", "dee_reference_tests",
            "dee_integration_persistence_tests", "dee_backend_tests",
            "dee_composition_catalog_tests", "dee_composition_snapshot_tests",
            "dee_core05_phase_memory_tests", "dee_cross_process_persistence",
            "dee_cross_language_bridge", "dee_protocol_checkpoint_bridge",
            "dee_integrated_protocols_tests", "dee_basal_tests",
            "dee_basal_checkpoint_bridge",
        )
    },
}

PROVENANCE_SECTIONS = (
    "include", "src", "bindings", "python", "tests", "examples", "fixtures",
    "benchmarks", "cmake", "tools",
)
PROVENANCE_EXCLUDED_PARTS = {
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "build",
    "dist", "CMakeFiles", "Testing",
}
PROVENANCE_EXCLUDED_SUFFIXES = {
    ".pyc", ".pyo", ".obj", ".o", ".pdb", ".ilk", ".tmp", ".zip",
    ".whl", ".pyd", ".dll", ".lib", ".exe",
}


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
    paths = [
        root / name for name in (
            "CMakeLists.txt", "pyproject.toml", "setup.py", "README.md",
            "PRODUCT_CONTRACT.json", "PROJECT_METADATA.json",
        )
    ]
    for section in PROVENANCE_SECTIONS:
        section_root = root / section
        if not section_root.is_dir() or is_reparse_point(section_root):
            raise RuntimeError(f"missing or reparse-point provenance section: {section_root}")
        for candidate in section_root.rglob("*"):
            if is_reparse_point(candidate):
                raise RuntimeError(f"reparse points are forbidden in provenance source: {candidate}")
            if not candidate.is_file():
                continue
            relative = candidate.relative_to(root)
            if any(part in PROVENANCE_EXCLUDED_PARTS for part in relative.parts):
                continue
            # Wheel builds materialize setuptools metadata below python/.  It
            # is deliberately excluded by package_3_0.py, so it cannot be part
            # of the source identity bound by BUILD_PROVENANCE either.
            if any(part.casefold().endswith(".egg-info") for part in relative.parts):
                continue
            if candidate.suffix.lower() in PROVENANCE_EXCLUDED_SUFFIXES:
                continue
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


def validate_ctest_junit(blob: bytes) -> list[str]:
    try:
        root = ET.fromstring(blob)
    except ET.ParseError as exc:
        raise RuntimeError(f"invalid CTest JUnit XML: {exc}") from exc
    cases = list(root.iter("testcase"))
    names = [case.attrib.get("name", "") for case in cases]
    failures = [
        case.attrib.get("name", "") for case in cases
        if case.find("failure") is not None or case.find("error") is not None
    ]
    if failures:
        raise RuntimeError(f"CTest JUnit contains failures: {failures}")
    if len(names) != len(set(names)) or set(names) != EXPECTED_TESTS:
        raise RuntimeError(
            "CTest 3.0 matrix mismatch: "
            f"count={len(names)}, missing={sorted(EXPECTED_TESTS - set(names))}, "
            f"extra={sorted(set(names) - EXPECTED_TESTS)}"
        )
    return names


def validate_ctest_log(blob: bytes) -> None:
    text = blob.decode("utf-8", errors="replace")
    required = {
        f"dee_ctest_expected_tests={len(EXPECTED_TESTS)}",
        "dee_ctest_exit_code=0",
        "100% tests passed",
    }
    missing = sorted(item for item in required if item not in text)
    if missing:
        raise RuntimeError(f"CTest log lacks release-success markers: {missing}")


def validate_build_log(blob: bytes) -> None:
    text = blob.decode("utf-8", errors="replace")
    required = {
        "dee_install_relocation_copy=true",
        "dee_installed_consumer_v3=true",
        "dee_basal_consumer_v3=true",
        "dee_build_pipeline_exit_code=0",
    }
    missing = sorted(item for item in required if item not in text)
    if missing:
        raise RuntimeError(f"build log lacks 3.0 consumer markers: {missing}")


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
    names = validate_ctest_junit(junit_blob)
    validate_ctest_log(ctest_log_blob)
    validate_build_log(build_log_blob)

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
