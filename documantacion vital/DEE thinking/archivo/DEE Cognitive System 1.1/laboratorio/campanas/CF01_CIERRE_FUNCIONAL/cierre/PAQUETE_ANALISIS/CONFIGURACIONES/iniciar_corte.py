"""Anclar un único presupuesto CF01 y registrar selección antes de evaluar."""
from pathlib import Path
from datetime import datetime, timezone
import ctypes, json, shutil, time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
START=datetime.fromisoformat('2026-10-22T23:47:38+00:00')

def main():
    budget=HERE/'PRESUPUESTO.json'
    if budget.exists():
        print(budget.read_text(encoding='utf8'));return
    stamp=time.monotonic();elapsed=(datetime.now(timezone.utc)-START).total_seconds()
    class Memory(ctypes.Structure):
        _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong),('physical_total',ctypes.c_ulonglong),('physical_available',ctypes.c_ulonglong),('page_total',ctypes.c_ulonglong),('page_available',ctypes.c_ulonglong),('virtual_total',ctypes.c_ulonglong),('virtual_available',ctypes.c_ulonglong),('extended_available',ctypes.c_ulonglong)]
    mem=Memory();mem.length=ctypes.sizeof(mem);ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
    value={'campaign':'CF01_CIERRE_FUNCIONAL','start_utc':START.isoformat(),'maximum_seconds':28800,
           'deadline_utc':'2026-10-23T07:47:38+00:00','delivery_reserved_from_utc':'2026-10-23T05:47:38+00:00',
           'monotonic_start':stamp-elapsed,'monotonic_deadline':stamp-elapsed+28800,
           'anchor':'First tool UTC mapped once to Windows monotonic clock; no budget restart',
           'memory_available_bytes_at_start':int(mem.physical_available),'physical_memory_bytes':int(mem.physical_total),
           'disk_free_bytes_at_start':shutil.disk_usage(ROOT).free,'owned_process_memory_limit_bytes':min(8*1024**3,int(mem.physical_available)//2),
           'storage_budget_bytes':20*1024**3,'one_writer_per_world':True,'maximum_complete_architecture_revisions':2,
           'selected_parent_before_new_results':{'life':'MI02_SOCIAL_REUSABLE_240','tick':15329,'profile':'fisica_directa','N':26,
             'snapshot':'estado/checkpoints/MI02_SOCIAL_REUSABLE_240.T15329.79e7779809ff.deetsnap.gz',
             'sha256':'dd008c7b0e73c464a75dd0fc55ec05862f8440b8ff5d106c2b77f0b4601c9e8a',
             'reason':'Earlier closed reusable native social reader with9/12late useful responses, before external continuation with2/4partial use. Choice uses only MI02 records, not CF01 outcomes. A new fork, not E1 inherited biography.'},
           'main_life_planned':'CF01_MAIN','protected_default':'E1_SOCIAL_11','new_research_not_a_historical_reaudit':True}
    budget.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(value,ensure_ascii=False))

if __name__=='__main__':main()
