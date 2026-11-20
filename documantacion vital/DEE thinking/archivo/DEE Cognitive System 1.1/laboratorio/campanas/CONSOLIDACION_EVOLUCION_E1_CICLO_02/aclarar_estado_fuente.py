"""Contraste causal de dos estados archivados, sin Runtime ni nuevos ticks."""
import sys,json,importlib.util
from pathlib import Path
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];SYSTEM=ROOT/'sistema';EV=ROOT/'evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02'
spec=importlib.util.spec_from_file_location('saved_bytes',SYSTEM/'capacidades/observador_causal_retrospectivo_01.py');saved=importlib.util.module_from_spec(spec);spec.loader.exec_module(saved)
old=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01';files=['MAIN_OWN_ACQUISITION_37.json','MAIN_COMMITTED_BODY_38.json'];states=[]
for file in files:
    h=json.loads((old/file).read_text(encoding='utf8'))['INSTRUMENTO']['snapshot_sha256']
    p=next(p for p in(SYSTEM/'estado/checkpoints').glob('E1_INTEGRADO_MAIN.T3312.*')if saved.sha(p.read_bytes())==h)
    states.append(saved.Snapshot(p))
a,b=states
out={'native_ticks':0,'worlds_instantiated':0,'actual_C2_social_source':a.summary(),'original_IC01_armed_body_source':b.summary(),
     'RAW_equal':a.raw==b.raw,'clocks_equal':a.clocks==b.clocks,'pending_equal':a.pending==b.pending,
     'pending_counts':[len(a.pending),len(b.pending)],'channel_counts':[len(a.channels),len(b.channels)],
     'interpretation':'C2 social/GUARD/DIV controls share the real learned pre-arm snapshot0658 atT3312, without the newly armed finite body opportunities of snapshotfa46. They are valid matched NEW isolated social contrasts, not exact repetitions of original record-only94. Current MAIN integration/reserves use their own complete parent state and are unaffected by this distinction.',
     'correction':'Earlier shorthand calling0658 the committed-body snapshot was inaccurate. Preserve original files and exact initial/future inputs rather than silently relabeling them.'}
(EV/'ACLARACION_CAUSAL_ESTADO_FUENTE.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:out[k]for k in('RAW_equal','clocks_equal','pending_equal','pending_counts','channel_counts','interpretation')},ensure_ascii=False))
