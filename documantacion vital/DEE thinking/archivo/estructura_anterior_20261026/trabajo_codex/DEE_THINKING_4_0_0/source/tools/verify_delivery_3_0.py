#!/usr/bin/env python3
"""Verify the self-contained DEE thinking 3.0.0 delivery archive.

The verifier is intentionally independent from the build tree.  It validates
ZIP structure and CRCs, the top-level manifest and digest ledger, wheel RECORD
digests, public version declarations, the frozen v27 kernel source digest, and
the minimum C++/Python product payload needed by downstream consumers.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath
from typing import Any


ARCHIVE_NAME = "DEE_thinking_3_0_0_ENTREGA_FINAL_RESULTADOS.zip"
PRODUCT_VERSION = "3.0.0"
WHEEL_NAME = "dee_thinking-3.0.0-cp313-cp313-win_amd64.whl"
KERNEL_SHA256 = "fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31"
SEED_SHA256 = "cd09a4d94f72e00d9a5163c8dfd1d62e1528f1d146e4cb44ae23d261b3da09e6"
MANIFEST_SCHEMA = "dee-thinking-3.0.0-delivery-manifest-v1"
EVIDENCE_SCHEMA = "dee-thinking-3.0.0-evidence-manifest-v1"
CLEAN_EXTRACTION_SCHEMA = "dee-thinking-3.0.0-clean-extraction-v1"
SOURCE_2_2_SHA256 = "ce088e902888e5ce0f61296d405b14b8acccc183cd73fcbd0fe7bc4eb8ce7cc3"
WHEEL_2_2_SHA256 = "39e6bc7cb8a6be74bfe105ae9e284eff4d3a4cc213780f410a048d3fd75301c6"
MBP4_SHA256 = "4d20d893d04486de047c66ce76c9f7dad067158941b553025bd946b7dc6ce086"
MBP4_MEMBER_COUNT = 294

EXPECTED_CTEST_TESTS = {
    "kernel_whl_differential",
    "runtime_contract",
    "reference_organizations",
    "integration_persistence",
    "execution_backends",
    "composition_catalog",
    "composition_snapshot_restore",
    "core05_phase_memory",
    "cross_process_persistence",
    "integrated_protocols",
    "basal_product_contract",
    "independent_consumer_e2e",
    "examples_smoke",
    "composition_a_e2e",
    "composition_b_e2e",
    "catalog_transport_e2e",
    "composition_c6_later_query_e2e",
    "integrated_protocols_e2e",
    "basal_product_e2e",
}
EXPECTED_COMMAND_KINDS = {
    "wheel_smoke",
    "unittest",
    "cross_language",
    "consumer",
    "benchmark",
}
EXPECTED_COMPATIBILITY_CHECKS = {
    "channel_protocol_raw_clock_exact",
    "kernel_constants_equal",
    "same_snapshot_bytes_loaded",
    "snapshot_after_32_ticks_raw_clock_exact",
    "snapshot_start_raw_clock_exact",
    "versions_are_2_2_0_and_3_0_0",
}
EXPECTED_BUILD_ARTIFACTS = {
    "build/Release/lib/dee_thinking.lib",
    "build/Release/bin/dee_basal_tests.exe",
    "build/Release/bin/dee_basal_checkpoint_bridge.exe",
    "build/Release/bin/dee_backend_benchmark.exe",
}
PROVENANCE_SOURCE_TOP = {
    "CMakeLists.txt",
    "pyproject.toml",
    "setup.py",
    "README.md",
    "PRODUCT_CONTRACT.json",
    "PROJECT_METADATA.json",
}
PROVENANCE_SOURCE_SECTIONS = {
    "include",
    "src",
    "bindings",
    "python",
    "tests",
    "examples",
    "fixtures",
    "benchmarks",
    "cmake",
    "tools",
}

REQUIRED_MEMBERS = {
    "README.md",
    "PRODUCT_CONTRACT.json",
    "PROJECT_METADATA.json",
    "THIRD_PARTY_NOTICES.md",
    "MANIFEST.json",
    "HASHES.sha256",
    f"wheel/{WHEEL_NAME}",
    "source/CMakeLists.txt",
    "source/pyproject.toml",
    "source/setup.py",
    "source/src/kernel_v27.cpp",
    "source/src/runtime.cpp",
    "source/src/basal.cpp",
    "source/src/observation.cpp",
    "source/src/genealogy.cpp",
    "source/src/diagnostics.cpp",
    "source/bindings/dee_thinking_pybind.cpp",
    "source/include/dee_thinking/version.hpp",
    "source/include/dee_thinking/runtime.hpp",
    "source/include/dee_thinking/basal.hpp",
    "source/include/dee_thinking/observation.hpp",
    "source/include/dee_thinking/genealogy.hpp",
    "source/include/dee_thinking/diagnostics.hpp",
    "source/python/dee_thinking/__init__.py",
    "source/python/dee_thinking/__init__.pyi",
    "source/python/dee_thinking/_native.pyi",
    "source/fixtures/mbp4/OBP_FRESH_VALIDATED_T32.deetsnap",
    "source/fixtures/mbp4/regressions/MANIFEST.json",
    "source/tests/basal_tests.cpp",
    "source/tests/python/test_basal_api.py",
    "source/tests/python/test_mbp4_regressions.py",
    "source/tests/python/basal_cross_language_driver.py",
    "source/tests/consumer_basal/CMakeLists.txt",
    "source/tests/consumer_basal/main.cpp",
    "source/tests/installed_consumer/CMakeLists.txt",
    "source/tests/installed_consumer/main.cpp",
    "source/examples/basal_product.cpp",
    "source/tools/build_windows.ps1",
    "source/tools/generate_validation_provenance.py",
    "source/tools/run_validation_3_0.py",
    "source/tools/package_3_0.py",
    "source/tools/verify_delivery_3_0.py",
    "install/include/dee_thinking/runtime.hpp",
    "install/include/dee_thinking/basal.hpp",
    "install/include/dee_thinking/observation.hpp",
    "install/include/dee_thinking/genealogy.hpp",
    "install/include/dee_thinking/diagnostics.hpp",
    "install/include/dee_thinking/version.hpp",
    "install/share/dee_thinking/fixtures/mbp4/OBP_FRESH_VALIDATED_T32.deetsnap",
    "install/lib/cmake/dee_thinking/dee_thinkingConfig.cmake",
    "install/lib/cmake/dee_thinking/dee_thinkingConfigVersion.cmake",
    "install/lib/cmake/dee_thinking/dee_thinkingTargets.cmake",
    "install/lib/cmake/dee_thinking/dee_thinkingTargets-release.cmake",
    "install/lib/dee_thinking.lib",
    "docs/API_AND_SCOPE.md",
    "docs/BUILD_AND_RECONSTRUCTION.md",
    "docs/MIGRATION_2_2_TO_3_0.md",
    "validation/VALIDATION_SUMMARY.json",
    "validation/BUILD_PROVENANCE.json",
    "validation/COMMAND_RESULTS.json",
    "validation/PROVENANCE.json",
    "validation/ctest.junit.xml",
    "validation/ctest.log",
    "validation/build_and_installed_consumer.log",
    "validation/compatibility_2_2_to_3_0/comparison.json",
    "validation/compatibility_2_2_to_3_0/result_2_2_0.json",
    "validation/compatibility_2_2_to_3_0/result_3_0_0.json",
    "validation/compatibility_2_2_to_3_0/run_version_probe.py",
    "validation/compatibility_2_2_to_3_0/compare_results.py",
    "validation/CLEAN_EXTRACTION_RESULT.json",
    "evidence/EVIDENCE_MANIFEST.json",
}

REQUIRED_PREFIXES = (
    "docs/",
    "evidence/",
    "validation/",
    "install/lib/cmake/dee_thinking/",
)

FORBIDDEN_SOURCE_PARTS = {
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
FORBIDDEN_SOURCE_SUFFIXES = {
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


class VerificationError(RuntimeError):
    """Raised for an invalid delivery archive."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_member_name(name: str) -> bool:
    if not name or "\\" in name or name.startswith("/") or "\x00" in name:
        return False
    path = PurePosixPath(name)
    return (
        not path.is_absolute()
        and path.as_posix() == name
        and not path.parts[0].endswith(":")
        and all(part not in {"", ".", ".."} for part in path.parts)
    )


def _read_json(package: zipfile.ZipFile, name: str) -> dict[str, Any]:
    try:
        value = json.loads(package.read(name).decode("utf-8"))
    except (KeyError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerificationError(f"invalid JSON member {name}: {exc}") from exc
    if not isinstance(value, dict):
        raise VerificationError(f"JSON member must be an object: {name}")
    return value


def _parse_hashes(data: bytes) -> dict[str, str]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise VerificationError("HASHES.sha256 is not UTF-8") from exc
    records: dict[str, str] = {}
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line:
            continue
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if match is None:
            raise VerificationError(f"malformed HASHES.sha256 line {line_number}")
        digest, name = match.groups()
        if not _safe_member_name(name):
            raise VerificationError(f"unsafe HASHES.sha256 path: {name}")
        key = name.casefold()
        if key in {item.casefold() for item in records}:
            raise VerificationError(f"duplicate/case-colliding hash path: {name}")
        records[name] = digest
    return records


def _require_sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise VerificationError(f"{label} is not a lowercase SHA-256 digest")
    return value


def _require_true(value: Any, label: str) -> None:
    if value is not True:
        raise VerificationError(f"{label} must be true")


def _validate_ctest_junit(data: bytes) -> set[str]:
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise VerificationError(f"validation/ctest.junit.xml is invalid: {exc}") from exc
    cases = list(root.iter("testcase"))
    names = [case.attrib.get("name", "") for case in cases]
    failed = [
        name for name, case in zip(names, cases)
        if case.find("failure") is not None
        or case.find("error") is not None
        or case.find("skipped") is not None
    ]
    if failed:
        raise VerificationError(f"CTest JUnit has failed/error/skipped tests: {failed}")
    if len(names) != len(set(names)) or set(names) != EXPECTED_CTEST_TESTS:
        raise VerificationError(
            "CTest JUnit matrix mismatch; "
            f"missing={sorted(EXPECTED_CTEST_TESTS - set(names))}, "
            f"extra={sorted(set(names) - EXPECTED_CTEST_TESTS)}"
        )
    return set(names)


def _assert_fixture_evidence(package: zipfile.ZipFile) -> dict[str, Any]:
    name = "source/fixtures/mbp4/regressions/MANIFEST.json"
    manifest = _read_json(package, name)
    if manifest.get("schema") != "dee-thinking.mbp4-regression-fixtures.v1":
        raise VerificationError("MBP4 regression fixture manifest schema mismatch")
    source = manifest.get("source_archive")
    if not isinstance(source, dict):
        raise VerificationError("MBP4 regression fixture source_archive is missing")
    if source.get("sha256") != MBP4_SHA256 or source.get("member_count") != MBP4_MEMBER_COUNT:
        raise VerificationError("MBP4 regression fixtures do not identify the authoritative archive")
    fixtures = manifest.get("fixtures")
    if not isinstance(fixtures, list) or len(fixtures) != 15:
        raise VerificationError("MBP4 regression fixture manifest must contain 15 fixtures")
    covered: set[str] = set()
    fixture_names: set[str] = set()
    for index, record in enumerate(fixtures):
        if not isinstance(record, dict):
            raise VerificationError(f"MBP4 fixture record {index} is not an object")
        relative = record.get("path")
        if not isinstance(relative, str) or not _safe_member_name(relative):
            raise VerificationError(f"MBP4 fixture record {index} has an unsafe path")
        member = f"source/fixtures/mbp4/regressions/{relative}"
        if member in fixture_names:
            raise VerificationError(f"MBP4 fixture manifest duplicates {member}")
        fixture_names.add(member)
        try:
            data = package.read(member)
        except KeyError as exc:
            raise VerificationError(f"MBP4 fixture is absent from source/: {member}") from exc
        digest = _require_sha256(record.get("sha256"), f"MBP4 fixture {relative} digest")
        if sha256_bytes(data) != digest or record.get("bytes") != len(data):
            raise VerificationError(f"MBP4 fixture identity mismatch: {member}")
        source_member = record.get("source_member")
        if not isinstance(source_member, str) or not _safe_member_name(source_member):
            raise VerificationError(f"MBP4 fixture {relative} lacks a safe source member")
        covers = record.get("covers")
        if not isinstance(covers, list) or not covers or not all(isinstance(item, str) for item in covers):
            raise VerificationError(f"MBP4 fixture {relative} lacks regression coverage")
        covered.update(covers)
    if covered != {f"R{index}" for index in range(1, 9)}:
        raise VerificationError(f"MBP4 fixture coverage mismatch: {sorted(covered)}")
    return {
        "fixture_count": len(fixtures),
        "covered_regressions": sorted(covered),
        "manifest_sha256": sha256_bytes(package.read(name)),
    }


def _assert_evidence_manifest(
    package: zipfile.ZipFile, fixture_report: dict[str, Any]
) -> None:
    manifest = _read_json(package, "evidence/EVIDENCE_MANIFEST.json")
    if manifest.get("schema") != EVIDENCE_SCHEMA:
        raise VerificationError("evidence/EVIDENCE_MANIFEST.json schema mismatch")
    inputs = manifest.get("inputs")
    if not isinstance(inputs, dict):
        raise VerificationError("evidence manifest inputs must be an object")
    expected = {
        "dee_thinking_2_2_0_source_zip": SOURCE_2_2_SHA256,
        "dee_thinking_2_2_0_wheel": WHEEL_2_2_SHA256,
        "mbp4_archive": MBP4_SHA256,
        "kernel_v27_source": KERNEL_SHA256,
    }
    for key, digest in expected.items():
        record = inputs.get(key)
        if not isinstance(record, dict) or record.get("sha256") != digest:
            raise VerificationError(f"evidence manifest input {key!r} is absent or has the wrong digest")
    mbp4 = inputs["mbp4_archive"]
    if mbp4.get("member_count") != MBP4_MEMBER_COUNT:
        raise VerificationError("evidence manifest MBP4 member count mismatch")
    fixtures = manifest.get("fixture_manifest")
    if not isinstance(fixtures, dict):
        raise VerificationError("evidence manifest fixture_manifest is missing")
    if (
        fixtures.get("path") != "source/fixtures/mbp4/regressions/MANIFEST.json"
        or fixtures.get("sha256") != fixture_report["manifest_sha256"]
        or fixtures.get("fixture_count") != fixture_report["fixture_count"]
    ):
        raise VerificationError("evidence manifest does not bind the delivered MBP4 fixture manifest")


def _command_output(command: dict[str, Any]) -> str:
    return f"{command.get('stdout', '')}\n{command.get('stderr', '')}"


def _source_tree_identity(package: zipfile.ZipFile) -> tuple[str, int]:
    relative_names: list[str] = []
    for member in package.namelist():
        if not member.startswith("source/"):
            continue
        relative = PurePosixPath(member).relative_to("source")
        if (
            relative.as_posix() in PROVENANCE_SOURCE_TOP
            or relative.parts[0] in PROVENANCE_SOURCE_SECTIONS
        ):
            relative_names.append(relative.as_posix())
    relative_names.sort()
    digest = hashlib.sha256()
    for relative in relative_names:
        encoded = relative.encode("utf-8")
        data = package.read(f"source/{relative}")
        digest.update(len(encoded).to_bytes(4, "little"))
        digest.update(encoded)
        digest.update(len(data).to_bytes(8, "little"))
        digest.update(data)
    return digest.hexdigest(), len(relative_names)


def _assert_command_evidence(package: zipfile.ZipFile) -> dict[str, Any]:
    document = _read_json(package, "validation/COMMAND_RESULTS.json")
    if document.get("schema_version") != 1:
        raise VerificationError("validation command-results schema mismatch")
    summary = document.get("summary")
    commands = document.get("commands")
    if not isinstance(summary, dict) or not isinstance(commands, list) or not commands:
        raise VerificationError("validation command results are incomplete")
    if (
        summary.get("status") != "passed"
        or summary.get("required_failed") != 0
        or summary.get("failed") != 0
        or summary.get("total") != len(commands)
        or summary.get("passed") != len(commands)
    ):
        raise VerificationError("external validation command suite did not pass completely")
    by_kind: dict[str, list[dict[str, Any]]] = {}
    names: set[str] = set()
    for index, command in enumerate(commands):
        if not isinstance(command, dict):
            raise VerificationError(f"validation command {index} is not an object")
        name = command.get("name")
        kind = command.get("kind")
        if not isinstance(name, str) or not name or name in names:
            raise VerificationError("validation commands must have unique non-empty names")
        names.add(name)
        if not isinstance(kind, str):
            raise VerificationError(f"validation command {name} has no kind")
        if (
            command.get("status") != "passed"
            or command.get("exit_code") != 0
            or command.get("timed_out") is not False
            or command.get("launch_error") is not None
        ):
            raise VerificationError(f"external validation command did not pass: {name}")
        for field in ("stdout_log", "stderr_log"):
            relative = command.get(field)
            if (
                not isinstance(relative, str)
                or not _safe_member_name(relative)
                or not relative.startswith("logs/")
            ):
                raise VerificationError(f"validation command {name} has an unsafe {field}")
            member = f"validation/{relative}"
            try:
                logged = package.read(member).decode("utf-8")
            except (KeyError, UnicodeDecodeError) as exc:
                raise VerificationError(f"validation command log is absent/invalid: {member}") from exc
            inline_field = "stdout" if field == "stdout_log" else "stderr"
            inline = command.get(inline_field)
            if not isinstance(inline, str) or logged.replace("\r\n", "\n") != inline.replace("\r\n", "\n"):
                raise VerificationError(f"validation command inline/log mismatch: {name}/{field}")
        by_kind.setdefault(kind, []).append(command)
    missing_kinds = EXPECTED_COMMAND_KINDS - set(by_kind)
    if missing_kinds:
        raise VerificationError(f"external validation lacks command kinds: {sorted(missing_kinds)}")

    combined = {
        kind: "\n".join(_command_output(command) for command in by_kind[kind])
        for kind in EXPECTED_COMMAND_KINDS
    }
    marker_sets = {
        "wheel_smoke": {
            "dee_thinking_version=3.0.0",
            "kernel_version=27",
            "module_origin_site_packages=true",
            "basal_api=true",
        },
        "unittest": {"Ran ", "OK"},
        "cross_language": {
            "cpp_to_python raw_clock_observation_exact=true",
            "python_to_cpp raw_clock_observation_exact=true",
        },
        "consumer": {
            "installed_find_package_consumer=true",
            "dee_thinking_version=3.0.0",
        },
        "benchmark": {"ALL_RAW_CLOCK_EXACT=true"},
    }
    for kind, markers in marker_sets.items():
        absent = sorted(marker for marker in markers if marker not in combined[kind])
        if absent:
            raise VerificationError(f"{kind} evidence lacks semantic markers: {absent}")
    return {"command_count": len(commands), "kinds": sorted(EXPECTED_COMMAND_KINDS)}


def _assert_command_provenance(package: zipfile.ZipFile, wheel_sha256: str) -> None:
    provenance = _read_json(package, "validation/PROVENANCE.json")
    if provenance.get("schema_version") != 1:
        raise VerificationError("external command provenance schema mismatch")
    inputs = provenance.get("inputs")
    if not isinstance(inputs, dict):
        raise VerificationError("external command provenance inputs are missing")
    wheel = inputs.get("wheel")
    kernel = inputs.get("kernel")
    if not isinstance(wheel, dict) or wheel.get("type") != "file" or wheel.get("sha256") != wheel_sha256:
        raise VerificationError("external command provenance is stale for the embedded wheel")
    if not isinstance(kernel, dict) or kernel.get("type") != "file" or kernel.get("sha256") != KERNEL_SHA256:
        raise VerificationError("external command provenance used the wrong kernel source")
    toolchain = provenance.get("toolchain")
    if not isinstance(toolchain, dict):
        raise VerificationError("external command provenance lacks a toolchain")
    for tool in ("python", "cmake", "cxx"):
        description = toolchain.get(tool)
        if (
            not isinstance(description, dict)
            or description.get("exists") is not True
            or description.get("type") != "file"
            or not isinstance(description.get("version_probe"), dict)
        ):
            raise VerificationError(f"external command provenance lacks tool {tool}")


def _assert_compatibility(package: zipfile.ZipFile, wheel_sha256: str) -> None:
    old_result = _read_json(
        package, "validation/compatibility_2_2_to_3_0/result_2_2_0.json"
    )
    new_result = _read_json(
        package, "validation/compatibility_2_2_to_3_0/result_3_0_0.json"
    )
    for label, result, version in (
        ("2.2.0", old_result, "2.2.0"),
        ("3.0.0", new_result, "3.0.0"),
    ):
        if (
            result.get("schema") != "dee_thinking.compatibility_probe.v1"
            or result.get("runtime_version") != version
            or result.get("kernel_modulus") != 19665
            or result.get("reducer_cap") != 19664
        ):
            raise VerificationError(f"compatibility probe {label} has the wrong identity")
        build_info = result.get("build_info")
        if (
            not isinstance(build_info, dict)
            or build_info.get("product_version") != version
            or build_info.get("kernel_version") != 27
            or build_info.get("native_module") is not True
            or build_info.get("delegates_to_dee_universe_v27") is not False
        ):
            raise VerificationError(f"compatibility probe {label} did not use the expected native product")
        cases = result.get("cases")
        if not isinstance(cases, dict) or set(cases) != {
            "legacy_channel_protocol", "legacy_snapshot_seed"
        }:
            raise VerificationError(f"compatibility probe {label} case set mismatch")
        seed = cases["legacy_snapshot_seed"]
        if not isinstance(seed, dict) or seed.get("snapshot_sha256") != SEED_SHA256:
            raise VerificationError(f"compatibility probe {label} used the wrong snapshot seed")

    if old_result["cases"]["legacy_channel_protocol"] != new_result["cases"]["legacy_channel_protocol"]:
        raise VerificationError("2.2 and 3.0 channel-protocol evidence differs")
    old_seed = dict(old_result["cases"]["legacy_snapshot_seed"])
    new_seed = dict(new_result["cases"]["legacy_snapshot_seed"])
    old_seed.pop("snapshot_path", None)
    new_seed.pop("snapshot_path", None)
    if old_seed != new_seed:
        raise VerificationError("2.2 and 3.0 snapshot continuation evidence differs")

    comparison = _read_json(
        package, "validation/compatibility_2_2_to_3_0/comparison.json"
    )
    if comparison.get("schema") != "dee_thinking.compatibility_comparison.v1":
        raise VerificationError("2.2-to-3.0 compatibility schema mismatch")
    _require_true(comparison.get("all_checks_passed"), "compatibility all_checks_passed")
    checks = comparison.get("checks")
    if not isinstance(checks, dict) or set(checks) != EXPECTED_COMPATIBILITY_CHECKS:
        raise VerificationError("compatibility check set mismatch")
    for key in EXPECTED_COMPATIBILITY_CHECKS:
        _require_true(checks.get(key), f"compatibility check {key}")
    versions = comparison.get("versions")
    if not isinstance(versions, dict) or versions != {"v22": "2.2.0", "v30": "3.0.0"}:
        raise VerificationError("compatibility version pair mismatch")
    provenance = comparison.get("wheel_provenance")
    if not isinstance(provenance, dict):
        raise VerificationError("compatibility wheel provenance is missing")
    v22 = provenance.get("v22")
    v30 = provenance.get("v30")
    if not isinstance(v22, dict) or v22.get("sha256") != WHEEL_2_2_SHA256:
        raise VerificationError("compatibility evidence used the wrong 2.2.0 wheel")
    if not isinstance(v30, dict) or v30.get("sha256") != wheel_sha256:
        raise VerificationError("compatibility evidence is stale for the embedded 3.0.0 wheel")


def _assert_clean_extraction(package: zipfile.ZipFile, wheel_sha256: str) -> None:
    result = _read_json(package, "validation/CLEAN_EXTRACTION_RESULT.json")
    if result.get("schema") != CLEAN_EXTRACTION_SCHEMA or result.get("status") != "passed":
        raise VerificationError("clean-extraction result is absent or not passed")
    if result.get("wheel_sha256") != wheel_sha256 or result.get("kernel_sha256") != KERNEL_SHA256:
        raise VerificationError("clean-extraction result is stale for this product payload")
    checks = result.get("checks")
    required = {
        "archive_extract",
        "wheel_install_fresh_venv",
        "python_import_external_cwd",
        "python_public_api",
        "seed_load",
        "documented_python_use",
        "cpp_find_package_configure",
        "cpp_find_package_build",
        "cpp_installed_consumer_run",
    }
    if not isinstance(checks, dict) or not required.issubset(checks):
        raise VerificationError("clean-extraction result lacks required checks")
    for check in required:
        _require_true(checks.get(check), f"clean-extraction check {check}")


def _assert_validation_evidence(
    package: zipfile.ZipFile, wheel_sha256: str
) -> dict[str, Any]:
    junit = package.read("validation/ctest.junit.xml")
    ctest_log = package.read("validation/ctest.log")
    build_log = package.read("validation/build_and_installed_consumer.log")
    tests = _validate_ctest_junit(junit)
    ctest_text = ctest_log.decode("utf-8", errors="replace")
    for marker in (
        f"dee_ctest_expected_tests={len(EXPECTED_CTEST_TESTS)}",
        "dee_ctest_exit_code=0",
        "100% tests passed",
    ):
        if marker not in ctest_text:
            raise VerificationError(f"CTest log lacks release marker {marker!r}")
    build_text = build_log.decode("utf-8", errors="replace")
    for marker in (
        "dee_install_relocation_copy=true",
        "dee_installed_consumer_v3=true",
        "dee_basal_consumer_v3=true",
        "dee_build_pipeline_exit_code=0",
    ):
        if marker not in build_text:
            raise VerificationError(f"build log lacks release marker {marker!r}")

    summary = _read_json(package, "validation/VALIDATION_SUMMARY.json")
    if summary.get("schema") != "dee-thinking-validation-summary-v2":
        raise VerificationError("validation summary schema mismatch")
    if (
        summary.get("configuration") != "Release"
        or summary.get("all_passed") is not True
        or summary.get("test_count") != len(EXPECTED_CTEST_TESTS)
        or set(summary.get("tests", [])) != tests
        or summary.get("installed_relocated_consumer") is not True
    ):
        raise VerificationError("validation summary does not describe the exact passing Release matrix")
    linked = {
        "ctest_junit_sha256": sha256_bytes(junit),
        "ctest_log_sha256": sha256_bytes(ctest_log),
        "build_log_sha256": sha256_bytes(build_log),
    }
    for key, digest in linked.items():
        if summary.get(key) != digest:
            raise VerificationError(f"validation summary does not bind {key}")

    provenance = _read_json(package, "validation/BUILD_PROVENANCE.json")
    if (
        provenance.get("schema") != "dee-thinking-build-provenance-v1"
        or provenance.get("configuration") != "Release"
        or provenance.get("installed_relocated_consumer") is not True
    ):
        raise VerificationError("build provenance does not describe a relocated Release build")
    source_tree_sha256, source_file_count = _source_tree_identity(package)
    if (
        provenance.get("source_tree_sha256") != source_tree_sha256
        or provenance.get("source_file_count") != source_file_count
    ):
        raise VerificationError("build provenance does not bind the delivered source tree")
    for key, digest in linked.items():
        if provenance.get(key) != digest:
            raise VerificationError(f"build provenance does not bind {key}")
    artifacts = provenance.get("release_artifact_sha256")
    if not isinstance(artifacts, dict) or not EXPECTED_BUILD_ARTIFACTS.issubset(artifacts):
        raise VerificationError("build provenance lacks key 3.0 Release artifacts")
    for name, digest in artifacts.items():
        _require_sha256(digest, f"Release artifact {name}")
    installed_library = package.read("install/lib/dee_thinking.lib")
    if artifacts["build/Release/lib/dee_thinking.lib"] != sha256_bytes(installed_library):
        raise VerificationError("installed static library differs from the validated Release library")

    command_report = _assert_command_evidence(package)
    _assert_command_provenance(package, wheel_sha256)
    _assert_compatibility(package, wheel_sha256)
    _assert_clean_extraction(package, wheel_sha256)
    return {
        "ctest_count": len(tests),
        "external_commands": command_report,
        "compatibility_verified": True,
        "clean_extraction_verified": True,
    }


def _assert_version_declarations(package: zipfile.ZipFile) -> None:
    pyproject = package.read("source/pyproject.toml").decode("utf-8")
    if not re.search(r'(?m)^version\s*=\s*"3\.0\.0"\s*$', pyproject):
        raise VerificationError("source/pyproject.toml does not declare version 3.0.0")

    cmake = package.read("source/CMakeLists.txt").decode("utf-8")
    if not re.search(r"project\s*\([^)]*VERSION\s+3\.0\.0\b", cmake, re.IGNORECASE | re.DOTALL):
        raise VerificationError("source/CMakeLists.txt does not declare project version 3.0.0")

    version_hpp = package.read("source/include/dee_thinking/version.hpp").decode("utf-8")
    if not re.search(r'\bkProductVersion\s*=\s*"3\.0\.0"\s*;', version_hpp):
        raise VerificationError("source version.hpp does not expose kProductVersion 3.0.0")
    if not re.search(r'\bkKernelVersion\s*=\s*"DEE v27"\s*;', version_hpp):
        raise VerificationError("source version.hpp does not expose frozen kernel version DEE v27")

    contract = _read_json(package, "PRODUCT_CONTRACT.json")
    contract_version = contract.get("product_version", contract.get("version"))
    if contract_version != PRODUCT_VERSION:
        raise VerificationError(
            f"PRODUCT_CONTRACT.json version is {contract_version!r}, expected {PRODUCT_VERSION!r}"
        )
    metadata = _read_json(package, "PROJECT_METADATA.json")
    if metadata.get("product_version") != PRODUCT_VERSION:
        raise VerificationError("PROJECT_METADATA.json product_version mismatch")
    kernel_metadata = metadata.get("kernel")
    if not isinstance(kernel_metadata, dict) or kernel_metadata.get("integrated_source_sha256") != KERNEL_SHA256:
        raise VerificationError("PROJECT_METADATA.json frozen kernel provenance mismatch")


def _verify_wheel(wheel_data: bytes) -> dict[str, Any]:
    try:
        wheel = zipfile.ZipFile(io.BytesIO(wheel_data))
    except zipfile.BadZipFile as exc:
        raise VerificationError(f"embedded wheel is not a ZIP: {exc}") from exc
    with wheel:
        bad = wheel.testzip()
        if bad is not None:
            raise VerificationError(f"embedded wheel CRC failure: {bad}")
        names = wheel.namelist()
        unsafe = [name for name in names if not _safe_member_name(name)]
        if unsafe:
            raise VerificationError(f"embedded wheel has unsafe members: {unsafe[:5]}")
        if len(names) != len(set(names)) or len(names) != len({name.casefold() for name in names}):
            raise VerificationError("embedded wheel has duplicate/case-colliding members")
        required = {
            "dee_thinking/__init__.py",
            "dee_thinking/__init__.pyi",
            "dee_thinking/_native.pyi",
            "dee_thinking/py.typed",
            "dee_thinking/data/OBP_FRESH_VALIDATED_T32.deetsnap",
            "dee_thinking-3.0.0.dist-info/METADATA",
            "dee_thinking-3.0.0.dist-info/WHEEL",
            "dee_thinking-3.0.0.dist-info/RECORD",
        }
        missing = sorted(required - set(names))
        if missing:
            raise VerificationError(f"embedded wheel is missing members: {missing}")
        native = [name for name in names if re.fullmatch(r"dee_thinking/_native[^/]*\.pyd", name)]
        if len(native) != 1:
            raise VerificationError(f"embedded wheel must contain one native extension, found {native}")
        if len(wheel.read(native[0])) < 100_000:
            raise VerificationError("embedded native extension is implausibly small")

        init_source = wheel.read("dee_thinking/__init__.py").decode("utf-8")
        stub = wheel.read("dee_thinking/_native.pyi").decode("utf-8")
        for symbol in (
            "create_relational_world",
            "create_contextual_world",
            "reference_seed_path",
            "kernel_identity",
        ):
            if f"def {symbol}" not in init_source:
                raise VerificationError(f"embedded Python package omits helper {symbol}")
        for symbol in (
            "class Runtime",
            "class BasalWorld",
            "class BasalConfig",
            "class ResearchStateEdit",
            "class PassiveTracker",
            "def inspect_write_gate",
        ):
            if symbol not in stub:
                raise VerificationError(f"embedded Python stub omits public API {symbol}")

        metadata = wheel.read("dee_thinking-3.0.0.dist-info/METADATA").decode("utf-8")
        if not re.search(r"(?m)^Name:\s*dee-thinking\s*$", metadata, re.IGNORECASE):
            raise VerificationError("embedded wheel METADATA has the wrong project name")
        if not re.search(r"(?m)^Version:\s*3\.0\.0\s*$", metadata):
            raise VerificationError("embedded wheel METADATA has the wrong version")

        wheel_meta = wheel.read("dee_thinking-3.0.0.dist-info/WHEEL").decode("utf-8")
        if not re.search(r"(?m)^Tag:\s*cp313-cp313-win_amd64\s*$", wheel_meta):
            raise VerificationError("embedded wheel does not declare cp313-cp313-win_amd64")

        record_name = "dee_thinking-3.0.0.dist-info/RECORD"
        rows = list(csv.reader(io.StringIO(wheel.read(record_name).decode("utf-8"))))
        record_paths: set[str] = set()
        for row in rows:
            if len(row) != 3:
                raise VerificationError("embedded wheel RECORD has a malformed row")
            name, digest_field, size_field = row
            if name in record_paths:
                raise VerificationError(f"embedded wheel RECORD duplicates {name}")
            record_paths.add(name)
            if name == record_name:
                if digest_field or size_field:
                    raise VerificationError("wheel RECORD self-row must omit digest and size")
                continue
            if name not in names:
                raise VerificationError(f"wheel RECORD references absent member {name}")
            if not digest_field.startswith("sha256="):
                raise VerificationError(f"wheel RECORD lacks sha256 digest for {name}")
            raw_digest = hashlib.sha256(wheel.read(name)).digest()
            encoded = base64.urlsafe_b64encode(raw_digest).rstrip(b"=").decode("ascii")
            if digest_field != f"sha256={encoded}":
                raise VerificationError(f"wheel RECORD digest mismatch for {name}")
            if size_field != str(len(wheel.read(name))):
                raise VerificationError(f"wheel RECORD size mismatch for {name}")
        if set(names) != record_paths:
            omitted = sorted(set(names) - record_paths)
            raise VerificationError(f"wheel RECORD omits members: {omitted}")
        return {
            "members": len(names),
            "native_extension": native[0],
            "native_extension_size": len(wheel.read(native[0])),
            "public_api_surface_verified": True,
            "record_verified": True,
        }


def verify_archive(
    archive: Path,
    *,
    require_canonical_name: bool = True,
    expected_kernel_sha256: str = KERNEL_SHA256,
) -> dict[str, Any]:
    if not archive.is_file():
        raise VerificationError(f"archive does not exist: {archive}")
    if require_canonical_name and archive.name != ARCHIVE_NAME:
        raise VerificationError(f"archive must be named {ARCHIVE_NAME}")

    archive_sha256 = hashlib.sha256(archive.read_bytes()).hexdigest()
    try:
        package = zipfile.ZipFile(archive)
    except zipfile.BadZipFile as exc:
        raise VerificationError(f"invalid ZIP: {exc}") from exc

    with package:
        bad = package.testzip()
        if bad is not None:
            raise VerificationError(f"ZIP CRC failure: {bad}")
        infos = package.infolist()
        names = [item.filename for item in infos]
        if any(item.is_dir() for item in infos):
            raise VerificationError("directory entries are not permitted in the canonical ZIP")
        unsafe = [name for name in names if not _safe_member_name(name)]
        if unsafe:
            raise VerificationError(f"unsafe ZIP member names: {unsafe[:5]}")
        if len(names) != len(set(names)):
            raise VerificationError("ZIP contains duplicate member names")
        if len(names) != len({name.casefold() for name in names}):
            raise VerificationError("ZIP contains case-colliding member names")
        missing = sorted(REQUIRED_MEMBERS - set(names))
        if missing:
            raise VerificationError(f"delivery is missing required members: {missing}")
        for prefix in REQUIRED_PREFIXES:
            if not any(name.startswith(prefix) for name in names):
                raise VerificationError(f"delivery has no payload under {prefix}")
        if not any(
            name.startswith("install/lib/") and PurePosixPath(name).suffix.casefold() in {".lib", ".a"}
            for name in names
        ):
            raise VerificationError("install/ does not contain the C++ static library")

        source_violations: list[str] = []
        for name in names:
            if not name.startswith("source/"):
                continue
            relative = PurePosixPath(name).relative_to("source")
            parts = {part.casefold() for part in relative.parts}
            if parts & FORBIDDEN_SOURCE_PARTS:
                source_violations.append(name)
            if any(part.casefold().endswith(".egg-info") for part in relative.parts):
                source_violations.append(name)
            if relative.suffix.casefold() in FORBIDDEN_SOURCE_SUFFIXES:
                source_violations.append(name)
        if source_violations:
            raise VerificationError(f"generated/binary files leaked into source/: {source_violations[:10]}")

        manifest = _read_json(package, "MANIFEST.json")
        if manifest.get("schema") != MANIFEST_SCHEMA:
            raise VerificationError("MANIFEST.json schema mismatch")
        if manifest.get("archive_name") != ARCHIVE_NAME:
            raise VerificationError("MANIFEST.json archive_name mismatch")
        if manifest.get("product_version") != PRODUCT_VERSION:
            raise VerificationError("MANIFEST.json product_version mismatch")
        if manifest.get("kernel_version") != 27:
            raise VerificationError("MANIFEST.json kernel_version mismatch")

        payload = manifest.get("payload")
        if not isinstance(payload, list):
            raise VerificationError("MANIFEST.json payload must be a list")
        manifest_records: dict[str, dict[str, Any]] = {}
        for record in payload:
            if not isinstance(record, dict):
                raise VerificationError("MANIFEST.json payload record is not an object")
            name = record.get("path")
            if not isinstance(name, str) or not _safe_member_name(name):
                raise VerificationError("MANIFEST.json contains an unsafe payload path")
            if name.casefold() in {item.casefold() for item in manifest_records}:
                raise VerificationError(f"MANIFEST.json duplicates/case-collides {name}")
            manifest_records[name] = record

        expected_payload_names = set(names) - {"MANIFEST.json", "HASHES.sha256"}
        if set(manifest_records) != expected_payload_names:
            absent = sorted(expected_payload_names - set(manifest_records))
            extra = sorted(set(manifest_records) - expected_payload_names)
            raise VerificationError(f"manifest/member set mismatch; absent={absent[:5]} extra={extra[:5]}")
        for name, record in manifest_records.items():
            data = package.read(name)
            if record.get("size") != len(data):
                raise VerificationError(f"MANIFEST.json size mismatch for {name}")
            if record.get("sha256") != sha256_bytes(data):
                raise VerificationError(f"MANIFEST.json digest mismatch for {name}")

        hashes = _parse_hashes(package.read("HASHES.sha256"))
        expected_hash_names = expected_payload_names | {"MANIFEST.json"}
        if set(hashes) != expected_hash_names:
            absent = sorted(expected_hash_names - set(hashes))
            extra = sorted(set(hashes) - expected_hash_names)
            raise VerificationError(f"HASHES/member set mismatch; absent={absent[:5]} extra={extra[:5]}")
        for name, digest in hashes.items():
            if sha256_bytes(package.read(name)) != digest:
                raise VerificationError(f"HASHES.sha256 mismatch for {name}")

        kernel = package.read("source/src/kernel_v27.cpp")
        kernel_sha256 = sha256_bytes(kernel)
        if kernel_sha256 != expected_kernel_sha256:
            raise VerificationError(
                f"frozen kernel digest mismatch: {kernel_sha256}, expected {expected_kernel_sha256}"
            )
        kernel_manifest = manifest.get("kernel")
        if not isinstance(kernel_manifest, dict) or kernel_manifest.get("sha256") != kernel_sha256:
            raise VerificationError("MANIFEST.json kernel record mismatch")

        wheel_record = manifest.get("wheel")
        if not isinstance(wheel_record, dict):
            raise VerificationError("MANIFEST.json wheel record is missing")
        wheel_member = f"wheel/{WHEEL_NAME}"
        wheel_data = package.read(wheel_member)
        if wheel_record.get("path") != wheel_member:
            raise VerificationError("MANIFEST.json wheel path mismatch")
        if wheel_record.get("sha256") != sha256_bytes(wheel_data):
            raise VerificationError("MANIFEST.json wheel digest mismatch")
        if wheel_record.get("size") != len(wheel_data):
            raise VerificationError("MANIFEST.json wheel size mismatch")

        _assert_version_declarations(package)
        wheel_report = _verify_wheel(wheel_data)

        for header in (
            "runtime.hpp",
            "basal.hpp",
            "observation.hpp",
            "genealogy.hpp",
            "diagnostics.hpp",
            "version.hpp",
        ):
            if package.read(f"source/include/dee_thinking/{header}") != package.read(
                f"install/include/dee_thinking/{header}"
            ):
                raise VerificationError(f"installed public header differs from source: {header}")
        if len(package.read("install/lib/dee_thinking.lib")) < 100_000:
            raise VerificationError("installed C++ static library is implausibly small")
        install_config = package.read(
            "install/lib/cmake/dee_thinking/dee_thinkingConfig.cmake"
        ).decode("utf-8")
        install_version = package.read(
            "install/lib/cmake/dee_thinking/dee_thinkingConfigVersion.cmake"
        ).decode("utf-8")
        install_targets = package.read(
            "install/lib/cmake/dee_thinking/dee_thinkingTargets.cmake"
        ).decode("utf-8")
        install_targets_release = package.read(
            "install/lib/cmake/dee_thinking/dee_thinkingTargets-release.cmake"
        ).decode("utf-8")
        if "dee_thinkingTargets.cmake" not in install_config:
            raise VerificationError("installed CMake config does not load its exported targets")
        if not re.search(r'set\(PACKAGE_VERSION\s+"3\.0\.0"\)', install_version):
            raise VerificationError("installed CMake version file does not declare 3.0.0")
        if "add_library(DEE::thinking STATIC IMPORTED)" not in install_targets:
            raise VerificationError("installed CMake targets omit DEE::thinking")
        if "dee_thinking.lib" not in install_targets_release:
            raise VerificationError("installed Release target does not reference dee_thinking.lib")

        for root_name in ("README.md", "PRODUCT_CONTRACT.json", "PROJECT_METADATA.json", "THIRD_PARTY_NOTICES.md"):
            if package.read(root_name) != package.read(f"source/{root_name}"):
                raise VerificationError(f"root/source duplicate differs: {root_name}")
        source_seed = package.read("source/fixtures/mbp4/OBP_FRESH_VALIDATED_T32.deetsnap")
        install_seed = package.read("install/share/dee_thinking/fixtures/mbp4/OBP_FRESH_VALIDATED_T32.deetsnap")
        if source_seed != install_seed or sha256_bytes(source_seed) != SEED_SHA256:
            raise VerificationError("source/install MBP4 seed identity mismatch")
        with zipfile.ZipFile(io.BytesIO(wheel_data)) as wheel:
            wheel_seed = wheel.read("dee_thinking/data/OBP_FRESH_VALIDATED_T32.deetsnap")
        if wheel_seed != source_seed:
            raise VerificationError("wheel/source MBP4 seed identity mismatch")

        fixture_report = _assert_fixture_evidence(package)
        _assert_evidence_manifest(package, fixture_report)
        validation_report = _assert_validation_evidence(package, sha256_bytes(wheel_data))

    return {
        "schema": "dee-thinking-3.0.0-zip-verification-v1",
        "archive": str(archive.resolve()),
        "archive_name": archive.name,
        "archive_sha256": archive_sha256,
        "archive_size": archive.stat().st_size,
        "product_version": PRODUCT_VERSION,
        "kernel_version": 27,
        "kernel_sha256": expected_kernel_sha256,
        "member_count": len(names),
        "crc_verified": True,
        "manifest_verified": True,
        "hashes_verified": True,
        "version_declarations_verified": True,
        "source_cleanliness_verified": True,
        "public_headers_source_install_exact": True,
        "primary_evidence": fixture_report,
        "validation": validation_report,
        "wheel": wheel_report,
        "status": "PASS",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--allow-noncanonical-name", action="store_true")
    parser.add_argument("--kernel-sha256", default=KERNEL_SHA256)
    args = parser.parse_args(argv)
    try:
        report = verify_archive(
            args.archive.resolve(),
            require_canonical_name=not args.allow_noncanonical_name,
            expected_kernel_sha256=args.kernel_sha256,
        )
    except VerificationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.report is not None:
        target = args.report.resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
