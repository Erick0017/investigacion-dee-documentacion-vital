#!/usr/bin/env python3
"""Verify a DEE thinking delivery archive without trusting its metadata.

The verifier uses only the Python standard library.  It validates member names,
CRC/readability, the internal manifest and hash list, the expected delivery
layout, and a clean extraction to a newly-created temporary directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any


MANIFEST_NAME = "MANIFEST.json"
HASHES_NAME = "HASHES.sha256"
EXPECTED_ARCHIVE_NAME = "DEE_thinking_ENTREGA_01_RESULTADOS.zip"
REQUIRED_FILES = {
    "CMakeLists.txt",
    MANIFEST_NAME,
    HASHES_NAME,
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
)


class VerificationError(RuntimeError):
    """Raised when an archive does not satisfy the delivery contract."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_member_name(name: str) -> bool:
    if not name or "\\" in name or name.startswith("/"):
        return False
    path = PurePosixPath(name)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        return False
    # Drive-qualified and alternate-data-stream paths are not valid payload names.
    if ":" in path.parts[0]:
        return False
    return True


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


def verify_archive(
    archive_path: Path,
    *,
    require_official_name: bool = False,
    clean_extract: bool = True,
) -> dict[str, Any]:
    """Return a machine-readable report or raise :class:`VerificationError`."""

    archive_path = archive_path.resolve()
    if not archive_path.is_file():
        raise VerificationError(f"Archive not found: {archive_path}")
    if require_official_name and archive_path.name != EXPECTED_ARCHIVE_NAME:
        raise VerificationError(
            f"Expected archive name {EXPECTED_ARCHIVE_NAME!r}, got {archive_path.name!r}"
        )

    archive_sha256 = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    extracted_files = 0

    try:
        with zipfile.ZipFile(archive_path, "r") as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            if len(names) != len(set(names)):
                raise VerificationError("Archive contains duplicate member names")
            if any(info.is_dir() for info in infos):
                raise VerificationError("Archive must contain files only; empty directory entries found")
            for name in names:
                if not _safe_member_name(name):
                    raise VerificationError(f"Unsafe archive member: {name!r}")
                if name.lower().endswith(".zip"):
                    raise VerificationError(f"Nested ZIP is forbidden: {name}")

            missing_files = sorted(REQUIRED_FILES.difference(names))
            if missing_files:
                raise VerificationError(f"Missing required files: {missing_files}")
            missing_prefixes = [
                prefix for prefix in REQUIRED_PREFIXES if not any(n.startswith(prefix) for n in names)
            ]
            if missing_prefixes:
                raise VerificationError(f"Missing/non-populated delivery sections: {missing_prefixes}")
            if not any(n.startswith("build/Release/lib/") and n.endswith(".lib") for n in names):
                raise VerificationError("No Release static library found under build/Release/lib")
            if not any(n.startswith("build/Release/bin/") and n.endswith(".exe") for n in names):
                raise VerificationError("No Release executables found under build/Release/bin")
            if "build/Release/bin/dee_thinking_consumer.exe" not in names:
                raise VerificationError("Independent consumer executable is absent")

            corrupt_member = archive.testzip()
            if corrupt_member is not None:
                raise VerificationError(f"CRC/read failure in member: {corrupt_member}")

            blobs = {name: archive.read(name) for name in names}
    except (OSError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
        raise VerificationError(f"Cannot read ZIP archive: {exc}") from exc

    try:
        manifest = json.loads(blobs[MANIFEST_NAME].decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerificationError(f"Invalid {MANIFEST_NAME}: {exc}") from exc
    if manifest.get("schema") != "dee-thinking-delivery-manifest-v1":
        raise VerificationError("Unsupported or missing manifest schema")
    if manifest.get("package") != EXPECTED_ARCHIVE_NAME:
        raise VerificationError("Manifest package identity is incorrect")
    records = manifest.get("files")
    if not isinstance(records, list):
        raise VerificationError("Manifest 'files' must be a list")

    manifest_records: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("path"), str):
            raise VerificationError("Malformed manifest file record")
        name = record["path"]
        if not _safe_member_name(name) or name in manifest_records:
            raise VerificationError(f"Invalid or duplicate manifest path: {name!r}")
        manifest_records[name] = record

    payload_names = set(blobs).difference({MANIFEST_NAME, HASHES_NAME})
    if set(manifest_records) != payload_names:
        missing = sorted(payload_names.difference(manifest_records))
        extra = sorted(set(manifest_records).difference(payload_names))
        raise VerificationError(f"Manifest membership mismatch; missing={missing}, extra={extra}")
    if manifest.get("file_count") != len(payload_names):
        raise VerificationError("Manifest file_count does not match payload")

    for name, record in manifest_records.items():
        blob = blobs[name]
        if record.get("size") != len(blob):
            raise VerificationError(f"Manifest size mismatch: {name}")
        if record.get("sha256") != sha256_bytes(blob):
            raise VerificationError(f"Manifest SHA-256 mismatch: {name}")

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

    if clean_extract:
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

    return {
        "schema": "dee-thinking-delivery-verification-v1",
        "archive": str(archive_path),
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument(
        "--require-official-name",
        action="store_true",
        help=f"require the basename {EXPECTED_ARCHIVE_NAME}",
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
        help="also extract a verified copy to this new or empty directory",
    )
    parser.add_argument(
        "--run-consumer",
        action="store_true",
        help="execute the independent consumer from --extract-to after extraction",
    )
    args = parser.parse_args()

    if args.run_consumer and args.extract_to is None:
        parser.error("--run-consumer requires --extract-to")

    try:
        report = verify_archive(
            args.archive,
            require_official_name=args.require_official_name,
            clean_extract=not args.no_clean_extract,
        )
    except VerificationError as exc:
        print(json.dumps({"zip_valid": False, "error": str(exc)}, indent=2))
        return 1


    if args.extract_to is not None:
        extraction_root = args.extract_to.resolve()
        try:
            if extraction_root.exists() and any(extraction_root.iterdir()):
                raise VerificationError(
                    f"Extraction destination is not empty: {extraction_root}"
                )
            extraction_root.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(args.archive.resolve(), "r") as archive:
                for info in archive.infolist():
                    # Member names were already validated by verify_archive().
                    target = extraction_root.joinpath(*PurePosixPath(info.filename).parts)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(archive.read(info.filename))
            report["persistent_clean_extraction"] = str(extraction_root)
            if args.run_consumer:
                consumer = extraction_root / "build" / "Release" / "bin" / "dee_thinking_consumer.exe"
                completed = subprocess.run(
                    [str(consumer)],
                    cwd=extraction_root,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=120,
                    check=False,
                )
                report["extracted_consumer"] = {
                    "path": str(consumer),
                    "returncode": completed.returncode,
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                }
                if completed.returncode != 0:
                    raise VerificationError(
                        f"Extracted independent consumer returned {completed.returncode}"
                    )
        except (OSError, subprocess.SubprocessError, zipfile.BadZipFile, VerificationError) as exc:
            print(json.dumps({"zip_valid": False, "error": str(exc)}, indent=2))
            return 1

    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    print(rendered, end="")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
