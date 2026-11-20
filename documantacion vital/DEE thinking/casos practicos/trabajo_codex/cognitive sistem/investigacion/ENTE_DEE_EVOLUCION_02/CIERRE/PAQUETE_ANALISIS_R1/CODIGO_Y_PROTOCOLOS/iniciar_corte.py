"""Register one finite EO02 budget and inspect only the necessary parent."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,time,os,ctypes,sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
def sha(p):
    h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def main():
    target=HERE/'PRESUPUESTO.json'
    if target.exists():raise FileExistsError('Existing budget is never restarted')
    start=datetime.fromisoformat('2026-10-24T21:20:15+00:00');now=datetime.now(timezone.utc)
    anchor=time.monotonic()-(now-start).total_seconds()
    budget={'campaign':'ENTE_DEE_EVOLUCION_02','start_utc':start.isoformat(),'limit_utc':(start+timedelta(hours=8)).isoformat(),'start_monotonic':anchor,'deadline_monotonic':anchor+28800,'release_quarter_from_monotonic':anchor+21600,'maximum_seconds':28800,'previous_EO01_cut':'Closed2026-10-24T18:33:04Z; this explicit new task starts one new finite construction, not a continuation or extension of EO01 research.','new_budget_not_restarted':True,'physics_threads':1,'writers_per_runtime':1,'storage_soft_limit_bytes':12000000000,'resident_memory_soft_limit_bytes':3500000000}
    target.write_text(json.dumps(budget,indent=2)+'\n',encoding='utf8')
    ev=ROOT/'evidencia/campanas/ENTE_DEE_EVOLUCION_02';ev.mkdir(parents=True,exist_ok=True)
    protected={}
    for name in('EO01_MAIN','CF01_MAIN','E1_SOCIAL_11'):
        record=ROOT/'sistema/estado/vidas'/name/'VIDA.json';d=json.loads(record.read_bytes())
        protected[name]={'record':str(record),'record_sha256':sha(record),'record_content':d}
    receipt={'registered_utc':now.isoformat(),'elapsed_seconds':(now-start).total_seconds(),'protected':protected,'active_sha256':sha(ROOT/'sistema/estado/ACTIVO.json'),'no_native_ticks':True,'disk_free_bytes':__import__('shutil').disk_usage(ROOT).free,'host_cpu_count':os.cpu_count(),'python':sys.version}
    (ev/'00_ESTADO_PROTEGIDO_INICIAL.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'budget':budget,'life_keys':[list(v['record_content'])for v in protected.values()],'disk_free_bytes':receipt['disk_free_bytes']},ensure_ascii=False))
if __name__=='__main__':main()
