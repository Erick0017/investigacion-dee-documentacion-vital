"""Close factual PI04 NO-ADOPTION authoring input. No DEE import or operational writes.
Default dry-run; --apply writes new decision/facts only after actual closed gates.
The separate positive-adoption helper remains unchanged and is not used here.
"""
from pathlib import Path
import argparse,copy,datetime,hashlib,json
P=Path(__file__).resolve().parents[1];R=P.parents[2];C=R/'DEE Cognitive 2.0';S=C/'sistema'
MARK='[[CIERRE_REAL_PENDIENTE]]';EXPECTED='5581d3785bf7d7194b5bdb545827aab55f0659d8b3f2c00301425d89616cf07b'
def need(x,s):
 if not x:raise ValueError(s)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def info(p):
 p=Path(p).resolve(strict=True);b=p.read_bytes();return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def main(a):
 draft=P/'control/CIERRE_CIENTIFICO_PI04_BORRADOR.json';panel=P/'control/CONSERVACION_REGRESION_PI04_VERIFICADA.json';pair=P/'control/EXPORTACION_ESTABLE_PI03_PI04_C2C_CONSERVACION_FALLIDA_T818074.json';cold=P/'control/C2C_COLD20_NATIVE_VERIFICADA_R01.json'
 activep=S/'estado/ACTIVO.json';cardp=S/'estado/vidas/ECI02_PI03_MAIN/VIDA.json';active=read(activep);card=read(cardp)
 decisionp=P/'control/DECISION_NO_ADOPCION_PI04.json';existing_decision=read(decisionp)
 need(existing_decision['schema']=='DEE.PI04.reasoned_no_adoption.v1'and existing_decision['adoption_performed']is False and existing_decision['approved_for_adoption']is False,'Actual Root no-adoption decision required')
 need(existing_decision['principal']['life_id']=='ECI02_PI03_MAIN'and existing_decision['principal']['tick']==775355 and existing_decision['gates']['conservation']['satisfied']is False and existing_decision['gates']['conservation']['correct']==5 and existing_decision['gates']['conservation']['actually_tested']==6,'Root decision contradicts actual blocked gate')
 inputs=[decisionp,draft,panel,pair,cold,activep,cardp,C/'PROYECTO.json',C/'CONTINUIDAD_DEE_COGNITIVE_2_0.json',P/'REGISTRO_CAMPANA.json'];before={str(p):info(p)for p in inputs}
 d=read(draft);need(d['closed_for_authoring']is False,'Preserved draft required')
 need(active['life_id']==card['life_id']=='ECI02_PI03_MAIN'and active['tick']==card['physical']['tick']==775355 and card['physical']['N']==67,'Protected original selection/current cut changed; no guessed principal')
 need(active['snapshot_sha256']==card['snapshot_sha256']==EXPECTED,'Protected original snapshot identity changed')
 snapshot=S/card['snapshot'];need(info(snapshot)['sha256']==EXPECTED,'Original snapshot bytes changed')
 p=read(panel);need(p['gate']=='BLOCKED_MATERIAL_REGRESSION'and p['correct']==5 and p['executed']==6 and p['planned_panel']==12 and p['after_tick']==818074 and p['complete_panel']is False,'Actual failed conservation proof required')
 need(p['rows'][-1]['name']=='FIplus'and p['rows'][-1]['actual']==-1 and p['rows'][-1]['expected']==1,'Exact actual regression required')
 for row in p['rows']:need(info(row['primary']['path'])==row['primary'],'Panel primary changed')
 e=read(pair);need(e['life_id']=='ECI02_PI03_REPRO_PI04_MAIN_02'and e['tick']==818074 and e['manifest_sha256']=='38f038262fd00bbae49033b645202bc81f77a6a0ab309603fcfc3c5076a509d2','Closed candidate full pair required')
 manifest=Path(e['destination'])/'MANIFIESTO_PAR.json'
 # Actual stable exporter may use its recorded manifest filename; integrity was checked by that exporter.
 need(Path(e['destination']).is_dir()and e['zero_tick_export_comparison']['physical_equal']is True,'Candidate preservation/zero-tick export proof missing')
 replay=read(cold);need(replay['status']=='NATIVE_REPLAY_VERIFIED'and replay['Native_executed']is True and replay['closed']is True and replay['opportunities']==20 and replay['products']==19 and replay['reserved_products']==8 and replay['Native_inputs_unique']==replay['Native_inputs_applied']==3720,'Actual cold Native replay witness required')
 project=read(C/'PROYECTO.json');cont=read(C/'CONTINUIDAD_DEE_COGNITIVE_2_0.json');need(project['selected_life']==cont['life_id']==active['life_id']and project['latest_saved_tick']==cont['physical_cut']['tick']==775355,'Original project/continuity selection changed')
 manual=C/project['manual_current'];need(info(manual)['sha256']==d['manual_original']['sha256']and project['manual_internal_edition']=='1.30','Original1.30 Manual changed before authoring')
 budget=read(P/'REGISTRO_CAMPANA.json');need(budget['budget']['Native_ticks_all_branches']==120000,'Native ceiling changed')
 floor=budget.get('new_Native_ticks_closed_floor');need(type(floor)is int and floor<=120000,'Actual direct Native ledger floor required')
 parent=card.get('PI03_provenance',{});need(parent,'Recorded PI03 physical provenance required; do not infer transport parent')
 principal={'life_id':'ECI02_PI03_MAIN','N':67,'tick':775355,'profile':card['profile'],'snapshot_sha256':EXPECTED,'snapshot_relative_to_product':'sistema/'+card['snapshot'],'physical_parent':parent,'transport_parent_preserved':card.get('parent'),'adoption_performed':False,'ACTIVO_reference_tick':active['tick'],'current_VIDA':info(cardp),'preserved_candidate':{'life_id':e['life_id'],'tick':818074,'full_pair':e['destination'],'manifest_sha256':e['manifest_sha256'],'role':'scientific_candidate_not_selected'}}
 closure='No se adopta PI04: la conservación se detuvo tras seis de doce usos previstos, con cinco correctos; FIplus 14/3 produjo −1 frente a +1 esperado. Las otras seis pruebas no se ejecutaron. El principal sigue siendo ECI02_PI03_MAIN, N67, T775355, con padre físico ECI02_PI02_MAIN, T753346. La candidata completa T818074 queda preservada por separado, sin fusionar recuerdos ni sustituir al principal.'
 paneltext='El panel material recorrió T817583→818074: luma+, nara−, clasifica−, suma+ y alfa− fueron correctos; FIplus 14/3 fue la sexta prueba y devolvió −1. Las 211 entradas únicas fueron aplicadas, incluidas 176/176 de FIplus. Hay una regresión funcional localizada, no una prueba de pérdida global ni causa única aislada; el criterio de conservación bloquea la promoción.'
 replaytext='La receta fría se ejecutó realmente en un diagnóstico nuevo desde T800379 hasta T816019: 19/20 productos, 8/8 reservas, 20 aritméticas, 3720/3720 entradas y 50/50 comprobaciones, con física final idéntica. Es reproducción material, separada del recálculo documental y de la experiencia del principal. El gestor permite listar y verificar sus requisitos; esa incorporación de reproducibilidad no equivale a adoptar la candidata.'
 def replace(x):
  if isinstance(x,str):return x.replace(MARK,closure).replace('Este borrador mantiene adopción=false.','No hubo adopción operativa.').replace('Cierre operativo pendiente.','La conservación bloqueó la adopción; el principal anterior permanece seleccionado.')
  if isinstance(x,list):return[replace(y)for y in x]
  if isinstance(x,dict):return{k:replace(v)for k,v in x.items()}
  return x
 out=replace(copy.deepcopy(d));out.update(schema='DEE.PI04.closed_scientific_authoring_facts.no_adoption.v1',closed_for_authoring=True,closed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),principal=principal,manual_before_publication_current_edition='1.30',intended_publication_edition='1.31',documents_published_by_finalizer=False)
 out['cover_summary']='PI04: coordinación Native contextual asistida, 19/20 productos y 8/8 reservas, frente a 12/20 y 6/8 con retorno constante. La señal desacoplada obtuvo 20/20 y 8/8; no hubo ventaja de contingencia verdadera. '+closure
 out['resume4']=closure;out['release_cut']='Corte científico PI04 del 2026-11-09. '+closure;out['state_of_edition']='Edición documental 1.31; base 1.30 preservada literalmente. '+closure
 for section in out['sections']:
  if section['title'].startswith('47.1'):
   section['paragraphs'][-1]='Los localizadores de este capítulo parten de DEE thinking/archivo/analisis_transversal_cognitivo/PROGRESION_INTEGRADA_04 y de DEE Cognitive 2.0/reproducibilidad. '+closure
  if section['title'].startswith('47.8'):
   section['paragraphs']=[paneltext,'Tras guardar y reabrir la candidata, dos trabajos consecutivos se completaron en T816019→817583: 2/2 productos y 372/372 entradas. Después el panel detectó la regresión; los trabajos nuevos no compensan silenciosamente el fallo de conservación.','El control de contexto cerrado obtuvo 2/4 frente a 4/4 comparables, omitiendo un dato por oportunidad: 185 frente a 186 entradas. El control del enlace produjo la aritmética 7 pero ningún producto, omitiendo cuatro entradas MU: 182 frente a 186. Mantienen 782 ticks por oportunidad; prueban dependencia de canales y eslabones, con dosis distintas, no controles semánticos de dosis perfectamente iguales.']
  if section['title'].startswith('47.9'):
   section['paragraphs']=['Los pares completos se conservan en RP, incluidos T775355, post-E3 T789431, C2 T798033, B T800379, C2C post-desarrollo T809763 y post-reserva T816019, además del futuro de conservación fallida T818074. La receta fría se utiliza sólo en destinos diagnósticos nuevos; los selectores del principal original no se cambiaron.',replaytext]
   section['commands']=a.comando or []
  if section['title'].startswith('47.10'):section['paragraphs']=[closure,'La mejora funcional local y los medios para repetirla se conservan. Para continuar la investigación debe compararse primero el acceso de FIplus y la historia de la candidata con el prefijo preservado, usando clones; no se atribuye la regresión a borrado de memoria ni se inicia aquí otra investigación.']
 out['compendium_paragraphs'][-1]=closure;out['compendium_paragraphs']+=[paneltext,replaytext]
 decision={'schema':'DEE.PI04.no_adoption.closed_gates.v1','decision':'NO_ADOPTION','adoption_performed':False,'reason':'Material prior-function regression blocks predefined conservation gate','principal':principal,'gate':info(panel),'candidate_full_pair':info(pair),'cold_replay':info(cold),'new_Native_ticks_by_finalizer':0,'operational_writes_by_finalizer':False}
 out['final_evidence']={'no_adoption_decision':'control/DECISION_NO_ADOPCION_PI04.json','conservation_regression':info(panel),'cold_replay':info(cold),'candidate_preservation':info(pair),'ACTIVO_reference':active,'current_VIDA':info(cardp),'current_snapshot':info(snapshot)}
 out['Native_budget_direct_record']={'source':info(P/'REGISTRO_CAMPANA.json'),'budget':budget['budget'],'new_Native_ticks_closed_floor':floor};out['unresolved_fields_must_be_filled_before_closed_true']=[]
 out['sources']+=[str(p.resolve())for p in[panel,pair,cold]];need(MARK not in json.dumps(out,ensure_ascii=False),'Closing marker remains');need(all(len(s['paragraphs'])<=12 for s in out['sections']),'Paragraph cap')
 for p,b in before.items():need(info(p)==b,'Input changed during passive finalization: '+p)
 out['final_evidence']['no_adoption_decision']=info(decisionp)
 diagp=P/'control/PI04_C2C_POSTPANEL_DIAG_CRUCE22_R01.json'
 if diagp.exists():
  diag=read(diagp);need(diag['owner_closed']is True and diag['completed']==diag['products']==1,'Closed post-panel diagnostic required')
  text='Una continuación diagnóstica separada del futuro T818074 completó el cruce 22: 29−4 produjo 25, que alimentó MU y la ruta positiva generó un archivo útil. Sus 186 entradas fueron aplicadas y llegó a T818365 en 291 ticks. El nuevo encadenamiento sigue utilizable pese a la comparación antigua regresiva; ese éxito no borra la regresión, no ocurrió sobre el principal y no autoriza adopción.'
  for section in out['sections']:
   if section['title'].startswith('47.8'):section['paragraphs'].append(text)
  out['compendium_paragraphs'].append(text);out['sources'].append(str(diagp.resolve()));out['final_evidence']['postpanel_diagnostic_not_principal']=info(diagp)
 incp=P/'control/INCORPORACION_MECANISMOS_PRODUCTO_PI04_JSON_R02.json'
 if incp.exists():
  inc=read(incp)
  text='Cognitive incorporó como mecanismos de producto el observador externo recalculable PI04_F1_OBSERVACION_EXTERNA_RECALCULABLE y la adquisición experimental reproducible PI04_C2C_ADQUISICION_EXPERIMENTAL_REPRODUCIBLE, con contrato PI04_OBSERVACION_Y_REPRODUCCION_01. El catálogo pasó de 120 a 122 entradas, con 0 ticks y conservación de los archivos críticos. Son instrumento y reproducción experimental con límites explícitos; no promoción de la candidata ni inserción de conocimientos en el principal.'
  for section in out['sections']:
   if section['title'].startswith('47.9'):section['paragraphs'].append(text)
  out['compendium_paragraphs'].append(text);out['sources'].append(str(incp.resolve()));out['final_evidence']['product_mechanisms_not_life_adoption']=info(incp)
 negp=P/'control/REGRESION_FIPLUS_REPLICA_CERRADA_R01.json';neg=read(negp)
 need(neg['Native_execution_by_Root']is True and neg['known_failure_reproduced']is True and neg['actual_total_Native_ticks']==2055,'Actual known-negative closed Native replay required')
 text='La regresión se reprodujo técnicamente desde el par completo T816019: dos trabajos útiles y los mismos seis usos del panel, 2055 ticks, 211 recibos de panel y las mismas seis respuestas. RAW, clocks, historia Native, interfaces y agenda finales coincidieron. Es una réplica técnica de prefijo compartido, no un segundo individuo independiente ni una prueba de causa única. La falla se conserva junto al positivo reproducido.'
 for section in out['sections']:
  if section['title'].startswith('47.8'):section['paragraphs'].append(text)
 out['compendium_paragraphs'].append(text);out['sources'].append(str(negp.resolve()));out['final_evidence']['known_negative_Native_replay']=info(negp)
 # Word-facing source locators stay short; full absolute paths/hashes remain in final_evidence.
 def source_label(value):
  q=Path(value)
  if not q.is_absolute():return value
  q=q.resolve()
  for base,prefix in [(P,''),(C/'reproducibilidad','DEE Cognitive 2.0/reproducibilidad/'),(R,'DEE thinking/')]:
   if q.is_relative_to(base):return prefix+q.relative_to(base).as_posix()
  return q.name
 out['sources']=list(dict.fromkeys(source_label(v)for v in out['sources']))
 targets=[(P/'control/CIERRE_CIENTIFICO_PI04.json',out)]
 if a.apply:
  need(all(not p.exists()for p,_ in targets),'Output exists; no overwrite')
  for p,j in targets:p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({'dry_run':not a.apply,'principal':principal,'decision':'NO_ADOPTION','closed_for_authoring':True,'outputs':[str(p)for p,_ in targets]},ensure_ascii=False,indent=2))
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');parser.add_argument('--comando',action='append');main(parser.parse_args())
