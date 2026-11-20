"""Locate open on-disk DEE directory/file handles without closing remote handles.

All probes duplicate a handle into THIS process; only that duplicate is closed.
No privileges are enabled, processes stopped, files written, ACLs changed or
remote handles closed. All outputs are restricted to the named DEE paths.
"""
from pathlib import Path
import ctypes as c
from ctypes import wintypes as w
import importlib.util
import json
import os
import time

spec = importlib.util.spec_from_file_location('cwd_readonly', Path(__file__).with_name('consultar_cwd_dee_sololectura.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
k, n, HANDLE, SIZE = m.k, m.n, m.HANDLE, m.SIZE

class HandleEntry(c.Structure):
    _fields_ = [('Object', c.c_void_p), ('UniqueProcessId', SIZE), ('HandleValue', SIZE),
        ('GrantedAccess', w.ULONG), ('CreatorBackTraceIndex', w.USHORT), ('ObjectTypeIndex', w.USHORT),
        ('HandleAttributes', w.ULONG), ('Reserved', w.ULONG)]

n.NtQuerySystemInformation.argtypes = [w.ULONG, c.c_void_p, w.ULONG, c.POINTER(w.ULONG)]
n.NtQuerySystemInformation.restype = w.LONG
k.CreateFileW.argtypes = [w.LPCWSTR, w.DWORD, w.DWORD, c.c_void_p, w.DWORD, w.DWORD, HANDLE]
k.CreateFileW.restype = HANDLE
k.GetFileType.argtypes = [HANDLE]
k.GetFileType.restype = w.DWORD

root = Path(r'D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\DEE thinking')
target = root / 'casos practicos'
own = k.CreateFileW(str(target), 0, 7, None, 3, 0x02000000, None)
if own == m.INVALID:
    raise OSError(c.get_last_error(), 'Open target directory read-only/share-all')

try:
    size = 1 << 20
    while True:
        data = c.create_string_buffer(size)
        returned = w.ULONG()
        status = n.NtQuerySystemInformation(64, data, size, c.byref(returned))
        if status >= 0:
            break
        if status & 0xffffffff not in (0xc0000004, 0xc0000023) or size >= 128 << 20:
            raise RuntimeError('NtQuerySystemInformation ' + hex(status & 0xffffffff))
        size = max(size * 2, int(returned.value) + 65536)
    count = SIZE.from_buffer_copy(data.raw[:8]).value
    if 16 + count * c.sizeof(HandleEntry) > size:
        raise ValueError('Handle table size mismatch')
    entries = (HandleEntry * count).from_buffer(data, 16)
    ours = next((x for x in entries if x.UniqueProcessId == os.getpid() and x.HandleValue == own), None)
    if ours is None:
        raise RuntimeError('Cannot establish File object type from own directory handle')
    file_type = int(ours.ObjectTypeIndex)

    names = {}
    snapshot = k.CreateToolhelp32Snapshot(2, 0)
    try:
        item = m.Entry()
        item.dwSize = c.sizeof(item)
        good = k.Process32FirstW(snapshot, c.byref(item))
        while good:
            names[int(item.th32ProcessID)] = (item.szExeFile, int(item.th32ParentProcessID))
            good = k.Process32NextW(snapshot, c.byref(item))
    finally:
        k.CloseHandle(snapshot)

    handles, denied, seen, hits = {}, set(), 0, []
    began = time.monotonic()
    output = c.create_unicode_buffer(32768)
    try:
        for entry in entries:
            pid = int(entry.UniqueProcessId)
            if entry.ObjectTypeIndex != file_type or pid == os.getpid() or pid in denied:
                continue
            if time.monotonic() - began > 50:
                break
            if pid not in handles:
                handle = k.OpenProcess(0x0040, False, pid)
                if not handle:
                    denied.add(pid)
                    continue
                handles[pid] = handle
            duplicate = HANDLE()
            if not k.DuplicateHandle(handles[pid], HANDLE(entry.HandleValue), k.GetCurrentProcess(), c.byref(duplicate), 0, False, 2):
                continue
            try:
                if k.GetFileType(duplicate) != 1:
                    continue
                seen += 1
                length = k.GetFinalPathNameByHandleW(duplicate, output, len(output), 0)
                if not 0 < length < len(output):
                    continue
                path = output.value
                if 'dee thinking' not in path.casefold() and 'casos practicos' not in path.casefold():
                    continue
                name, parent = names.get(pid, ('unknown', None))
                hits.append({'pid': pid, 'parent_pid': parent, 'name': name, 'path': path,
                    'remote_handle_value': int(entry.HandleValue), 'granted_access': hex(entry.GrantedAccess),
                    'remote_handle_unchanged': True})
            finally:
                k.CloseHandle(duplicate)
    finally:
        for handle in handles.values():
            k.CloseHandle(handle)
    print(json.dumps({'mode': 'READ_ONLY_DISK_HANDLE_LOCATOR', 'system_handle_count': int(count),
        'disk_handles_inspected': seen, 'elapsed_seconds': time.monotonic() - began,
        'processes_opened_read_only_for_duplication': len(handles), 'inaccessible_process_count': len(denied),
        'bounded_50_second_scan_complete': time.monotonic() - began <= 50,
        'matches': hits, 'no_remote_handles_closed': True,
        'limitation': 'Read-only open-handle evidence; a matched handle alone does not disclose its original share-delete flags.'},
        ensure_ascii=False, indent=2))
finally:
    k.CloseHandle(own)
