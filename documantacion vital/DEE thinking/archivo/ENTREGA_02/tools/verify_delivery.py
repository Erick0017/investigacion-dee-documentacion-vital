#!/usr/bin/env python3
"""Verify a DEE thinking delivery archive without trusting its metadata.

The verifier uses only the Python standard library.  It validates member names,
CRC/readability, the internal manifest and hash list, the expected delivery
layout, and a clean extraction to a newly-created temporary directory.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import stat
import struct
import subprocess
import tempfile
import unicodedata
import zipfile
import zlib
from pathlib import Path, PurePosixPath
from typing import Any
from xml.etree import ElementTree


MANIFEST_NAME = "MANIFEST.json"
HASHES_NAME = "HASHES.sha256"
EXPECTED_ARCHIVE_NAME = "DEE_thinking_ENTREGA_02_RESULTADOS.zip"
REQUIRED_FILES = {
    "CMakeLists.txt",
    "docs/TECHNICAL_REPORT.md",
    "docs/PENDING.md",
    "validation/backend_benchmark.json",
    "validation/ctest.log",
    "validation/ctest.junit.xml",
    "validation/build_and_installed_consumer.log",
    "validation/VALIDATION_SUMMARY.json",
    "validation/BUILD_PROVENANCE.json",
    MANIFEST_NAME,
    HASHES_NAME,
}
EXPECTED_RELEASE_FILES = {
    "build/Release/lib/dee_thinking.lib",
    *{
        f"build/Release/bin/{name}.exe"
        for name in (
            "dee_backend_benchmark", "dee_thinking_demo", "dee_thinking_consumer",
            "dee_composition_a", "dee_composition_b", "dee_catalog_transport",
            "dee_composition_c6_later_query", "dee_kernel_fixture_tests",
            "dee_runtime_tests", "dee_reference_tests",
            "dee_integration_persistence_tests", "dee_backend_tests",
            "dee_composition_catalog_tests", "dee_composition_snapshot_tests",
        )
    },
}
REQUIRED_PREFIXES = (
    "include/",
    "src/",
    "tests/",
    "examples/",
    "tools/",
    "fixtures/",
    "docs/",
    "build/Release/",
    "validation/",
    "benchmarks/",
    "cmake/",
)
# The current delivery is roughly 10 MiB.  These ceilings leave ample growth
# room without allowing a small verification request to retain gigabytes.
MAX_ARCHIVE_BYTES = 128 * 1024 * 1024
MAX_MEMBER_COUNT = 1024
MAX_MEMBER_UNCOMPRESSED = 64 * 1024 * 1024
MAX_TOTAL_UNCOMPRESSED = 256 * 1024 * 1024
# The canonical DTR fixtures intentionally contain long repeated grids and one
# currently compresses at roughly 294:1.  The hard per-member/total ceilings
# remain the primary allocation bounds.
MAX_COMPRESSION_RATIO = 500
MAX_EVIDENCE_BYTES = 16 * 1024 * 1024
MAX_CONSUMER_OUTPUT_BYTES = 1024 * 1024
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)
TOP_LEVEL_SOURCE_FILES = {"CMakeLists.txt", "README.md", "PROJECT_METADATA.json"}
TOP_LEVEL_FILES = TOP_LEVEL_SOURCE_FILES | {MANIFEST_NAME, HASHES_NAME}
SOURCE_SECTIONS = (
    "include", "src", "tests", "examples", "tools", "fixtures", "docs",
    "validation", "benchmarks", "cmake",
)
SECTION_SUFFIXES = {
    "include": {".hpp"}, "src": {".cpp"},
    "tests": {".cpp", ".hpp", ".txt"}, "examples": {".cpp"},
    "tools": {".py", ".ps1", ".cmd", ".cpp"},
    "fixtures": {".dtr", ".deetsnap", ".json", ".md"},
    "docs": {".md"}, "validation": {".json", ".log", ".xml", ".deetsnap"},
    "benchmarks": {".cpp"}, "cmake": {".in", ".cmake"},
}
SECTION_EXACT_NAMES = {"tests": {"CMakeLists.txt"}}
EXCLUDED_PARTS = {
    ".git", ".vs", ".vscode", "__pycache__", ".pytest_cache",
    "CMakeFiles", "Testing",
}
EXCLUDED_SUFFIXES = {
    ".obj", ".o", ".pch", ".pdb", ".idb", ".ilk", ".tlog",
    ".recipe", ".lastbuildstate", ".cache", ".pyc", ".tmp", ".zip",
}
SENSITIVE_SUFFIXES = {".pem", ".key", ".pfx", ".p12", ".cer", ".crt", ".env"}
SENSITIVE_NAMES = {
    ".env", ".npmrc", ".pypirc", "credentials", "credentials.json",
    "secrets.txt", "id_rsa", "id_ed25519",
}
PROVENANCE_SOURCE_PREFIXES = (
    "include/", "src/", "tests/", "examples/", "fixtures/", "benchmarks/", "cmake/",
)
WINDOWS_RESERVED_STEMS = {
    "con", "prn", "aux", "nul", "clock$", "conin$", "conout$",
    *(f"com{i}" for i in range(1, 10)),
    *(f"lpt{i}" for i in range(1, 10)),
}


class VerificationError(RuntimeError):
    """Raised when an archive does not satisfy the delivery contract."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_sha256(value: object) -> bool:
    return (isinstance(value, str) and len(value) == 64 and
            all(character in "0123456789abcdef" for character in value))


def release_flags_are_optimized(flags: object) -> bool:
    """Accept actual Release flags, never substring matches such as ``-O0``."""
    if not isinstance(flags, str):
        return False
    tokens = re.findall(r'[^\s"]+|"[^"]*"', flags)
    folded = {token.strip('"').casefold() for token in tokens}
    optimizing = {"/o1", "/o2", "/ox", "-o1", "-o2", "-o3", "-os", "-oz", "-ofast"}
    disabling = {"/od", "-o0", "-og"}
    ndebug = {"/dndebug", "-dndebug"}
    undefining = {"/undebug", "-undebug"}
    return bool(folded & optimizing) and not (folded & disabling) and bool(folded & ndebug) and not (folded & undefining)


def is_reparse_point(path: Path) -> bool:
    """Return true for symlinks and Windows junction/reparse-point entries."""
    try:
        metadata = path.lstat()
    except OSError:
        return False
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    attributes = getattr(metadata, "st_file_attributes", 0)
    return path.is_symlink() or bool(attributes & reparse_flag)


def existing_file_within_root(path: Path, root: Path) -> bool:
    """Require a regular file reached without crossing a reparse point."""
    try:
        root_absolute = Path(os.path.abspath(root))
        path_absolute = Path(os.path.abspath(path))
        relative = path_absolute.relative_to(root_absolute)
        cursor = root_absolute
        for part in relative.parts:
            cursor = cursor / part
            if is_reparse_point(cursor):
                return False
        return (path_absolute.is_file() and
                path_absolute.resolve(strict=True).is_relative_to(root_absolute.resolve(strict=True)))
    except (OSError, ValueError):
        return False


def _json_no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise VerificationError(f"Duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def load_json_object(blob: bytes, label: str) -> dict[str, Any]:
    if len(blob) > MAX_EVIDENCE_BYTES:
        raise VerificationError(f"{label} exceeds the evidence-size limit")
    try:
        value = json.loads(
            blob.decode("utf-8"), object_pairs_hook=_json_no_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerificationError(f"Invalid {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise VerificationError(f"{label} root must be an object")
    return value


EXPECTED_TESTS = {
    "kernel_whl_differential", "runtime_contract", "reference_organizations",
    "integration_persistence", "execution_backends", "composition_catalog",
    "composition_snapshot_restore", "independent_consumer_e2e", "examples_smoke",
    "composition_a_e2e", "composition_b_e2e", "catalog_transport_e2e",
    "composition_c6_later_query_e2e",
}


def validate_ctest_junit(blob: bytes) -> list[str]:
    if not blob or len(blob) > MAX_EVIDENCE_BYTES:
        raise VerificationError("CTest JUnit record is empty or too large")
    try:
        root = ElementTree.fromstring(blob)
    except ElementTree.ParseError as exc:
        raise VerificationError(f"Invalid CTest JUnit XML: {exc}") from exc
    cases = list(root.iter("testcase"))
    names = [case.attrib.get("name", "") for case in cases]
    if len(cases) != len(EXPECTED_TESTS) or len(names) != len(set(names)) or set(names) != EXPECTED_TESTS:
        raise VerificationError(
            "CTest JUnit inventory mismatch; "
            f"count={len(cases)}, missing={sorted(EXPECTED_TESTS - set(names))}, "
            f"extra={sorted(set(names) - EXPECTED_TESTS)}"
        )
    rejected_states: list[str] = []
    for case in cases:
        status_value = case.attrib.get("status", "").casefold()
        if status_value in {"disabled", "error", "failed", "failure", "notrun", "skipped"}:
            rejected_states.append(f"{case.attrib.get('name', '')}:{status_value}")
        child_kinds = {child.tag.rsplit("}", 1)[-1].casefold() for child in case}
        if child_kinds.intersection({"failure", "error", "skipped"}):
            rejected_states.append(case.attrib.get("name", ""))
    for suite in root.iter():
        if suite.tag.rsplit("}", 1)[-1].casefold() not in {"testsuite", "testsuites"}:
            continue
        for attribute in ("failures", "errors", "skipped", "disabled"):
            raw_value = suite.attrib.get(attribute)
            if raw_value is not None:
                try:
                    nonzero = int(raw_value) != 0
                except ValueError:
                    nonzero = True
                if nonzero:
                    rejected_states.append(f"{suite.tag}:{attribute}={raw_value}")
    if rejected_states:
        raise VerificationError(f"CTest JUnit contains failed/skipped/disabled cases: {rejected_states}")
    return names


def validate_ctest_log(blob: bytes) -> None:
    if not blob or len(blob) > MAX_EVIDENCE_BYTES:
        raise VerificationError("CTest log is empty or too large")
    text = blob.decode("utf-8-sig", errors="replace")
    if "dee_ctest_exit_code=0" not in text or "dee_ctest_expected_tests=13" not in text:
        raise VerificationError("CTest log lacks the successful 13-test pipeline markers")


def validate_build_log(blob: bytes) -> None:
    if not blob or len(blob) > MAX_EVIDENCE_BYTES:
        raise VerificationError("Build/installed-consumer log is empty or too large")
    text = blob.decode("utf-8-sig", errors="replace")
    if ("installed_find_package_consumer=true" not in text or
            "dee_build_pipeline_exit_code=0" not in text):
        raise VerificationError("Build log lacks the successful relocated-consumer pipeline markers")


def payload_source_tree_hash(blobs: dict[str, bytes]) -> str:
    names = [
        name for name in blobs
        if name == "CMakeLists.txt" or name.startswith(PROVENANCE_SOURCE_PREFIXES)
    ]
    hasher = hashlib.sha256()
    for name in sorted(names):
        encoded = name.encode("utf-8")
        blob = blobs[name]
        hasher.update(len(encoded).to_bytes(4, "little"))
        hasher.update(encoded)
        hasher.update(len(blob).to_bytes(8, "little"))
        hasher.update(blob)
    return hasher.hexdigest()


def _safe_member_name(name: str) -> bool:
    if (not name or "\\" in name or name.startswith("/") or
            any(character in name for character in ':<>"|?*') or
            any(ord(character) < 32 for character in name)):
        return False
    raw_parts = name.split("/")
    if any(part in {"", ".", ".."} for part in raw_parts):
        return False
    path = PurePosixPath(name)
    if path.is_absolute() or tuple(path.parts) != tuple(raw_parts):
        return False
    for part in raw_parts:
        if part.endswith((" ", ".")):
            return False
        normalized = unicodedata.normalize("NFC", part)
        if normalized != part:
            return False
        stem = part.split(".", 1)[0].casefold()
        if stem in WINDOWS_RESERVED_STEMS:
            return False
    return True


def _canonical_member_name(name: str) -> str:
    return unicodedata.normalize("NFC", name).casefold()


def _expected_role(name: str) -> str:
    first = PurePosixPath(name).parts[0]
    roles = {
        "include": "public_header", "src": "native_source",
        "tests": "test_source", "examples": "example_or_independent_consumer_source",
        "tools": "build_validation_tool", "fixtures": "reference_fixture",
        "docs": "documentation", "validation": "validation_output",
        "build": "compiled_release_artifact",
    }
    return roles.get(first, "build_definition")


def payload_name_allowed(name: str) -> bool:
    """One shared allowlist used by both packaging and verification."""
    path = PurePosixPath(name)
    folded_parts = {part.casefold() for part in path.parts}
    if folded_parts.intersection(part.casefold() for part in EXCLUDED_PARTS):
        return False
    if any(part.casefold() in SENSITIVE_NAMES for part in path.parts):
        return False
    if path.suffix.casefold() in SENSITIVE_SUFFIXES or path.suffix.casefold() in EXCLUDED_SUFFIXES:
        return False
    if len(path.parts) == 1:
        return name in TOP_LEVEL_FILES
    section = path.parts[0]
    if section == "build":
        return name in EXPECTED_RELEASE_FILES
    if section not in SECTION_SUFFIXES:
        return False
    suffix = PurePosixPath(path.name).suffix.casefold()
    if path.name in SECTION_EXACT_NAMES.get(section, set()):
        return True
    return suffix in SECTION_SUFFIXES[section]


# Backward-compatible private spelling for local callers/tests.
_payload_name_allowed = payload_name_allowed


def _read_archive_once(archive_path: Path) -> bytes:
    try:
        with archive_path.open("rb") as stream:
            blob = stream.read(MAX_ARCHIVE_BYTES + 1)
    except OSError as exc:
        raise VerificationError(f"Cannot read archive: {exc}") from exc
    if len(blob) > MAX_ARCHIVE_BYTES:
        raise VerificationError("Archive exceeds the compressed-size safety limit")
    return blob


def _parse_hashes(text: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        pieces = line.split("  ", 1)
        if len(pieces) != 2:
            raise VerificationError(
                f"Malformed {HASHES_NAME} line {line_number}: expected two spaces"
            )
        digest, name = pieces
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise VerificationError(f"Invalid SHA-256 at {HASHES_NAME}:{line_number}")
        if not _safe_member_name(name) or name in parsed:
            raise VerificationError(f"Invalid or duplicate hash path: {name!r}")
        parsed[name] = digest
    return parsed


def _validate_canonical_zip_layout(
    archive_blob: bytes, archive: zipfile.ZipFile, infos: list[zipfile.ZipInfo]
) -> None:
    """Reject prefixes, trailers, data descriptors, and noncanonical headers."""
    local_offset = 0
    local_times: dict[str, tuple[int, int]] = {}
    for info in infos:
        if info.header_offset != local_offset or local_offset + 30 > len(archive_blob):
            raise VerificationError(f"Non-canonical local-header offset: {info.filename}")
        fields = struct.unpack_from("<IHHHHHIIIHH", archive_blob, local_offset)
        (signature, version_needed, flags, method, mod_time, mod_date, crc,
         compressed, uncompressed, name_length, extra_length) = fields
        expected_name = info.filename.encode("ascii" if info.filename.isascii() else "utf-8")
        name_start = local_offset + 30
        name_end = name_start + name_length
        if (signature != 0x04034B50 or version_needed != 20 or flags != info.flag_bits or
                method != zipfile.ZIP_DEFLATED or crc != info.CRC or
                compressed != info.compress_size or uncompressed != info.file_size or
                extra_length != 0 or archive_blob[name_start:name_end] != expected_name):
            raise VerificationError(f"Non-canonical local ZIP header: {info.filename}")
        local_times[info.filename] = (mod_time, mod_date)
        local_offset = name_end + info.compress_size
    if local_offset != archive.start_dir:
        raise VerificationError("ZIP contains a prefix, data descriptor, or gap before central directory")

    central_offset = archive.start_dir
    for info in infos:
        if central_offset + 46 > len(archive_blob):
            raise VerificationError("Truncated central directory")
        fields = struct.unpack_from("<IHHHHHHIIIHHHHHII", archive_blob, central_offset)
        (signature, made_by, version_needed, flags, method, mod_time, mod_date, crc,
         compressed, uncompressed, name_length, extra_length, comment_length,
         disk_start, internal_attr, external_attr, header_offset) = fields
        expected_name = info.filename.encode("ascii" if info.filename.isascii() else "utf-8")
        name_start = central_offset + 46
        name_end = name_start + name_length
        if (signature != 0x02014B50 or made_by != ((3 << 8) | 20) or
                version_needed != 20 or flags != info.flag_bits or
                method != zipfile.ZIP_DEFLATED or (mod_time, mod_date) != local_times[info.filename] or
                crc != info.CRC or compressed != info.compress_size or uncompressed != info.file_size or
                extra_length != 0 or comment_length != 0 or disk_start != 0 or
                internal_attr != 0 or external_attr != (0o100644 << 16) or
                header_offset != info.header_offset or archive_blob[name_start:name_end] != expected_name):
            raise VerificationError(f"Non-canonical central ZIP header: {info.filename}")
        central_offset = name_end

    if central_offset + 22 != len(archive_blob):
        raise VerificationError("ZIP has trailing bytes or a non-canonical end record")
    (signature, disk_number, central_disk, disk_entries, total_entries,
     central_size, central_start, comment_length) = struct.unpack_from(
        "<IHHHHIIH", archive_blob, central_offset)
    if (signature != 0x06054B50 or disk_number != 0 or central_disk != 0 or
            disk_entries != len(infos) or total_entries != len(infos) or
            central_size != central_offset - archive.start_dir or
            central_start != archive.start_dir or comment_length != 0):
        raise VerificationError("Non-canonical ZIP end-of-central-directory record")


def verify_archive_bytes(
    archive_blob: bytes,
    archive_label: str,
    *,
    require_official_name: bool = False,
    clean_extract: bool = True,
) -> dict[str, Any]:
    """Verify one immutable in-memory snapshot of an archive."""

    label_path = Path(archive_label)
    if require_official_name and label_path.name != EXPECTED_ARCHIVE_NAME:
        raise VerificationError(
            f"Expected archive name {EXPECTED_ARCHIVE_NAME!r}, got {label_path.name!r}"
        )
    if len(archive_blob) > MAX_ARCHIVE_BYTES:
        raise VerificationError("Archive exceeds the compressed-size safety limit")

    archive_sha256 = hashlib.sha256(archive_blob).hexdigest()
    extracted_files = 0

    try:
        with zipfile.ZipFile(io.BytesIO(archive_blob), "r") as archive:
            if archive.comment:
                raise VerificationError("Archive comment is forbidden in the canonical delivery")
            infos = archive.infolist()
            if len(infos) > MAX_MEMBER_COUNT:
                raise VerificationError("Archive exceeds the member-count safety limit")
            names = [info.filename for info in infos]
            if names != sorted(names):
                raise VerificationError("Archive members are not in canonical sorted order")
            if len(names) != len(set(names)):
                raise VerificationError("Archive contains duplicate member names")
            canonical_names = [_canonical_member_name(name) for name in names]
            if len(canonical_names) != len(set(canonical_names)):
                raise VerificationError("Archive contains names that collide on Windows/Unicode normalization")
            if any(info.is_dir() for info in infos):
                raise VerificationError("Archive must contain files only; empty directory entries found")
            total_uncompressed = 0
            for info in infos:
                name = info.filename
                if not _safe_member_name(name):
                    raise VerificationError(f"Unsafe archive member: {name!r}")
                if not payload_name_allowed(name):
                    raise VerificationError(f"Archive member is outside the reviewed payload allowlist: {name}")
                if name.lower().endswith(".zip"):
                    raise VerificationError(f"Nested ZIP is forbidden: {name}")
                expected_flags = 0 if name.isascii() else 0x800
                if info.flag_bits != expected_flags:
                    raise VerificationError(f"Non-canonical ZIP flags for member: {name}")
                if info.compress_type not in {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED}:
                    raise VerificationError(f"Unsupported compression method for member: {name}")
                mode = (info.external_attr >> 16) & 0xFFFF
                if info.create_system == 3 and mode and stat.S_IFMT(mode) != stat.S_IFREG:
                    raise VerificationError(f"Non-regular archive member is forbidden: {name}")
                if (info.date_time != FIXED_ZIP_TIME or info.compress_type != zipfile.ZIP_DEFLATED or
                        info.create_system != 3 or info.create_version != 20 or
                        info.extract_version != 20 or info.reserved != 0 or info.volume != 0 or
                        info.internal_attr != 0 or mode != 0o100644 or info.extra or info.comment):
                    raise VerificationError(f"Non-canonical ZIP metadata for member: {name}")
                if info.file_size > MAX_MEMBER_UNCOMPRESSED:
                    raise VerificationError(f"Archive member exceeds size limit: {name}")
                total_uncompressed += info.file_size
                if total_uncompressed > MAX_TOTAL_UNCOMPRESSED:
                    raise VerificationError("Archive exceeds total uncompressed-size safety limit")
                if info.file_size and info.compress_size == 0:
                    raise VerificationError(f"Invalid zero compressed size for nonempty member: {name}")
                if (info.compress_size and
                        info.file_size / info.compress_size > MAX_COMPRESSION_RATIO):
                    raise VerificationError(f"Archive member exceeds compression-ratio limit: {name}")

            _validate_canonical_zip_layout(archive_blob, archive, infos)

            missing_files = sorted(REQUIRED_FILES.difference(names))
            if missing_files:
                raise VerificationError(f"Missing required files: {missing_files}")
            missing_prefixes = [
                prefix for prefix in REQUIRED_PREFIXES if not any(n.startswith(prefix) for n in names)
            ]
            if missing_prefixes:
                raise VerificationError(f"Missing/non-populated delivery sections: {missing_prefixes}")
            release_names = {
                name for name in names
                if name.startswith("build/Release/") and name.lower().endswith((".lib", ".exe", ".dll"))
            }
            if release_names != EXPECTED_RELEASE_FILES:
                raise VerificationError(
                    "Release artifact allowlist mismatch; "
                    f"missing={sorted(EXPECTED_RELEASE_FILES - release_names)}, "
                    f"extra={sorted(release_names - EXPECTED_RELEASE_FILES)}"
                )

            # archive.read performs the CRC validation.  Do it once rather than
            # testzip() followed by a second full decompression.
            blobs = {name: archive.read(name) for name in names}
    except (OSError, RuntimeError, ValueError, zlib.error,
            zipfile.BadZipFile, zipfile.LargeZipFile, NotImplementedError) as exc:
        raise VerificationError(f"Cannot read ZIP archive: {exc}") from exc

    manifest = load_json_object(blobs[MANIFEST_NAME], MANIFEST_NAME)
    expected_manifest_keys = {
        "schema", "package", "deterministic_zip_timestamp", "file_count",
        "section_source_file_counts", "selected_release_artifacts", "files",
    }
    if set(manifest) != expected_manifest_keys:
        raise VerificationError("Manifest fields do not match the canonical schema")
    if manifest.get("schema") != "dee-thinking-delivery-manifest-v1":
        raise VerificationError("Unsupported or missing manifest schema")
    if manifest.get("package") != EXPECTED_ARCHIVE_NAME:
        raise VerificationError("Manifest package identity is incorrect")
    records = manifest.get("files")
    if not isinstance(records, list):
        raise VerificationError("Manifest 'files' must be a list")

    manifest_records: dict[str, dict[str, Any]] = {}
    for record in records:
        if (not isinstance(record, dict) or set(record) != {"path", "role", "sha256", "size"} or
                not isinstance(record.get("path"), str) or
                not isinstance(record.get("size"), int) or isinstance(record.get("size"), bool) or
                not is_sha256(record.get("sha256"))):
            raise VerificationError("Malformed manifest file record")
        name = record["path"]
        if not _safe_member_name(name) or name in manifest_records:
            raise VerificationError(f"Invalid or duplicate manifest path: {name!r}")
        manifest_records[name] = record
        if record.get("role") != _expected_role(name):
            raise VerificationError(f"Manifest role mismatch: {name}")

    payload_names = set(blobs).difference({MANIFEST_NAME, HASHES_NAME})
    if set(manifest_records) != payload_names:
        missing = sorted(payload_names.difference(manifest_records))
        extra = sorted(set(manifest_records).difference(payload_names))
        raise VerificationError(f"Manifest membership mismatch; missing={missing}, extra={extra}")
    if manifest.get("file_count") != len(payload_names):
        raise VerificationError("Manifest file_count does not match payload")
    if manifest.get("deterministic_zip_timestamp") != "1980-01-01T00:00:00":
        raise VerificationError("Manifest deterministic timestamp declaration is incorrect")
    selected_release = manifest.get("selected_release_artifacts")
    if (not isinstance(selected_release, list) or
            any(not isinstance(name, str) for name in selected_release) or
            selected_release != sorted(EXPECTED_RELEASE_FILES)):
        raise VerificationError("Manifest selected Release artifacts do not match allowlist")
    actual_section_counts: dict[str, int] = {}
    for name in payload_names:
        first = PurePosixPath(name).parts[0]
        if first in SECTION_SUFFIXES:
            actual_section_counts[first] = actual_section_counts.get(first, 0) + 1
    if manifest.get("section_source_file_counts") != dict(sorted(actual_section_counts.items())):
        raise VerificationError("Manifest section source-file counts are incorrect")

    for name, record in manifest_records.items():
        blob = blobs[name]
        if record.get("size") != len(blob):
            raise VerificationError(f"Manifest size mismatch: {name}")
        if record.get("sha256") != sha256_bytes(blob):
            raise VerificationError(f"Manifest SHA-256 mismatch: {name}")

    canonical_manifest = (
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    if blobs[MANIFEST_NAME] != canonical_manifest:
        raise VerificationError("Manifest JSON is not in canonical encoding/order")

    try:
        hash_records = _parse_hashes(blobs[HASHES_NAME].decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise VerificationError(f"Invalid UTF-8 in {HASHES_NAME}") from exc
    expected_hashed_names = set(blobs).difference({HASHES_NAME})
    if set(hash_records) != expected_hashed_names:
        missing = sorted(expected_hashed_names.difference(hash_records))
        extra = sorted(set(hash_records).difference(expected_hashed_names))
        raise VerificationError(f"Hash-list membership mismatch; missing={missing}, extra={extra}")
    for name, expected_digest in hash_records.items():
        if sha256_bytes(blobs[name]) != expected_digest:
            raise VerificationError(f"Hash-list SHA-256 mismatch: {name}")

    canonical_hashes = (
        "\n".join(f"{hash_records[name]}  {name}" for name in sorted(hash_records)) + "\n"
    ).encode("utf-8")
    if blobs[HASHES_NAME] != canonical_hashes:
        raise VerificationError("Hash list is not in canonical sorted encoding")

    validation = load_json_object(
        blobs["validation/VALIDATION_SUMMARY.json"], "validation/VALIDATION_SUMMARY.json")
    provenance = load_json_object(
        blobs["validation/BUILD_PROVENANCE.json"], "validation/BUILD_PROVENANCE.json")
    benchmark = load_json_object(
        blobs["validation/backend_benchmark.json"], "validation/backend_benchmark.json")
    tests = validation.get("tests")
    if (validation.get("schema") != "dee-thinking-validation-summary-v2" or
            validation.get("configuration") != "Release" or
            validation.get("all_passed") is not True or
            validation.get("installed_relocated_consumer") is not True or
            validation.get("test_count") != len(EXPECTED_TESTS) or
            not isinstance(tests, list) or
            any(not isinstance(name, str) for name in tests) or
            tests != sorted(EXPECTED_TESTS)):
        raise VerificationError("Validation summary is stale, incomplete, or not all-passing")
    if provenance.get("schema") != "dee-thinking-build-provenance-v1":
        raise VerificationError("Build provenance schema is missing or unsupported")
    if provenance.get("configuration") != "Release":
        raise VerificationError("Build provenance does not identify Release")
    if provenance.get("installed_relocated_consumer") is not True:
        raise VerificationError("Build provenance lacks relocated-consumer success")
    flags = provenance.get("cxx_flags_release", "")
    if not release_flags_are_optimized(flags):
        raise VerificationError("Build provenance lacks Release optimization/NDEBUG flags")
    if (not is_sha256(provenance.get("source_tree_sha256")) or
            provenance.get("source_tree_sha256") != payload_source_tree_hash(blobs)):
        raise VerificationError("Build provenance source-tree hash does not match payload")
    source_names = [
        name for name in blobs
        if name == "CMakeLists.txt" or name.startswith(PROVENANCE_SOURCE_PREFIXES)
    ]
    if provenance.get("source_file_count") != len(source_names):
        raise VerificationError("Build provenance source-file count does not match payload")
    artifact_hashes = provenance.get("release_artifact_sha256")
    if (not isinstance(artifact_hashes, dict) or set(artifact_hashes) != EXPECTED_RELEASE_FILES or
            any(not is_sha256(digest) for digest in artifact_hashes.values())):
        raise VerificationError("Build provenance artifact set does not match release allowlist")
    for name, digest in artifact_hashes.items():
        if digest != sha256_bytes(blobs[name]):
            raise VerificationError(f"Build provenance artifact hash mismatch: {name}")
    junit_blob = blobs["validation/ctest.junit.xml"]
    ctest_log_blob = blobs["validation/ctest.log"]
    build_log_blob = blobs["validation/build_and_installed_consumer.log"]
    validate_ctest_junit(junit_blob)
    validate_ctest_log(ctest_log_blob)
    validate_build_log(build_log_blob)
    if validation.get("ctest_junit_sha256") != sha256_bytes(junit_blob):
        raise VerificationError("Validation summary does not bind the delivered CTest JUnit record")
    if validation.get("ctest_log_sha256") != sha256_bytes(ctest_log_blob):
        raise VerificationError("Validation summary does not bind the delivered CTest log")
    if validation.get("build_log_sha256") != sha256_bytes(build_log_blob):
        raise VerificationError("Validation summary does not bind the installed-consumer build log")
    if provenance.get("ctest_junit_sha256") != sha256_bytes(junit_blob):
        raise VerificationError("Build provenance does not bind the delivered CTest JUnit record")
    if provenance.get("ctest_log_sha256") != sha256_bytes(ctest_log_blob):
        raise VerificationError("Build provenance does not bind the delivered CTest log")
    if provenance.get("build_log_sha256") != sha256_bytes(build_log_blob):
        raise VerificationError("Build provenance does not bind the delivered build log")
    if benchmark.get("all_raw_clock_exact") is not True:
        raise VerificationError("Benchmark does not report exact RAW+clock equivalence")

    if clean_extract:
        try:
            with tempfile.TemporaryDirectory(prefix="dee-thinking-delivery-") as temp_name:
                destination = Path(temp_name)
                for name, blob in blobs.items():
                    target = destination.joinpath(*PurePosixPath(name).parts)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(blob)
                for name, blob in blobs.items():
                    extracted = destination.joinpath(*PurePosixPath(name).parts).read_bytes()
                    if extracted != blob:
                        raise VerificationError(f"Clean-extraction byte mismatch: {name}")
                    extracted_files += 1
        except OSError as exc:
            raise VerificationError(f"Clean extraction failed: {exc}") from exc

    return {
        "schema": "dee-thinking-delivery-verification-v1",
        "archive": archive_label,
        "archive_sha256": archive_sha256,
        "zip_valid": True,
        "manifest_valid": True,
        "hashes_valid": True,
        "safe_paths": True,
        "clean_extraction_valid": clean_extract,
        "member_count": len(blobs),
        "payload_file_count": len(payload_names),
        "extracted_file_count": extracted_files,
    }


def verify_archive(
    archive_path: Path,
    *,
    require_official_name: bool = False,
    clean_extract: bool = True,
) -> dict[str, Any]:
    """Read once, then verify exactly those bytes."""

    archive_path = archive_path.resolve()
    if not archive_path.is_file():
        raise VerificationError(f"Archive not found: {archive_path}")
    archive_blob = _read_archive_once(archive_path)
    return verify_archive_bytes(
        archive_blob,
        str(archive_path),
        require_official_name=require_official_name,
        clean_extract=clean_extract,
    )


def _extract_verified_snapshot(archive_blob: bytes, destination: Path) -> None:
    """Stream a previously verified immutable snapshot into a private directory."""
    try:
        with zipfile.ZipFile(io.BytesIO(archive_blob), "r") as archive:
            for info in archive.infolist():
                target = destination.joinpath(*PurePosixPath(info.filename).parts)
                if not target.resolve(strict=False).is_relative_to(destination.resolve(strict=True)):
                    raise VerificationError(f"Extraction target escaped staging root: {info.filename}")
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(info, "r") as source, target.open("xb") as output:
                    shutil.copyfileobj(source, output, length=1024 * 1024)
                    output.flush()
                    os.fsync(output.fileno())
    except (OSError, RuntimeError, ValueError, zlib.error,
            zipfile.BadZipFile, zipfile.LargeZipFile, NotImplementedError) as exc:
        raise VerificationError(f"Persistent extraction failed: {exc}") from exc


def _read_bounded_output(stream: Any, label: str) -> str:
    stream.seek(0)
    blob = stream.read(MAX_CONSUMER_OUTPUT_BYTES + 1)
    if len(blob) > MAX_CONSUMER_OUTPUT_BYTES:
        raise VerificationError(f"Extracted consumer {label} exceeded output limit")
    return blob.decode("utf-8", errors="replace")


def _run_staged_consumer(staging_root: Path) -> dict[str, Any]:
    consumer = staging_root / "build" / "Release" / "bin" / "dee_thinking_consumer.exe"
    with tempfile.TemporaryDirectory(prefix="dee-thinking-consumer-run-") as run_name:
        run_directory = Path(run_name)
        snapshot = run_directory / "consumer_composition.deetsnap"
        with tempfile.TemporaryFile() as stdout_stream, tempfile.TemporaryFile() as stderr_stream:
            completed = subprocess.run(
                [str(consumer), str(snapshot)],
                cwd=run_directory,
                stdin=subprocess.DEVNULL,
                stdout=stdout_stream,
                stderr=stderr_stream,
                timeout=120,
                check=False,
            )
            result = {
                "path": str(consumer),
                "returncode": completed.returncode,
                "stdout": _read_bounded_output(stdout_stream, "stdout"),
                "stderr": _read_bounded_output(stderr_stream, "stderr"),
            }
    if completed.returncode != 0:
        raise VerificationError(
            f"Extracted independent consumer returned {completed.returncode}: {result['stderr']}"
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument(
        "--require-official-name",
        action="store_true",
        help=f"require the basename {EXPECTED_ARCHIVE_NAME}",
    )
    parser.add_argument(
        "--expected-sha256",
        help="external expected SHA-256; mandatory before --run-consumer",
    )
    parser.add_argument(
        "--no-clean-extract",
        action="store_true",
        help="skip the temporary clean-extraction check",
    )
    parser.add_argument("--report", type=Path, help="optional JSON report path")
    parser.add_argument(
        "--extract-to",
        type=Path,
        help="atomically publish a verified copy to this not-yet-existing directory",
    )
    parser.add_argument(
        "--run-consumer",
        action="store_true",
        help="execute the independent consumer from --extract-to after extraction",
    )
    args = parser.parse_args()

    if args.run_consumer and args.extract_to is None:
        parser.error("--run-consumer requires --extract-to")
    if args.run_consumer and args.expected_sha256 is None:
        parser.error("--run-consumer requires an externally supplied --expected-sha256")

    try:
        archive_path = args.archive.resolve()
        archive_blob = _read_archive_once(archive_path)
        report = verify_archive_bytes(
            archive_blob,
            str(archive_path),
            require_official_name=args.require_official_name,
            clean_extract=not args.no_clean_extract,
        )
        if args.expected_sha256 is not None:
            expected = args.expected_sha256.casefold()
            if (len(expected) != 64 or any(ch not in "0123456789abcdef" for ch in expected) or
                    report["archive_sha256"] != expected):
                raise VerificationError("Archive SHA-256 does not match --expected-sha256")
    except (OSError, VerificationError) as exc:
        print(json.dumps({"zip_valid": False, "error": str(exc)}, indent=2))
        return 1


    if args.extract_to is not None:
        requested = args.extract_to
        staging_root: Path | None = None
        try:
            extraction_parent = requested.parent.resolve(strict=True)
            extraction_root = extraction_parent / requested.name
            if extraction_root.exists() or extraction_root.is_symlink():
                raise VerificationError(f"Extraction destination must not exist: {extraction_root}")
            staging_root = Path(tempfile.mkdtemp(
                prefix=f".{extraction_root.name}.verified-", dir=extraction_parent))
            try:
                staging_root.chmod(0o700)
            except OSError:
                pass
            _extract_verified_snapshot(archive_blob, staging_root)
            if args.run_consumer:
                consumer_report = _run_staged_consumer(staging_root)
            # Rename only after every extraction/execution check succeeds, so a
            # failure never leaves a partially populated requested directory.
            os.rename(staging_root, extraction_root)
            staging_root = None
            report["persistent_clean_extraction"] = str(extraction_root)
            if args.run_consumer:
                consumer_report["path"] = str(
                    extraction_root / "build" / "Release" / "bin" / "dee_thinking_consumer.exe")
                report["extracted_consumer"] = consumer_report
        except (OSError, subprocess.SubprocessError, zipfile.BadZipFile, VerificationError) as exc:
            print(json.dumps({"zip_valid": False, "error": str(exc)}, indent=2))
            return 1
        finally:
            if staging_root is not None and staging_root.exists():
                shutil.rmtree(staging_root, ignore_errors=True)

    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    print(rendered, end="")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
