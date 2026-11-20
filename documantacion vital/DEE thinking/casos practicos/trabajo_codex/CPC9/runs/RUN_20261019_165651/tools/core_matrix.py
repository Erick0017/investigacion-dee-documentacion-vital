"""Forensic source coverage. Historical assertions are never fresh reproduction."""
from pathlib import Path
from collections import Counter
import hashlib,json
RUN=Path(__file__).resolve().parents[1];CORE=RUN/'core/DEE_COGNITIVE_CORE'
idx=json.loads((CORE/'documentacion/INDICE_MIEMBROS.json').read_text(encoding='utf8'))['paths']
old=RUN.parents[3]/'trabajo_codex/CPC8/runs/RECONSTRUCCION_20261019_002104'
ancestry=json.loads((old/'genealogia/MATRIZ_ANTECEDENTES_47.json').read_text(encoding='utf8'))
rows=[]
for original in ancestry['capabilities']:
 sources=[]
 for s in original.get('historical_source_identities',[]):
  proposed=['historico/'+(s.get('member')or''),'cpc8/'+(s.get('copied_as')or'')]
  recovered=next((n for n in proposed if n in idx and idx[n]['sha256']==s.get('member_sha256')),None)
  if recovered is None:recovered=next((n for n,r in idx.items()if r['sha256']==s.get('member_sha256')),None)
  sources.append({**s,'recovered_core_path':recovered,'byte_identity_verified':recovered is not None})
 row={'id':original['id'],'CPC_origin':original.get('group',original['id'].split('_')[0]),'mechanism':original.get('mechanism'),'domain':original.get('domain'),'controls':original.get('controls'),'limits':original.get('limits'),'historical_source_identities':sources,'source_bytes_recovered':all(s['byte_identity_verified']for s in sources),'source_count':len(sources),'current_recovery_status':'D','current_status_explanation':'Historical source/evidence preserved. The complete historical domain is not newly reproduced by presence in the product or by another apparatus.','integrated_in_CPC9_E1':False,'CPC9_integration_source':'Await root experimental result; no automatic promotion','original_row_unchanged':original}
 cid=original['id']
 if cid.startswith('CP01_C'):
  proof=RUN/'notes/core_audit/CP01_RECALCULADO.json'
  if proof.exists():
   v=json.loads(proof.read_text(encoding='utf8'));key='C08_INTERFACE_V2'if cid=='CP01_C08'else cid[-3:]
   r=next((q for q in v['cases']if q['field']==key),None)
   if r and r['measurement_equal']and r['all_full_RAW_clocks_tick_digests_equal']:
    row.update(current_recovery_status='C',current_status_explanation='Original source/inputs/positivecontrols/reserves reproduced onofficial4.5, neutralmeasurements and fullphysicalcheckpointdigests exact. CP01C07isderiveddiagnosisusingreproducedC05notanindependentnativepreparation.',recovery_proof='verificaciones/CP01_RECALCULADO.json',recovered_contract=r)
 if cid=='CP02_B':
  proof=RUN/'notes/core_audit/CP02_v1/RECOVERY.json'
  if proof.exists()and json.loads(proof.read_text())['status']=='PASS':row.update(current_recovery_status='B',current_status_explanation='Original predictor implementation on six newly prepared reserved-geometry paired/omitted/unpaired cases with prospectiveforecast and exactrestore; not the original maternalMAINtrajectory.',recovery_proof='verificaciones/CP02_RECOVERY.json')
 for family,ids in(('CPC7_v1',('CPC7_U0_CONTINUITY','CPC7_SELECTIVE_REVISION_M1_M2','CPC7_DIRECTIONAL_COMPOSITION_AND_POST_NAME')),):
  proof=RUN/'notes/core_audit'/family/'RECOVERY.json'
  if cid in ids and proof.exists()and json.loads(proof.read_text())['status']=='PASS':row.update(current_recovery_status='C',current_status_explanation='Four originalCPC7 finite0→472 contracts reproduced, fullbase338/final472state and receipts match. DoesnotintegrateentirehistoricalfamilyintoCPC9E1.',recovery_proof='verificaciones/CPC7_RECOVERY.json')
 additional_proofs={
  'SEM01':('SEM01_RECALCULADO.json','Siete realizaciones originales: historias opuestas, ausencia, desacoplamiento, acción omitida y dos reservas. Estado inicial/final, enseñanza y uso exactos. Los repr del host no son estado físico.'),
  'CPC4_AB':('CPC4_v1/RECOVERY.json','Cuatro realizaciones originales de la red A/B/C/D: filtro, ausencia, mismo aporte fuera de ruta y reserva. No se incorpora toda variante histórica de comunicación.'),
  'CPC4_REGULATION_ABCD':('CPC4_v1/RECOVERY.json','Contraflujo fijo preparado en aparato original N67; utilidad5 frente a4, sham4 y reserva5. No estrategia reguladora aprendida.'),
  'CPC5_COMPOUND':('CPC5_v1/RECOVERY.json','Siete realizaciones originales con reutilización y respaldos adquiridos: desacoplado, historia opuesta, no emparejado, corte/sham y reserva. La carga no mide profundidad conceptual.'),
  'CPC6_INTEGRATED':('CPC6_v1/RECOVERY.json','Cuatro vidas originales N67 T0–170, historia/comparación/acción/retorno/asociaciones y lector remoto. Rutas preparadas, no política general.'),
  'CPC6_TWO_FORMS':('CPC6_v1/RECOVERY.json','Cuatro protocolos word-bus originales con relación adicional y reexpresión tardía; controles no-repeat, nombre no emparejado e historia invertida.'),
  'PRODUCT45_PORT_VALIDATION':('PRODUCT45_v1/RECOVERY.json','68 regresiones técnicas de la API oficial. Se distinguen de los casos científicos originales y sus observaciones.'),
  'MBP4_CONTEXTUAL_REWRITE':('PRODUCT45_EXTRA_v1/RECOVERY.json','14 regresiones Basal/MBP4. Semillas/checkpoints históricos indispensables incluidos. Continuaciones y controles locales, no nuevo E1 entrenado.')}
 if cid in additional_proofs:
  name,scope=additional_proofs[cid];proof=RUN/'notes/core_audit'/name
  if proof.exists()and json.loads(proof.read_text())['status']=='PASS':row.update(current_recovery_status='C',current_status_explanation=scope,recovery_proof='verificaciones/'+name.replace('/','_'))
 rows.append(row)
new=[
 ('CPC8_MAIN_ORDER_CONTACT','Order/contact/nativejoin/opaqueformretention','FreshN67MCTS0→616','mcts'),
 ('CPC8_MAIN_QUANTITY_UPDATE','Actualacquiredreference36→47/native11addition/oldformuse','MCTS616finitepanel','mcts'),
 ('CPC8_CONTACT_SOCIAL','E1learnedcontact→nativecarrier→receiverlearns→lateruse','Bsimpleapparatus,finite554/559;notsecondcompleteE1','mcts'),
 ('CPC8_MAGNITUDE_SOCIAL','Separatelyexperiencedbackup→physicalmessage→Bacquiredreference','B36reference/actual18,45,31; noBlocalreferenceteacher','mcts'),
 ('CPC8_K65_PUBLISHED','65opaqueformcorrespondences/acquisition32+33/revision','N131separatefromN67MAIN','repertoire'),
 ('CPC8_RCA_REGULATION','Nativeactualconsequence→preparedcomparison/policy→regulator→lateraccess','Fresh72supportMCTS+addedRcomparator;notoriginal35world','rca'),
 ('CPC8_COUNT_SIGN','Normalizedcontactunit/B-onlysignretention/failedTWOoperativeaccess','Auxiliaryunit2threshold,notMCTSjointvocabulary','count'),
 ('CPC8_QFM_MOVING_FORM','Pastcomparisonword/movingmemoryremoteplanes','Auxiliarypreparedremoteinterface,notMORElexiconinMAIN','pending'),
 ('CPC8_L15_DIAGNOSIS','Acquiredrelation,transformedcarrierandaccessdissociation','L15delta16+7→23;originalreaderstillfailsaftercut','pending')]
for cid,mechanism,domain,family in new:
 proof=RUN/'notes/core_audit'/({'mcts':'MCTS_v1','repertoire':'K65_v1','rca':'RCA_v1','count':'COUNT_v1'}.get(family,'NOT_RUN'))/'RECOVERY.json'
 if family=='repertoire'and(RUN/'notes/core_audit/K65_RECALCULADO.json').is_file():proof=RUN/'notes/core_audit/K65_RECALCULADO.json'
 good=proof.exists()and json.loads(proof.read_text())['status']=='PASS'
 source_file={'mcts':'src/transferencia_magnitud/cts_integrado.py','repertoire':'base_validada/reproducir_repertorio65.py','rca':'src/regulacion_acoplada/mcts.py','count':'src/count_sign/branch_session.py'}.get(family,'src/cantidad_forma_movil.py'if cid=='CPC8_QFM_MOVING_FORM'else'src/diagnostico_l15_causal.py')
 logical='cpc8/'+source_file;source=idx[logical];proofname={'mcts':'MCTS_RECOVERY.json','repertoire':'K65_RECALCULADO.json','rca':'RCA_RECOVERY.json','count':'COUNT_RECOVERY.json'}.get(family)
 rows.append({'id':cid,'CPC_origin':'CPC8 reconstructed','mechanism':mechanism,'domain':domain,'controls':'Original stored matchingcontrols and reserves; pendinggroups notclaimedexecuted','current_recovery_status':'C'if good else'D','current_status_explanation':'Originalsource/nativeframes/receipts/finalstate reproduced'if good else'Source,configurationandprimaryterminalrecords preservedbycontenthash; currentcleanreproductionnotyetcomplete','source_bytes_recovered':True,'source_count':1,'historical_source_identities':[{'member':source_file,'member_sha256':source['sha256'],'bytes':source['bytes'],'recovered_core_path':logical,'byte_identity_verified':True,'source_archive_sha256':'4cf266a0ab968e26986a9935317ba146a8f769fc5717092470c4bead8983b8ed'}],'source_lookup':'documentacion/INDICE_MIEMBROS.json#'+logical,'recovery_proof':None if not good else'verificaciones/'+proofname,'integrated_in_CPC9_E1':False,'CPC9_integration_source':'No automaticpromotionfromhistoricalorauxiliaryworlds'})
result={'schema':'DEE_CORE.capabilities.forensic.v1','classification':{'A':'ReproducedandintegratedinCPC9E1','B':'Reproducedinauxiliaryfreshorganization','C':'Reproducedindividuallynotintegrated','D':'Documented/preservedpendingcleanreproduction','E':'Partialorconditioned','F':'Refutedornonreproducible'},'counts':dict(Counter(r['current_recovery_status']for r in rows)),'historical_rows':47,'additional_CPC8_rows':len(new),'rows':rows,'scope':'Classificationcountsarecapabilityprovenancerows,notuniqueconceptsorindependentindividuals. Broadhistoricaldomainsmayhaveonlyboundedcurrentrecovery.'}
# Additional original contracts were recovered after the first sealed candidate.
# These are bounded individual recoveries, never automatic integration in CPC9 E1.
extended={
 'CPC3_MAIN_AND_COMPARISON':(['CENTRAL_RECALCULADO.json','NATIVE_LOOP_RECALCULADO.json'],'Ocho casos originales de comparación central y ocho de bucle nativo: historia, informes, corte, omisión y reservas. Se comparan todos los observables primarios originales; las anotaciones pasivas posteriores se conservan por separado. No existía un digest histórico del mundo completo para esta familia.'),
 'CPC3_POLICY':(['POLICY_RECOVERY.json'],'Ocho realizaciones originales R14 de política finita: historias opuestas, verdad ±, corte de acción, ausencia y reservas trasladadas. Coinciden trazas locales y recibos. No se generaliza esta recuperación al dominio completo de Ingeniería01.'),
 'CPC5_CAPACITY65':(['CAPACITY_RECOVERY.json'],'Cuatro aparatos originales CPC5 de 65 correspondencias físicas: emparejado, desacoplado, evento omitido y nueva historia/carga reservada. Tres rondas, estado final completo y estado operativo exactos. No son 65 significados NSM.'),
 'CPC5_LONGITUDINAL65':(['LONGITUDINAL_RECOVERY.json'],'Dos vidas originales: adquisición32+33, con consulta temprana y sin ella; continuidad, consultas posteriores y restauración. No se suman sus aprendizajes como un individuo.'),
 'CPC5_ORDER_AND_DIALOGUE':(['ORDERED_RECALCULADO.json','STREAM_RECOVERY.json','NETWORK_RECOVERY.json'],'Diecinueve realizaciones originales: composición AB/BA, cortes y sham, intervalos y referentes reservados, red de roles A1/A2/A4. La comparación física es exacta; el indicador documental antiguo de metadata de restauración se contrasta aparte y actualmente es verdadero.'),
 'CPC6_RETENTION_CAUSAL':(['RETENTION_EARLY_RECOVERY.json','RETENTION_WORD_RECOVERY.json','RETENTION_LATE_RECOVERY.json'],'Dieciocho forks/continuaciones diagnósticos desde ocho checkpoints históricos exactos: cortes y sham de portador tardío, delta relativa, acceso alternativo y dosis. Incluye clocks/colas originales. No son dieciocho individuos nuevos ni aprendizaje de CPC9 E1.'),
 'CPC6_ARCHITECTURES':(['ARCHITECTURES_RECOVERY.json','BRIDGE_RECOVERY.json'],'Seis cribados originales de uno/dos/cuatro participantes y cuatro puentes de memoria relativa/móvil. Se conserva la contribución desigual de recursos; no demuestra superioridad por número de compuestos.'),
 'CPC7_PREPARED_DISCREPANCY_REQUEST':(['NEED_RECOVERY.json'],'Siete aparatos originales N67: pregunta física condicionada por comparación, historia opuesta, fuente omitida, expectativa no adquirida, corte y sham del mensaje y reserva. Oportunidad y rutas preparadas; no curiosidad general.'),
 'CPC7_ABSENCE_APERTURE':(['MISSING_RECOVERY.json'],'Seis aparatos originales del perfil de ausencia v2: ausencia, coincidencia, discrepancia, fuente vacía, fallo del lector e historia opuesta reservada. No se fusiona automáticamente con el U0 de discrepancia.'),
 'CPC8_QFM_MOVING_FORM':(['QFM_RECOVERY.json'],'Cinco mundos originales: historia comparativa, signo omitido/desacoplado y nueva referencia/señal. Forma conservada en memoria móvil y tres planos remotos140/207/274. El acceso instrumental está preparado, no selección de lector aprendida.'),
 'CPC8_L15_DIAGNOSIS':(['L15_RECOVERY.json'],'Seis continuaciones diagnósticas del checkpoint históricoT78: delta16, aporte7, soporte transformado23, cortes/sham y lector alternativo. Se conserva el padre sin intervención. Pérdida de acceso original no equivale a destrucción del contenido.'),
 'CPC8_CONTACT_SOCIAL':(['SOCIAL_RECOVERY.json','MCTS_RECOVERY.json'],'Cuatro vidas CTS originales con sus19fuentes ejecutadas exactas y tres diagnósticos de mensaje formado: corte/sham/contenido modificado de igual carga. E1 adquirido→portador v27→adquisición de B→uso posterior. B es receptor simple, no segunda mente completa; dirección y ruta no se disocian totalmente.')}
for row in rows:
 if row['id'] in('CORE06_RELEARNING','CORE07_REPROGRAMMING'):
  family='CORE06'if row['id']=='CORE06_RELEARNING'else'CORE07';proof=CORE/'verificaciones'/(family+'_RECOVERY.json')
  if proof.is_file()and json.loads(proof.read_text(encoding='utf8'))['status']=='PASS':
   row.update(current_recovery_status='C',current_status_explanation=('Panel original completo de134realizaciones:25transferencias entrenadas/100controles,4extinciones y5reversiones/reaprendizajes.'if family=='CORE06'else'Panel original congelado completo de144realizaciones en cuatro celdas:48positivas/96negativas de reprogramación.')+' Fuentes y observaciones locales originales exactas. Adaptador de transición4.5 para arrays directos con escrituras instrumentales explícitas; no colas Runtime históricas. NumPy2.2.6 es dependencia opcional declarada. Los estados completos NUEVOS del portado se conservan aparte de los hashes históricos globales no disponibles.',recovery_proof=['verificaciones/'+family+'_RECOVERY.json','verificaciones/'+family+'_PRIMARY_TRANSITIONS.json'],modality='native physical transition / instrumented direct-state import; independent auxiliary worlds')
 if row['id'] in('CORE15_OBSERVER_SHADOW','CORE16_OBSERVER_INFORMATION','CORE17_COMPRESSED_OPERATOR_AND_REPAIR'):
  row['historical_data_recalculation']={'proof':'verificaciones/CORE15_17_RECALCULADO.json','status':'RECALCULATED_NOT_NATIVE_RERUN','effect_on_recovery_class':'Remains D; hashes and denominator congruence do not replace a fresh native reproduction.','source_index_prefix':'cores/CORE'+row['CPC_origin'][-2:]+'/'}
 if row['id'] in extended:
  names,scope=extended[row['id']]
  files=[CORE/'verificaciones'/name for name in names]
  if all(p.is_file()and json.loads(p.read_text(encoding='utf8'))['status']=='PASS'for p in files):
   row.update(current_recovery_status='C',current_status_explanation=scope,recovery_proof=['verificaciones/'+name for name in names])
 if row['id']=='CPC8_CONTACT_SOCIAL':
  proof=CORE/'verificaciones/INITIAL_CPC8_RECOVERY.json';good=proof.is_file()and json.loads(proof.read_text(encoding='utf8'))['status']=='PASS'
  row['additional_preserved_implementation']={'id':'CPC8_INITIAL_SOC_I21_N131','archive_sha256':'65164c939621464c7d4faa800240bb1c2e25538ba9d878a65863016f57387c00','source_prefix':'cpc8_inicial/','status':'C'if good else'D','proof':'verificaciones/INITIAL_CPC8_RECOVERY.json'if good else None,'scope':'Primer CPC8: aparato N131 continuo T0–1182, repertorio propio de formas, L17→adquisición social→uso posterior B, revisión L01 y controles fuera de ruta. Continúa el SOC_I21 regenerado para adquirir RIGHT y usarlo posteriormente; retiene 63/63 asociaciones en T1051. Cuatro historias originales y cinco continuaciones/ramas se identifican por separado; no son nueve individuos independientes ni el mismo aparato N67 MCTS posterior.'}
result['counts']=dict(Counter(r['current_recovery_status']for r in rows))
(CORE/'documentacion/MATRIZ_CAPACIDADES.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
missing=[{'id':r['id'],'missing':[s for s in r.get('historical_source_identities',[])if not s['byte_identity_verified']]}for r in rows if not r.get('source_bytes_recovered',False)]
(RUN/'notes/core_audit/COBERTURA_Y_HUECOS.json').write_text(json.dumps({'capabilities':len(rows),'missing_primary_source_bytes':missing,'classification_counts':result['counts'],'automatic_E1_integration':0},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'rows':len(rows),'missing_source_rows':len(missing),'counts':result['counts']}))
