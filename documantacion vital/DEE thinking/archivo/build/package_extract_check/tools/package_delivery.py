#!/usr/bin/env python3
"""Build the single deterministic DEE thinking Entrega 01 archive.

The existing official archive, if any, is left untouched until a complete
temporary candidate passes all validations in ``verify_delivery.py``.  The
script deliberately packages only reproducible source material, fixtures,
documentation, validation records, and selected Release deliverables; CMake
caches, object files, and nested ZIPs are never included.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import zipfile
from pathlib import Path, PurePosixPath
from typing import Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_delivery import EXPECTED_ARCHIVE_NAME, VerificationError, verify_archive


SOURCE_SECTIONS = (
    "include",
    "src",
    "tests",
    "examples",
    "tools",
    "fixtures",
    "docs",
    "validation",
)
TOP_LEVEL_FILES = {
    "CMakeLists.txt",
    "README.md",
    "LICENSE",
    "LICENSE.txt",
    "NOTICE",
    "NOTICE.txt",
}
TOP_LEVEL_SUFFIXES = {".json", ".md", ".txt", ".cmake"}
GENERATED_NAMES = {"MANIFEST.json", "HASHES.sha256"}
EXCLUDED_PARTS = {
    ".git",
    ".vs",
    ".vscode",
    "__pycache__",
    ".pytest_cache",
    "CMakeFiles",
    "Testing",
}
EXCLUDED_SUFFIXES = {
    ".obj",
    ".o",
    ".pch",
    ".pdb",
    ".idb",
    ".ilk",
    ".tlog",
    ".recipe",
    ".lastbuildstate",
    ".cache",
    ".pyc",
    ".tmp",
    ".zip",
}
RELEASE_SUFFIXES = {".exe", ".dll", ".lib"}
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)


class PackagingError(RuntimeError):
    """Raised before the official archive is replaced."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _excluded(path: Path) -> bool:
    return bool(EXCLUDED_PARTS.intersection(path.parts)) or path.suffix.lower() in EXCLUDED_SUFFIXES


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
        "build": "compiled_release_artifact",
    }
    return roles.get(first, "build_definition")


def _insert(payload: dict[str, bytes], archive_name: str, data: bytes) -> None:
    normalized = PurePosixPath(archive_name).as_posix()
    if normalized in GENERATED_NAMES or normalized.lower().endswith(".zip"):
        raise PackagingError(f"Forbidden payload name: {normalized}")
    previous = payload.get(normalized)
    if previous is not None and previous != data:
        raise PackagingError(f"Archive-name collision with different bytes: {normalized}")
    payload[normalized] = data


def _collect_tree(project_root: Path, section: str, payload: dict[str, bytes]) -> int:
    root = project_root / section
    if not root.is_dir():
        raise PackagingError(f"Required source section is missing: {root}")
    count = 0
    for path in sorted((p for p in root.rglob("*") if p.is_file()), key=lambda p: p.as_posix()):
        relative = path.relative_to(project_root)
        if _excluded(relative):
            continue
        _insert(payload, relative.as_posix(), path.read_bytes())
        count += 1
    if count == 0:
        raise PackagingError(f"Required source section has no packageable files: {section}")
    return count


def _release_destination(path: Path) -> str:
    suffix = path.suffix.lower()
    category = "lib" if suffix == ".lib" else "bin"
    return f"build/Release/{category}/{path.name}"


def _collect_release(build_root: Path, payload: dict[str, bytes]) -> list[str]:
    if not build_root.is_dir():
        raise PackagingError(f"Build root is missing: {build_root}")
    selected: list[str] = []
    for path in sorted((p for p in build_root.rglob("*") if p.is_file()), key=lambda p: p.as_posix()):
        relative = path.relative_to(build_root)
        if _excluded(relative):
            continue
        if path.suffix.lower() not in RELEASE_SUFFIXES:
            continue
        # Multi-config generators put artifacts below a Release directory.  A
        # single-config build may instead place them directly under bin/lib;
        # in that case the build root itself is expected to identify Release.
        is_release = any(part.casefold() == "release" for part in relative.parts)
        if not is_release and "release" not in build_root.name.casefold():
            continue
        destination = _release_destination(path)
        _insert(payload, destination, path.read_bytes())
        selected.append(destination)
    if not any(name.endswith(".lib") for name in selected):
        raise PackagingError("No Release .lib was found in the build tree")
    if "build/Release/bin/dee_thinking_consumer.exe" not in selected:
        raise PackagingError("Release independent consumer executable was not found")
    if not any(name.endswith(".exe") for name in selected):
        raise PackagingError("No Release executable was found in the build tree")
    return sorted(selected)


def collect_payload(project_root: Path, build_root: Path) -> tuple[dict[str, bytes], dict[str, int], list[str]]:
    payload: dict[str, bytes] = {}
    section_counts: dict[str, int] = {}
    top_level_paths = {
        project_root / name for name in TOP_LEVEL_FILES if (project_root / name).is_file()
    }
    top_level_paths.update(
        path
        for path in project_root.iterdir()
        if path.is_file()
        and path.suffix.lower() in TOP_LEVEL_SUFFIXES
        and path.name not in GENERATED_NAMES
    )
    for path in sorted(top_level_paths, key=lambda item: item.name):
        _insert(payload, path.name, path.read_bytes())
    if "CMakeLists.txt" not in payload:
        raise PackagingError("CMakeLists.txt is required")
    for section in SOURCE_SECTIONS:
        section_counts[section] = _collect_tree(project_root, section, payload)
    release_files = _collect_release(build_root, payload)
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
    parser.add_argument("--build-root", type=Path, help="defaults to PROJECT_ROOT/build")
    parser.add_argument("--output", type=Path, help=f"defaults to PROJECT_ROOT/{EXPECTED_ARCHIVE_NAME}")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="collect and validate inputs but do not create an archive",
    )
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    build_root = (args.build_root or (project_root / "build")).resolve()
    output = (args.output or (project_root / EXPECTED_ARCHIVE_NAME)).resolve()
    if output.parent != project_root:
        print("ERROR: official delivery output must be directly under the project root", file=sys.stderr)
        return 2

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

        temporary = output.with_name(f".{output.name}.candidate-{os.getpid()}")
        if temporary.exists():
            temporary.unlink()
        try:
            write_candidate(temporary, payload, section_counts, release_files)
            report = verify_archive(temporary, require_official_name=False, clean_extract=True)
            # Atomic replacement happens only after the candidate has passed all checks.
            os.replace(temporary, output)
            final_report = verify_archive(output, require_official_name=True, clean_extract=True)
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
