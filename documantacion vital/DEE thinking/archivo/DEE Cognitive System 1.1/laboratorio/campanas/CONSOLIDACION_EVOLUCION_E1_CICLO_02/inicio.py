"""Corte único y selección previa; no avanza ningún mundo DEE."""
from pathlib import Path
import ctypes, datetime as dt, hashlib, json, platform, sys, time

LAB = Path(__file__).resolve().parent
ROOT = LAB.parents[2]
SYS = ROOT / 'sistema'
EV = ROOT / 'evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02'
EV.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(SYS))
from app.lives import Store
from app.native_tools import identity

def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

budget = LAB / 'PRESUPUESTO.json'
if not budget.exists():
    now = dt.datetime.now(dt.timezone.utc)
    # Primer resultado horario de esta vuelta no quedó recuperable tras truncación.
    # Se descuenta conservadoramente todo el intervalo desde 21:40 UTC, sin ampliarlo.
    conservative_start = dt.datetime(2026,10,21,21,40,tzinfo=dt.timezone.utc)
    allowance = max(0, 21600 - (now-conservative_start).total_seconds())
    class MEM(ctypes.Structure):
        _fields_ = [('length',ctypes.c_ulong),('load',ctypes.c_ulong),
                    ('total',ctypes.c_ulonglong),('available',ctypes.c_ulonglong),
                    ('page_total',ctypes.c_ulonglong),('page_avail',ctypes.c_ulonglong),
                    ('virt_total',ctypes.c_ulonglong),('virt_avail',ctypes.c_ulonglong),
                    ('extended',ctypes.c_ulonglong)]
    mem=MEM(); mem.length=ctypes.sizeof(mem)
    ok=ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
    save(budget, {'campaign':'CONSOLIDACION_EVOLUCION_E1_CICLO_02',
        'start_bound_utc':conservative_start.isoformat(), 'registered_utc':now.isoformat(),
        'monotonic_registered':time.monotonic(), 'monotonic_deadline':time.monotonic()+allowance,
        'deadline_utc':(conservative_start+dt.timedelta(seconds=21600)).isoformat(),
        'maximum_seconds':21600, 'elapsed_before_registration_deducted':(now-conservative_start).total_seconds(),
        'reserved_closure_seconds':2400, 'native_writers_max':1,
        'ram_available_bytes':mem.available if ok else None,'ram_total_bytes':mem.total if ok else None,
        'own_process_ram_limit_bytes':6_000_000_000, 'campaign_storage_limit_bytes':12_000_000_000,
        'storage_drive':'D:', 'C_drive_policy':'No large artifacts or installs; D local temp only',
        'note':'Cutoff fixed conservatively after first clock output truncation. Never restart this budget.'})

store=Store()
ids=['E1_SOCIAL_11','E1_INTEGRADO_MAIN','E1_INTEGRADO_CONTINUABLE_01','E1_INTEGRADO_RECUPERACION_01']
out={'identity':identity(), 'python':sys.executable,'platform':platform.platform(),
     'records':{x:store.record(x) for x in ids}, 'ticks_advanced':0,
     'parent_selected_before_new_evaluation':'E1_INTEGRADO_RECUPERACION_01',
     'reason':'Continuación exacta ya validada con comparación adquirida, soporte social recuperado por acceso genérico preparado y puente ambiental persistente. No seleccionada por resultados de CICLO02.',
     'protected_default':'E1_SOCIAL_11','main_id':'E1_CICLO02_MAIN'}
save(EV/'INICIO_Y_PADRE.json',out)
print(json.dumps({'budget':json.loads(budget.read_text(encoding='utf-8')),
    'lives':{x:{k:out['records'][x].get(k) for k in ['life_id','tick','profile','snapshot','snapshot_sha256','parent','physical']} for x in ids},
    'identity':out['identity']}, ensure_ascii=False,indent=2))
