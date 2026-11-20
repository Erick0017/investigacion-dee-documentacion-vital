"""Read-only process current-directory locator for a DEE directory rename.

No process is stopped, suspended, injected, changed or written. Only bounded
PEB/process-parameters/CWD string bytes are read. Only matching DEE paths print.
Uses dynamically linked Windows APIs and the x64 PEB/process-parameters layout.
"""
from __future__ import annotations
import ctypes as c
from ctypes import wintypes as w
from datetime import datetime, timezone
import json
import os
import struct

if os.name != 'nt' or struct.calcsize('P') != 8:
    raise SystemExit('Windows x64 required')

k = c.WinDLL('kernel32', use_last_error=True)
n = c.WinDLL('ntdll', use_last_error=True)
HANDLE = w.HANDLE
SIZE = c.c_size_t
INVALID = c.c_void_p(-1).value

class Entry(c.Structure):
    _fields_ = [('dwSize', w.DWORD), ('cntUsage', w.DWORD), ('th32ProcessID', w.DWORD),
        ('th32DefaultHeapID', SIZE), ('th32ModuleID', w.DWORD), ('cntThreads', w.DWORD),
        ('th32ParentProcessID', w.DWORD), ('pcPriClassBase', w.LONG), ('dwFlags', w.DWORD),
        ('szExeFile', w.WCHAR * 260)]

class Basic(c.Structure):
    _fields_ = [('Reserved1', c.c_void_p), ('PebBaseAddress', c.c_void_p),
        ('Reserved2', c.c_void_p * 2), ('UniqueProcessId', SIZE), ('Reserved3', c.c_void_p)]

k.CreateToolhelp32Snapshot.argtypes = [w.DWORD, w.DWORD]
k.CreateToolhelp32Snapshot.restype = HANDLE
k.Process32FirstW.argtypes = [HANDLE, c.POINTER(Entry)]
k.Process32FirstW.restype = w.BOOL
k.Process32NextW.argtypes = [HANDLE, c.POINTER(Entry)]
k.Process32NextW.restype = w.BOOL
k.OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]
k.OpenProcess.restype = HANDLE
k.CloseHandle.argtypes = [HANDLE]
k.CloseHandle.restype = w.BOOL
k.ReadProcessMemory.argtypes = [HANDLE, c.c_void_p, c.c_void_p, SIZE, c.POINTER(SIZE)]
k.ReadProcessMemory.restype = w.BOOL
k.IsWow64Process.argtypes = [HANDLE, c.POINTER(w.BOOL)]
k.IsWow64Process.restype = w.BOOL
k.GetCurrentProcess.argtypes = []
k.GetCurrentProcess.restype = HANDLE
k.DuplicateHandle.argtypes = [HANDLE, HANDLE, HANDLE, c.POINTER(HANDLE), w.DWORD, w.BOOL, w.DWORD]
k.DuplicateHandle.restype = w.BOOL
k.GetFinalPathNameByHandleW.argtypes = [HANDLE, w.LPWSTR, w.DWORD, w.DWORD]
k.GetFinalPathNameByHandleW.restype = w.DWORD
n.NtQueryInformationProcess.argtypes = [HANDLE, w.ULONG, c.c_void_p, w.ULONG, c.POINTER(w.ULONG)]
n.NtQueryInformationProcess.restype = w.LONG

def read(handle, address, length):
    if not address or not 1 <= length <= 65536:
        raise ValueError('Bounded remote read refused')
    result = c.create_string_buffer(length)
    got = SIZE()
    if not k.ReadProcessMemory(handle, address, result, length, c.byref(got)) or got.value != length:
        raise OSError(c.get_last_error(), 'ReadProcessMemory')
    return result.raw

def path_from_remote_cwd_handle(pid, remote_handle):
    # Duplicate only a matching CWD directory handle. NEVER DUPLICATE_CLOSE_SOURCE.
    source = k.OpenProcess(0x0040, False, pid)
    if not source:
        return {'status': 'duplicate_process_open_denied', 'winerror': c.get_last_error()}
    duplicate = HANDLE()
    try:
        if not k.DuplicateHandle(source, HANDLE(remote_handle), k.GetCurrentProcess(), c.byref(duplicate), 0, False, 2):
            return {'status': 'duplicate_denied', 'winerror': c.get_last_error()}
        try:
            output = c.create_unicode_buffer(32768)
            length = k.GetFinalPathNameByHandleW(duplicate, output, len(output), 0)
            if not 0 < length < len(output):
                return {'status': 'path_unavailable', 'winerror': c.get_last_error()}
            return {'status': 'directory_handle_resolved', 'path': output.value,
                'source_handle_left_open_and_unchanged': True}
        finally:
            k.CloseHandle(duplicate)
    finally:
        k.CloseHandle(source)

names = {'cmd.exe', 'pwsh.exe', 'powershell.exe', 'python.exe', 'pythonw.exe',
    'node.exe', 'codex.exe', 'explorer.exe', 'code.exe'}
rows, errors = [], {}
snapshot = k.CreateToolhelp32Snapshot(2, 0)
if snapshot == INVALID:
    raise OSError(c.get_last_error(), 'CreateToolhelp32Snapshot')
try:
    item = Entry()
    item.dwSize = c.sizeof(Entry)
    exists = k.Process32FirstW(snapshot, c.byref(item))
    selected = []
    while exists:
        if item.szExeFile.casefold() in names:
            selected.append((int(item.th32ProcessID), int(item.th32ParentProcessID), item.szExeFile))
        exists = k.Process32NextW(snapshot, c.byref(item))
finally:
    k.CloseHandle(snapshot)

for pid, parent, name in selected:
    handle = k.OpenProcess(0x0410, False, pid)
    if not handle:
        code = str(c.get_last_error())
        errors[code] = errors.get(code, 0) + 1
        continue
    try:
        wow = w.BOOL()
        if not k.IsWow64Process(handle, c.byref(wow)) or wow.value:
            errors['wow64_or_unknown'] = errors.get('wow64_or_unknown', 0) + 1
            continue
        basic = Basic()
        returned = w.ULONG()
        status = n.NtQueryInformationProcess(handle, 0, c.byref(basic), c.sizeof(basic), c.byref(returned))
        if status < 0:
            raise ValueError('NtQueryInformationProcess status ' + hex(status & 0xffffffff))
        peb = read(handle, basic.PebBaseAddress, 0x28)
        params_ptr = int.from_bytes(peb[0x20:0x28], 'little')
        # x64 RTL_USER_PROCESS_PARAMETERS: CurrentDirectory at byte56.
        # CURDIR.DosPath is UNICODE_STRING; CURDIR.Handle is at byte72.
        params = read(handle, params_ptr, 0x50)
        length, maximum = struct.unpack_from('<HH', params, 56)
        buffer_ptr = int.from_bytes(params[64:72], 'little')
        cwd_handle = int.from_bytes(params[72:80], 'little')
        if length % 2 or not 0 < length <= maximum <= 65534:
            raise ValueError('Invalid bounded CWD Unicode length')
        cwd = read(handle, buffer_ptr, length).decode('utf-16-le')
        if 'dee thinking' in cwd.casefold() or 'casos practicos' in cwd.casefold():
            rows.append({'pid': pid, 'parent_pid': parent, 'name': name, 'cwd': cwd,
                'cwd_directory_handle_present': bool(cwd_handle),
                'cwd_directory_handle': path_from_remote_cwd_handle(pid, cwd_handle) if cwd_handle else None})
    except Exception as error:
        key = type(error).__name__ + ': ' + str(error)
        errors[key] = errors.get(key, 0) + 1
    finally:
        k.CloseHandle(handle)

print(json.dumps({'utc': datetime.now(timezone.utc).isoformat(), 'mode': 'READ_ONLY_CWD_HANDLE_LOCATOR',
    'selected_process_count': len(selected), 'matches': rows, 'unreadable_counts': errors,
    'not_read': ['command_lines', 'environment_variables', 'general_memory_contents'],
    'not_done': ['write_process_memory', 'suspend', 'terminate', 'close_remote_handle', 'change_acl', 'move']},
    ensure_ascii=False, indent=2))
