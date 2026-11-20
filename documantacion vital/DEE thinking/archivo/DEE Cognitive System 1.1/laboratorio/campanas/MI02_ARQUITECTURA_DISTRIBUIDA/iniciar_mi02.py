"""Start MI02 once, record the fixed budget and inspect exact existing parents.
No restoration, no native ticks, no inventory rebuild.
"""
import ctypes,hashlib,importlib.util,json,platform,shutil,sys,time
from pathlib import Path
from datetime import datetime,timezone
L=Path(__file__).resolve().parent;R=L.parents[2];S=R/'sistema';E=R/'evidencia/campanas/MI02_ARQUITECTURA_DISTRIBUIDA';E.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(S))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8')
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
bp=L/'PRESUPUESTO.json';now=datetime.now(timezone.utc);start=datetime.fromisoformat('2026-10-22T14:58:00+00:00');end=datetime.fromisoformat('2026-10-22T22:58:00+00:00')
if not bp.exists():
    b={'campaign':'MI02_ARQUITECTURA_DISTRIBUIDA','start_bound_utc':start.isoformat(),'deadline_utc':end.isoformat(),'maximum_seconds':28800,'registered_utc':now.isoformat(),'monotonic_registered':time.monotonic(),'monotonic_deadline':time.monotonic()+(end-now).total_seconds(),'construction_latest_utc':'2026-10-22T20:18:00+00:00','final_third_reserved_seconds':9600,'native_writers_max':1,'process_ram_limit_bytes':4294967296,'campaign_storage_limit_bytes':12000000000,'D_free_bytes':shutil.disk_usage(R).free,'note':'New explicit MI02 eight-hour cut. MI01 remains closed; no restart of either budget.'};save(bp,b)
else:raise FileExistsError('MI02 already started; inspect existing cut, do not restart')
from app.native_tools import identity
spec=importlib.util.spec_from_file_location('readonly_snapshot',S/'capacidades/observador_causal_retrospectivo_01.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
active=read(S/'estado/ACTIVO.json');main=read(S/'estado/vidas/E1_MI01_MAIN/VIDA.json');cont=read(R/'CONTINUIDAD_MENTE_DEE_INTEGRAL_MI01.json')
candidate=S/next(v['snapshot']for v in cont['historical_functional_cuts']if v['tick']==24752)
assert sha(candidate)=='23114e8445f2b651ce9dfd53011b9749b357e1fa9a4191e87982b0fafec081a4'
x=m.Snapshot(candidate);assert x.tick==24752 and not x.pending
result={'native_ticks':0,'identity':identity(),'active_protected':active,'MI01_adverse_current':main,'A_parent_selected_before_evaluation':{'life':'E1_MI01_MAIN','snapshot':str(candidate.relative_to(S)),'sha256':sha(candidate),'tick':x.tick,'pending':x.pending,'summary':x.summary(),'reason':'Own positive145 reuse and earlier code use, before MI01 frozen preparation. Does not claim recurrent contact/order composer availability.'},'B_intent':'New T0 distributed organization in one Runtime; no memory transplant; must acquire its own histories. Domain chosen after bounded architecture calibration.','budget':b};save(E/'INICIO_Y_PADRES.json',result)
print(json.dumps({'budget':b,'identity':result['identity'],'A_parent':result['A_parent_selected_before_evaluation'],'active':active['life_id'],'MI01_current_tick':main['physical']['tick']},ensure_ascii=False,indent=2))
