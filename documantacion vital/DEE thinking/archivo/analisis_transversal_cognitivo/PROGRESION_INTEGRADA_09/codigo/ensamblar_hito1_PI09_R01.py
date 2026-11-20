"""Code-only hito1 checklist and closed-evidence assembly; never adopts.

Default prepares instructions without live state reads. --ensamblar consumes
only named CLOSED actual proofs plus C2's unique six-gate evaluation. It emits
references for Root's separate explicit approval and existing adoption CLI.
"""
from pathlib import Path
import argparse,datetime,hashlib,json
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad';PY=C/'motor/python313/python.exe'
RID='pi09_consulta_native12_desde_C_T884835_R03';REPRO='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_REPRO_01';NATIVE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01'
GATES=('functional_gain','conservation','causal_controls','source_reopening','new_function_at_final_cut','decisive_recipe_replay')
FILES=('validar_paneles_hito1_PI09_R01.py','reabrir_SOURCE_NATIVE_PI09_0_R01.py','comprobar_procesos_afectados_PI09_R01.py','construir_decision_PI09_R02.py','incorporar_PI09_misma_identidad_R03.py','ejecutar_administracion_con_tope_PI09_R03.py','reabrir_producto_PI09_0_R02.py')
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':str(Path(p).resolve(strict=True)),'sha256':sha(Path(p))}
def put(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def instructions():
 return f'''HITO1 PI09 — OPERACIONES INDIVIDUALES ROOT, NO EJECUTAR EN BLOQUE

Estado de esta preparación: no aprobación, no Native y no escrituras producto.
Todas las fuentes R01/R02 previas, recetas y controles quedan preservados.

$P9 = '{P}'
$H = Join-Path $P9 'codigo'
$C = '{C}'
$PY = '{PY}'

1. RP cold12 ya cerrado y registrado: NO repetirlo. Usar la verificación
   {RP/'verificaciones'/RID/(REPRO+'.json')}
   y su comparación Native completa real. La receta literal permanece
   PREPARADA; el registro efectivo aditivo contiene la ejecución real.

2. Esperar los DOS paneles cerrados,18 registros cada uno, sin alterar plan.
   Ejecutar UNA validación stdlib de los nuevos comprobantes cerrados:
& $PY -I -B -X utf8 (Join-Path $H 'validar_paneles_hito1_PI09_R01.py') --panel (Join-Path $P9 'control/PI09_PANEL_P0_R01.json') --discovery (Join-Path $P9 'control/PI09_DISCOVERY_P0_R01.json') --salida (Join-Path $P9 'control/PANELES_HITO1_VERIFICADOS_PI09_R01.json')
   Salida: cierre,12 testigos antiguos,5 nuevos,RAW numérico/FI,recibos,
   gate P0 5/5 y ganancia>=2 y no peor conservación. Los dos números
   heredados forman una cadena causal; NULL nunca se convierte en0.

3. Reabrir el MISMO NATIVE maduro903603, sin clon, código ni avance:
& $PY -I -B -X utf8 (Join-Path $H 'reabrir_SOURCE_NATIVE_PI09_0_R01.py') --ejecutar
   Esperado: public gestionar STATE PI09=12,C2C=31,FI=4; guardar/cerrar0;
   igualdad exacta RAW/clocks/prefijo/recibos/agenda/fase/stock y claves
   científicas. Sólo puede variar SYSTEM/SERVICE/queue. Guardar SHA nueva.

4. C2 emite su evaluación ÚNICA schema
   DEE.PI09.consultation.combined_actual_gates.R01 desde los cierres reales.
   Este ensamblador no inventa ese comando ni marca gates pendientes true.
   Se requiere6gates satisfechos antes de la aprobación de Root.

5. Comprobante fresco de procesos, después de cerrar todos los owners:
& $PY -I -B -X utf8 (Join-Path $H 'comprobar_procesos_afectados_PI09_R01.py') --salida (Join-Path $P9 'control/PROCESOS_PI09_PREPARAR_R01.json')
   Esperado no_live_affected_writers=true,<=600seg. Si hay duda PID/lock,
   preservar; no matar procesos ni limpiar marcadores automáticamente.

6. Ensamblar referencias con los nombres REALES emitidos en4/5:
& $PY -I -B -X utf8 (Join-Path $H 'ensamblar_hito1_PI09_R01.py') --ensamblar --panel-validation (Join-Path $P9 'control/PANELES_HITO1_VERIFICADOS_PI09_R01.json') --source-reopening (Join-Path $P9 'control/REAPERTURA_SOURCE_NATIVE_PI09_R01.json') --evaluacion '<JSON_REAL_C2_SEIS_GATES>' --process-proof (Join-Path $P9 'control/PROCESOS_PI09_PREPARAR_R01.json') --rp-comparison '<JSON_REAL_COMPARACION_COLD>' --salida (Join-Path $H 'CIERRE_HITO1_ACTUAL_R01')
   Los dos placeholders son rutas explícitas todavía producidas por Root/C2,
   no son comandos ejecutables literales. No ejecutar hasta sustituirlas.

7. Sólo tras revisión razonada y aprobación EXPLÍCITA Root:
& $PY -I -B -X utf8 (Join-Path $H 'construir_decision_PI09_R02.py') --evaluacion '<JSON_REAL_C2_SEIS_GATES>' --referencias (Join-Path $H 'CIERRE_HITO1_ACTUAL_R01/REFERENCIAS.json') --process-proof (Join-Path $P9 'control/PROCESOS_PI09_PREPARAR_R01.json') --salida (Join-Path $P9 'control/DECISION_ADOPCION_PI09_HITO1_R01.json') --aprobar
   --aprobar es la acción explícita Root; ningún helper la agrega solo.

8. Mover continuación completa/330deps+delta exacta sin duplicar memoria:
& $PY -I -B -X utf8 (Join-Path $H 'ejecutar_administracion_con_tope_PI09_R03.py') --accion preparar --decision (Join-Path $P9 'control/DECISION_ADOPCION_PI09_HITO1_R01.json') --process-proof (Join-Path $P9 'control/PROCESOS_PI09_PREPARAR_R01.json') --ejecutar
   Esperado PREPARED_MOVED_NOT_PROMOTED, misma vida/UUID,todos3directorios
   y checkpoints/historia,0ticks. Sólo C2C.life_id es hoja administrativa.
   A861426 queda preservado. No seleccionar ante copia/movimiento parcial.

9. Reabrir PRODUCTO todavía NO seleccionado mediante gestor público0:
& $PY -I -B -X utf8 (Join-Path $H 'reabrir_producto_PI09_0_R02.py') --ejecutar
   Esperado REAPERTURA_PRODUCTO_PI09.json: física/prefijo/stock iguales,
   owner_closed y pending_reconciled true; no FI/EP material.

10. Nuevo comprobante fresco para adoptar; no reutilizar uno caducado:
& $PY -I -B -X utf8 (Join-Path $H 'comprobar_procesos_afectados_PI09_R01.py') --salida (Join-Path $P9 'control/PROCESOS_PI09_ADOPTAR_R01.json')
& $PY -I -B -X utf8 (Join-Path $H 'ejecutar_administracion_con_tope_PI09_R03.py') --accion adoptar --decision (Join-Path $P9 'control/DECISION_ADOPCION_PI09_HITO1_R01.json') --process-proof (Join-Path $P9 'control/PROCESOS_PI09_ADOPTAR_R01.json') --reopening-proof (Join-Path $P9 'control/REAPERTURA_PRODUCTO_PI09.json') --ejecutar
   Store.promote debe dejar testigo COMMITTED real antes de publicar contrato.
   Después contrato exacto COMMITTED,6referencias y transporte existente.

11. Sólo STATE público/guardar/cerrar0 del seleccionado, manteniendo903603:
& $PY -I -B -X utf8 (Join-Path $H 'reabrir_producto_PI09_0_R02.py') --seleccionado --ejecutar
   No afirmar nueva prueba material postCOMMITTED. Base del hito: último
   EP11real +RPexact +paneldiagnóstico +reaperturas0/equivalencia.
   El uso público material final se reserva para DESPUÉS de decidir D.

D: DISCOVERY postPanel es descendiente coherente de Native12; NATIVE queda
quieto. No declarar D seleccionado, FI8 admitido, Source0 realizado ni cambios
de presupuesto hasta sus comprobantes reales. Los permisos D son revisión
separada y no modifican los cuerpos R02/D2 ni activan controles en principal.
'''
def assemble(a):
 required=(a.panel_validation,a.source_reopening,a.evaluacion,a.process_proof,a.rp_comparison)
 need(all(required),'Closed actual panel/source0/C2evaluation/process/RP comparison paths required')
 panel=read(a.panel_validation);source=read(a.source_reopening);evaluation=read(a.evaluacion);process=read(a.process_proof);comparison=read(a.rp_comparison)
 need(panel.get('schema')=='DEE.PI09.closed_panels_and_prospective_P0_gate.validation.R01'and panel.get('closed')is True and panel.get('error')is None and panel['minimum_previous_function_gate']['satisfied']is True,'Actual minimum closed conservation failed or missing')
 need(source.get('schema')=='DEE.PI09.mature_source.public_reopening0.R01'and source.get('life_id')==NATIVE and source.get('closed')is True and source.get('new_ticks')==0 and all(source.get(k)is True for k in('physical_unchanged','causal_prefix_equal','operational_state_valid','stock_unchanged','source_code_unchanged','current_principal_unchanged')),'Actual mature same-ID source0 required')
 need(evaluation.get('schema')=='DEE.PI09.consultation.combined_actual_gates.R01'and set(evaluation['gates'])==set(GATES)and all(g.get('satisfied')is True for g in evaluation['gates'].values()),'C2 actual six gates are not all satisfied')
 need(process.get('no_live_affected_writers')is True and process.get('scope')and process.get('evidence'),'Actual scoped fresh process proof required')
 age=(datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(process['recorded_utc'].replace('Z','+00:00'))).total_seconds();need(0<=age<=600,'Scoped process proof expired; obtain another new proof')
 need(comparison.get('overall')is True and comparison.get('physical_equal')is True and comparison.get('causal_prefix_equal')is True and comparison.get('unexpected_metadata_changes')==[],'Actual complete RP Native comparison required')
 result=P/'estados/RP_REPRO_R01/RESULTADO_REPRODUCCION.json';verification=RP/'verificaciones'/RID/(REPRO+'.json');r=read(result);v=read(verification)
 need(r.get('status')=='COMPLETED'and r.get('owner_closed_coherently')is True and r.get('criteria_met')is True and v.get('actual_native_execution_completed')is True and v.get('fixed_local_criteria_met')is True,'Actual completed and additively registered cold12 required')
 four=P/'fuentes/EVALUACION_CUATRO_CIERRES_PI09_R01.json';actual4=read(four);need(actual4['gates']['candidate_floor']['result']is True and actual4['gates']['bounded_Native_access']['result']is True and actual4['gates']['causal_content_witness']['result']is True,'Actual bounded-information/causal scientific gate required')
 scope='One same-identity continuous Native12 successor at903603: bounded material consultation, actual technical register release and second-stage Native use. Existing anatomy/codecs and generic second return remain prepared; specific learning of asking value is not established.'
 chain=panel['guard']['arithmetic_causal_chain'];chain_ok=type(chain['first_actual'])is int and type(chain['second_actual'])is int and chain['first_actual']==13 and chain['second_actual']==8
 losses=[{'scope':'published_direct_arithmetic_chain','actual':chain,'status':'AVAILABLE_IN_ACTUAL_CLOSED_PANEL'if chain_ok else'PARTIAL_AVAILABILITY_REPORTED','not_two_independent_losses':True},'Historical direct-arithmetic failures remain preserved; a positive current panel does not establish universal availability or prove phase67 is the cause.','No first-query-specific credit, general planning or universal superiority over always-query claimed.','No new public material test after COMMITTED before D; final public material use remains pending.']
 entry={'id':'PI09_CONSULTA_REGISTRADA_NATIVE_R02','name':'Acceso condicional Native a información registrada: integración acotada PI09','kind':'bounded_integration_of_existing_Native_functions','status':'ACTUAL_GATES_PASSED_PENDING_ROOT_COMMIT','scope':scope,'mental_concept_count_increase_claimed':False,'causal_evidence':ref(four),'conservation_evidence':ref(a.panel_validation),'new_material_post_COMMITTED_test_executed':False,'reproduction':{'recipe':RID,'actual_registered_verification':ref(verification)}}
 references={'PI09_actual_closed_arms':{role:{'path':actual4['source_evidence'][role]['path'],'sha256':actual4['source_evidence'][role]['sha256']}for role in('native_real','always_real','never','always_desacoplado')},'PI09_source_full_pair':{'path':str(P/'pares/NATIVE_POST12_T903603'),'manifest_sha256':'0cce6bcfe366551b52b0ca25c5959bd6e07ed4493221ec26b76af962c13b6553'},'PI09_source_reopening_proof':ref(a.source_reopening),'PI09_reproduction_result':ref(result),'PI09_reproduction_comparison':ref(a.rp_comparison),'PI09_conservation_proof':ref(Path(panel['guard']['proof']['path'])),'scope':scope,'gains':['Canonical Native12/12 useful including6/6reserved,8actual applied questions/actual registered bits.','Always12/12,Never3/12,decoupled6/12; matched local content contrast changes Native action and actual useful outcome from equal pre-datum material prefix.'],'losses':losses,'uncertainties':['Questions and sequence remain prepared opportunities; asking-specific causal credit is not isolated.','Exact deterministic cold replay shares the complete past; it is not independent acquisition replication.','Later D availability/adoption and public material use are still pending.'],'assistance':['Inherited N67/TC anatomy, fixed codecs and fixed sensor/tool/calendar.','Technical external register releases an already measured actual RAW bit only after own applied request/signature; it is not Native memory or a fresh later observation.','Explicit18-offer lot and fixed generic second-stage consequence, no bank reset.'],'regression_coverage':{'word_context7':panel['guard']['words_context_correct'],'signed_FI3':panel['guard']['signed_FI_correct'],'published12':panel['guard']['published_correct'],'direct_arithmetic_actual_chain':panel['guard']['arithmetic_causal_chain'],'P0_fresh':panel['P0_public_access_gate'],'not_on_selected_MAIN':True},'catalog_entry':entry,'public_arithmetic_policy':'P0_phase19_fixed'if panel['P0_public_access_gate']['satisfied']else'legacy_partial','arithmetic_guard_actual_gate_met':panel['P0_public_access_gate']['satisfied'],'arithmetic_guard_actual_evidence':[panel['legacy']['proof'],panel['guard']['proof'],ref(a.panel_validation)]}
 return references,{'schema':'DEE.PI09.hito1.closed_evidence_assembly.R01','ready_for_Root_reasoned_decision':True,'approval':False,'Native_executed':False,'product_modified':False,'sources':[ref(x)for x in required]+[ref(four),ref(verification)],'candidate_tick':903603,'current_source_encoded_snapshot_sha256':source['snapshot_sha256'],'frozen_canonical_full_pair_snapshot_sha256':source['before_snapshot']['sha256'],'new_material_post_COMMITTED_test_executed':False,'selected_material_use_still_pending':True}
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--ensamblar',action='store_true');ap.add_argument('--panel-validation',type=Path);ap.add_argument('--source-reopening',type=Path);ap.add_argument('--evaluacion',type=Path);ap.add_argument('--process-proof',type=Path);ap.add_argument('--rp-comparison',type=Path);ap.add_argument('--salida',type=Path,default=H/'CIERRE_HITO1_PREPARADO_R01');a=ap.parse_args();out=a.salida.resolve();need(out.is_relative_to(H.resolve())and not out.exists(),'Fresh output directory only under codigoPI09');out.mkdir()
 if a.ensamblar:
  references,proof=assemble(a);put(out/'REFERENCIAS.json',references);put(out/'ENSAMBLADO.json',proof)
 else:put(out/'PLAN.json',{'schema':'DEE.PI09.hito1.code_only_close_assembler.R01','Native_executed':False,'source_live_state_read':False,'approval':False,'code_sources':{name:ref(H/name)for name in FILES},'pending_closed_evidence':['PANEL/DISCOVERY18records','matureSourceNative0','C2combined6gates','freshProcessProof','actualRPcomparison+registeredCold12'],'selected_material_use_still_pending':True})
 (out/'INSTRUCCIONES_ROOT.txt').write_text(instructions(),'utf8');print(json.dumps({'prepared':str(out),'Native_executed':False,'product_modified':False,'actual_assembly':a.ensamblar,'approval':False},ensure_ascii=False))
if __name__=='__main__':main()
