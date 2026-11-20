"""Real official Native factory; called only after explicit service start."""
from pathlib import Path
import ctypes
import importlib.util
import time
from common_focal import RUNTIME, budget, closed_native, operational_window, read, safe, sha

def free_memory():
    class Memory(ctypes.Structure):
        _fields_ = [('length', ctypes.c_ulong), ('load', ctypes.c_ulong), ('total', ctypes.c_ulonglong),
                    ('free', ctypes.c_ulonglong), ('totalPage', ctypes.c_ulonglong), ('freePage', ctypes.c_ulonglong),
                    ('totalVirtual', ctypes.c_ulonglong), ('freeVirtual', ctypes.c_ulonglong), ('extended', ctypes.c_ulonglong)]
    m = Memory(); m.length = ctypes.sizeof(m)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)): raise OSError('Host memory unavailable')
    return m.free

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module); return module

def create_session(home, cfg, window):
    window = operational_window(cfg, RUNTIME)
    if any((home / p).exists() for p in ('IMPORT0_EN_CURSO.json','IMPORT0_INCOMPLETO.json','PREPARACION_EN_CURSO.json','PREPARACION_INCOMPLETA.json','SDK_LEASE_IN_PROGRESS.json')):
        raise RuntimeError('INCOMPLETE_PREPARATION_PRESERVED_NO_OWNER')
    if free_memory() < window['minimumHostFreeBytes']: raise RuntimeError('HOST_FREE_RAM_BELOW_3_5GiB')
    proof = closed_native(home, cfg)
    if proof['dimension'] != 67: raise ValueError('Exact inherited N67')
    ready = read(home / 'SDK_READY.json')
    if not ready['physical_equal'] or not ready['causal_prefix_equal']: raise ValueError('Whole prefix import proof required')
    pair = home / 'SDK_PAIR.json'
    if pair.exists():
        old = read(pair)
        for key in ('nativeTick', 'snapshotSha256', 'databaseSha256', 'cardSha256'):
            if old['native'][key] != proof[key]: raise RuntimeError('Paired Native changed; no continuation')
        if old['sessionId'] != cfg['sessionId'] or old['localSequence'] != cfg['localSequence']:
            raise ValueError('Paired cursor/session differs')
    elif cfg['localSequence'] != 0 or proof['nativeTick'] != 991187:
        raise ValueError('NEW requires unadvanced full PAR28; continuation requires a sealed pair')
    support = load('_sdk_official_owner', Path(__file__).with_name('sdk_owner_focal.py'))
    owner = support.configured_owner(RUNTIME / 'dependencias/producto', home,
        RUNTIME / 'estado_demo/LEDGER_SDK.json', tag='SDK_REAL',
        cutoff_epoch=window['hardFinishUtcEpoch'], continuous=True)
    actual = load('_sdk_native_adapter', Path(__file__).with_name('native_adapter_focal.py')).create_adapter({'owner': owner})
    class BoundedAdapter:
        def execute(self, kind, payload, context):
            if free_memory() < 1073741824: raise RuntimeError('HOST_FREE_RAM_BELOW_1GiB_BEFORE_QUEUE_ADMISSION')
            return actual.execute(kind, payload, context)
    return owner, BoundedAdapter()
