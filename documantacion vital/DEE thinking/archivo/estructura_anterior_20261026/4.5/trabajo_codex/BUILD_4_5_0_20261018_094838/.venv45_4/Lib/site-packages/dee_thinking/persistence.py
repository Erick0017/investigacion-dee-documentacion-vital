"""Bounded, byte-preserving persistence for native operational snapshots.

Compression is a storage adapter, not a reconstruction or physical edit. CRC,
size and optional SHA-256 are checked before the native loader sees a gzip file.
No arbitrary Python object, function or pickle is serialized.
"""
from __future__ import annotations

from contextlib import contextmanager
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import uuid

BLOCK_BYTES = 1024 * 1024
DEFAULT_MAX_SNAPSHOT_BYTES = 2 * 1024**3
DEFAULT_MAX_METADATA_BYTES = 8 * 1024**2


def _positive_integer(value, name):
    if type(value) is not int or value <= 0:
        raise ValueError(name + " must be a positive exact integer")
    return value


def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(BLOCK_BYTES), b""):
            h.update(block)
    return h.hexdigest()


def _expected_hash(value):
    if value is not None and (not isinstance(value, str) or len(value) != 64
            or any(c not in "0123456789abcdefABCDEF" for c in value)):
        raise ValueError("expected_sha256 must be a 64-character hexadecimal SHA-256")
    return value.lower() if value else None


def _walk_json(value, *, depth=0, counter=None):
    if counter is None:
        counter = [0]
    counter[0] += 1
    if counter[0] > 250000 or depth > 40:
        raise ValueError("Session metadata exceeds its structural bound")
    kind = type(value)
    if value is None or kind is bool:
        return
    if kind is int:
        if not -(2**63) <= value < 2**64:
            raise ValueError("Session metadata integer is outside exact 64-bit range")
        return
    if kind is str:
        if len(value) > 1024**2:
            raise ValueError("Session metadata string exceeds its bound")
        return
    if kind is list:
        for item in value:
            _walk_json(item, depth=depth + 1, counter=counter)
        return
    if kind is dict:
        if not all(type(key) is str for key in value):
            raise TypeError("Session metadata keys must be strings")
        for key, item in value.items():
            _walk_json(key, depth=depth + 1, counter=counter)
            _walk_json(item, depth=depth + 1, counter=counter)
        return
    raise TypeError("Session metadata accepts JSON objects, lists and exact scalar values only")


def encode_metadata(value, *, max_bytes=DEFAULT_MAX_METADATA_BYTES):
    """Encode bounded operational metadata; floats and arbitrary objects fail."""
    _positive_integer(max_bytes, "max_bytes")
    _walk_json(value)
    text = json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    if len(text.encode("utf-8")) > max_bytes:
        raise ValueError("Session metadata exceeds its byte bound")
    return text


def decode_metadata(text, *, max_bytes=DEFAULT_MAX_METADATA_BYTES):
    _positive_integer(max_bytes, "max_bytes")
    if not isinstance(text, str):
        raise TypeError("Snapshot metadata must be UTF-8 text")
    if len(text.encode("utf-8")) > max_bytes:
        raise ValueError("Session metadata exceeds its byte bound")
    def no_float(_):
        raise ValueError("Floating-point numbers are not an operational integer encoding")
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON metadata key")
            result[key] = value
        return result
    try:
        value = json.loads(text, parse_float=no_float, parse_constant=no_float,
                           object_pairs_hook=unique_pairs)
    except (RecursionError, UnicodeError) as error:
        raise ValueError("Malformed session metadata") from error
    _walk_json(value)
    return value


@contextmanager
def materialized_snapshot(path, *, max_bytes=DEFAULT_MAX_SNAPSHOT_BYTES,
                          expected_sha256=None):
    """Yield ``(ASCII plain path, proof)`` without modifying the input.

    ``expected_sha256`` identifies the *decoded native bytes*, not the gzip
    transport. Explicit ``.gz`` is required for compressed input; no directory
    searches or restoration from another checkpoint are performed.
    """
    _positive_integer(max_bytes, "max_bytes")
    expected_sha256 = _expected_hash(expected_sha256)
    path = Path(path).resolve(strict=True)
    if not path.is_file():
        raise ValueError("Snapshot must be a regular file")
    if path.stat().st_size > max_bytes:
        raise ValueError("Encoded/plain snapshot exceeds the explicit byte bound")
    compressed = path.suffix.lower() == ".gz"
    with tempfile.TemporaryDirectory(prefix="dee45-state-") as temporary:
        target = Path(temporary) / "native.deetsnap"
        if not str(target).isascii():
            raise ValueError("This native Windows toolchain requires an ASCII temporary path")
        h = hashlib.sha256()
        size = 0
        opener = gzip.open if compressed else open
        # Reading through EOF validates every gzip member's CRC before yield.
        try:
            with opener(path, "rb") as source, target.open("xb") as destination:
                for block in iter(lambda: source.read(BLOCK_BYTES), b""):
                    size += len(block)
                    if size > max_bytes:
                        raise ValueError("Decoded snapshot exceeds the explicit byte bound")
                    h.update(block)
                    destination.write(block)
        except (OSError, EOFError, gzip.BadGzipFile) as error:
            raise ValueError("Truncated, corrupt or unreadable snapshot storage") from error
        digest = h.hexdigest()
        if expected_sha256 is not None and digest != expected_sha256:
            raise ValueError("Decoded native snapshot SHA-256 mismatch")
        proof = {"encoding": "gzip" if compressed else "native",
                 "decoded_bytes": size, "decoded_sha256": digest,
                 "encoded_bytes": path.stat().st_size,
                 "encoded_sha256": sha256_file(path),
                 "gzip_crc_verified": True if compressed else None,
                 "original_modified": False}
        yield target, proof


def inspect_snapshot(path, *, max_bytes=DEFAULT_MAX_SNAPSHOT_BYTES, expected_sha256=None):
    """Verify storage only; this does not certify a native format or function."""
    with materialized_snapshot(path, max_bytes=max_bytes, expected_sha256=expected_sha256) as (_, proof):
        return proof


def save_world_snapshot(world, path, *, include_trace=True, compress=None,
                        overwrite=False, max_bytes=DEFAULT_MAX_SNAPSHOT_BYTES):
    """Save one native world atomically, preserving an existing file by default."""
    if type(include_trace) is not bool or type(overwrite) is not bool:
        raise TypeError("include_trace and overwrite must be explicit booleans")
    _positive_integer(max_bytes, "max_bytes")
    path = Path(path).resolve()
    if compress is None:
        compress = path.suffix.lower() == ".gz"
    if type(compress) is not bool:
        raise TypeError("compress must be bool or None")
    if compress != (path.suffix.lower() == ".gz"):
        raise ValueError("Compressed snapshots use an explicit .gz suffix")
    if path.exists() and not overwrite:
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_name(path.name + ".pending." + uuid.uuid4().hex)
    try:
        with tempfile.TemporaryDirectory(prefix="dee45-save-") as temporary:
            plain = Path(temporary) / "native.deetsnap"
            if not str(plain).isascii():
                raise ValueError("Use an ASCII temporary path with this Windows native build")
            world.save_snapshot(str(plain), include_trace)
            if plain.stat().st_size > max_bytes:
                raise ValueError("Native snapshot exceeds explicit storage bound")
            logical_hash = sha256_file(plain)
            with plain.open("rb") as source, pending.open("xb") as sink:
                if compress:
                    with gzip.GzipFile(filename="", mode="wb", fileobj=sink,
                                       compresslevel=6, mtime=0) as encoded:
                        shutil.copyfileobj(source, encoded, BLOCK_BYTES)
                else:
                    shutil.copyfileobj(source, sink, BLOCK_BYTES)
            # A pending filename has no .gz suffix; use a native byte comparison
            # here and read gzip explicitly when requested.
            h = hashlib.sha256(); count = 0
            opener = gzip.open if compress else open
            with opener(pending, "rb") as stream:
                for block in iter(lambda: stream.read(BLOCK_BYTES), b""):
                    count += len(block)
                    if count > max_bytes:
                        raise ValueError("Snapshot verification exceeds byte bound")
                    h.update(block)
            if count != plain.stat().st_size or h.hexdigest() != logical_hash:
                raise ValueError("Saved snapshot storage failed byte identity verification")
            if overwrite:
                os.replace(pending, path)
            else:
                if os.name == "nt":
                    os.rename(pending, path)  # Windows fails if destination exists
                else:
                    os.link(pending, path)  # no-overwrite publication on POSIX
                    pending.unlink()
        return {"path": str(path), "encoding": "gzip" if compress else "native",
                "decoded_sha256": logical_hash, "decoded_bytes": count,
                "encoded_sha256": sha256_file(path), "encoded_bytes": path.stat().st_size,
                "gzip_crc_verified": True if compress else None,
                "scope": "NATIVE_OPERATIONAL_SNAPSHOT_STORAGE"}
    finally:
        if pending.exists():
            pending.unlink()  # only this operation's uniquely named partial


def load_world_snapshot(path, *, max_bytes=DEFAULT_MAX_SNAPSHOT_BYTES, expected_sha256=None):
    from . import _native as native
    with materialized_snapshot(path, max_bytes=max_bytes, expected_sha256=expected_sha256) as (plain, proof):
        world = native.OrganizationalWorld.load_snapshot(str(plain))
    return world, proof
