"""Añade pre-cierre cerrado real antes de sincronizar; conserva helper R01."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;source=H/'cerrar_presupuesto_y_estado_PI09_R01.py';target=H/'cerrar_presupuesto_y_estado_PI09_R02.py'
if target.exists():raise FileExistsError('R02 anterior conservada')
t=source.read_text('utf8');a=" sync=read(a.sync_proof);need(sync.get('schema')=='DEE.PI09.final_current_metadata.applied.R03'and sync.get('applied')is True and sync['actual_current']['life_id']==LIFE and sync['actual_current']['snapshot']['sha256']==card['snapshot_sha256'],'SincronizaciónR03 aplicada al corte actual requerida')\n scope=sync['actual_current']['operational_validation_scope'];need(scope['selected_material_function_test_pending']is True and scope['selected_material_function_test_executed']is False and scope['selected_check_scope']=='ACTUAL_SELECTED_STATE0_SAVE_CLOSE_ONLY','No atribuir función material seleccionada que no se ejecutó')"
b=""" if a.pre_cierre:
  status=load('PI09_final_selected_scope_only',H/'sincronizar_cierre_actual_PI09_R03.py');scope=status.selected_validation(LIFE,selected,ref(a.selected_zero),ref(a.source_function))
 else:
  sync=read(a.sync_proof);need(sync.get('schema')=='DEE.PI09.final_current_metadata.applied.R03'and sync.get('applied')is True and sync['actual_current']['life_id']==LIFE and sync['actual_current']['snapshot']['sha256']==card['snapshot_sha256'],'SincronizaciónR03 aplicada al corte actual requerida');scope=sync['actual_current']['operational_validation_scope']
 need(scope['selected_material_function_test_pending']is True and scope['selected_material_function_test_executed']is False and scope['selected_check_scope']=='ACTUAL_SELECTED_STATE0_SAVE_CLOSE_ONLY','No atribuir función material seleccionada que no se ejecutó')
 source0=read(a.source_zero);need(source0.get('closed')is True and source0.get('new_ticks')==0 and source0.get('new_Native_inputs')==0 and source0.get('physical_unchanged')is True,'Source0 real sin nuevos inputs/ticks requerida')
 sourcefun=read(a.source_function);need(sourcefun.get('closed')is True and sourcefun.get('error')is None and sourcefun.get('life_id')==LIFE and sourcefun.get('final_tick')==922371,'Última función Source cerrada del corte real requerida')
 last=[r for r in sourcefun.get('records',[])if r.get('literal',{}).get('modo')=='eci01-pi09-d-episodio'];need(last and last[-1]['rows'][0].get('actual_failed')is False,'Última función útil Source requerida')"""
assert t.count(a)==1;t=t.replace(a,b).replace("'final_sync':ref(a.sync_proof)","'final_sync':ref(a.sync_proof)if a.sync_proof else None,'final_sync_pending_after_actual_closed_facts':bool(a.pre_cierre)")
t=t.replace("ap.add_argument('--cerrar',action='store_true');","ap.add_argument('--cerrar',action='store_true');ap.add_argument('--pre-cierre',action='store_true');")
t=t.replace(" if not a.cerrar:print("," if not a.cerrar and not a.pre_cierre:print(")
old=" need(all(getattr(a,k)is not None for k in('writers_proof','selected_zero','source_zero','source_function','publication','sync_proof')),'Todas las referencias finales explícitas son obligatorias');close(a)"
new=""" need(all(getattr(a,k)is not None for k in('writers_proof','selected_zero','source_zero','source_function','publication'))and(a.pre_cierre or a.sync_proof is not None),'Referencias explícitas requeridas; sync sólo después de pre-cierre')
 if a.pre_cierre:
  need(not a.actualizar_registro and not a.leer_primero,'Pre-cierre sólo genera hechos cerrados; REGISTRO/ficha después de sync')
  globals()['OUTPUT']=P/'control/CIERRE_PREVIO_A_SYNC_PI09_R01.json'
 close(a)"""
assert t.count(old)==1;t=t.replace(old,new);ast.parse(t);target.write_text(t,'utf8');print(json.dumps({'file':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'Native_executed':False,'product_writes':False}))
