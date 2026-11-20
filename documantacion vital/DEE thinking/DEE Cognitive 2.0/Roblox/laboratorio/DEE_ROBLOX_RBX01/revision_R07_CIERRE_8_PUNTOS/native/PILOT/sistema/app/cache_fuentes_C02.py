"""Opt-in immutable source-byte cache, never operational state or Native data.

Every cached file is fully read and SHA256 recorded once while a Windows
read-only, deny-write/delete handle stays open. Existing validators still run
and hash the exact same bytes. Handles and fresh hashes are checked at exit.
No cache entry is admitted from estado, Native binaries or linked paths.
"""
from pathlib import Path
import ctypes
import hashlib
import io
import os
import stat

MAX_BYTES = 32 * 1024 * 1024
MAX_FILE_BYTES = 4 * 1024 * 1024
_READ_BYTES = Path.read_bytes
_READ_TEXT = Path.read_text


def key(path):
    return os.path.normcase(os.path.abspath(os.fspath(path)))


class WindowsReadLease:
    """Share-read only prevents concurrent source replacement or writing."""
    def __init__(self, path):
        if os.name != 'nt':
            raise RuntimeError('Source cache requires Windows deny-write leases')
        from ctypes import wintypes
        k = ctypes.WinDLL('kernel32', use_last_error=True)
        k.CreateFileW.argtypes = (wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                 wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD,
                                 wintypes.HANDLE)
        k.CreateFileW.restype = wintypes.HANDLE
        k.CloseHandle.argtypes = (wintypes.HANDLE,)
        k.CloseHandle.restype = wintypes.BOOL
        # GENERIC_READ, FILE_SHARE_READ only, OPEN_EXISTING; no write/delete share.
        self.api = k
        raw = str(Path(path).absolute())
        if not raw.startswith('\\\\?\\'):
            raw = '\\\\?\\UNC\\' + raw[2:] if raw.startswith('\\\\') else '\\\\?\\' + raw
        self.handle = k.CreateFileW(raw, 0x80000000, 1, None, 3, 0x00200000, None)
        if self.handle == wintypes.HANDLE(-1).value:
            raise OSError(ctypes.get_last_error(), 'Cannot lock immutable source', str(path))

    def close(self):
        if self.handle is not None:
            if not self.api.CloseHandle(self.handle):
                raise OSError(ctypes.get_last_error(), 'Source lease close failed')
            self.handle = None


class ImmutableSourceCache:
    def __init__(self, system, *, lease_factory=WindowsReadLease):
        self.system = Path(system).resolve(strict=True)
        self.lease_factory = lease_factory
        self.entries = {}
        self.leases = []
        self.total_bytes = 0
        self.hits = 0
        self.active = False

    def _regular(self, path, checked):
        for parent in (path, *path.parents):
            k = key(parent)
            if k in checked:
                break
            value = parent.lstat()
            if stat.S_ISLNK(value.st_mode) or getattr(value, 'st_file_attributes', 0) & 1024:
                raise ValueError('Linked/reparse source rejected: ' + str(parent))
            checked.add(k)
        if not path.is_file():
            raise ValueError('Regular immutable source required')

    def open(self):
        if self.active or Path.read_bytes is not _READ_BYTES or Path.read_text is not _READ_TEXT:
            raise RuntimeError('One explicit source cache per owner only')
        checked = set()
        try:
            for folder in ('app', 'capacidades'):
                root = self.system / folder
                self._regular(root / '__init__.py', checked) if (root / '__init__.py').exists() else None
                for current, directories, files in os.walk(root, followlinks=False):
                    directories[:] = sorted(d for d in directories if d != '__pycache__'
                                            and not (Path(current).name == 'core'
                                                     and d in ('mecanismos', 'verificaciones')))
                    for name in sorted(files):
                        path = Path(current) / name
                        if path.suffix.lower() not in ('.py', '.json'):
                            continue
                        self._regular(path, checked)
                        if path.stat().st_size > MAX_FILE_BYTES:
                            raise ValueError('Immutable source exceeds finite cache bound')
                        lease = self.lease_factory(path)
                        self.leases.append(lease)
                        data = _READ_BYTES(path)
                        self.total_bytes += len(data)
                        if self.total_bytes > MAX_BYTES:
                            raise ValueError('Immutable source cache exceeds32MiB')
                        self.entries[key(path)] = (path, data, hashlib.sha256(data).hexdigest())
            owner = self
            def read_bytes(path):
                item = owner.entries.get(key(path))
                if item is None:
                    return _READ_BYTES(path)
                owner.hits += 1
                return item[1]
            def read_text(path, encoding=None, errors=None, newline=None):
                item = owner.entries.get(key(path))
                if item is None:
                    # Path.read_text acquired newline in Python3.13.
                    if newline is None:
                        return _READ_TEXT(path, encoding=encoding, errors=errors)
                    return _READ_TEXT(path, encoding=encoding, errors=errors, newline=newline)
                owner.hits += 1
                with io.TextIOWrapper(io.BytesIO(item[1]), encoding=io.text_encoding(encoding),
                                      errors=errors, newline=newline) as source:
                    return source.read()
            Path.read_bytes = read_bytes
            Path.read_text = read_text
            self.active = True
            return self
        except BaseException:
            for lease in reversed(self.leases):
                lease.close()
            self.leases.clear()
            raise

    def witness(self):
        return {'schema': 'DEE.RBX01.C02.immutable_source_cache.v1',
                'source_files': len(self.entries), 'bytes': self.total_bytes, 'hits': self.hits,
                'source_sha256': {p.relative_to(self.system).as_posix(): sha
                                  for p, data, sha in self.entries.values()},
                'windows_deny_write_delete_leases': self.lease_factory is WindowsReadLease,
                'operational_state_cached': False, 'validators_not_skipped': True}

    def close(self):
        if not self.active:
            return
        # Restore methods before physical reads; hold all leases during recheck.
        Path.read_bytes = _READ_BYTES
        Path.read_text = _READ_TEXT
        self.active = False
        try:
            for path, data, expected in self.entries.values():
                if hashlib.sha256(_READ_BYTES(path)).hexdigest() != expected:
                    raise RuntimeError('Immutable source changed under lease: ' + str(path))
        finally:
            for lease in reversed(self.leases):
                lease.close()
            self.leases.clear()

