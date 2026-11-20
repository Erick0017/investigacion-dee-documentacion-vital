"""Verify official4.5 and stage only minimal immutable execution dependencies."""
from __future__ import annotations
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import platform
import struct
import sys
import zipfile
import winreg

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT.parents[4]
PRODUCT = BASE / '4.5'
NAME = 'DEE_THINKING_4_5_0_COMPILACION_Y_VALIDACION_RESULTADOS.zip'
WHL = 'dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'
EXPECTED_ZIP = 'ae9ff8ba5fef7a0bf6ca6c760a7e471610e171eca682cee878e9276b20a70128'
EXPECTED_WHEEL = '09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'
EXPECTED_NATIVE = '17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'
EXPECTED_KERNEL = 'fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()

def put(name, value):
    path = ROOT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [('dwLength', wintypes.DWORD), ('dwMemoryLoad', wintypes.DWORD)] + [(k, ctypes.c_ulonglong) for k in
        ('ullTotalPhys','ullAvailPhys','ullTotalPageFile','ullAvailPageFile','ullTotalVirtual','ullAvailVirtual','ullAvailExtendedVirtual')]

def main():
    assert sys.implementation.name == 'cpython' and sys.version_info[:2] == (3,13) and struct.calcsize('P') == 8
    archive = PRODUCT / NAME
    assert sha(archive) == EXPECTED_ZIP
    previous = json.loads((PRODUCT / 'VERIFICACION_FINAL_EXTERNA.json').read_text(encoding='utf-8-sig'))
    assert previous['status'] == 'VERIFIED' and previous['candidate_sha256'] == EXPECTED_ZIP
    prefix = 'DEE_thinking_4_5_0/'
    selected = []
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        manifest = json.loads(z.read(prefix + 'MANIFEST.json'))
        records = {r['path']: r for r in manifest['files']}
        targets = {
            'wheel/' + WHL: 'runtime/' + WHL,
            'source/src/kernel_v27.cpp': 'genealogia/product45/kernel_v27.cpp',
            'source/src/consolidated.cpp': 'genealogia/product45/consolidated.cpp',
            'source/include/dee_thinking/consolidated.hpp': 'genealogia/product45/consolidated.hpp',
            'PRODUCT_CONTRACT.json': 'genealogia/product45/PRODUCT_CONTRACT.json',
            'MATRIZ_CAPACIDADES_CPC.json': 'genealogia/product45/MATRIZ_CAPACIDADES_CPC.json',
            'MATRIZ_SUPERSESIONES.json': 'genealogia/product45/MATRIZ_SUPERSESIONES.json',
            'VALIDATION_REPORT.json': 'genealogia/product45/VALIDATION_REPORT.json',
            'BUILD_INFO.json': 'genealogia/product45/BUILD_INFO.json',
        }
        for name in records:
            if name.startswith(('source/tests/python/', 'source/fixtures/')):
                targets[name] = 'base_validada/product45/' + name.removeprefix('source/')
        for name, relative in sorted(targets.items()):
            data = z.read(prefix + name)
            assert len(data) == records[name]['bytes'] and hashlib.sha256(data).hexdigest() == records[name]['sha256']
            output = ROOT / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            if output.exists():
                assert sha(output) == records[name]['sha256']
            else:
                output.write_bytes(data)
            selected.append({'source_member': name, 'path': relative, 'bytes': len(data), 'sha256': records[name]['sha256']})
    assert sha(ROOT / 'runtime' / WHL) == EXPECTED_WHEEL
    assert sha(ROOT / 'genealogia/product45/kernel_v27.cpp') == EXPECTED_KERNEL
    with zipfile.ZipFile(ROOT / 'runtime' / WHL) as z:
        native = next(x for x in z.namelist() if x.endswith('.pyd'))
        assert hashlib.sha256(z.read(native)).hexdigest() == EXPECTED_NATIVE
    memory = MEMORYSTATUSEX(); memory.dwLength = ctypes.sizeof(memory)
    assert ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory))
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'HARDWARE\DESCRIPTION\System\CentralProcessor\0') as key:
        cpu = winreg.QueryValueEx(key, 'ProcessorNameString')[0].strip()
    put('runtime/REFERENCE_IDENTITY.json', {'schema':'CPC8.official-instrument.v1','archive':str(archive),
        'archive_sha256':EXPECTED_ZIP,'archive_bytes':archive.stat().st_size,'CRC':'PASS',
        'previous_exact_zip_proof_sha256':sha(PRODUCT/'VERIFICACION_FINAL_EXTERNA.json'),
        'wheel_sha256':EXPECTED_WHEEL,'native_sha256':EXPECTED_NATIVE,'kernel_source_sha256':EXPECTED_KERNEL,
        'selected_members':selected,'historical_bytes_not_embedded':'Original historical ZIPs are not copied into CPC8.'})
    put('revision/INITIAL_RESOURCES.json', {'schema':'CPC8.machine-resources.v1','machine':platform.node(),
        'cpu':cpu,'logical_processors':os.cpu_count(),'total_physical_bytes':memory.ullTotalPhys,
        'available_physical_bytes':memory.ullAvailPhys,'memory_load_percent':memory.dwMemoryLoad,
        'python':sys.version,'python_executable':sys.executable,'initial_cim_probe':'First sandbox query denied; approved read confirmed Lenovo20AWA15L00 and total RAM16852312064.',
        'budget':json.loads((ROOT/'BUDGET.json').read_text(encoding='utf-8')),
        'memory_formula':'32*N^3 basic Runtime buffers plus scratch, Python arrays, snapshots, analysis and pending queues; job hard limit3GiB.'})
    print(json.dumps({'status':'VERIFIED','selected_files':len(selected),'cpu':cpu,'RAM':memory.ullTotalPhys,
        'available_RAM':memory.ullAvailPhys,'wheel_sha256':EXPECTED_WHEEL}))

if __name__ == '__main__':
    main()
