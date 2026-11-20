"""Recalculate bounded regulation profiles and exact adverse mechanism.

This script reads completed measurements only. None of its metrics or symbolic
branch reconstruction is used as the participant's policy or physical engine.
"""
from pathlib import Path
from collections import Counter
import hashlib,json,math
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rel(p):return p.relative_to(ROOT).as_posix()
def proof(p,scope):p=ROOT/p;return{'path':rel(p),'sha256':sha(p),'scope':scope}
def main():
 rows=[]
 for p in sorted((ROOT/'resultados/regulacion').glob('*/MEASUREMENTS.json')):
  d=load(p)
  if 'readings'in d:observations=d['readings'];criterion='correct_with_reference'if'correct_with_reference'in observations[0]else'correct'
  elif'rounds'in d:observations=d['rounds'];criterion='correct'
  else:continue
  flags=[bool(x[criterion])for x in observations];readings=[]
  for x in observations:
   pre=x.get('pre');post=x.get('post');readings.append({'tick':x['tick'],'correct':bool(x[criterion]),'reference':x.get('reference_pre',pre['reference']if pre else None),
    'object':x.get('object_pre',pre['object']if pre else None),'center':x.get('reading',post['center']if post else None),'auditor_expected_reference':x.get('expected_reference_auditor_only')})
  requests=d.get('inputs',[]);readreceipts=[r for r in requests if r['port']=='quantity.reader'];family='FBL_LONGITUDINAL'if p.parent.name.startswith('FBL_')else'FB3_NATIVE_FINITE_FEEDBACK'if p.parent.name.startswith('FB3_')else'RG_ACQUIRED_DIRECTION'if p.parent.name.startswith('RG_')else'PREVIOUS_FEEDBACK_DISCOVERY'
  rows.append({'case_id':d['case_id'],'family':family,'primary':proof(rel(p),'Actual finished originaltrajectory; not reexecuted by this audit'),'configuration':d.get('config'),
   'correct':sum(flags),'queries':len(flags),'per_query':readings,'reader_admission':dict(Counter(x['receipt']['status']for x in readreceipts)),
   'prepared_initial_material':d['geometry'].get('initial_material'),'host_RAW_clock_edits_on_MAIN':d.get('RAW_clock_edits_on_MAIN',[]),'final_physical':d['final']})
 diagnostic=load(ROOT/'resultados/regulacion/FBL_DIAG_R2/MEASUREMENTS.json');trace=load(ROOT/'resultados/regulacion/FBL_PROCEDENCIA7_R1/MEASUREMENTS.json')
 origin=trace['chain_backward'][-1];pre=origin['effective_pre_at_destination'];neighbors=origin['effective_pre_Moore26'];center=origin['destination']
 alive={tuple(((o['site'][k]-center[k]+33)%67)-33 for k in range(3)):o['state']>0 and o['semantic']!=5 for o in neighbors}
 tetra=[[(sx,0,0),(0,sy,0),(0,0,sz),(sx,sy,sz)]for sx in(-1,1)for sy in(-1,1)for sz in(-1,1)]
 hadron=any(all(alive.get(v,False)for v in pattern)for pattern in tetra);n=sum(alive.values());tension=16.0 if hadron and n<7 else 2.5;rho=n*tension/26;state=math.floor(rho+0.5)
 sums=[sum(o['direction'][k]for o in neighbors if o['state']>0 and o['semantic']!=5)for k in range(3)];protected=n>=7 and sums==[0,0,0];anchors=8-n;period=782//anchors if 0<anchors<=8 else None;clock=int(pre['clock']);increment=int(not protected and period is not None and clock%max(period,1)==0)
 gradient=origin['grad'];direction=[(x>0)-(x<0)for x in gradient]if pre['direction']!=[0,0,0]or pre['semantic']==5 else[0,0,0];payload=pre['s_reg']+increment
 def pack(e,s,v,semantic):return e|(s<<32)|sum(((v[i]&15)<<(48+4*i))for i in range(3))|(semantic<<60)
 material={'site':center,'pre':pre,'post_actual':origin['actual'],'n_active':n,'tetrahedral_hadron':hadron,'tension':tension,'rho_eff':rho,'rounded_rule_state':state,
  'sum_neighbor_directions':sums,'write_protected':protected,'clock_exact':str(clock),'period_if_missing_anchors':period,'clock_increment_to_payload':increment,'gradient':gradient,
  'derived_payload':payload,'derived_direction':direction,'derived_raw':str(pack(state,payload,direction,pre['semantic']or 1)),
  'matches_actual_record':pack(state,payload,direction,pre['semantic']or 1)==int(origin['actual']['raw']),
  'kernel_source':proof('genealogia/product45/kernel_v27.cpp','Materialprecedence/survival/clocks/momentum lines335–430; staticpost-runbranch reconstruction only'),
  'interpretation':'At270 an already present reader7(+Z), four observer supports, acquiredreference36(+Y) and zero-loadcue(−X) yield sixactive neighbors. The cue is physical even withload0. The native material branch emits7(+X)271 while the separate reference acquisition forms47 correctly. No current-object episode was scheduled271, but that does not prevent an internal expression.'}
 assert material['matches_actual_record']
 clocks=[e['intervention']['clock_preserved']for e in diagnostic['conditional_forks']];queues=[e['queue_equal_to_unaltered_pre']for e in diagnostic['conditional_forks']]
 output={'schema':'CPC8R.regulation.classification.audit.v1','profiles':{
  'R0_PREPARED':'Fixed on-path interceptors or externally scheduled counterflows realize a prepared filter by v27. Useful but not adaptation by experience.',
  'R1_ACQUIRED_STATE':'A postT0paired directional carrier changes which residual is neutralized under fixedopportunities. Opposite/unpaired/omitted histories and cut/sham separate its contribution.',
  'R1_NATIVE_FEEDBACK':'A native secondary comparisonproduct is physically transformed by allcandidate zero-load relays into another counterflow; its payload/direction is not computed/injected by Python. The relay geometry, timings and resources are fixed.',
  'R2_GENERAL_STRATEGY':'No general utility-trained selection of an attention/regulation strategy is accredited. A prepared policy and a state updated by actual experience remain distinct.'},
  'rows':rows,'R0_reference':proof('revision/CANTIDAD_ADQUIRIDA.json','Separate fixed-interceptor apparatus; preparedsupports/context differ from feedbackF3, so no unqualified resource-matched superiority claim'),
  'R1_reserves_and_cuts':proof('resultados/regulacion/RG_RESERVAS_CAUSALES/MEASUREMENTS.json','Twoacquired-directionreserves and explicitlatepulsecut/sham, no returntoMAIN'),
  'native_feedback_cuts':proof('resultados/regulacion/FB3_CAUSAL/MEASUREMENTS.json','Root-owned latepulse97cut/sham, nativefinitefeedbackcausality'),
  'longitudinal_adverse':{'primary':proof('resultados/regulacion/FBL_P01/MEASUREMENTS.json','Sevenactualquerywindows; firstthreecorrect, laterreference interference'),'first_reference_deviation':diagnostic['first_deviation'],
   'exact_replay204_to338_equal':diagnostic['unchanged_replay338_equal'],'parent_unchanged':diagnostic['parent_unchanged'],'base_unchanged':diagnostic['base_bytes_unchanged'],'all_cut_sham_clocks_preserved':all(clocks),'all_original_queues_preserved':all(queues),
   'causal_continuations':diagnostic['conditional_forks'],'primary_diagnostic':proof('resultados/regulacion/FBL_DIAG_R2/MEASUREMENTS.json','Firstreferencechange337andselectiveextraneous7cut/sham'),
   'source7_trace':{'primary':proof('resultados/regulacion/FBL_PROCEDENCIA7_R1/MEASUREMENTS.json','Exactdirected-inputbacktrace, no proximity/load-onlyancestry'),'certified_VOID_steps':sum(x['VOID_reducer_certified']for x in trace['chain_backward']),'material_origin270_to271':material,'ancestry_before_material_origin':'Not reconstructed as a unique entity; reader69Applied and laterreaderrejections are separately documented.'},
   'corrected_reading':'Reference update271 is47asdeclared, not54. A reader-derived7emitted271 traverses65certifiedempty-destinationsteps to336, then combineswith47into54at337. Cuttingonlythat7inadiagnosticforkpreserves47; shamconserves54. First338signcanagree despitecorruptoperand, so correctdirectionaloneisnotfunctionalretention.'},
  'limits':['FiniteF3success70/137/204doesnotestablishlongitudinalindefiniteclosedregulation.','Azero-loadformattingcuecanchange support/survival and thereforeemitnewphysicaltraffic.','Thelongitudinalrelayagendaomitsafter271althoughthereisnativeexpression271; thisisamethod-localcadence/accessobstacle,notaglobalkernelincapacity.','Thecutat336isanexternaldiagnostic,notanoperativeautonomousrepair.','FeedbackR1isaseparatecohortunlessanidentifiednewE1profilephysicallyintegratesitwithitsowncontrols.'],
  'source_sha256':sha(Path(__file__))}
 if(ROOT/'revision/REGULACION_POR_CONSECUENCIA_ANTECEDENTE.json').exists():output['exact_historical_consequence_policy_reference']=proof('revision/REGULACION_POR_CONSECUENCIA_ANTECEDENTE.json','SixexacthistoricalV2preparationsandfournewlateformedreturncut/shamforks; nativeconsequencechangesfinitepreparedpolicy, noarbitraryutilitystrategy orcurrentE1integration')
 if(ROOT/'revision/REGULACION_E1_FINITA.json').exists():output['distinct_finite_E1_R1']=proof('revision/REGULACION_E1_FINITA.json','NewseparatefreshN67E1profilewithacquireddirectionandfourdeclaredexternalmaintenanceexposures; preservedquantity4/4andjoint549; notIUEorR2general')
 put(ROOT/'revision/REGULACION_R0_R1_R2.json',output)
 lines=['# Regulación preparada, adquirida y realimentación nativa','',
  'La dirección adquirida por experiencia puede neutralizar un producto que interferiría con la referencia. La realimentación F3 consigue además transformar un producto nativo de comparación en el siguiente contraflujo, mediante cuatro etapas físicas de carga cero previamente declaradas. En su positivo y reserva de referencia17 conserva las tres primeras comparaciones, incluida la igualdad activa de dirección cero.','',
  'R0 designa el filtro preparado; R1, un estado o contenido adquirido que cambia su efecto bajo una arquitectura preparada. La trayectoria F3 sigue siendo finita: la geometría y las ventanas de los ocho recursos formateadores no se aprenden. No se acredita aquí una estrategia general R2 seleccionada por utilidad.','',
  '## Obstáculo longitudinal localizado','',
  'FBL_P01 acierta tres de siete ventanas bajo el criterio congelado de operandos y lectura, no sólo signo. La referencia36 se actualiza correctamente a47 en271. La primera corrupción ocurre337:47(0,+1,0) y7(+1,0,0) confluyen y producen54(+1,+1,0). La referencia corrupta aún puede dar el signo correcto338; eso no satisface el criterio de retención.','',
  'El7 procede del centro material271, certificado por65 pasos de transporte/reducción hasta336. En270 permanecía un lector7(+Z); cuatro soportes, referencia36 y señal de carga cero aportan seis vecinos activos. El gradiente(36,0,0) orienta ese lector hacia+X sin modificar su carga. Al mismo tiempo, la adquisición vecina sí forma47. Omitir una consulta programada no evitó una expresión interna; la agenda repetida no ofrecía relays para esa emisión271.','',
  'Un corte tardío sólo del7 en336 conserva47; el sham reproduce54. Los clocks, la cola y el padre se preservan. El replay204→338 es exactamente igual al snapshot primario. Son diagnósticos externos: no se devolvió una solución al MAIN ni se borró materia para presentar regulación continua.','',
  '## Evidencia y alcance','',
  'REGULACION_R0_R1_R2.json enlaza todos los positivos, controles, reservas y los intentos adversos F1/F2/FBL. Conserva recibos y denominadores; lectores136/203/... rechazados no cuentan como sondas nuevas aplicadas. Las causas anteriores a la rama material270→271 no se completan por igualdad de carga o proximidad. La tabla permite comparar este límite de cadencia sin convertirlo en un límite universal ni atribuir a la evolución la agenda preparada por el investigador.','']
 (ROOT/'revision/REGULACION_R0_R1_R2.md').write_text('\n'.join(lines),encoding='utf-8')
 print(json.dumps({'rows':len(rows),'material271_exact':material['matches_actual_record'],'first_deviation_tick':diagnostic['first_deviation']['tick'],'certified_source7_steps':output['longitudinal_adverse']['source7_trace']['certified_VOID_steps']}))
if __name__=='__main__':main()
