"""One-time APD01 budget and exact parent receipt, with no DEE evolution."""
import ctypes,hashlib,json,shutil,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
LAB=Path(__file__).resolve().parent
EV=ROOT/'evidencia/campanas/ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=LAB/'PRESUPUESTO.json'
    if out.exists():raise FileExistsError('Budget cannot be restarted')
    EV.mkdir(parents=True,exist_ok=True)
    now=datetime.now(timezone.utc);mono=time.perf_counter();start=datetime.fromisoformat('2026-10-25T17:48:11+00:00');end=datetime.fromisoformat('2026-10-26T01:48:11+00:00')
    files={
      'parent_VIDA':ROOT/'sistema/estado/vidas/MU_MAIN_FASE_R3/VIDA.json',
      'parent_snapshot':ROOT/'sistema/estado/checkpoints/MU_MAIN_FASE_R3.T104472.cb632d5d0e08.deetsnap.gz',
      'parent_queue':ROOT/'sistema/estado/servicios_persistentes/MU_MAIN_FASE_R3/cola.sqlite3',
      'ACTIVO':ROOT/'sistema/estado/ACTIVO.json',
      'prior_continuity':ROOT/'CONTINUIDAD_MENTE_UNIFICADA_Y_FI01.json'}
    rows={k:{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}for k,p in files.items()}
    assert rows['parent_snapshot']['sha256']=='f389f64325390daa31b8f684ac14e0a0c4c75a65e4713af4c861effd9e38a97a'
    assert rows['parent_VIDA']['sha256']=='446a04513908f408b07f88bf9f5b74703025b4a79db713888f36ef3d7c34985e'
    assert rows['parent_queue']['sha256']=='3cc08ae2026a1d9c495ec292a70da1b7e4cded160ecd825abadc0a715dac7a80'
    result={'schema':'DEE.APD01.one_budget.v1','campaign':'ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01','start_utc':start.isoformat(),'deadline_utc':end.isoformat(),'max_seconds':28800,'initial_clock_sample_utc':now.isoformat(),'initial_monotonic_sample':mono,'elapsed_before_monotonic_sample_seconds':(now-start).total_seconds(),'monotonic_deadline':mono+(end-now).total_seconds(),'sampling_limit':'The first command recorded UTC. This first monotonic anchor subtracts all already elapsed startup time; it does not reset the eight-hour deadline.','native_workers_max':2,'OMP_NUM_THREADS':1,'one_writer_per_runtime':True,'native_worker_memory_budget_bytes':536870912,'minimum_closure_reserve_seconds':7200,'disk_free_bytes':shutil.disk_usage(ROOT).free,'parent_and_protected':rows,'new_native_ticks':0}
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
