"""Read-only start of PC01. No native advance, probe or installation."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, ctypes, hashlib, json, os, platform, shutil, sys, time

p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
a.out.mkdir(parents=True,exist_ok=False)
sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import identity,physical,digest_file
now=datetime.now(timezone.utc)
# The first tool output was truncated across context compaction. Do not invent
# that QPC sample or restart the budget: adopt an EARLIER conservative ceiling.
ceiling=datetime.fromisoformat('2026-10-20T12:20:00+00:00')
mono=time.perf_counter();elapsed=(now-ceiling).total_seconds()
budget={'schema':'DCS1.1.PC01.budget.v1','reference_start_utc':ceiling.isoformat(),'reference_kind':'CONSERVATIVE_EARLIER_BOUND_NOT_RECOVERED_FIRST_COMMAND_TIMESTAMP','first_retained_clock_utc':'2026-10-20T12:32:44+00:00','first_command_record_gap':'Initial PowerShell command captured UTC, deadline and Stopwatch QPC but its output was truncated before persistence. Exact original sample unavailable; use earlier bound, never extend.','budget_seconds':21600,'deadline_utc':'2026-10-20T18:20:00+00:00','captured_utc':now.isoformat(),'monotonic_capture':mono,'elapsed_conservative_at_capture':elapsed,'monotonic_deadline':mono+21600-elapsed,'max_native_workers':2,'worker_memory_limit_bytes':4*1024**3,'closure_reserve_seconds':2700,'platform':platform.platform(),'logical_cpus':os.cpu_count(),'disk':dict(zip(('total','used','free'),shutil.disk_usage(a.system)))}
class Memory(ctypes.Structure):
    _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong),('total_phys',ctypes.c_ulonglong),('avail_phys',ctypes.c_ulonglong),('total_page',ctypes.c_ulonglong),('avail_page',ctypes.c_ulonglong),('total_virtual',ctypes.c_ulonglong),('avail_virtual',ctypes.c_ulonglong),('avail_extended',ctypes.c_ulonglong)]
m=Memory();m.length=ctypes.sizeof(m);ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m));budget['RAM_total_bytes']=m.total_phys;budget['RAM_available_bytes']=m.avail_phys
(a.out/'PRESUPUESTO.json').write_text(json.dumps(budget,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
s=Store(a.system);records=[]
for name in ('E1_SOCIAL_11','E1_ESPANOL_01','ES01_LATE_ACCESS29_passive'):
    rec,w=s.load(name);records.append({'life':name,'record':rec,'verified_passive_physical':physical(w.world,occupation=True),'snapshot_actual_sha256':digest_file(s.snapshot(rec))})
report={'identity':identity(a.system),'records':records,'active':json.loads((a.system/'estado/ACTIVO.json').read_bytes()),'no_evolution':True,'no_probe':True,'earliest_budget':budget,'manual_sha256':digest_file(a.system.parent/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_0.docx')}
(a.out/'ESTADO_INICIAL.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'identity':report['identity'],'states':[{k:r['verified_passive_physical'][k]for k in('tick','N','occupied')}|{'life':r['life']}for r in records],'deadline':budget['deadline_utc'],'RAM':m.total_phys,'free':budget['disk']['free']}))
