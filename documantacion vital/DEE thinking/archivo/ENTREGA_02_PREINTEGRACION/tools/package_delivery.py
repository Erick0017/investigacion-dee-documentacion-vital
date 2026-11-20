#!/usr/bin/env python3
"""Build the deterministic Entrega 02 preintegration archive.

The existing official archive, if any, is left untouched until a complete
temporary candidate passes all validations in ``verify_delivery.py``.  The
script deliberately packages only reproducible source material, fixtures,
documentation, validation records, and selected Release deliverables; CMake
caches, object files, and nested ZIPs are never included.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
import os
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_delivery import (
    EXCLUDED_PARTS,
    EXCLUDED_SUFFIXES,
    EXPECTED_ARCHIVE_NAME,
    EXPECTED_RELEASE_FILES,
    EXPECTED_TESTS,
    MAX_ARCHIVE_BYTES,
    PROVENANCE_SOURCE_PREFIXES,
    SECTION_EXACT_NAMES,
    SECTION_SUFFIXES,
    SOURCE_SECTIONS,
    TOP_LEVEL_SOURCE_FILES,
    VerificationError,
    existing_file_within_root,
    is_sha256,
    is_reparse_point,
    payload_name_allowed,
    payload_source_tree_hash,
    release_flags_are_optimized,
    validate_build_log,
    validate_ctest_junit,
    validate_ctest_log,
    verify_archive,
    verify_archive_bytes,
)


TOP_LEVEL_FILES = TOP_LEVEL_SOURCE_FILES
GENERATED_NAMES = {"MANIFEST.json", "HASHES.sha256"}
RELEASE_SUFFIXES = {".exe", ".dll", ".lib"}
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)


class PackagingError(RuntimeError):
    """Raised before the official archive is replaced."""


def _bounded_read(path: Path) -> bytes:
    try:
        with path.open("rb") as stream:
            blob = stream.read(MAX_ARCHIVE_BYTES + 1)
    except OSError as exc:
        raise PackagingError(f"Cannot read staged archive: {exc}") from exc
    if len(blob) > MAX_ARCHIVE_BYTES:
        raise PackagingError("Staged archive exceeds the compressed-size limit")
    return blob


def _durable_temp_bytes(parent: Path, prefix: str, blob: bytes) -> Path:
    descriptor, name = tempfile.mkstemp(prefix=prefix, suffix=".zip", dir=parent)
    path = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(blob)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        path.unlink(missing_ok=True)
        raise
    return path


def _sync_directory(directory: Path) -> None:
    """Persist a rename on platforms that permit fsync on directories."""
    if os.name == "nt":
        return
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    descriptor = os.open(directory, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _sync_file(path: Path) -> None:
    with path.open("r+b") as stream:
        stream.flush()
        os.fsync(stream.fileno())


@contextmanager
def _publication_lock(path: Path):
    """Use an OS lock; a crash cannot leave a stale logical lock behind."""
    stream = path.open("a+b")
    try:
        if stream.seek(0, os.SEEK_END) == 0:
            stream.write(b"\0")
            stream.flush()
            os.fsync(stream.fileno())
        stream.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise PackagingError(f"Another package publication holds {path}") from exc
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
    finally:
        stream.close()


def _publish_verified_blob(blob: bytes, official: Path) -> dict[str, object]:
    """Publish atomically and restore the previous official on a failed check."""
    verify_archive_bytes(blob, str(official), require_official_name=True, clean_extract=True)
    lock = official.parent / ".dee-thinking-entrega02-closure.publish.lock"
    previous: bytes | None = None
    temporary: Path | None = None
    replaced = False
    with _publication_lock(lock):
        try:
            previous = _bounded_read(official) if official.exists() else None
            temporary = _durable_temp_bytes(official.parent, f".{official.name}.publish-", blob)
            os.replace(temporary, official)
            temporary = None
            replaced = True
            _sync_directory(official.parent)
            published = _bounded_read(official)
            if sha256_bytes(published) != sha256_bytes(blob):
                raise PackagingError("Published archive bytes differ from verified candidate")
            return verify_archive_bytes(
                published, str(official), require_official_name=True, clean_extract=True)
        except Exception:
            if replaced and previous is not None:
                recovery = _durable_temp_bytes(
                    official.parent, f".{official.name}.recovery-", previous)
                os.replace(recovery, official)
                _sync_directory(official.parent)
            elif replaced and official.exists():
                official.unlink()
                _sync_directory(official.parent)
            raise
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _excluded(path: Path) -> bool:
    folded_parts = {part.casefold() for part in path.parts}
    return bool({part.casefold() for part in EXCLUDED_PARTS}.intersection(folded_parts)) or path.suffix.lower() in EXCLUDED_SUFFIXES


def _allowed_section_file(archive_name: str) -> bool:
    return payload_name_allowed(archive_name)


def _role(name: str) -> str:
    first = PurePosixPath(name).parts[0]
    roles = {
        "include": "public_header",
        "src": "native_source",
        "tests": "test_source",
        "examples": "example_or_independent_consumer_source",
        "tools": "build_validation_tool",
        "fixtures": "reference_fixture",
        "docs": "documentation",
        "validation": "validation_output",
        "laboratory": "experimental_laboratory_evidence",
        "candidates": "isolated_candidate_implementation",
        "build": "compiled_release_artifact",
    }
    return roles.get(first, "build_definition")


def _insert(payload: dict[str, bytes], archive_name: str, data: bytes) -> None:
    normalized = PurePosixPath(archive_name).as_posix()
    if (normalized in GENERATED_NAMES or normalized.lower().endswith(".zip") or
            not payload_name_allowed(normalized)):
        raise PackagingError(f"Forbidden payload name: {normalized}")
    previous = payload.get(normalized)
    if previous is not None and previous != data:
        raise PackagingError(f"Archive-name collision with different bytes: {normalized}")
    payload[normalized] = data


def _collect_tree(project_root: Path, section: str, payload: dict[str, bytes]) -> int:
    root = project_root / section
    if not root.is_dir():
        raise PackagingError(f"Required source section is missing: {root}")
    if is_reparse_point(root):
        raise PackagingError(f"Required source section is a reparse point: {root}")
    count = 0
    for candidate in sorted(root.rglob("*"), key=lambda p: p.as_posix()):
        if is_reparse_point(candidate):
            raise PackagingError(f"Symbolic/reparse links are forbidden in payload trees: {candidate}")
        if not candidate.is_file():
            continue
        path = candidate
        if not existing_file_within_root(path, project_root):
            raise PackagingError(f"Payload path escapes project root: {path}")
        relative = path.relative_to(project_root)
        if _excluded(relative):
            continue
        if not _allowed_section_file(relative.as_posix()):
            raise PackagingError(f"Unreviewed file type/name in {section}: {relative}")
        _insert(payload, relative.as_posix(), path.read_bytes())
        count += 1
    if count == 0:
        raise PackagingError(f"Required source section has no packageable files: {section}")
    return count


def _collect_release(project_root: Path, build_root: Path,
                     payload: dict[str, bytes]) -> list[str]:
    if not build_root.is_dir():
        raise PackagingError(f"Build root is missing: {build_root}")
    cache = build_root / "CMakeCache.txt"
    if not cache.is_file():
        raise PackagingError(f"CMakeCache.txt is missing from build root: {build_root}")
    cache_text = cache.read_text(encoding="utf-8", errors="strict")
    if "CMAKE_BUILD_TYPE:STRING=Release" not in cache_text:
        raise PackagingError("Build tree is not configured with CMAKE_BUILD_TYPE=Release")
    release_flags = next(
        (line.partition("=")[2] for line in cache_text.splitlines()
         if line.startswith("CMAKE_CXX_FLAGS_RELEASE:")),
        "",
    )
    if not release_flags_are_optimized(release_flags):
        raise PackagingError(
            "CMAKE_CXX_FLAGS_RELEASE must contain an exact optimizing flag and NDEBUG, "
            "without /Od, -O0, or -Og")

    compile_inputs = [project_root / "CMakeLists.txt"]
    for section in ("include", "src", "tests", "examples", "benchmarks", "cmake"):
        compile_inputs.extend(
            path for path in (project_root / section).rglob("*")
            if path.is_file() and not path.is_symlink()
        )
    latest_input_ns = max(path.stat().st_mtime_ns for path in compile_inputs)

    observed: set[str] = set()
    for category in ("bin", "lib"):
        directory = build_root / category
        if not directory.is_dir() or is_reparse_point(directory):
            raise PackagingError(f"Missing or reparse-point Release directory: {directory}")
        for candidate in directory.iterdir():
            if is_reparse_point(candidate):
                raise PackagingError(f"Symbolic/reparse build entry is forbidden: {candidate}")
            if candidate.is_file() and candidate.suffix.casefold() in RELEASE_SUFFIXES:
                observed.add(f"build/Release/{category}/{candidate.name}")
    unexpected = sorted(observed - EXPECTED_RELEASE_FILES)
    if unexpected:
        raise PackagingError(f"Unexpected compiled payloads in canonical Release directories: {unexpected}")

    selected: list[str] = []
    for destination in sorted(EXPECTED_RELEASE_FILES):
        relative_parts = PurePosixPath(destination).parts[2:]
        path = build_root.joinpath(*relative_parts)
        if not existing_file_within_root(path, build_root):
            raise PackagingError(f"Missing, escaping, or reparse-point Release artifact: {path}")
        if path.stat().st_mtime_ns < latest_input_ns:
            raise PackagingError(f"Release artifact is older than current compile inputs: {path}")
        _insert(payload, destination, path.read_bytes())
        selected.append(destination)
    return sorted(selected)


def _validate_validation_inputs(payload: dict[str, bytes]) -> None:
    required_evidence = {
        "validation/ctest.junit.xml",
        "validation/ctest.log",
        "validation/build_and_installed_consumer.log",
    }
    missing_evidence = sorted(required_evidence - set(payload))
    if missing_evidence:
        raise PackagingError(f"Missing mandatory validation evidence: {missing_evidence}")
    try:
        summary = json.loads(payload["validation/VALIDATION_SUMMARY.json"].decode("utf-8"))
        provenance = json.loads(payload["validation/BUILD_PROVENANCE.json"].decode("utf-8"))
        benchmark = json.loads(payload["validation/backend_benchmark.json"].decode("utf-8"))
    except (KeyError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PackagingError(f"Missing or invalid validation input: {exc}") from exc
    if (not isinstance(summary, dict) or
            summary.get("schema") != "dee-thinking-validation-summary-v2" or
            summary.get("configuration") != "Release" or
            summary.get("all_passed") is not True or
            summary.get("installed_relocated_consumer") is not True or
            summary.get("test_count") != len(EXPECTED_TESTS) or
            summary.get("tests") != sorted(EXPECTED_TESTS)):
        raise PackagingError("Validation summary is stale or incomplete")
    if (not isinstance(provenance, dict) or
            provenance.get("schema") != "dee-thinking-build-provenance-v1" or
            provenance.get("configuration") != "Release" or
            provenance.get("installed_relocated_consumer") is not True or
            not release_flags_are_optimized(provenance.get("cxx_flags_release")) or
            not is_sha256(provenance.get("source_tree_sha256")) or
            provenance.get("source_tree_sha256") != payload_source_tree_hash(payload)):
        raise PackagingError("Build provenance is stale, missing, or not Release")
    source_names = [
        name for name in payload
        if name == "CMakeLists.txt" or name.startswith(PROVENANCE_SOURCE_PREFIXES)
    ]
    if provenance.get("source_file_count") != len(source_names):
        raise PackagingError("Build provenance source-file count is incorrect")
    hashes = provenance.get("release_artifact_sha256")
    if not isinstance(hashes, dict) or set(hashes) != EXPECTED_RELEASE_FILES:
        raise PackagingError("Build provenance artifact allowlist mismatch")
    for name, expected in hashes.items():
        if not is_sha256(expected) or name not in payload or sha256_bytes(payload[name]) != expected:
            raise PackagingError(f"Build provenance hash mismatch: {name}")
    junit_blob = payload["validation/ctest.junit.xml"]
    ctest_log_blob = payload["validation/ctest.log"]
    build_log_blob = payload["validation/build_and_installed_consumer.log"]
    validate_ctest_junit(junit_blob)
    validate_ctest_log(ctest_log_blob)
    validate_build_log(build_log_blob)
    if (summary.get("ctest_junit_sha256") != sha256_bytes(junit_blob) or
            summary.get("ctest_log_sha256") != sha256_bytes(ctest_log_blob) or
            summary.get("build_log_sha256") != sha256_bytes(build_log_blob) or
            provenance.get("ctest_junit_sha256") != sha256_bytes(junit_blob) or
            provenance.get("ctest_log_sha256") != sha256_bytes(ctest_log_blob) or
            provenance.get("build_log_sha256") != sha256_bytes(build_log_blob)):
        raise PackagingError("Validation evidence hashes do not match the delivered records")
    if not isinstance(benchmark, dict) or benchmark.get("all_raw_clock_exact") is not True:
        raise PackagingError("Benchmark equivalence result is missing or not exact")


def collect_payload(project_root: Path, build_root: Path) -> tuple[dict[str, bytes], dict[str, int], list[str]]:
    payload: dict[str, bytes] = {}
    section_counts: dict[str, int] = {}
    top_level_paths = {project_root / name for name in TOP_LEVEL_FILES if (project_root / name).is_file()}
    for path in sorted(top_level_paths, key=lambda item: item.name):
        if is_reparse_point(path) or not existing_file_within_root(path, project_root):
            raise PackagingError(f"Unsafe top-level payload path: {path}")
        _insert(payload, path.name, path.read_bytes())
    if "CMakeLists.txt" not in payload:
        raise PackagingError("CMakeLists.txt is required")
    for section in SOURCE_SECTIONS:
        section_counts[section] = _collect_tree(project_root, section, payload)
    release_files = _collect_release(project_root, build_root, payload)
    _validate_validation_inputs(payload)
    return payload, section_counts, release_files


def _manifest_bytes(payload: dict[str, bytes], section_counts: dict[str, int], release_files: list[str]) -> bytes:
    records = [
        {
            "path": name,
            "role": _role(name),
            "sha256": sha256_bytes(payload[name]),
            "size": len(payload[name]),
        }
        for name in sorted(payload)
    ]
    manifest = {
        "schema": "dee-thinking-delivery-manifest-v1",
        "package": EXPECTED_ARCHIVE_NAME,
        "deterministic_zip_timestamp": "1980-01-01T00:00:00",
        "file_count": len(records),
        "section_source_file_counts": dict(sorted(section_counts.items())),
        "selected_release_artifacts": release_files,
        "files": records,
    }
    return (json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def _hashes_bytes(payload: dict[str, bytes], manifest_blob: bytes) -> bytes:
    hashed = dict(payload)
    hashed["MANIFEST.json"] = manifest_blob
    lines = [f"{sha256_bytes(hashed[name])}  {name}" for name in sorted(hashed)]
    return ("\n".join(lines) + "\n").encode("utf-8")


def _zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(filename=name, date_time=FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    info.flag_bits |= 0x800  # UTF-8 names where applicable.
    return info


def write_candidate(
    destination: Path,
    payload: dict[str, bytes],
    section_counts: dict[str, int],
    release_files: list[str],
) -> None:
    manifest_blob = _manifest_bytes(payload, section_counts, release_files)
    hashes_blob = _hashes_bytes(payload, manifest_blob)
    complete = dict(payload)
    complete["MANIFEST.json"] = manifest_blob
    complete["HASHES.sha256"] = hashes_blob
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        destination,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        allowZip64=True,
    ) as archive:
        for name in sorted(complete):
            archive.writestr(_zip_info(name), complete[name], compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def main() -> int:
    script_path = Path(__file__).resolve()
    default_root = script_path.parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=default_root)
    parser.add_argument("--build-root", type=Path, help="defaults to PROJECT_ROOT/build/release")
    parser.add_argument(
        "--output", type=Path,
        help=f"defaults to PROJECT_ROOT/../{EXPECTED_ARCHIVE_NAME}",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="collect and validate inputs but do not create an archive",
    )
    parser.add_argument(
        "--stage-only",
        action="store_true",
        help="write and verify --output but do not publish the official archive",
    )
    parser.add_argument(
        "--publish-staged",
        type=Path,
        help="verify this already-tested staged archive and atomically publish it",
    )
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    build_root = (args.build_root or (project_root / "build" / "release")).resolve()
    output = (args.output or (project_root.parent / EXPECTED_ARCHIVE_NAME)).resolve()
    if output.parent != project_root.parent:
        print("ERROR: official delivery output must be directly under DEE thinking", file=sys.stderr)
        return 2
    if args.stage_only and output.name == EXPECTED_ARCHIVE_NAME:
        print("ERROR: --stage-only requires a non-official candidate filename", file=sys.stderr)
        return 2
    if args.stage_only and args.publish_staged:
        print("ERROR: --stage-only and --publish-staged are mutually exclusive", file=sys.stderr)
        return 2
    if args.dry_run and (args.stage_only or args.publish_staged):
        print("ERROR: --dry-run cannot be combined with --stage-only or --publish-staged", file=sys.stderr)
        return 2

    if args.publish_staged:
        staged = Path(os.path.abspath(args.publish_staged))
        official = project_root.parent / EXPECTED_ARCHIVE_NAME
        try:
            safe_staged = (
                staged.parent.resolve(strict=True) == project_root.parent and
                staged != official and not is_reparse_point(staged) and
                existing_file_within_root(staged, project_root.parent)
            )
        except OSError:
            safe_staged = False
        if not safe_staged:
            print("ERROR: staged archive must be a separate file directly under DEE thinking", file=sys.stderr)
            return 2
        try:
            staged_identity = staged.stat()
            staged_blob = _bounded_read(staged)
            staged_report = verify_archive_bytes(
                staged_blob, str(staged), require_official_name=False, clean_extract=True)
            final_report = _publish_verified_blob(staged_blob, official)
            current_identity = staged.stat()
            unchanged = (
                current_identity.st_dev == staged_identity.st_dev and
                current_identity.st_ino == staged_identity.st_ino and
                current_identity.st_size == staged_identity.st_size and
                current_identity.st_mtime_ns == staged_identity.st_mtime_ns
            )
            if unchanged:
                staged.unlink()
            else:
                final_report["staged_cleanup_warning"] = (
                    "staged path changed during publication and was deliberately left untouched")
        except (OSError, PackagingError, VerificationError) as exc:
            print(json.dumps({"published": False, "error": str(exc)}, indent=2), file=sys.stderr)
            return 1
        print(json.dumps({"published": True, "staged_report": staged_report, **final_report},
                         indent=2, sort_keys=True))
        return 0

    try:
        payload, section_counts, release_files = collect_payload(project_root, build_root)
        if args.dry_run:
            print(
                json.dumps(
                    {
                        "dry_run": True,
                        "payload_file_count": len(payload),
                        "section_counts": section_counts,
                        "release_files": release_files,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0

        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{output.name}.candidate-", suffix=".zip", dir=output.parent)
        os.close(descriptor)
        temporary = Path(temporary_name)
        try:
            write_candidate(temporary, payload, section_counts, release_files)
            _sync_file(temporary)
            report = verify_archive(temporary, require_official_name=False, clean_extract=True)
            if args.stage_only:
                os.replace(temporary, output)
                _sync_directory(output.parent)
                final_report = verify_archive(output, require_official_name=False, clean_extract=True)
            else:
                if output.name != EXPECTED_ARCHIVE_NAME:
                    raise PackagingError(
                        f"non-staged output must be named {EXPECTED_ARCHIVE_NAME}"
                    )
                candidate_blob = _bounded_read(temporary)
                final_report = _publish_verified_blob(candidate_blob, output)
        finally:
            if temporary.exists():
                temporary.unlink()
    except (OSError, PackagingError, VerificationError) as exc:
        print(json.dumps({"packaged": False, "error": str(exc)}, indent=2), file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "packaged": True,
                "staged_only": args.stage_only,
                "candidate_member_count": report["member_count"],
                "output": str(output),
                **final_report,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
