"""Assemble the private thin PC01 analysis from existing immutable records.

No native import, simulation, retargeting or semantic verdict generation.
"""
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
import argparse,json,hashlib,shutil,csv,sys,tarfile,io
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--evidence',type=Path,required=True);p.add_argument('--lab',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();root=a.system.parent;ev=a.evidence;lab=a.lab;dest=a.out;dest.mkdir(parents=True,exist_ok=False)
def sha(b):return hashlib.sha256(b).hexdigest()
def write(name,value):
    path=dest/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def copy(path,name):
    target=dest/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
def table(name,rows,fields=None):
    path=dest/name;path.parent.mkdir(parents=True,exist_ok=True)
    if fields is None:fields=list(rows[0])if rows else['sin_registros']
    with path.open('w',encoding='utf-8-sig',newline='')as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
def raw(v):
    n=int(v['raw']);s=lambda k:((n>>k)&15)-16 if((n>>k)&15)&8 else(n>>k)&15
    return{'state':n&0xffffffff,'semantic':n>>60,'s_reg':(n>>32)&65535,'direction':[s(48),s(52),s(56)]}
def valid(v,d):
    r=raw(v);return r['state']==1 and r['semantic']==1 and r['direction']==list(d)
def words(q):
    v=q.get('SPANISH_DECODED',q.get('TRADUCCION',{}).get('SPANISH_DECODED',[]));return sorted(set(r.get('text')if isinstance(r,dict)else r for r in v))
def pointer(obj,path):
    for step in path.strip('/').split('/')if path else[]:obj=obj[int(step)]if isinstance(obj,list)else obj[step.replace('~1','/').replace('~0','~')]
    return obj

data_folder=ev/'EMPAQUETADO_DATOS_48/main';data_index=json.loads((data_folder/'INDICE_REGISTROS.json').read_bytes());copy(data_folder/'REGISTROS_COMPLETOS.tar.xz','EVIDENCIA_ESENCIAL/REGISTROS_COMPLETOS.tar.xz');copy(data_folder/'INDICE_REGISTROS.json','EVIDENCIA_ESENCIAL/INDICE_REGISTROS.json')
for name in('INFORME_RESULTADOS.md','CAMBIOS_INCORPORADOS.md'):copy(lab/name,name)
for name in('recalcular_analisis.py','extraer_registros.py','calcular_hallazgos_01.py','instrumentos_pc01.py','agenda_binaria_pc01.py','admisiones_y_linajes_21.py','analizar_retencion_nueva_38.py','analizar_acontecimientos_26.py','interferencia_basal_23.py'):copy(lab/name,'CODIGO_Y_RECALCULO/'+name)
copy(lab/'FLUJOS_DE_INFORMACION.md','CODIGO_Y_RECALCULO/FLUJOS_DE_INFORMACION.md')
copy(root/'ADDENDUM_MANUAL_MAESTRO_EF01_PAISAJE01_EDICION_1_1.md','ADDENDUM_MANUAL_MAESTRO_EDICION_1_1.md')
copy(a.system/'contratos/PAISAJE_CAUSAL_01.json','CODIGO_Y_RECALCULO/CONTRATO_PAISAJE_CAUSAL_01.json');copy(a.system/'capacidades/NSM65_ACTUALIZACIONES_PAISAJE_01.json','NSM65_CAMBIOS_AFECTADOS.json');copy(ev/'RECALCULO_FINAL_DATOS_49.json','ATLAS_CAUSAL/RECALCULO_DATOS.json');copy(ev/'CALCULOS_PROVISIONALES.json','ATLAS_CAUSAL/CALCULOS_CAUSALES.json')
for name in('ADMISIONES_Y_LINAJES_21.json','CAUSAS_DETALLADAS_13.json','INTERFERENCIA_BASAL_23.json','ACONTECIMIENTOS_SIN_PALABRA_26.json','CONTINUIDAD_Y_NUEVO_LIMITE_28.json','RETENCION_NUEVA_Y_LECTOR_38.json'):
    if(ev/name).exists():copy(ev/name,'ATLAS_CAUSAL/'+name)
for path in sorted(lab.glob('INCIDENTE*.md')):copy(path,'CODIGO_Y_RECALCULO/incidentes/'+path.name)
for src,name in((ev/'ACCESO_TRAYECTO_LIBRE_19/trace_events/PRE_SNAPSHOT_NATIVE_DIAGNOSTIC_ONLY.deetsnap.gz','T26165_NATIVO_SOLO_DIAGNOSTICO.deetsnap.gz'),(ev/'SEGUNDO_ENCUENTRO_LIBRE_32/full/PRE_NATIVE_DIAGNOSTIC_ONLY.deetsnap.gz','T32597_NATIVO_SOLO_DIAGNOSTICO.deetsnap.gz')):
    if src.exists():copy(src,'EVIDENCIA_ESENCIAL/'+name)

recalc=json.loads((ev/'RECALCULO_FINAL_DATOS_49.json').read_bytes());cases=[];trials=[];cards=[];comparisons=[];quick=[];current_lives={};selected={};original_index={r['source_relative']:r for r in data_index['members']}
quick_plan={
 'ACCESO_TRAYECTO_LIBRE_19/trace_events':['/first_nominal_departure'],
 'SEGUNDO_ENCUENTRO_LIBRE_32/full':['/first_departure'],
 'INTEGRACION_MAGNITUD_25/paired_guard':['/new_experience','/magnitude/4','/spatial/0','/old/1'],
 'LECTOR_POST_TRANSFORMACION_41/full':['/lesson','/transformed','/reader','/action','/requests'],
 'LECTOR_POST_TRANSFORMACION_41/sham':['/transformed','/reader','/action'],
 'LECTOR_POST_TRANSFORMACION_41/no_word':['/transformed','/reader','/action'],
 'LECTOR_POST_TRANSFORMACION_41/no_A':['/transformed','/reader','/action'],
 'CONTEXTO_UTIL_MIXTO_44/cut':['/old_collision_site','/reader','/action','/old_reader'],
 'CONTEXTO_UTIL_MIXTO_44/uncut':['/old_collision_site','/reader','/action','/old_reader'],
 'CONSERVAR_NUEVA_ASOCIACION_40/guard':['/lesson','/reserved/0','/reserved/5','/reserved/10','/reserved/11','/old_after'],
 'CONSERVAR_NUEVA_ASOCIACION_40/guard_sham':['/reserved/0','/reserved/5'],
 'CONSERVAR_NUEVA_ASOCIACION_40/no_word_cue':['/reserved/0'],
 'CONTINUIDAD_NORMALIZADA_45/main':['/operations','/new_process_after_save']}
for path in sorted(ev.glob('*/*/PRIMARIOS.json')):
    key='/'.join(path.parts[-3:-1])
    if key not in recalc['cases']:continue
    v=json.loads(path.read_bytes());metric=recalc['cases'][key];parent=v.get('parent');parent_rec=parent if isinstance(parent,dict)else{};initial=v.get('pre',{});initial=initial if isinstance(initial,dict)else{};post=v.get('post',{});post=post if isinstance(post,dict)else{};n=v.get('N',post.get('N',initial.get('N',parent_rec.get('physical',{}).get('N'))));life=v.get('life');kind='INSTRUMENTO_EXISTENTE_ESTADO_PASIVO'if key.startswith(('INDICE_ESTADOS_COMPLETOS_47/','AGENDAS_Y_CANALES_20/','OBSERVACION_02/'))else'PRUEBA_TECNICA_DE_INTERFAZ'if key.startswith(('API_','CONTINUIDAD_NORMALIZADA_45/'))else'DIAGNOSTICO_COPIA_INTERVENIDA'if key.startswith('COALESCENCIA_DIAGNOSTICA_22/')else'ENSAYO_FISICO_O_REPRODUCCION_IDENTIFICADA'
    config={k:v[k]for k in('criteria_before','scope_before','reserved_before','definition','scope','type','schedule','reserve','current_values','fixed_calendar','event','actual_curriculum')if k in v};entry={'id':key,'life':life,'parent':{k:parent_rec.get(k)for k in('life_id','snapshot_sha256','profile')}if parent_rec else parent,'kind':kind,'N':n,'tick_initial':metric['tick_initial'],'tick_final':metric['tick_final'],'source_primary_member':'primarios/'+path.relative_to(ev).as_posix(),'source_primary_sha256':sha(path.read_bytes()),'executed_driver_sha256':v.get('source_sha256'),'configuration_and_frozen_criteria':config,'admissions':metric.get('admission_accounting'),'recalculated_metrics':{k:metric[k]for k in('dose_current_correct','dose_current_total','magnitude_current','transformed_reader')if k in metric},'no_global_cognitive_verdict':True};cases.append(entry)
    for category in('dose_current','legacy_current','magnitude_current'):
        for j,q in enumerate(metric.get(category,[])):
            trials.append({'case':key,'life':life,'trial_kind':category,'locator':q.get('locator'),'actual_parameter':q.get('parameter',q.get('actual_magnitude')),'dose':q.get('dose'),'native_decoded_words':' | '.join(q['words']),'standard_task_correct':q.get('standard_task_correct','NOT_SCORED_AS_UNIVERSAL'),'physical_presentations':q.get('physical_presentations',''),'primary_sha256':entry['source_primary_sha256']})
    if 'worlds'in v and isinstance(v['worlds'],dict):
        for name,w in v['worlds'].items():cards.append({'experiment':key+'/'+name,'identity':w['identity'],'classification':'Organización simple de transporte e interacción; no mente completa','prepared':'Dominio, interfaces y oportunidadesH/I; sin materia objetivo en T0','acquired':'Influencia H conservada y efecto posterior de I, según factorial. No palabras objetivo.','host_decides':'Sitios/tiempos/condiciones; el resultado se produce por v27','boundary':'Whole toroidalRuntime; one differentRuntime per listedworld','primary_member':entry['source_primary_member'],'control_identity':name,'same_history_until_contrast':v.get('before_I_pair_equality'),'no_language_or_autonomy_claim':True})
    elif life or n:
        classification='Organización especializada de asociaciones opacas'if key.startswith('ESPECIALISTA')else'Nueva preparación especializada de referencia más asociación auxiliar'if key.startswith('ESCALA')else'Organización simple con receptor material auxiliar'if key.startswith('RETORNO_UTIL')else'Compuesto funcional N67 con historia y regiones/receptores; autonomía de regiones no establecida'
        cards.append({'experiment':key,'life':life,'parent':entry['parent'],'profile':parent_rec.get('profile','Native research preparation when no Storeprofile applies'),'Runtime':'One full world per branch; multiple views do not duplicate matter','N':n,'initial_tick':metric['tick_initial'],'classification':classification,'classification_criterion':'Physical co-location, actual channels and tested functional dependencies; not connected-component count or a human anatomy analogy','components_tested':{'magnitude_uses':len(metric['magnitude_current']),'context_uses':len(metric['dose_current'])+len(metric['legacy_current']),'communication_mentioned_in_primary':'communication'in v,'other_old_functions_measured':list(v.get('old_after',{}))},'prepared':'Geometry, external interfaces, timing, supplies, fixed readers/guards and teaching opportunities are investigator resources; exact configurations/source bytes included','history_and_current_knowledge':'Use measured native records/locators, not phase metadata or catalog membership; failures and unanswered cases retained','can_change_natively':'RAW, clocks, encounters, directions, supports, routes and downstream functions within fixed N','host_decides':'Curriculum, introduced events, fixed teacher/word codes, access opportunities, preparations, branch and participant selection','boundary':'Whole toroidalworld considered; nominal ports do not enclose all memory. Environmental inputs are explicit.','external_runtime_bridge':False,'basic_native_buffers_bytes':32*n**3 if isinstance(n,int)else None,'primary_member':entry['source_primary_member']})
    else:
        cards.append({'experiment':key,'classification':'Instrumental/passive or explicit native-copy diagnostic; no new learned organism claimed','kind':kind,'inspected_state_ids':list(v.get('states',{}))or list(v.get('parents',{})),'N':'Use the indexed complete source state/native header; not inferred from a role name','boundary':'All fields/queues represented by the actual inspected snapshot, not a new empty world','host_decides':'Inspection or explicit diagnostic intervention, never a policy attributed to the source life','primary_member':entry['source_primary_member']})
    if key in quick_plan:
        for ptr in quick_plan[key]:
            value=pointer(v,ptr);b=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode();quick.append({'primary_member':entry['source_primary_member'],'primary_sha256':entry['source_primary_sha256'],'json_pointer':ptr,'canonical_extracted_value_sha256':sha(b),'kind':'EXACT_VALUES_EXTRACTION_NOT_ORIGINAL_SERIALIZATION_BYTES','value':value})
    if key=='INDICE_ESTADOS_COMPLETOS_47/passive':current_lives=v['current_lives']
    if key.startswith(('ESCALA_CANTIDAD_10_R1/','ESCALA_CANTIDAD_10_R1_RESTO/')):
        scored=[]
        for q in v['rounds']:
            sign=(86>q['actual_object'])-(86<q['actual_object']);ok=valid(q['comparison'],(sign,0,0));scored.append({'round':q['round'],'tick':q['tick'],'actual':q['actual_object'],'correct':ok,'native':raw(q['comparison'])})
        comparisons.append({'experiment':key,'architecture':'SpecializednewT0quantityN'+str(n),'N':n,'question':'10matchedorbitalopportunities; noE1transplant','functional_correct':sum(r['correct']for r in scored),'functional_total':len(scored),'first_failure_tick':next((r['tick']for r in scored if not r['correct']),''),'other_function':'Auxiliary association later queried; raw recorded even if comparison fails','resources':str(32*n**3)+' basicbufferbytes; actualinputs in primary','limits':'Nchangesphase/calendar/returntime, not merely free volume','primary_member':entry['source_primary_member']})
        write('ATLAS_CAUSAL/ESCALA/'+key.split('/')[-1]+'.json',scored)
    if key.startswith('PROTECCION_BIDIRECCIONAL_33/'):
        samples=v['blocks'];m=[q['magnitude']for q in samples]+[v['final']['less'],v['final']['more']];sp=[q['spatial']for q in samples]+[v['final']['near'],v['final']['far']];c=[q['contact']for q in samples if'contact'in q]+[v['final']['contact']];fr=[q['free']for q in samples if'free'in q]+[v['final']['free']]
        scores={'magnitude':[sum(words(q)==(['menos']if q['ENTORNO']['actual_object_magnitude']<86 else['más'])for q in m),len(m)],'spatial':[sum(words(q)==(['cerca']if q['actual_parameter']>0 else['lejos'])for q in sp),len(sp)],'contact':[sum(words(q)==['toca']for q in c),len(c)],'free':[sum(words(q)==['no toca']for q in fr),len(fr)]}
        row={'experiment':key,'architecture':'SamecompleteN67parent; '+v['case'],'N':67,'question':'Nativeoppositesideguard/diversionvsitsmaterialsham','functional_correct':'NOT_AGGREGATED_DIFFERENT_FUNCTIONS','functional_total':'See per-function panel','first_failure_tick':'Seeindividualcategories; noopaquecombinedwinner','other_function':json.dumps(scores,ensure_ascii=False),'resources':'12blocks536ticks=96returnopportunities; fixednativezero-loadintervention','limits':'P0; finitewindow, notP2orindefinitestability','primary_member':entry['source_primary_member']};comparisons.append(row);selected[key]=scores

executions=[]
for path in sorted(ev.glob('*/EJECUCION.json')):
    doc=json.loads(path.read_bytes())
    for case in doc['cases']:
        primary=ev/path.parent.name/case['case']/'PRIMARIOS.json';executions.append({'batch':path.parent.name,**case,'primary_exists':primary.exists(),'scientific_result_not_inferred_from_exit_code':True})
write('ENSAYOS_Y_CONTROLES.json',{'cases_with_primary':cases,'execution_records_including_instrumental_failures':executions,'primary_records_are_not_independent_individuals':True,'frozen_design_and_actual_source_bytes_index':'CODIGO_Y_RECALCULO/REVISIONES.json','complete_negative_records_retained':True})
table('TABLA_TODOS_LOS_USOS.csv',trials,['case','life','trial_kind','locator','actual_parameter','dose','native_decoded_words','standard_task_correct','physical_presentations','primary_sha256']);table('COMPARACION_ARQUITECTURAS.csv',comparisons)
write('FICHAS_ENTES.json',{'definition':'Physical/functional classification, not an ontology of conscious individuals','common_engine':'Official4.5kernel27unchanged','cards':cards,'current_complete_states':current_lives,'wholeworld_checkpoint_once_perRuntime':True,'auxiliary_functions_not_summed_into_main':True})
write('EVIDENCIA_ESENCIAL/EXTRACTOS_DECISIVOS.json',{'notice':'Readable extracted values for first review. Full original JSON bytes and their hashes remain in the indexed data archive.','extractions':quick})
write('ATLAS_CAUSAL/PANEL_R33_POR_FUNCION.json',selected)

# Preserve every relevant executed revision by content, not only a hash.
objects=dest/'CODIGO_Y_RECALCULO/objetos';objects.mkdir(parents=True);revisions=[];seen_objects=set()
def relevant(path):
    low=str(path).lower().replace('\\','/');base=str(a.system).lower().replace('\\','/');prefix=str(lab).lower().replace('\\','/')
    return low.startswith(prefix+'/')or low.startswith(base+'/app/')or low.startswith(base+'/organizaciones/cpc9/')or(low.startswith(base+'/capacidades/')and'/core/'not in low)or low==base+'/gestionar.py'
for manifest in sorted(ev.glob('*/FUENTES_EJECUTADAS.json')):
    content=json.loads(manifest.read_bytes());subset={}
    for name,info in content['sources'].items():
        if not relevant(Path(name)):continue
        original=Path(info['object']);b=original.read_bytes();h=sha(b)
        if h!=info['sha256']:raise ValueError('Frozen executed source hash mismatch')
        if h not in seen_objects:(objects/(h+'.py')).write_bytes(b);seen_objects.add(h)
        subset[name]={'sha256':h,'object':'objetos/'+h+'.py','bytes':len(b)}
    revisions.append({'batch':manifest.parent.name,'original_manifest_sha256':sha(manifest.read_bytes()),'driver':content['script'],'captured_sources_not_a_claim_every_source_was_executed':True,'relevant_source_bytes':subset,'full_original_manifest_in_data_archive':True})
current_sources={}
for path in sorted(set(lab.glob('*.py'))|set((a.system/'app').glob('*.py'))|set((a.system/'capacidades').glob('*.py'))|set((a.system/'organizaciones/cpc9').rglob('*.py'))|{a.system/'gestionar.py'}):
    b=path.read_bytes();h=sha(b)
    if h not in seen_objects:(objects/(h+'.py')).write_bytes(b);seen_objects.add(h)
    current_sources[str(path)]={'sha256':h,'object':'objetos/'+h+'.py','bytes':len(b),'role':'CURRENT_SOURCE_NOT_AN_AUTOMATIC_PHYSICAL_VALIDATION'}
for h in('c5b981891257a7f1f8da91f537943f1245f8815e6b2c6ea9ca9fd1848b170405','76ce1ec9b7ee38a656046badf6919025c6f57869f96974f4313f20cdce015cb3','055039447614a38a3b45d03807fc835343adda9d1a0dbfdc5bf690b00ab41a35'):
    path=lab/'versiones_codigo/objetos'/(h+'.py')
    if path.exists():copy(path,'CODIGO_Y_RECALCULO/revisiones_fallidas_preservadas/'+h+'.py')
write('CODIGO_Y_RECALCULO/REVISIONES.json',{'executed_batches':revisions,'current_sources':current_sources,'objects_count':len(seen_objects),'engine_source_and_binary_intentionally_not_included':True})

calc=json.loads((ev/'CALCULOS_PROVISIONALES.json').read_bytes());atlas=calc['global_atlas'];global_rows=[];sites=[]
for name,q in atlas.items():
    global_rows.append({'trace':name,'source_gzip_sha256':q['source_sha256'],'N':q['N'],'frames':q['sampled_frames'],'tick_first':q['timeline'][0]['tick'],'tick_last':q['timeline'][-1]['tick'],'occupied_min':q['min_occupied'],'occupied_max':q['max_occupied'],'state0_RAW_nonzero_max':q['max_state_zero_raw_nonzero'],'visited_in_sampled_frames':q['visited_sites_in_sampled_frames'],'ballistic_candidate_events':q['encounter_candidate_events'],'coverage':q['coverage']})
    for key,count in q['encounter_sites']:
        x,y,z=map(int,key.split(','));sites.append({'trace':name,'x':x,'y':y,'z':z,'candidate_count':count,'not_all_native_encounters':True})
table('ATLAS_CAUSAL/COBERTURA_Y_OCUPACION.csv',global_rows);table('ATLAS_CAUSAL/CONCENTRACION_CANDIDATOS.csv',sites)

budget=json.loads((ev/'ARRANQUE_01/PRESUPUESTO.json').read_bytes());identity=json.loads((ev/'ARRANQUE_01/ESTADO_INICIAL.json').read_bytes())['identity'];chosen=['E1_SOCIAL_11','E1_ESPANOL_01','ES01_LATE_ACCESS29_passive','E1_PAISAJE_01','PC01_CONTINUIDAD28_far_guard','PC01_CONTINUIDAD28_far_divert','PC01_RETENCION40_guard','PC01_RETENCION40_divert','PC01_NORMALIZADO45'];lives={name:current_lives[name]for name in chosen if name in current_lives}
continuity={'schema':'DCS1.1.PC01.continuity.v1','software':'1.1.0','engine_identity_at_start':identity,'protected_default':'E1_SOCIAL_11','recommended_by_task':{'wide_current_functions':'PC01_CONTINUIDAD28_far_guard or far_divert','new+1current_with_documented_losses':'PC01_RETENCION40_guard or divert','assisted_acquired_code_and_other_functions':'PC01_NORMALIZADO45'},'failed_main_future_preserved':'E1_PAISAJE_01 T44300','lives':lives,'latest_operation':'Actual CLI continuation45; no hidden recreation or re-teaching','normalizer_limit':'PreparedXcontribution plus acquiredhistory; recall/use, not demonstrationofcurrent+1spatialtruth','required_files':'Existing system code, official installedengine and the exact complete snapshot identified per-life; not arrays extracted from this analysis','next_task':'Chooseoneexplicitcompletebranchandtestoneadditionaluse/experiencewithoutreapplyingnormalizationorrewinding. Preserveanyfailure; pending-1/P2are not certified.','budget':budget,'automatic_future_resume_authorized':False,'analysis_package_is_not_operational_backup':True};write('CONTINUIDAD_PAISAJE_CAUSAL_01.json',continuity)

source_inventory=[]
for path in sorted((lab/'fuentes_dirigidas').glob('*.json')):
    doc=json.loads(path.read_bytes());source_inventory.append({'extract_local_path':str(path),'extract_sha256':sha(path.read_bytes()),'original_reference_metadata':{k:v for k,v in doc.items()if k not in('paragraphs','text','tables','body')},'access':'Actually extracted and directed relevant sections read; not a claim of linearly reading the entire corpus','original_document_not_redistributed':True})
omitted=[]
for base in(ev,lab):
    for path in sorted(base.rglob('*')):
        if not path.is_file()or'__pycache__'in path.parts or'versiones_codigo'in path.parts or'EMPAQUETADO_DATOS_48'in path.parts:continue
        rel=path.relative_to(base).as_posix();sourcekey=rel if base==ev else None
        if sourcekey in original_index:continue
        role='OPERATIONAL_OR_DIAGNOSTIC_SNAPSHOT_RETAINED_LOCALLY'if path.name.endswith('.deetsnap.gz')else'LOCAL_DERIVED_OR_SUPPORT_SOURCE_NOT_AN_UNIQUE_OMITTED_TRIAL'
        if path.suffix in('.json','.gz','.md','.py','.txt')or path.name.endswith('.log'):omitted.append({'path':str(path),'bytes':path.stat().st_size,'sha256':sha(path.read_bytes()),'role':role})
write('INDICE_FUENTES_Y_OMISIONES.json',{'data_archive_index':'EVIDENCIA_ESENCIAL/INDICE_REGISTROS.json','all_recorded_primary_JSON_bytes_and_trace_payloads_preserved':True,'gzip_original_containers_local_but_payloads_exact_in_archive':True,'sources_directed':source_inventory,'requested_45_docs_not_located_in_directed_search':['DEE_thinking_4_5_0_Libro_Blanco_y_Manual_Tecnico.docx','DEE_thinking_4_5_0_Maestro_Arquitectura_Reconstruccion.docx'],'fallback':'Installed4.5executablecontracts/source and verified officialidentity, withavailabletheorydocuments','no_historical_conversation_access_claim':True,'local_additional_files':omitted,'full_CPC_archives_engine_whl_and_most_complete_snapshots_not_carried':True,'scope':'Analysis of this campaign, not a new consolidation of CPC1-CPC9 or a complete historical archive'})
resources={'budget':budget,'generated_utc':datetime.now(timezone.utc).isoformat(),'execution_count':len(executions),'successful_exit_count':sum(r['exit_code']==0 for r in executions),'instrument_failure_exits':sum(r['exit_code']!=0 for r in executions),'native_episodes_not_inferred_from_process_count':True,'summed_owned_process_seconds':sum(r['seconds']for r in executions),'max_peak_owned_job_bytes':max((r.get('resources',{}).get('peak_job_committed_bytes',0)for r in executions),default=0),'payload_expanded_bytes':data_index['payload_expanded_bytes'],'solid_data_archive_bytes':data_index['archive_bytes'],'no_resumed_budget':True};write('RECURSOS_Y_COMPRESION.json',resources)
write('DEPENDENCIAS.json',{'analysis':'Python3.10+standardlibrary for tarfile/lzma/json/hashlib/array/struct; noengine needed for included recalculation','native_continuation':'Existing CPython3.13x64officialDEEthinking4.5environment and full local snapshots; deliberately not in this analysisZIP','optional_atlas_rendering':'Pillow12.3.0 used from authorized workspace runtime, not needed for data recalculation','private':True})
write('PREPARACION_PAQUETE.json',{'schema':'PC01.stage.v1','created_utc':datetime.now(timezone.utc).isoformat(),'primary_files':len(cases),'data_members':len(data_index['members']),'source_objects':len(seen_objects),'trial_rows':len(trials),'classification_cards':len(cards),'no_simulation_executed_by_this_builder':True,'final_zip_not_yet_sealed':True})
print(json.dumps({'stage':str(dest),'primary_cases':len(cases),'source_objects':len(seen_objects),'trial_rows':len(trials),'data_archive_bytes':data_index['archive_bytes']},ensure_ascii=False))
