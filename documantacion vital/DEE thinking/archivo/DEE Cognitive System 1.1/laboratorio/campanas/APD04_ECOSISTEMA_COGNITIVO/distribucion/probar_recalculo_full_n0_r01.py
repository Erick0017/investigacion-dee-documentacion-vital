"""Archive-only tests and closure of the complementary calculator; no DEE import."""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path

p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args()
r=a.root.resolve();lab=r/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/distribucion'
out=r/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/FULL_RECALCULO_COMPLEMENTARIO_PREPARADO_N0_R01'
source=lab/'recalcular_full_apd04_sesiones_n0_r01.py'
ast.parse(source.read_text(encoding='utf8'))
spec=importlib.util.spec_from_file_location('pure_full_archive_recalculation',source)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
fixtures=m.selftest()
old=r/'sistema/estado/servicios_persistentes/APD04_CALIB_R02/resultados/ui_m_39cb78fdbfe4496881a39c66c5177921.json'
oldcalc=r/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/CALIBRACION_R02/RECALCULO_DESDE_RAW.json'
computed=[m.numeric(n) for _,n in m.walk(json.loads(old.read_bytes())) if isinstance(n,dict) and n.get('kind') in ('APD04_candidate_scalar_classification','APD04_candidate_native_balance')]
archived=json.loads(oldcalc.read_bytes())['cases']
assert len(computed)==len(archived)==6
for new,prior in zip(computed,archived):
    assert new['sign_RAW']==prior['choice_from_RAW'] and new['read_tick']==prior['read_tick']
    assert new['native_requested_distinct_IDs']==prior['requested']
test={'scope':'N0 PURE STDLIB ONLY; fixtures fabricated, old primary existing and NOT Full',
      'native_ticks':0,'fixture_results':fixtures,
      'historical_six_cases_agree':True,
      'historic_signs':[x['sign_RAW'] for x in computed],
      'historic_receipts':[x['native_requested_distinct_IDs'] for x in computed],
      'syntax_test':'AST parsed','sources':{str(x.relative_to(r)):m.sha(x) for x in (source,old,oldcalc)},
      'Full_results_exist_in_this_test':False,
      'post_run_usage':['python recalcular_full_apd04_sesiones_n0_r01.py --sesiones SESIONES_ORIGINALES.jsonl --criterio CRITERIO_NUMERICO_FULL_ANTES_DE_EJECUCION_R01.json --protocolo PROTOCOLO_FULL_APD04_CERRADO_R02.json --salida RECALCULO_COMPLEMENTARIO_FULL.json']}
dest=out/'PRUEBAS_Y_CIERRE_N0.json'
with dest.open('x',encoding='utf8',newline='\n') as f:json.dump(test,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
paths=[source,Path(__file__).resolve(),lab/'CRITERIO_NUMERICO_FULL_ANTES_DE_EJECUCION_R01.json',lab/'PROTOCOLO_FULL_APD04_CERRADO_R02.json',dest]
manifest={'schema':'APD04.Full.complementary_recalculation.prospective_manifest.N0.R01','native_ticks':0,
          'files':[{'path':str(x.relative_to(r)),'bytes':x.stat().st_size,'sha256':m.sha(x)} for x in paths]}
mf=out/'MANIFIESTO_CIERRE_N0.json'
with mf.open('x',encoding='utf8',newline='\n') as f:json.dump(manifest,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
print(json.dumps({'manifest':str(mf),'sha256':m.sha(mf),'calculation_sha256':m.sha(source),'tests':'synthetic+archived six, NO Full Native'},ensure_ascii=False))
