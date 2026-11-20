"""Register continuation of the existing ENTE02 time bound, never reset it."""
from pathlib import Path
import hashlib,json,time,shutil
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];EV=ROOT/'evidencia/campanas/MENTE_ACUMULATIVA'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    dest=HERE/'PRESUPUESTO.json'
    if dest.exists():raise FileExistsError('Existing cutoff is preserved')
    old=json.loads((ROOT/'laboratorio/campanas/ENTE_DEE_EVOLUCION_02/PRESUPUESTO.json').read_bytes())
    now=time.monotonic()
    if now>=old['deadline_monotonic']:raise TimeoutError('Original fixed deadline already exhausted')
    EV.mkdir(parents=True,exist_ok=True)
    b={**old,'campaign':'MENTE_ACUMULATIVA','task_started_utc':datetime.now(timezone.utc).isoformat(),'task_started_monotonic':now,'deadline_reused_from_ENTE02':True,'not_a_fresh_eight_hour_budget':True,'release_target_utc':'2026-10-25T04:35:00Z','remaining_seconds_at_registration':old['deadline_monotonic']-now}
    dest.write_text(json.dumps(b,indent=2)+'\n',encoding='utf8')
    records={}
    for name in ['EO02_MAIN','EO02_SENSORIAL_R10_T0','EO01_MAIN','E1_SOCIAL_11']:
        p=ROOT/'sistema/estado/vidas'/name/'VIDA.json';rec=json.loads(p.read_bytes())
        records[name]={'record_sha256':sha(p),'snapshot':rec['snapshot'],'snapshot_sha256':rec['snapshot_sha256'],'physical':rec['physical'],'parent':rec.get('parent')}
    (EV/'00_PADRES_Y_PLAZO.json').write_text(json.dumps({'records':records,'active':json.loads((ROOT/'sistema/estado/ACTIVO.json').read_bytes()),'active_sha256':sha(ROOT/'sistema/estado/ACTIVO.json'),'registered_utc':b['task_started_utc'],'disk_free_bytes':shutil.disk_usage(ROOT).free,'no_ticks':True},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'remaining_seconds':b['remaining_seconds_at_registration'],'deadline':b['limit_utc'],'parents':{i:v['physical']['tick']for i,v in records.items()}}))
if __name__=='__main__':main()
