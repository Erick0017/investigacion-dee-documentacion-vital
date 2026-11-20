#!/usr/bin/env python3
"""Structural verifier for the DEE thinking 2.2.0 definitive delivery.

This verifier is intentionally independent from the legacy Entrega 02 and
preintegration verifiers.  It never executes the scientific tests; it checks
that the already-produced evidence, native install tree and CPython wheel are
packaged coherently and without development/cache material.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any


ARCHIVE_NAME = "DEE_thinking_ENTREGA_02_DEFINITIVA_RESULTADOS.zip"
PRODUCT_VERSION = "2.2.0"
WHEEL_NAME = "dee_thinking-2.2.0-cp313-cp313-win_amd64.whl"
KERNEL_PORT_SHA256 = (
    "fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31"
)
KERNEL_CANONICAL_HISTORICAL_SHA256 = (
    "44a80f7863d78f596099ddf7d41c9947fa8513503f65067097f1f3b05a8207ab"
)
PROTOCOL_IDS = {
    "delay_position_bank.core05.nrh05.v1",
    "destination_repertoires.core07.c7h02.v1",
    "trained_redundancy_repair.core17.v1",
    "accessibility.history_conditioned_finite_response.v1",
    "reusable_lineage_revision.c7h03.v1",
    "environmental_demux_return.v1",
}
ALLOWED_TOP_LEVEL = {
    "CMakeLists.txt",
    "HASHES.sha256",
    "MANIFEST.json",
    "PROJECT_METADATA.json",
    "README.md",
    "THIRD_PARTY_NOTICES.md",
    "pyproject.toml",
    "setup.py",
    "artifacts",
    "benchmarks",
    "bindings",
    "cmake",
    "docs",
    "evidence",
    "examples",
    "fixtures",
    "include",
    "install",
    "python",
    "src",
    "tests",
    "tools",
    "validation",
    "wheel",
}
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
    "build-definitive",
    "build-wheel",
    "install-definitive",
}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo", ".obj", ".o", ".ilk", ".tmp"}
REQUIRED = {
    "CMakeLists.txt",
    "PROJECT_METADATA.json",
    "README.md",
    "THIRD_PARTY_NOTICES.md",
    "pyproject.toml",
    "setup.py",
    "benchmarks/backend_benchmark.cpp",
    "include/dee_thinking/integrated_protocols.hpp",
    "include/dee_thinking/runtime.hpp",
    "src/integrated_protocols.cpp",
    "src/kernel_v27.cpp",
    "src/runtime.cpp",
    "bindings/dee_thinking_pybind.cpp",
    "python/dee_thinking/__init__.py",
    "cmake/python/dee_thinking_python.cmake",
    "cmake/python/validate_wheel.ps1",
    "examples/integrated_protocols.cpp",
    "tests/integrated_protocols_tests.cpp",
    "tests/python/test_wheel_api.py",
    "tests/python/test_integrated_protocols.py",
    "tests/protocol_checkpoint_bridge.cpp",
    "tests/python/protocol_checkpoint_bridge.py",
    "tests/installed_consumer/main.cpp",
    "docs/DEFINITIVE_INTEGRATION_REPORT.md",
    "docs/ARCHITECTURE_AND_BUILD.md",
    "docs/CAPABILITY_CONTRACTS.md",
    "docs/TEST_MATRIX_DEFINITIVE.md",
    "evidence/laboratory_final/results.json",
    "evidence/laboratory_final/SCIENTIFIC_REPORT.md",
    "tools/build_definitive.ps1",
    "tools/package_definitive.py",
    "tools/verify_definitive_delivery.py",
    "validation/FINAL_VALIDATION_SUMMARY.json",
    "install/include/dee_thinking/integrated_protocols.hpp",
    "install/lib/dee_thinking.lib",
    "install/lib/cmake/dee_thinking/dee_thinkingConfig.cmake",
    "artifacts/native/bin/dee_integrated_protocols_tests.exe",
    "artifacts/native/bin/dee_integrated_protocols.exe",
    "artifacts/native/bin/dee_cross_language_bridge.exe",
    "artifacts/native/bin/dee_protocol_checkpoint_bridge.exe",
    f"wheel/{WHEEL_NAME}",
    "MANIFEST.json",
    "HASHES.sha256",
}


class VerificationError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json_object(data: bytes, name: str) -> dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerificationError(f"{name} is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise VerificationError(f"{name} must contain a JSON object")
    return value


def _safe_name(name: str) -> PurePosixPath:
    if "\\" in name or name.startswith("/") or re.match(r"^[A-Za-z]:", name):
        raise VerificationError(f"unsafe archive path: {name!r}")
    path = PurePosixPath(name)
    if not name or any(part in {"", ".", ".."} for part in path.parts):
        raise VerificationError(f"unsafe archive path: {name!r}")
    if path.parts[0] not in ALLOWED_TOP_LEVEL:
        raise VerificationError(f"unexpected top-level entry: {name}")
    lowered = {part.casefold() for part in path.parts}
    if lowered & {part.casefold() for part in FORBIDDEN_PARTS}:
        raise VerificationError(f"forbidden development/cache path: {name}")
    if any(part.casefold().endswith(".egg-info") for part in path.parts):
        raise VerificationError(f"egg-info must be regenerated, not delivered: {name}")
    if path.suffix.casefold() in FORBIDDEN_SUFFIXES:
        raise VerificationError(f"forbidden temporary/object file: {name}")
    if path.suffix.casefold() == ".zip":
        raise VerificationError(f"nested ZIP is forbidden: {name}")
    return path


def _wheel_metadata(wheel_data: bytes) -> None:
    try:
        with zipfile.ZipFile(io.BytesIO(wheel_data), "r") as wheel:
            names: set[str] = set()
            folded_names: set[str] = set()
            for info in wheel.infolist():
                if info.is_dir():
                    continue
                name = info.filename
                path = PurePosixPath(name)
                if (
                    "\\" in name
                    or name.startswith("/")
                    or re.match(r"^[A-Za-z]:", name)
                    or any(part in {"", ".", ".."} for part in path.parts)
                ):
                    raise VerificationError(f"unsafe wheel path: {name!r}")
                folded = name.casefold()
                if name in names or folded in folded_names:
                    raise VerificationError(f"duplicate/case-colliding wheel entry: {name}")
                mode = (info.external_attr >> 16) & 0xFFFF
                if mode and stat.S_ISLNK(mode):
                    raise VerificationError(f"wheel symlink is forbidden: {name}")
                if any(part.casefold() == "__pycache__" for part in path.parts):
                    raise VerificationError(f"wheel cache entry is forbidden: {name}")
                if path.suffix.casefold() in {".pyc", ".pyo"}:
                    raise VerificationError(f"wheel bytecode cache is forbidden: {name}")
                names.add(name)
                folded_names.add(folded)
            metadata_names = [
                name for name in names if name.endswith(".dist-info/METADATA")
            ]
            if len(metadata_names) != 1:
                raise VerificationError("wheel must contain exactly one METADATA file")
            metadata = wheel.read(metadata_names[0]).decode("utf-8", errors="strict")
            if "Name: dee-thinking\n" not in metadata.replace("\r\n", "\n"):
                raise VerificationError("wheel project name is not dee-thinking")
            if f"Version: {PRODUCT_VERSION}\n" not in metadata.replace("\r\n", "\n"):
                raise VerificationError("wheel version is not 2.2.0")
            if "dee_thinking/__init__.py" not in names:
                raise VerificationError("wheel is missing dee_thinking/__init__.py")
            native = [
                name
                for name in names
                if name.startswith("dee_thinking/_native") and name.endswith(".pyd")
            ]
            if len(native) != 1:
                raise VerificationError("wheel must contain one native CPython .pyd")
            wheel_names = [name for name in names if name.endswith(".dist-info/WHEEL")]
            if len(wheel_names) != 1:
                raise VerificationError("wheel must contain exactly one WHEEL metadata file")
            wheel_metadata = wheel.read(wheel_names[0]).decode("utf-8", errors="strict")
            normalized_wheel_metadata = wheel_metadata.replace("\r\n", "\n")
            if "Tag: cp313-cp313-win_amd64\n" not in normalized_wheel_metadata:
                raise VerificationError("wheel tag is not cp313-cp313-win_amd64")
            if "root-is-purelib: false\n" not in normalized_wheel_metadata.lower():
                raise VerificationError("native wheel incorrectly declares itself pure Python")
            if any("dee_universe_v27" in name for name in names):
                raise VerificationError("wheel embeds the old dee_universe_v27 package")
    except zipfile.BadZipFile as exc:
        raise VerificationError(f"invalid wheel ZIP: {exc}") from exc


def _validate_metadata(metadata: dict[str, Any]) -> None:
    if metadata.get("product") != "DEE thinking":
        raise VerificationError("PROJECT_METADATA product mismatch")
    if metadata.get("product_version") != PRODUCT_VERSION:
        raise VerificationError("PROJECT_METADATA version mismatch")
    if metadata.get("delivery") != "ENTREGA 02 DEFINITIVA":
        raise VerificationError("PROJECT_METADATA delivery mismatch")
    kernel = metadata.get("kernel")
    if not isinstance(kernel, dict) or kernel.get("version") != 27:
        raise VerificationError("PROJECT_METADATA kernel version mismatch")
    if kernel.get("law_modified") is not False:
        raise VerificationError("PROJECT_METADATA must state law_modified=false")
    if (
        kernel.get("canonical_historical_source_sha256")
        != KERNEL_CANONICAL_HISTORICAL_SHA256
    ):
        raise VerificationError("canonical historical kernel source hash mismatch")
    if (
        kernel.get("integrated_port_source_sha256_before_product_changes")
        != KERNEL_PORT_SHA256
    ):
        raise VerificationError("integrated kernel port source hash mismatch")
    protocols = metadata.get("integrated_protocols")
    if (
        not isinstance(protocols, list)
        or len(protocols) != len(PROTOCOL_IDS)
        or set(protocols) != PROTOCOL_IDS
    ):
        raise VerificationError("PROJECT_METADATA integrated protocol set mismatch")
    not_exported = metadata.get("not_exported")
    if not isinstance(not_exported, dict) or "functional_replication_fanout" not in not_exported:
        raise VerificationError("PROJECT_METADATA must retain F3 as not exported")
    target = metadata.get("wheel_target")
    expected_target = {
        "import": "dee_thinking",
        "python": "CPython 3.13",
        "abi": "cp313",
        "platform": "win_amd64",
    }
    if not isinstance(target, dict) or any(target.get(k) != v for k, v in expected_target.items()):
        raise VerificationError("PROJECT_METADATA wheel target mismatch")
    validation = metadata.get("validation")
    if not isinstance(validation, dict):
        raise VerificationError("PROJECT_METADATA validation object is missing")
    status = validation.get("status")
    if status not in {"VERIFIED", "PARTIAL"}:
        raise VerificationError(
            "validation.status must be VERIFIED or PARTIAL before definitive packaging"
        )
    if status == "VERIFIED":
        required_results = {
            "native_ctest",
            "python_tests",
            "clean_install",
            "cross_language_persistence",
            "clean_extract_rebuild",
        }
        missing = sorted(
            key
            for key in required_results
            if validation.get(key) not in {True, "PASS"}
        )
        if missing:
            raise VerificationError(
                "VERIFIED metadata has empty validation results: " + ", ".join(missing)
            )


def _validate_validation_summary(
    summary: dict[str, Any], metadata_status: str
) -> None:
    if summary.get("schema") != "dee-thinking-definitive-validation-v1":
        raise VerificationError("final validation summary schema mismatch")
    if summary.get("product_version") != PRODUCT_VERSION:
        raise VerificationError("final validation summary version mismatch")
    if summary.get("status") != metadata_status:
        raise VerificationError("validation summary and PROJECT_METADATA status differ")
    checks = summary.get("checks")
    required = {
        "native_ctest",
        "installed_consumer",
        "wheel_clean_install",
        "python_api",
        "cross_language_persistence",
        "clean_extract_rebuild",
    }
    if not isinstance(checks, dict) or set(checks) != required:
        raise VerificationError(
            "validation summary must contain exactly the six acceptance checks"
        )
    allowed = {"PASS", "FAIL", "PENDING", "NOT_EXECUTED"}
    if any(value not in allowed for value in checks.values()):
        raise VerificationError("validation summary contains an invalid check status")
    if metadata_status == "VERIFIED" and any(value != "PASS" for value in checks.values()):
        raise VerificationError("VERIFIED delivery requires every acceptance check to PASS")


def verify_delivery(archive: Path, external_wheel: Path) -> dict[str, Any]:
    archive = archive.resolve()
    external_wheel = external_wheel.resolve()
    if archive.name != ARCHIVE_NAME:
        raise VerificationError(
            f"archive must be named {ARCHIVE_NAME}, got {archive.name}"
        )
    if external_wheel.name != WHEEL_NAME:
        raise VerificationError(
            f"external wheel must be named {WHEEL_NAME}, got {external_wheel.name}"
        )
    if not archive.is_file() or not external_wheel.is_file():
        raise VerificationError("archive or external wheel does not exist")

    external_wheel_data = external_wheel.read_bytes()
    _wheel_metadata(external_wheel_data)

    try:
        with zipfile.ZipFile(archive, "r") as package:
            infos = [item for item in package.infolist() if not item.is_dir()]
            names: set[str] = set()
            casefolded: set[str] = set()
            blobs: dict[str, bytes] = {}
            for info in infos:
                path = _safe_name(info.filename)
                normalized = path.as_posix()
                folded = normalized.casefold()
                if normalized in names or folded in casefolded:
                    raise VerificationError(f"duplicate/case-colliding entry: {normalized}")
                mode = (info.external_attr >> 16) & 0xFFFF
                if mode and stat.S_ISLNK(mode):
                    raise VerificationError(f"symlink entry is forbidden: {normalized}")
                names.add(normalized)
                casefolded.add(folded)
                blobs[normalized] = package.read(info)
    except zipfile.BadZipFile as exc:
        raise VerificationError(f"invalid definitive ZIP: {exc}") from exc

    missing = sorted(REQUIRED - names)
    if missing:
        raise VerificationError("required package entries missing: " + ", ".join(missing))
    if not any(name.startswith("fixtures/") for name in names):
        raise VerificationError("fixtures directory is empty")
    if not any(name.startswith("validation/") for name in names):
        raise VerificationError("validation evidence is missing")
    if not any(name.startswith("install/include/") for name in names):
        raise VerificationError("installed headers are missing")
    if not any(name.startswith("install/lib/") and name.endswith(".lib") for name in names):
        raise VerificationError("installed native library is missing")
    if not any(name.startswith("install/lib/cmake/dee_thinking/") for name in names):
        raise VerificationError("installed CMake package is missing")
    if not any(name.startswith("artifacts/native/bin/") and name.endswith(".exe") for name in names):
        raise VerificationError("built native executables are missing")

    internal_wheel_name = f"wheel/{WHEEL_NAME}"
    internal_wheel = blobs[internal_wheel_name]
    if internal_wheel != external_wheel_data:
        raise VerificationError("internal and external wheel bytes differ")
    _wheel_metadata(internal_wheel)

    manifest = _json_object(blobs["MANIFEST.json"], "MANIFEST.json")
    if manifest.get("schema") != "dee-thinking-definitive-manifest-v1":
        raise VerificationError("manifest schema mismatch")
    if manifest.get("archive_name") != ARCHIVE_NAME:
        raise VerificationError("manifest archive name mismatch")
    if manifest.get("product_version") != PRODUCT_VERSION:
        raise VerificationError("manifest product version mismatch")
    wheel_record = manifest.get("wheel")
    if not isinstance(wheel_record, dict):
        raise VerificationError("manifest wheel record missing")
    if wheel_record.get("path") != internal_wheel_name:
        raise VerificationError("manifest wheel path mismatch")
    if wheel_record.get("sha256") != sha256_bytes(internal_wheel):
        raise VerificationError("manifest wheel hash mismatch")

    payload_names = names - {"MANIFEST.json", "HASHES.sha256"}
    records = manifest.get("payload")
    if not isinstance(records, list):
        raise VerificationError("manifest payload must be a list")
    record_map: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("path"), str):
            raise VerificationError("invalid manifest payload record")
        path = record["path"]
        if path in record_map:
            raise VerificationError(f"duplicate manifest record: {path}")
        record_map[path] = record
    if set(record_map) != payload_names:
        raise VerificationError("manifest payload does not cover exactly the ZIP payload")
    for name in sorted(payload_names):
        record = record_map[name]
        if record.get("size") != len(blobs[name]):
            raise VerificationError(f"manifest size mismatch: {name}")
        if record.get("sha256") != sha256_bytes(blobs[name]):
            raise VerificationError(f"manifest hash mismatch: {name}")

    hash_lines = blobs["HASHES.sha256"].decode("utf-8", errors="strict").splitlines()
    hash_map: dict[str, str] = {}
    for line in hash_lines:
        digest, separator, name = line.partition("  ")
        if not separator or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise VerificationError(f"invalid HASHES.sha256 line: {line!r}")
        if name in hash_map:
            raise VerificationError(f"duplicate hash entry: {name}")
        hash_map[name] = digest
    hashed_names = names - {"HASHES.sha256"}
    if set(hash_map) != hashed_names:
        raise VerificationError("HASHES.sha256 does not cover every non-self entry")
    for name in sorted(hashed_names):
        if hash_map[name] != sha256_bytes(blobs[name]):
            raise VerificationError(f"HASHES.sha256 mismatch: {name}")

    metadata = _json_object(blobs["PROJECT_METADATA.json"], "PROJECT_METADATA.json")
    _validate_metadata(metadata)
    validation_summary = _json_object(
        blobs["validation/FINAL_VALIDATION_SUMMARY.json"],
        "validation/FINAL_VALIDATION_SUMMARY.json",
    )
    _validate_validation_summary(validation_summary, metadata["validation"]["status"])
    if sha256_bytes(blobs["src/kernel_v27.cpp"]) != KERNEL_PORT_SHA256:
        raise VerificationError("integrated kernel source differs from the frozen port")
    cmake = blobs["CMakeLists.txt"].decode("utf-8", errors="strict")
    if "project(dee_thinking VERSION 2.2.0" not in cmake:
        raise VerificationError("CMake product version mismatch")
    pyproject = blobs["pyproject.toml"].decode("utf-8", errors="strict")
    if 'version = "2.2.0"' not in pyproject:
        raise VerificationError("pyproject version mismatch")
    readme = blobs["README.md"].decode("utf-8", errors="strict")
    if "DEE thinking 2.2.0" not in readme or "Entrega 02 definitiva" not in readme:
        raise VerificationError("README does not identify the definitive 2.2.0 product")
    header = blobs["include/dee_thinking/integrated_protocols.hpp"].decode(
        "utf-8", errors="strict"
    )
    for protocol_id in PROTOCOL_IDS:
        if protocol_id not in header:
            raise VerificationError(f"public protocol ID absent from header: {protocol_id}")
    if "fanout.general" in header or "run_functional_fanout" in header:
        raise VerificationError("F3/fan-out must not be exported as a public API")

    return {
        "archive": str(archive),
        "archive_sha256": sha256_bytes(archive.read_bytes()),
        "wheel": str(external_wheel),
        "wheel_sha256": sha256_bytes(external_wheel_data),
        "entry_count": len(names),
        "validation_status": metadata["validation"]["status"],
        "verified": True,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--external-wheel", required=True, type=Path)
    parser.add_argument("--json", action="store_true", help="emit compact JSON")
    args = parser.parse_args(argv)
    try:
        result = verify_delivery(args.archive, args.external_wheel)
    except (OSError, VerificationError) as exc:
        print(f"DEFINITIVE_DELIVERY_VERIFIED=false error={exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        for key, value in result.items():
            print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
