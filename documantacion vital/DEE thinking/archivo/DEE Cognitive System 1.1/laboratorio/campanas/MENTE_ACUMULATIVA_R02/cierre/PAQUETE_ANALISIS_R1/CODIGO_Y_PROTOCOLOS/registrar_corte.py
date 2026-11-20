"""Registro único del corte R02; no importa ni avanza DEE."""
import datetime, hashlib, json, os, time
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OUT=ROOT/'evidencia/campanas/MENTE_ACUMULATIVA_R02'
UTC=datetime.timezone.utc
START=datetime.datetime.fromisoformat('2026-10-25T05:42:02+00:00')
DEADLINE=START+datetime.timedelta(hours=8)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    path=HERE/'PRESUPUESTO.json'
    if path.exists():raise FileExistsError('El presupuesto ya está fijado; no reiniciarlo')
    now=datetime.datetime.now(UTC); mono=time.monotonic()
    ids=['MA_MAIN_R9','MA_U0_ACUMULATIVO_AUX','EO02_MAIN','EO02_SENSORIAL_R10_T0','E1_SOCIAL_11']
    protected={}
    for name in ids:
        rec=ROOT/'sistema/estado/vidas'/name/'VIDA.json'
        if not rec.is_file():raise FileNotFoundError(rec)
        x=json.loads(rec.read_text(encoding='utf-8-sig'))
        snap=ROOT/'sistema'/x['snapshot']
        protected[name]={'record':str(rec),'record_sha256':sha(rec),'snapshot':str(snap),'sha256':sha(snap),'tick':x.get('tick',x.get('physical',{}).get('tick'))}
    OUT.mkdir(parents=True,exist_ok=True)
    data={'campaign':'MENTE_ACUMULATIVA_R02','start_utc':START.isoformat(),'limit_utc':DEADLINE.isoformat(),'registered_utc':now.isoformat(),'registered_monotonic':mono,'deadline_monotonic':mono+(DEADLINE-now).total_seconds(),'maximum_seconds':28800,'monotonic_budget_fixed_once':True,'previous_MA_campaign_closed':True,'protected':protected,'available_memory_bytes':None,'storage_free_bytes':__import__('shutil').disk_usage(ROOT).free,'native_workers_max':2,'OMP_NUM_THREADS':1,'one_writer_per_Runtime':True,'no_original_life_ticks':True}
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(data,ensure_ascii=False))
if __name__=='__main__':main()
