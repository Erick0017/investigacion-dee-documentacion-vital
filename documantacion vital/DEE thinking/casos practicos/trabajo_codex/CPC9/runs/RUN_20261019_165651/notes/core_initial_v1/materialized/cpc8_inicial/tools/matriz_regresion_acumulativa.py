"""Read-only documentary overlay; never imports DEE or executes a trajectory."""
from pathlib import Path
from datetime import datetime,timezone
import ast,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'genealogia/MATRIZ_CAPACIDADES_ACUMULADAS.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def ref(relative,role,scope):
 p=ROOT/relative
 if not p.is_file():raise FileNotFoundError(p)
 return {'path':relative,'sha256':sha(p),'role':role,'scope':scope}
TEST_MAP={
0:[1,3,49],1:[8,15,59],2:[60,67,78],3:[68],4:[61,70],5:[66],6:[2,57,78],7:[17,24,25],
8:[18],9:[6,16,18],10:[11],11:[8,15],12:[61,66,73],13:[33,34],14:[62],15:[19,25,59],16:[19,22,25],17:[9,17,62],
18:[22,38],19:[15,19,72,74],20:[2,25,57,73],21:[36],22:[21],23:[21],24:[11,45],25:[1,3,49],26:[63],27:[64,67],
28:[19,59,62,63,66],29:[57,64],30:list(range(82)),31:[22],32:[21,22],33:[22,38,39,40],34:[29,30,31,32],35:[15,22],36:[71],
37:list(range(82)),38:[],39:[],40:[47],41:[],42:[],43:[],44:[],45:[48,49,50,51,52,53,54,55,56],46:[]}
ADAPT={0:'Two-event order used in new N131 geometry, not replay of the original N47 body.',
 1:'Reutilización de asociación móvil en otra preparación; no se atribuye a E1 la calibración afín completa de CP01.',
 4:'A native source product reaches a prepared receiver in N131; not the original transfer constructor.',
 6:'External causal lab forks/cuts reused; no introspection attributed to participant.',
 7:'Persistent session and explicit probes reused in a new participant; MOD31 external habitat not integrated.',
 12:'New N131 social channel and acquired receiver; R1/R2/R3 geometries not silently equated.',
 13:'Prepared and experience-dependent pulse protocols evaluated separately; no learned regulation policy claimed.',
 15:'Native repertoire source adapted/relocated into N131 E1, opaque forms and two direction classes.',
 16:'Old/new acquired relations queried in the same E1 lineage and retained through declared panels.',
 17:'Finite temporal order/composition reused; no reproduction of every CPC5 population architecture.',
 18:'CPC6/U0 functions rebuilt into Research N131, not fusion or restoration of the N67 individual.',
 19:'Separate named content/access functions reused; full CPC6 F1/F2 protocol not reproduced.',
 20:'Diagnostic separation of memory/access/reader reused as external instrumentation.',
 23:'Directional revision used; not exact replay of CORE07 additive reprogramming.',
 25:'Relative-memory mechanism exercised by preserved CP01 N47 body, not ING02 long retention replay.',
 30:'Inherited4.0 interfaces exercised through official4.5, not a fresh4.0 install.',
 31:'CPC7 source mechanisms rebuilt in E1 N131; continuity scoped to that newly prepared MAIN.',
 32:'M1 revised L01 within E1; late M2 tested separately outside finite helper, not integrated into E1.',
 33:'Prepared comparison/opportunity physically conditions request/use; no general learned when/whom policy.',
 35:'Directional content and post-name use integrated with explicit routes/readers; not arbitrary grammar.',
 37:'Official4.5 runtime installed and82 Python contracts executed; no new compiler/product change.',
 40:'CORE17 carrier-assisted redundant repair ported to4.5; diagnostic clocks and channel clock contracts distinguished.'}
INTEGRATED={0,4,7,12,15,16,18,19,31,32,33,35}
EVIDENCE={
 'cp01':('resultados/genealogia_cp01_cp02_r1/CP01.json','8 original-source cases:4order,4mobile; not all eight application fields'),
 'cp02':('resultados/genealogia_cp01_cp02_r1/CP02.json','11 forecast cases, including absent/unpaired/equalized and changed-regularity misses'),
 'pending':('resultados/genealogia_cp01_cp02_r1/CP01_CONTINUATION.json','Pending input T8 toT11; physical continuation exact; external habitat remains external'),
 'sem':('resultados/sem01_reproduccion/SUMMARY.json','5 actual SEM01 cohorts through129, including controls and reserve'),
 'semparity':('resultados/sem01_reproduccion/HISTORICAL_PARITY.json','One A_future_UV reference: initial/final full RAW/clocks physical equality; metadata not equated'),
 'core17':('resultados/core17_repair/CLOSURE.json','12 local repair comparisons and continuation; not R0_FACTOR_52 and not integrated E1'),
 'coreclock':('resultados/core17_repair/CLOCK_CONTRACT_CORRECTION.json','Preserved clock-label incident; no retroactive missing per-input clock reconstruction'),
 'cmp':('comparadores/SUMMARY.json','Two standalone N131 genealogies plus matched conventional comparators; not E1 or65NSM'),
 'e1':('resultados/integracion/E1_P11_AB/MEASUREMENTS.json','New same-world N131 order/current-information/action/name plus acquired lower repertoire'),
 'e1cut':('resultados/integracion/E1_D11_CUT/MEASUREMENTS.json','Explicit diagnostic cut; separate cohort, not returned to MAIN'),
 'e1sham':('resultados/integracion/E1_D12_SHAM/MEASUREMENTS.json','Paired diagnostic sham'),
 'e1reserve':('resultados/integracion/E1_R211_BA/MEASUREMENTS.json','Reserved opposite order/content realization'),
 'm1':('resultados/integracion/UP_P11_M1/MEASUREMENTS.json','L01 revision while other64 lower relations checked in same world; prepared protocol'),
 'm1control':('resultados/integracion/UP_C12_NO_UPDATE/MEASUREMENTS.json','No-update control'),
 'm1reserve':('resultados/integracion/UP_R811_OPPOSITE/MEASUREMENTS.json','Opposite current consequence reserved'),
 'l17':('resultados/semantica/SOC_I11_L17_REAL/MEASUREMENTS.json','Native social response physically reaches and trains L17 in Research N131'),
 'l17cut':('resultados/semantica/SOC_I15_L17_MESSAGE_CUT/MEASUREMENTS.json','Selective message cut'),
 'l17sham':('resultados/semantica/SOC_I16_L17_MESSAGE_SHAM/MEASUREMENTS.json','Message sham'),
 'l17reserve':('resultados/semantica/SOC_I14_L17_RESERVED_NEGATIVE/MEASUREMENTS.json','Reserved negative source/receiver combination'),
 'l17restore':('resultados/semantica/SOC_I17_RESTORED_NEW_QUERY/MEASUREMENTS.json','Same saved physical/operational lineage, fresh subsequent query'),
 'l17revision':('resultados/semantica/SOC_I21_SOCIAL_THEN_L01_REVISION/MEASUREMENTS.json','Socially acquired L17 followed by L01 revision, separately audited access'),
 'late_order_adverse':('resultados/integracion/LIF_C11_NEW_BA/MEASUREMENTS.json','Intento longitudinal: nuevos acontecimientos de orden786/787 y sonda788 rechazados por ocupación; no se cuenta como nueva adquisición de orden'),
}
def main():
 original_sha=sha(SOURCE);old=load(SOURCE)['capabilities'];assert len(old)==47
 result=load(ROOT/'resultados/regresion_producto45/RESULT.json')
 tests=[json.loads(x) for x in (ROOT/'resultados/regresion_producto45/TESTS.jsonl').read_text(encoding='utf-8').splitlines()]
 assert len(tests)==82 and result['tests']==82 and result['successful']
 assert all(t['status']=='SUCCESS' for t in tests)
 registry=[]
 for i,t in enumerate(tests):
  module,cls,method=t['test'].split('.')
  path=ROOT/'base_validada/product45/tests/python'/(module+'.py')
  tree=ast.parse(path.read_text(encoding='utf-8'));line=None
  for node in tree.body:
   if isinstance(node,ast.ClassDef) and node.name==cls:
    line=next(x.lineno for x in node.body if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef)) and x.name==method)
  assert line is not None,t['test']
  registry.append({'index':i,'id':t['test'],'status':t['status'],'elapsed_seconds':t['elapsed_seconds'],
    'source':{'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'line':line},
    'result_locator':{'path':'resultados/regresion_producto45/TESTS.jsonl','jsonl_line':i+1},
    'kind':'REGRESION_DE_CONTRATO_PUBLICADO; exact historical reproduction only where separately stated'})
 refs={k:ref(path,'EVIDENCIA_CPC8_EJECUTADA',scope) for k,(path,scope) in EVIDENCE.items()}
 rows=[]
 for i,c in enumerate(old):
  links=[];replay=None;reproduced=False;repro_scope=None
  if i in (0,1,7,25):links.append(refs['cp01'])
  if i==7:links.append(refs['pending'])
  if i in (0,1,7):
   reproduced=True;repro_scope='REPRODUCIDA_PARCIAL: preserved CP01 source selected cases, not entire C01-C08 campaign'
  if i==8:links.append(refs['cp02']);reproduced=True;repro_scope='REPRODUCIDA_PARCIAL:11 actual CP02 forecast scenarios; not integrated E1'
  if i==11:links.extend([refs['sem'],refs['semparity']]);reproduced=True;repro_scope='REPRODUCIDA_PARCIAL:5 actual cases; one historical positive with exact initial/final full physical hashes'
  if i in INTEGRATED:links.extend([refs['e1'],refs['e1cut'],refs['e1sham'],refs['e1reserve']])
  if i in (4,12,19,35):links.extend([refs['l17'],refs['l17cut'],refs['l17sham'],refs['l17reserve'],refs['l17restore']])
  if i in (15,16,31,32):links.extend([refs['m1'],refs['m1control'],refs['m1reserve'],refs['l17revision']])
  if i in (0,16,18,19,31,35):links.append(refs['late_order_adverse'])
  if i in (15,16,32):links.append(refs['cmp'])
  if i==40:links.extend([refs['core17'],refs['coreclock']]);reproduced=True;repro_scope='REPRODUCIDA_PARCIAL_REPARACION:local RAW/function and save/load; full compressed operator and full historical clock arrays not reproduced'
  if i==45:
   reproduced=True;repro_scope='REPRODUCIDA_PARCIAL_INCLUIDA_EN_REGRESION: MBP4 R1-R8 fixtures, R3 full RAW/clocks continuation and R4 causal controls; not a new independent MBP4 campaign'
   links.append(ref('base_validada/product45/fixtures/mbp4/regressions/MANIFEST.json','FIXTURES_HISTORICOS_INCLUIDOS','Source identities for primary checkpoints/oracles used by executed R1-R8 tests'))
  commands={'cwd':'Extracted CPC8/ root with the official4.5 wheel installed in isolated CPython3.13x64; no private source tree required',
    'technical_regression':{'autocontenido':'SI' if TEST_MAP[i] else 'NO','command':'python -I -B ejecutar.py regresion --salida NUEVA_REGRESION' if TEST_MAP[i] else None,
      'scope':'Runs all82 technical tests, including listed relevant tests; does not imply exact replay of the historical apparatus'}}
  if i in (0,1,7,8,11):
   commands['historical_selected_reference']={'autocontenido':'SI','command':'python -I -B ejecutar.py referencias --salida NUEVAS_REFERENCIAS',
      'scope':repro_scope,'sources':['base_validada/reproducir_cp01_cp02.py','base_validada/reproducir_sem01.py']}
  else:commands['historical_selected_reference']={'autocontenido':'NO','command':None,
      'reason':'Only source/documentary reference or a different apparatus is offered, not an executable promise of exact complete historical replay'}
  if i in INTEGRATED:
   commands['new_integrated_case']={'autocontenido':'SI','command':'python -I -B src/integracion/run_shared.py --config configuraciones/integracion/E1_CASES_FROZEN.json --case-id E1_P11_AB --out NUEVA_E1',
      'scope':'Recreates NEW N131 E1 preparation; not the historical individual, no complete historical repertoire inherited by name'}
  states={'historica_segun_expediente':'EVIDENCIA_REPORTADA_EN_EL_CORTE_ORIGINAL; no equivale a éxito funcional global',
      'codigo_historico_original_preservado':c['state']['historical'],'preservada':c['state']['source_preserved'],
      'reproducida':reproduced,'reproduccion_alcance':repro_scope,'adaptada':i in ADAPT,
      'adaptacion_alcance':ADAPT.get(i),'integrada_con_limites':i in INTEGRATED,
      'integracion_alcance':ADAPT.get(i) if i in INTEGRATED else 'No se atribuye una nueva integración nativa en E1 a esta fila',
      'pendiente':'El aparato histórico completo, horizontes largos y todos sus controles quedan fuera del subconjunto salvo comparación explícita; disponer de fuente/API no acredita toda su función.'}
  if i==8:states['pendiente']='El pronóstico CP02 se ejecutó por separado, no se integró en E1; se conservan los errores tras cambiar la regularidad.'
  if i==40:states['pendiente']='R0_FACTOR_52 no reejecutado; no hay igualdad histórica de todos los clocks; reparación no integrada E1. Esta matriz no ofrece un CLI CORE17 con salida nueva.'
  if i in (36,46,28,29):states['pendiente']='Sector documental/teórico preservado; su catálogo o nombre no acredita una realización cognitiva/física completa.'
  status=('INTEGRADA_CON_LIMITES' if i in INTEGRATED else 'ADAPTADA' if i in ADAPT else 'REPRODUCIDA_PARCIAL' if reproduced else 'PRESERVADA')
  rows.append({'id':c['id'],'original_row_index':i,'original_json_pointer':'/capabilities/'+str(i),'mechanism':c['mechanism'],
      'historical_domain':c['domain'],'historical_controls':c['controls'],'historical_limits':c['published_limits'],
      'original_matrix':{'path':SOURCE.relative_to(ROOT).as_posix(),'sha256':original_sha},
      'origin_identities':[{k:o.get(k) for k in ('source_id','source_archive','archive_sha256','member','member_sha256','copied_as','copy_state')} for o in c.get('origins',[])],
      'estado_actual':status,'estados_independientes':states,'executed_test_indices':TEST_MAP[i],
      'technical_test_relation':'Relevant interface/mechanism regression, not automatically the exact historical recipe or all controls',
      'CPC8_primary_links':list({x['path']:x for x in links}.values()),'commands':commands})
 assert sha(SOURCE)==original_sha,'Original47-row matrix changed'
 test_path=ROOT/'resultados/regresion_producto45/TESTS.jsonl'
 overlay={'schema':'CPC8.cumulative_regression_overlay.v1','created_utc':datetime.now(timezone.utc).isoformat(),
  'scope':'Documentary crosswalk only; no Runtime executed by this generator; original47-row matrix byte-preserved',
  'original_matrix_sha256':original_sha,'counts':{'capability_rows':len(rows),'executed_python_tests':len(tests),
    'test_successes':sum(t['status']=='SUCCESS' for t in tests),'test_failures':result['failures'],'test_errors':result['errors'],'test_skipped':result['skipped'],
    'rows_with_selected_physical_reproduction':sum(r['estados_independientes']['reproducida'] for r in rows),
    'rows_adapted':sum(r['estados_independientes']['adaptada'] for r in rows),
    'rows_with_limited_new_integration':sum(r['estados_independientes']['integrada_con_limites'] for r in rows),
    'counting_rule':'Overlapping states and shared cases are not independent capacities/replicas; never sum row counts with tests'},
  'regression_primary':[ref('resultados/regresion_producto45/RESULT.json','TECHNICAL_RESULT','82 executed Python contracts, not82 new scientific worlds'),
    ref('resultados/regresion_producto45/TESTS.jsonl','TECHNICAL_TEST_LEDGER','Each row executed with source locator below')],
  'test_registry':registry,'capabilities':rows,
  'exceptions':[{'capability':'SEM01','rule':'Only A_future_UV pair initial/final RAW/clocks is historical full-state parity; the other4 are actually executed controls/reserve.'},
    {'capability':'MBP4_CONTEXTUAL_REWRITE','rule':'Some API regression tests truly continue primary checkpoints and compare full RAW/clocks; this limited reproduction is explicit, not denied because test is technical.'},
    {'capability':'CPC7_SELECTIVE_REVISION_M1_M2','rule':'N131 M1 integrated in E1; late M2 separate comparator research continuation outside helper cadence. Do not merge them.'},
    {'capability':'CPC7_NSM65_SCOPE','rule':'Documentary65 catalogue and opaque forms are not65 acquired semantic meanings.'}],
  'source_generator_sha256':sha(Path(__file__))}
 target=ROOT/'revision/MATRIZ_REGRESION_ACUMULATIVA.json'
 target.write_text(json.dumps(overlay,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'path':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'counts':overlay['counts']},ensure_ascii=False))
if __name__=='__main__':main()
