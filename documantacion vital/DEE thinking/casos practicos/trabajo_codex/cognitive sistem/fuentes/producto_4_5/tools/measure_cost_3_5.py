"""Small measured reference windows, not industrial performance promises."""
import argparse
import ctypes
from ctypes import wintypes
import json
from pathlib import Path
import time
import dee_thinking as d


class ProcessMemory(ctypes.Structure):
    _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD),
                *[(n, ctypes.c_size_t) for n in ('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage')]]


def memory():
    psapi = ctypes.WinDLL('psapi'); kernel = ctypes.WinDLL('kernel32')
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(ProcessMemory), wintypes.DWORD]
    info = ProcessMemory(); info.cb = ctypes.sizeof(info)
    assert psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(info), info.cb)
    return {'process_working_set_bytes': info.WorkingSetSize, 'process_peak_working_set_bytes': info.PeakWorkingSetSize}


def main(a):
    results = []
    for recipe, ticks in [('mobile_pair', 11), ('mobile_basal', 12), ('distributed', 40)]:
        before = memory(); start = time.perf_counter(); w = d.create_organization(recipe)
        if recipe == 'mobile_pair':
            for j, teacher in enumerate((7,11)):
                w.submit(f'l{j}.cue',5,0); w.submit(f'l{j}.teacher',teacher,0)
            w.probe('q0.query',13,6)
        elif recipe == 'distributed':
            w.submit('integration.A',8,0); w.submit('integration.B',9,0)
        prepared = time.perf_counter(); w.advance(ticks); end = time.perf_counter()
        results.append({'recipe':recipe, 'N':w.runtime.dimension, 'ticks':ticks,
                        'backend':str(w.runtime.execution_options.backend), 'threads':w.runtime.execution_options.threads,
                        'prepare_seconds':prepared-start, 'advance_seconds':end-prepared,
                        'before':before, 'after':memory(), 'four_basic_buffers_bytes':32*w.runtime.dimension**3,
                        'tracing_enabled':False, 'scope':'one measured trajectory; process memory includes allocator/scratch; not an isolated allocation estimate'})
        del w
    result = {'version':d.__version__, 'measurements':results, 'performance_guarantee':False}
    Path(a.output).write_text(json.dumps(result,indent=2),encoding='utf-8'); print(json.dumps(result,indent=2))


if __name__ == '__main__':
    p=argparse.ArgumentParser(); p.add_argument('--output',required=True); main(p.parse_args())
