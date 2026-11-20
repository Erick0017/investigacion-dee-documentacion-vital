"""Build a concrete PI08 A decision from closed actual evidence. Default is
approved_for_adoption=False; Root alone may explicitly request --aprobar.
No Native/Store/product writes. Two exact prior scientific JSONs are preserved
locally, with original provenance, to satisfy the bounded adopter contract.
"""
from pathlib import Path
import argparse,copy,datetime,hashlib,json,shutil
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';CS=P/'estados/RP_A01/sistema';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01'
GATES=('functional_gain','conservation','causal_controls','source_reopening','new_function_at_final_cut','decisive_recipe_replay')
def read(path):return json.loads(path.read_text('utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def info(path):return {'path':str(path),'sha256':sha(path)}
def main(a):
 out=a.salida.resolve()
 if out.exists()or not out.is_relative_to((P/'control').resolve()):raise ValueError('Fresh P8/control decision required')
 factsfile=P/'control/EVALUACION_CONSOLIDACION_A_PI08_R01.json';deltafile=P/'control/DELTA_OPERATIVO_PRODUCTO_PROPUESTO_PI08_R02.json';facts=read(factsfile);delta=read(deltafile);process=a.process_proof.resolve(strict=True);writers=read(process)
 if not process.is_relative_to((P/'control').resolve())or writers.get('no_live_affected_writers')is not True:raise ValueError('Actual scoped closed-writer proof required')
 if facts.get('schema')!='DEE.PI08.A.combined_actual_gates.R01'or facts.get('life_id')!=LIFE or facts.get('all_fixed_evidence_gates_met')is not True:raise ValueError('Actual canonical A evaluation required')
 cardfile=CS/'estado/vidas'/LIFE/'VIDA.json';card=read(cardfile)
 if card['physical']['tick']!=facts['T']or card['physical']['N']!=67 or sha(CS/card['snapshot'])!=card['snapshot_sha256']:raise ValueError('Actual source moved beyond the evaluated coherent cut')
 for name,digest in delta['selectors_cas'].items():
  if sha(C/name)!=digest:raise ValueError('A product reference changed after bounded code proposal')
 for row in delta['proposed_code_files']:
  if sha(Path(row['source']))!=row['sha256']:raise ValueError('Reviewed source delta changed')
 inherited=[]
 def ref(value):
  path=Path(value['path']).resolve(strict=True)
  if sha(path)!=value['sha256']:raise ValueError('Closed scientific evidence changed')
  if path.is_relative_to(P.resolve()):return {'path':str(path),'sha256':value['sha256']}
  allowed=P.parent/'PROGRESION_INTEGRADA_07/control'
  if not path.is_relative_to(allowed.resolve())or path.name not in('COMPARACION_R03_REAL_NOFAIL_YOKE_Y_CORTES_PI07_R02.json','GATES_R03_A_B_RECALCULADOS_PI07.json'):raise ValueError('Only two explicit inherited scientific controls may be localized')
  target=P/'evidencia/HEREDADOS'/path.name;target.parent.mkdir(parents=True,exist_ok=True)
  if target.exists():
   if sha(target)!=value['sha256']:raise ValueError('Different preserved inherited evidence')
  else:shutil.copyfile(path,target)
  inherited.append({'original_path':str(path),'local_path':str(target),'sha256':value['sha256'],'classification':'Exact inherited control evidence, shared prefix; not a PI08 Native rerun.'})
  return {'path':str(target),'sha256':value['sha256']}
 gates={}
 for name in GATES:
  gate=facts['gates'][name]
  if gate.get('result')is not True or not gate.get('criterion')or not gate.get('evidence'):raise ValueError('Actual gate missing or negative: '+name)
  gates[name]={'satisfied':True,'criterion':gate['criterion'],'result':True,'evidence':[ref(v)for v in gate['evidence']]}
 profile=read(CS/'contratos/PI08_USO_OPERATIVO_R01.json')
 if profile['status']!='PREPARED_DIAGNOSTIC'or profile['life_id']!=LIFE:raise ValueError('No premature permission commitment')
 evidence=[info(factsfile),info(deltafile),info(process)]
 gains=['Regulación R03 adquirida en la trayectoria PI07, ahora reproducida y utilizada en una sucesora completa: OP4..7=4/4 conjuntos y OP8..11=3/4, con pulso Native admitido y mensaje real conservado sin pulso.','Acceso público FI alternativo con signo positivo, negativo y cero material:3/3; palabras/memoria nombradas4/4; tres composiciones C2C reales produjeron23,17,23 y productos64B.','Integración P0 real30->32 con validación previa de la cadena efectiva, preparación separada, rechazo34 sin cambio científico, interrupción e idempotencia/reapertura comprobadas; un recurso32nuevo fue consumido realmente.']
 losses=['La comparación FI directa legacy no se declara reparada ni conservada intacta: en esta vida la ruta exterior se sustituye explícitamente por la retimada; el contrato directo histórico y su fallo PI07 permanecen preservados.','Se acepta mayor coste temporal/material del acceso FI retimado, según cada caso real; no se presenta782/182 como constante universal. Un resultado conjunto deOP8..11 fue adverso.','El suministro adicional y la selección del acceso/calendario son preparación P0. Esta decisión no atribuye esa ingeniería a aprendizaje Native.']
 uncertainties=['No se demuestra agencia general, planificación autónoma ni superioridad sobre toda referencia contextual.','Los controles heredados comparten prefijos. Se reutiliza su alcance causal medido, sin convertirlos en nuevos individuos o ensayos PI08.','No hubo panel completo nuevo enT860622: las coberturas pertenecen a sus cortes explícitos. B/C siguen pendientes y no condicionan esta ganancia A.','Recursos finitos al corte evaluado: R03ordinal12,6ofertas; C2Cordinal31,1recurso. El uso público posterior deberá registrar su propio consumo y corte.']
 assistance=['El anfitrión prepara anatomía, interfaces, sensores/transductores fijos, oportunidades, dispositivo, calendario y evaluación; inicia las peticiones públicas.','DEE produce las elecciones, comparaciones y aritmética Native; los retornos genéricos transportan consecuencias reales, sin soluciones esperadas al actor.','Cambios de identidad/selección, traslado completo, protección de procesos, suministro y contrato FI son administración/ingeniería explícitas; no recuerdos fusionados ni autorreparación.']
 result={'schema':'DEE.PI08.A.reasoned_adoption_decision.v1','built_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'approved_for_adoption':bool(a.aprobar),'decision_id':'PI08_CONSOLIDACION_A_OPERATIVA_01','life_id':LIFE,'source_snapshot_sha256':card['snapshot_sha256'],'source_tick':facts['T'],'gates':gates,'approved_code_files':delta['proposed_code_files'],'selectors_cas':delta['selectors_cas'],'new_contract':profile,'catalog_entry':{'id':'PI08_REGULACION_ADQUIRIDA_CONSOLIDADA_A_01','name':'Regulación R03 consolidada con acceso FI alternativo e integración C2C32','kind':'vida_con_regulacion_adquirida_y_acceso_P0_migrado','status':'OPERATIVE_WITH_DECLARED_LIMITS','domain':'Regulación local contextual,FIindependiente0..20,palabras/memoria nombradas y composición C2C dentrodecontratos finitos','not_claimed':['generalagency','Nativeautonomousplanning','P0supplylearned','unchangedlegacyFIaccess','branchmemoryfusion'],'limits':uncertainties+losses,'functional_changes':[{'function':'R03regulation','classification':'inherited_acquired_function_consolidated'},{'function':'outerFI','classification':'alternative_access_and_explicit_contract_substitution'},{'function':'C2Cenvironment32','classification':'prepared_external_supply_and_operational_migration'}]},'scope':'Adoptar una sucesora completa de la genealogía principal con regulación R03 útil y acceso publicado coherente. Ganancia parcial delimitada; no exige inmovilizar microestado, aprobarB/C ni fingir conservación del antiguo calendarioFI.','gains':gains,'losses':losses,'uncertainties':uncertainties,'assistance':assistance,'evidence':evidence,'regression_coverage':{'named_memory':facts['named_memory'],'public_FI':facts['public_FI'],'C2C_actual_products':[{'ordinal':v['ordinal'],'actual_Native_number':v['actual_Native_number'],'64B_actual_valid':v['actual_64B_product_valid']}for v in facts['C2C_products']],'R03_OP4_7':facts['regulation_OP4_7_joint'],'R03_OP8_11':facts['regulation_OP8_11_joint'],'coverage_at_final_tick':'Última consultaalfa y continuidad cerrada; no otro panel completoenelúltimotick.','actual_Native_denominators':facts['Native_inputs_actual_deduplicated']},'process_proof':str(process),'inherited_control_localization':inherited,'Root_explicit_approval_flag_used':bool(a.aprobar),'adoption_executed_by_builder':False,'Native_executed_by_builder':False}
 with out.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'decision':str(out),'sha256':sha(out),'approved_for_adoption':result['approved_for_adoption'],'source_tick':facts['T'],'source_snapshot_sha256':card['snapshot_sha256'],'gates':list(gates),'code_files':len(result['approved_code_files']),'inherited_exact_JSON_copies':len(inherited),'Native_executed':False}))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--process-proof',type=Path,required=True);ap.add_argument('--salida',type=Path,required=True);ap.add_argument('--aprobar',action='store_true');main(ap.parse_args())
