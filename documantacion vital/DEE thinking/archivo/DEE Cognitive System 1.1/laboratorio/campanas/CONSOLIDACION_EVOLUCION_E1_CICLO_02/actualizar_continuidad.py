"""Ficha enfocada a estados actuales; cero ticks, sin nueva auditoría histórica."""
import sys,json,datetime,importlib.util
from pathlib import Path
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];SYSTEM=ROOT/'sistema';EV=ROOT/'evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02'
sys.path.insert(0,str(SYSTEM))
from app.lives import Store
from app.native_tools import atomic_json,digest_file
spec=importlib.util.spec_from_file_location('snapshot_only',SYSTEM/'capacidades/observador_causal_retrospectivo_01.py');snap=importlib.util.module_from_spec(spec);spec.loader.exec_module(snap)
s=Store();names=['E1_SOCIAL_11','E1_CICLO02_MAIN','E1_INTEGRADO_MAIN','E1_INTEGRADO_CONTINUABLE_01','E1_INTEGRADO_RECUPERACION_01','C02_PRE_110_PLUS_RESOURCE','C02_PRE_113_MINUS_RESOURCE','C02_DIV_080_MINUS','C02_DIV_081_PLUS']
rows=[]
for name in names:
    if not s.life_dir(name).exists():continue
    r=s.record(name);rows.append({k:r.get(k)for k in('life_id','world_id','profile','branch','parent','snapshot','snapshot_sha256','physical')})
main=next(x for x in rows if x['life_id']=='E1_CICLO02_MAIN');x=snap.Snapshot(SYSTEM/main['snapshot'])
obj={'campaign':'CONSOLIDACION_EVOLUCION_E1_CICLO_02','updated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
     'state':'IN_PROGRESS_UNLESS_FINAL_SEAL_EXISTS','protected_default':'E1_SOCIAL_11','main':main,'pending_inputs':x.pending,
     'snapshot_checksum_valid':x.checksum_valid,'lives':rows,
     'current_main_verified_scope':'19/19 useful gate opportunities throughT20927, actual earlier/new social content, two old comparisons and external actions. P1 fallback is not P2 initiation; inspect latest primary operations before extrapolating.',
     'commands':['integrado-estado --vida E1_CICLO02_MAIN','integrado-externo --vida E1_CICLO02_MAIN --pasos 1','integrado-experiencia --vida E1_CICLO02_MAIN --tipo puerta --parametros {forces:[77,100],wear:5}'],
     'commands_note':'Use quoted valid JSON as in the installed guide; command descriptions here are not automatically executed.',
     'main_next':'Continue actual gate state and Pendulum state. Do not silently prepare another baseline or resupply prepositioned resources.',
     'analysis_package_is_not_a_complete_backup':True}
atomic_json(ROOT/'CONTINUIDAD_CICLO02.json',obj)
atomic_json(EV/'CONTINUIDAD_TRABAJO_ACTUAL.json',obj)
print(json.dumps({'main_tick':main['physical']['tick'],'snapshot':main['snapshot'],'pending_count':len(x.pending),'protected':rows[0]['snapshot_sha256']},ensure_ascii=False))
