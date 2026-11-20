"""Fija recursos observados del corte; no restaura ni avanza universos."""
import ctypes,json,shutil,time,sys
from pathlib import Path
from datetime import datetime,timezone
class Memory(ctypes.Structure):
    _fields_=[('length',ctypes.c_ulong),('load_percent',ctypes.c_ulong),('total_physical',ctypes.c_ulonglong),('available_physical',ctypes.c_ulonglong),('total_pagefile',ctypes.c_ulonglong),('available_pagefile',ctypes.c_ulonglong),('total_virtual',ctypes.c_ulonglong),('available_virtual',ctypes.c_ulonglong),('available_extended_virtual',ctypes.c_ulonglong)]
here=Path(__file__).resolve().parent
p=here/'RECURSOS_INICIALES.json'
if p.exists():raise FileExistsError(p)
m=Memory();m.length=ctypes.sizeof(m);ok=bool(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)));d=shutil.disk_usage(here)
r={'observed_utc':datetime.now(timezone.utc).isoformat(),'monotonic':time.monotonic(),'disk_total_bytes':d.total,'disk_free_bytes':d.free,'memory_api_ok':ok,'memory':{k:getattr(m,k)for k,t in m._fields_},'native_python':sys.executable,'resource_limit':'One writer per Runtime, OMP/BLAS1; sequential simulations; no new heavy dependencies; preserve last quarter for closure','native_ticks':0}
p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(r))
