"""One-time resource/budget record; never restarts an existing campaign budget."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ctypes,json,platform,shutil,time,os
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);a=p.parse_args();base=a.system/'evidencia/campanas/ACCESO_ADAPTATIVO_01';base.mkdir(parents=True,exist_ok=True);dest=base/'PRESUPUESTO.json'
if dest.exists():
    print(dest.read_text(encoding='utf8'));raise SystemExit(0)
class Memory(ctypes.Structure):
    _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong),('total',ctypes.c_ulonglong),('available',ctypes.c_ulonglong),('page_total',ctypes.c_ulonglong),('page_available',ctypes.c_ulonglong),('virtual_total',ctypes.c_ulonglong),('virtual_available',ctypes.c_ulonglong),('extended',ctypes.c_ulonglong)]
m=Memory();m.length=ctypes.sizeof(m);ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m));disk=shutil.disk_usage(a.system);clock=time.perf_counter()
record={'schema':'DCS1.1.AA01.budget.v1','campaign':'ACCESO_ADAPTATIVO_01','start_utc':'2026-10-20T22:11:53.0840393Z','first_command_QPC':7132579898914,'QPC_frequency':10000000,'start_monotonic':713257.9898914,'budget_seconds':21600,'monotonic_deadline':734857.9898914,'deadline_utc':'2026-10-21T04:11:53.0840393Z','recorded_utc':datetime.now(timezone.utc).isoformat(),'recorded_monotonic':clock,'elapsed_seconds':clock-713257.9898914,'max_native_workers':2,'worker_memory_limit_bytes':4294967296,'closure_reserve_seconds':2400,'logical_cpus':os.cpu_count(),'platform':platform.platform(),'RAM_total_bytes':m.total,'RAM_available_bytes':m.available,'disk':dict(zip(('total','used','free'),disk)),'no_budget_restart':True}
dest.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(record,ensure_ascii=False))
