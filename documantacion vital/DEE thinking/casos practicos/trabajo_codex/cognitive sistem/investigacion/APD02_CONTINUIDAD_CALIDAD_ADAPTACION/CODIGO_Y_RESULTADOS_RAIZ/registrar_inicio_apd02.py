"""APD02 one-time budget and read-only parent pin. No DEE ticks."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import struct
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
EV = ROOT / 'evidencia/campanas/APD02_CONTINUIDAD_CALIDAD_ADAPTACION'
START = dt.datetime.fromisoformat('2026-10-26T03:17:43+00:00')
LIMIT = START + dt.timedelta(hours=8)

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576), b''): h.update(b)
    return h.hexdigest()

def main():
    EV.mkdir(parents=True, exist_ok=True)
    dest=EV/'PRESUPUESTO_E_IDENTIDAD_INICIAL.json'
    if dest.exists(): raise SystemExit('Existing immutable start; refusing to reset budget.')
    now=dt.datetime.now(dt.timezone.utc)
    mono=time.monotonic()
    pair=ROOT/'evidencia/campanas/ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01/servicio/SERVICIO_60MIN_APD_R04/PAQUETE_FINAL_POSTSTOP/EXPORTACION_SERVICIO.json'
    record=ROOT/'sistema/estado/vidas/ASISTENTE_MAIN/VIDA.json'
    r=json.loads(record.read_text(encoding='utf-8-sig'))
    snap=ROOT/'sistema'/r['snapshot']
    import dee_thinking
    binary=Path(dee_thinking.__file__)
    doc={
        'schema':'APD02.budget_and_parent.v1','campaign':'APD02_CONTINUIDAD_CALIDAD_ADAPTACION',
        'start_utc':START.isoformat(),'deadline_utc':LIMIT.isoformat(),'total_seconds':28800,
        'capture_utc':now.isoformat(),'capture_monotonic':mono,
        'monotonic_start_estimated_from_first_command':mono-(now-START).total_seconds(),
        'final_quarter_starts_utc':(START+dt.timedelta(hours=6)).isoformat(),
        'elapsed_seconds_at_capture':(now-START).total_seconds(),
        'resource_policy':{'native_main_owners':1,'native_aux_owners_max':1,'omp_threads_each':1,'job_memory_bytes_each':536870912,'reserve_disk_bytes_min':10737418240},
        'disk_free_bytes':shutil.disk_usage(ROOT).free,
        'python':{'executable':sys.executable,'version':sys.version,'bits':8*struct.calcsize('P'),'platform':platform.platform()},
        'engine':{'path':str(binary),'sha256':sha(binary),'version':getattr(dee_thinking,'__version__',None)},
        'protected_active':json.loads((ROOT/'sistema/estado/ACTIVO.json').read_text(encoding='utf-8-sig')),
        'parent':{'life_id':r['life_id'],'physical':r['physical'],'record':str(record),'record_sha256':sha(record),'snapshot':str(snap),'snapshot_sha256':sha(snap),'pair_manifest':str(pair),'pair_manifest_sha256':sha(pair)},
        'zero_new_ticks':True,
    }
    dest.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(doc,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
