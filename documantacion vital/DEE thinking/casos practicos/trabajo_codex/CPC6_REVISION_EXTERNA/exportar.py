"""Private, read-only projection of sealed CPC6. This exporter is not delivered.

Only explicitly constructed external fields leave this work directory. Never
copy source dictionaries, strings, filenames, commands or exception traces.
"""
import argparse,collections,hashlib,json,os,re,shutil,sys,time,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))

NAME='CPC6_REVISION_EXTERNA.zip'
SOURCE='CPC6_MENTE_DEE_INTEGRADA_APRENDIZAJE_Y_COMUNICACION_RESULTADOS.zip'
SOURCE_SHA='9d8c72a2536a7d8a782e0f3885d6d9ceba48b5f3d9111f618386def13fff708b'
HERE=Path(__file__).resolve().parent
CASES=HERE.parents[1]
PAYLOAD=HERE/'entrega'/'CPC6_REVISION_EXTERNA'

def sha_bytes(x):return hashlib.sha256(x).hexdigest()
def sha_file(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def write_json(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def write_lines(p,rows):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8',newline='\n') as f:
        for x in rows:f.write(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def read(z,p):return json.loads(z.read('CPC6/'+p.replace('\\','/')))
def code(v):return {1:'CONTENIDO_A',-1:'CONTENIDO_B'}.get(v,'SIN_CLASE_PUBLICADA')

def normalize_requests(m):
    source=m.get('requests',m.get('calls',m.get('all_parent_requests',[])))
    detached=m.get('receipts',[])
    indexed={r['id']:r for r in detached if isinstance(r,dict) and 'id' in r}
    assert len(indexed)==len(detached), 'Detached receipts must have unique explicit IDs'
    rows=[]
    for q in source:
        r=q.get('receipt') or indexed.get(q.get('id'),{})
        if not r:continue
        rows.append((q,r))
    if m.get('schema')=='CPC6.retention.field_localization.v1':
        assert not rows and not source
        single=m['query_receipt'];receipts=m['final_operational']['receipts']
        assert len({r['id'] for r in receipts})==len(receipts)
        assert single in receipts
        for r in receipts:
            rows.append(({'tick':r['requested_tick'],'kind':r['kind'],
                'channel':r['channels'][0] if len(r.get('channels',[]))==1 else '',
                'receipt_only':True,'receipt_inherited':r['id']!=single['id']},r))
    single=m.get('query_receipt')
    if isinstance(single,dict) and 'id' in single:
        assert single['id'] in {r.get('id') for q,r in rows}, 'Unmatched explicit query receipt'
    return rows

def role(q):
    if q.get('receipt_only') and not q.get('receipt_inherited'):return 'CONSULTA_FUNCIONAL'
    p=q.get('port',q.get('channel','')).lower()
    if p=='event.a':return 'ACONTECIMIENTO_E1'
    if p=='event.b':return 'ACONTECIMIENTO_E2'
    if p.startswith('order_form.teach') or 'SECOND_OPAQUE_SIGN' in q.get('origin',''):return 'ENSENANZA_FORMA_02'
    if p.startswith('order_form.query'):return 'CONSULTA_FORMA_02'
    if p.startswith('language.teach') or 'LATER_OPAQUE_FORM' in q.get('origin',''):return 'ENSENANZA_FORMA_01'
    if p.startswith('language.query') or p.startswith('word_bus.'):return 'CONSULTA_FORMA_01'
    if 'actual' in p:return 'OBSERVACION_DE_CONSECUENCIA'
    if 'source' in p or 'teach' in p:return 'EXPOSICION_DE_FUENTE'
    if p=='order.read' or p.startswith('renewed.') or p.startswith('retention.'):return 'CONSULTA_DE_HISTORIA'
    if 'query' in p or 'read' in p:return 'CONSULTA_FUNCIONAL'
    return 'RECURSO_EXTERNO_DEL_APARATO_NO_DETALLADO'

def status(v):
    text=str(v or '').lower()
    return text if text in {'applied','scheduled','rejected_occupied','rejected_conflict','rejected_invalid','cancelled','rejected_out_of_range','rejected_protected','rejected_tick'} else 'otro_estado_registrado'

def condition(e,m):
    c=m.get('case',{}) or {};result={}
    if c.get('history') in ('AB','BA','NONE'):
        result['experiencia_inicial']={'AB':'E1_ANTES_DE_E2','BA':'E2_ANTES_DE_E1','NONE':'SIN_EXPERIENCIA_INICIAL'}[c['history']]
    if c.get('actual') in (1,-1):result['consecuencia_externa_presentada']=code(c['actual'])
    if isinstance(c.get('source_values'),dict):
        result['contenido_de_fuentes']={f'FUENTE_{i+1}':code(c['source_values'][k]) for i,k in enumerate(sorted(c['source_values']))}
    translations={'paired':'EMPAREJADA','unpaired':'DESACOPLADA','none':'OMITIDA','omitted':'OMITIDA','signal_only':'SOLO_SENAL','outcome_only':'SOLO_CONSECUENCIA'}
    for old,new in [('source_mode','exposicion_fuentes'),('language_mode','ensenanza_forma_01'),('order_language_mode','ensenanza_forma_02')]:
        if c.get(old) in translations:result[new]=translations[c[old]]
    for old,new in [('actual_omitted','observacion_consecuencia_omitida'),('late_omitted','consulta_funcional_omitida'),('omit_consolidation_query','consulta_posterior_omitida')]:
        if old in c:result[new]=bool(c[old])
    if c.get('source_codec')=='balanced':result['dosis_fuente_comparable_declarada']=True
    private=' '.join(str(x) for x in (e.get('case_id'),m.get('arm'),c.get('operation'),c.get('mechanism'))).lower()
    tags=[]
    for needles,label in [
        (('sham',),'CONTROL_SIMULADO'),(('unpaired',),'EXPERIENCIA_DESACOPLADA'),
        (('no_repeat',),'SIN_CONSULTA_POSTERIOR'),(('virgin','no_source_learning','no_experience'),'SIN_EXPERIENCIA_PERTINENTE'),
        (('no_actual','actual_omitted'),'SIN_OBSERVACION_DE_CONSECUENCIA'),
        (('omitted','no_name'),'OMISION_DECLARADA'),(('equaliz',),'EQUIPARACION_DIAGNOSTICA'),
        (('cut','remove','clear'),'INTERVENCION_DIAGNOSTICA_DECLARADA'),
        (('inverted','opposite','wrong'),'HISTORIA_O_CONTENIDO_ALTERNATIVO'),
        (('no_source','absent'),'AUSENCIA_DE_FUENTE_DECLARADA')]:
        if any(n in private for n in needles):tags.append(label)
    result['condiciones_de_control']=tags
    return result

def phase(e):
    if e['record_kind']=='DIAGNOSTIC_FORK':return 'DIAGNOSTICO_EN_RAMA'
    if e['record_kind']=='CONTROLLED_CONTINUATION':return 'CONTINUACION_CONTROLADA'
    if e['family'] in ('R01','R02','R03','AF_CTRL'):return 'RESERVA_DECLARADA_CON_CONTROLES'
    return 'EXPLORACION_O_COMPONENTE'

def build():
    from observables_export import extract_observables
    source=CASES/SOURCE;initial=sha_file(source);assert initial==SOURCE_SHA
    if PAYLOAD.exists():
        assert not (CASES/NAME).exists(), 'Never rewrite a published external revision'
        assert json.loads((PAYLOAD/'PROCEDENCIA.json').read_text(encoding='utf-8'))['sha256_expediente_fuente']==SOURCE_SHA
    PAYLOAD.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(source) as z:
        assert z.testzip() is None
        index=read(z,'revision/INDICE_EVIDENCIA.json');entries=index['cases'];assert len(entries)==129
        public={e['case_key']:f'EX{i+1:04}' for i,e in enumerate(entries)}
        families={v:f'F{i+1:02}' for i,v in enumerate(dict.fromkeys(e['family'] for e in entries))}
        by_original=collections.defaultdict(list)
        for e in entries:by_original[e['case_id']].append(public[e['case_key']])
        # Actual requested external intensities become equality-preserving opaque
        # levels. Their physical encoding is deliberately not delivered.
        magnitudes=set();loaded={}
        for e in entries:
            p=e['primary'].replace('\\','/');blob=z.read('CPC6/'+p);assert sha_bytes(blob)==e['sha256']
            m=json.loads(blob)
            if e.get('primary_subcase'):
                for k in e['primary_subcase'].split('/'):m=m[int(k)] if isinstance(m,list) else m[k]
            loaded[e['case_key']]=(m,blob)
            for q,r in normalize_requests(m):
                if isinstance(q.get('payload'),int):magnitudes.add(q['payload'])
        levels={v:f'NIVEL_{i+1:03}' for i,v in enumerate(sorted(magnitudes))}
        trials=[];inputs=[];outputs=[];predictions=[];missing=[]
        for e in entries:
            pid=public[e['case_key']];m,blob=loaded[e['case_key']];start=int(e['tick_start']);end=int(e['tick_end'])
            candidates=by_original.get(str(e.get('parent')),[])
            parent=candidates[0] if len(candidates)==1 else None
            parent_desc='VINCULO_DECLARADO_UNIVOCO' if parent else 'SIN_VINCULO_PUBLICO_UNIVOCO'
            c=condition(e,m)
            trials.append({'ensayo':pid,'familia':families[e['family']],
                'tipo':e['record_kind'],'fase_evaluacion':phase(e),'condiciones':c,
                'padre_publico':parent,'vinculo':parent_desc,'preparaciones':e['preparations'],
                'forks_diagnosticos':e['diagnostic_forks'],'continuaciones':e['controlled_continuations'],
                'duracion_relativa_registrada':end-start,'segundos_de_ejecucion_registrados':e.get('elapsed_seconds'),
                'estado_registro':'MEDIDO','sha256_primario_privado':e['sha256'],
                'sha256_subregistro_privado':sha_bytes(json.dumps(m,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()) if e.get('primary_subcase') else None,
                'cobertura_respuesta':'PENDIENTE_PROYECCION','estado_reserva':'RESERVA_DECLARADA' if phase(e)=='RESERVA_DECLARADA_CON_CONTROLES' else 'NO_RESERVA_GENERAL_ATRIBUIDA'})
            grouped=collections.Counter()
            for q,r in normalize_requests(m):
                rr=role(q)
                inherit=(int(q.get('tick',r.get('requested_tick',start)))<start or
                    (isinstance(q.get('call_tick'),int) and q['call_tick']<start))
                if q.get('receipt_only'):inherit=q['receipt_inherited']
                elif e['record_kind']=='DIAGNOSTIC_FORK' and 'call_tick' not in q:
                    added=m.get('postfork_added_inputs',m.get('new_participant_inputs_after_fork'))
                    if added==[]:inherit=True
                # Apparatus-only resources are counted but their agenda and
                # encoding are not disclosed as an experimental recipe.
                requested=int(q.get('tick',r.get('requested_tick',start)))-start if rr!='RECURSO_EXTERNO_DEL_APARATO_NO_DETALLADO' else None
                effective=(int(r['effective_tick'])-start) if r.get('effective_tick') is not None and rr!='RECURSO_EXTERNO_DEL_APARATO_NO_DETALLADO' else None
                level=levels.get(q.get('payload')) if rr!='RECURSO_EXTERNO_DEL_APARATO_NO_DETALLADO' else None
                op=str(q.get('kind',r.get('kind',''))).lower();op=op if op in ('submit','probe','experience') else 'entrada_registrada'
                grouped[(rr,requested,effective,level,op,status(r.get('status')),inherit)]+=1
            for key,count in sorted(grouped.items(),key=repr):
                rr,req,eff,lev,op,st,inherit=key
                inputs.append({'ensayo':pid,'funcion_de_entrada':rr,'t_solicitado_rel':req,'t_aplicado_rel':eff,
                    'nivel_opaco':lev,'operacion':op,'estado_admision':st,'cantidad':count,'heredada_del_padre':inherit})
            extracted=extract_observables(m,e)
            coverage=collections.Counter()
            for o in extracted:
                assert set(o)<= {'t','variable','estado','respuestas','n','origen','definicion'}
                responses=o.get('respuestas');assert responses is None or all(type(v) in (str,int,bool) for v in responses)
                outputs.append({'ensayo':pid,'t_rel':int(o['t'])-start if o.get('t') is not None else None,
                    'variable':o['variable'],'estado':o['estado'],
                    'respuestas':None if o['estado'] in ('no_publicado','valor_no_admitido') else responses,
                    'numero_respuestas':None if o['estado'] in ('no_publicado','valor_no_admitido') else o.get('n'),
                    'procedencia':o['origen'],'definicion_medida':o.get('definicion')})
                coverage[o['estado']]+=1
            trials[-1]['cobertura_respuesta']=dict(coverage)
            if not extracted:missing.append(pid)
            for pred in m.get('predictions',[]):
                t=pred.get('tick_emission',pred.get('emission_tick'));target=pred.get('target_tick')
                if t is not None and target is not None:
                    predictions.append({'ensayo':pid,'emision_rel':int(t)-start,'objetivo_rel':int(target)-start,
                        'horizonte':int(target)-int(t),'valor_predicho_publicado':None,
                        'alcance':'Anotación de instante asignado a emisión y objetivo; no certifica emisión activa ni acierto predictivo.'})
        assert not missing
        write_lines(PAYLOAD/'datos/ENSAYOS.jsonl',trials)
        write_lines(PAYLOAD/'datos/ENTRADAS.jsonl',inputs)
        write_lines(PAYLOAD/'datos/RESPUESTAS.jsonl',outputs)
        write_lines(PAYLOAD/'datos/PREDICCIONES_TEMPORALES.jsonl',predictions)
        errors=[]
        causes={
            'architecture_bridge_delayed_01':'Atributo auxiliar inexistente; fallo antes de preparar el mundo.',
            'architecture_bridge_delayed_03':'La validación rechazó una preparación inconsistente antes de evolucionar.',
            'reference_central':'Discrepancias de contrato del observador; datos físicos conservados en el expediente privado.',
            'reference_central_normalized01':'La normalización del contenedor no resolvió diferencias documentales del observador.',
            'reference_sem01':'Comparación del contenedor y representación; posterior contraste separó datos de metadatos.',
            'snapshot_storage_tests_01':'Importación local bajo aislamiento; ninguna prueba de compresión había comenzado.',
            'technical_integrated_01':'Nombre de opción de backend incompatible; ninguna trayectoria nativa comenzó.'}
        for i,x in enumerate(index['technical_errors_and_timeouts']):
            cmd=read(z,x['command']);errors.append({'incidencia':f'INC{i+1:03}','tipo':'COMANDO_TECNICO_HISTORICO',
                'codigo_salida':cmd.get('exit_code'),'duracion_segundos':cmd.get('elapsed_seconds'),
                'descripcion':causes.get(x['job'],'Incidencia técnica conservada; detalle interno omitido.'),
                'sha256_registro_privado':x['sha256'],'cuenta_como_ensayo_cientifico':False})
        for attempt,description in [(1,'Restricción de ubicación del entorno; instalación e identidad pasaron, no comenzó la referencia.'),(2,'Dependencia de arranque y de ruta del índice; la referencia pasó, las cinco trayectorias nuevas no comenzaron.'),(3,'Reproducción limpia preliminar completada después de reparar sólo la capa de ejecución.')]:
            p=f'resultados/clean_preliminary/attempt_{attempt:02}/CLEAN_REPORT.json';r=read(z,p)
            errors.append({'incidencia':f'LIMPIA_{attempt:02}','tipo':'REPRODUCCION_TECNICA','estado':'VERIFICADA' if r['status']=='VERIFIED' else 'ERROR',
                'comandos_completados':sum(c.get('exit_code')==0 for c in r['commands']),
                'comandos_fallidos':sum(c.get('exit_code') not in (None,0) for c in r['commands']),
                'descripcion':description,'sha256_registro_privado':sha_bytes(z.read('CPC6/'+p)),'cuenta_como_ensayo_cientifico':False})
        for label,p,desc in [
            ('META_01','resultados/PROVENANCE_REPORT_ATTEMPT01.json','Fallo de importación de un generador de metadatos; no afectó trayectorias.'),
            ('META_02','resultados/clean_preflight/PREFLIGHT_COMMAND_ATTEMPT_01.json','Error de sintaxis de una inspección técnica; no comenzó una trayectoria.')]:
            payload=z.read('CPC6/'+p)
            errors.append({'incidencia':label,'tipo':'METADATOS_O_PREPARACION_TECNICA','estado':'ERROR_PREOPERACION_RESUELTO',
                'codigo_salida':1,'descripcion':desc,'sha256_registro_privado':sha_bytes(payload),'cuenta_como_ensayo_cientifico':False})
        external_path=CASES/'CPC6_VERIFICACION_FINAL.json';external_blob=external_path.read_bytes();external=json.loads(external_blob)
        assert external['sha256']==SOURCE_SHA and external['status']=='VERIFIED'
        for i,attempt in enumerate(external['publication_attempts']):
            errors.append({'incidencia':f'PUBLICACION_{i+1:02}','tipo':'PUBLICACION_TECNICA','codigo_salida':attempt['exit_code'],
                'estado':'ERROR_PREOPERACION_RESUELTO' if attempt['exit_code'] else 'VERIFICADA',
                'descripcion':'Error de sintaxis antes de iniciar operaciones; resuelto con un lanzador explícito.' if attempt['exit_code'] else 'Publicación, reunión de segmentos e integridad comprobadas.',
                'sha256_registro_privado':sha_bytes(external_blob),'cuenta_como_ensayo_cientifico':False})
        final_clean=external['exact_candidate_clean_reproduction']
        errors.append({'incidencia':'LIMPIA_FINAL','tipo':'REPRODUCCION_TECNICA','estado':'VERIFICADA',
            'comandos_completados':sum(c['exit_code']==0 for c in final_clean['commands']),
            'comandos_fallidos':sum(c['exit_code']!=0 for c in final_clean['commands']),
            'descripcion':'Prueba limpia del corte final, incluyendo consulta posterior a restauración.',
            'sha256_registro_privado':sha_bytes(external_blob),'cuenta_como_ensayo_cientifico':False})
        write_lines(PAYLOAD/'datos/INCIDENCIAS_Y_REPRODUCCIONES.jsonl',errors)
        # Contrasts declared from actual reserved identifiers, never selected by
        # their result. No equality of resources or selectivity is inferred.
        def find(cid):
            v=by_original.get(cid,[]);assert len(v)==1;return v[0]
        baseline=find('WR01_BA_balanced_Qminus')
        contrasts=[{'contraste':f'C{i+1:02}','referencia':baseline,'comparador':find(cid),'factor_declarado':desc,
            'variable_de_lectura':var,'t_rel':t,'igualdad_de_recursos':'No certificable desde esta proyección; consultar limitaciones.'}
            for i,(cid,desc,var,t) in enumerate([
                ('WR02_BA_balanced_Qplus','Historia inicial mantenida; contenido de fuente distinto.','FORMA_01_REMOTA',162),
                ('WR03_AB_balanced_Qminus','Cambian conjuntamente el orden de experiencia inicial y la consecuencia emparejada; no aísla el orden por sí solo.','FORMA_02',90),
                ('WR04_BA_no_repeat','Se omite el episodio de consulta posterior completo, incluida la señal y el protocolo lector asociado.','FORMA_01_REMOTA',162),
                ('WR05_BA_unpaired_name','Primera enseñanza desacoplada.','FORMA_01_REMOTA',162)])]
        write_json(PAYLOAD/'CONTROLES_Y_RESERVAS.json',{'contrastes_reservados_completos':contrasts,
            'todas_las_condiciones':'ENSAYOS.jsonl conserva las condiciones de los129 registros, no sólo estos cuatro contrastes.',
            'cautela':'Las descripciones de intervención son factores declarados, no prueba independiente de selectividad interna.'})
        write_json(PAYLOAD/'PROCEDENCIA.json',{'tipo':'PROYECCION_OBSERVACIONAL_NO_RECONSTRUCTIVA','proyecto':'DEE Universe / INVESTIGACION DEE',
            'autor_del_proyecto':'Ivan Erick Tlaltecatl Morales','instrumento_declarado':'DEE thinking 4.0.0, modelo v27',
            'expediente_fuente':SOURCE,'sha256_expediente_fuente':initial,'sha256_acta_suplementaria':sha_bytes(external_blob),
            'seleccion':'Todos los129 registros del índice científico sellado, sin filtrar por éxito.',
            'reconciliacion_recibos':{'resumen_historico':7593,'recibos_separados_de_componentes':372,'recibos_de_cuatro_ramas_adicionales':152,
                'de_los_152_heredados':148,'de_los_152_sondas_nuevas':4,'total_reconciliado':8117,
                'metodo':'Recibos separados unidos por ID explícito; recibos individuales no duplicados. El índice histórico no los resumía. Sin modificación del índice ni ciencia nueva.',
                'recibos_sin_llamada_publicada':'Operación, admisión y tiempos del recibo original; nivel de entrada no publicado en ese primario, conservado como null. No se reconstruyen desde el padre.'},
            'registros_cientificos':129,'familias':len(families),'nuevas_preparaciones':94,'forks_diagnosticos':29,'continuaciones':6,
            'compromisos':'Cada ensayo incluye SHA-256 del primario privado. Sirve para enlazar una auditoría autorizada; no publica los bytes omitidos.',
            'redaccion':'Lista blanca construida campo a campo; IDs sustituidos, sin rutas privadas ni nombres de archivos primarios.',
            'niveles_de_entrada':'Códigos opacos conservan igualdad/diferencia del valor solicitado, no entregan codificación física ni una receta de ejecución.',
            'tiempo':'Unidades relativas del protocolo desde el inicio registrado de cada ensayo; no son estados de los relojes internos. Valores negativos indican entradas heredadas anteriores a una continuación.',
            'no_demostrado_por_el_export':'La fidelidad de la decodificación requiere confianza en esta proyección o auditoría autorizada del primario privado; su hash es un compromiso, no una demostración de contenido.',
            'fuente_crc_comprobado':True,'original_no_modificado':True})
    for name in ('LEER_PRIMERO.md','DESCRIPCION_FUNCIONAL.md','FORMULAS_Y_DICCIONARIO.md','ALCANCE_Y_CONCLUSIONES.md','RECALCULAR.py'):
        shutil.copyfile(HERE/'documentos'/name,PAYLOAD/name)
    assert sha_file(source)==initial
    print(json.dumps({'trials':len(trials),'inputs':len(inputs),'outputs':len(outputs),'families':len(families),'source_unchanged':True}))

def seal():
    import subprocess
    result=subprocess.run([sys.executable,'-I','-B',str(PAYLOAD/'RECALCULAR.py'),'--raiz',str(PAYLOAD)],capture_output=True,text=True,timeout=60)
    assert result.returncode==0,result.stderr
    audit=audit_tree(PAYLOAD);write_json(PAYLOAD/'REVISION_EXPORTACION.json',audit)
    files=[]
    for p in sorted(PAYLOAD.rglob('*')):
        if p.is_file() and p.name not in ('MANIFEST.json','HASHES.sha256'):
            files.append({'archivo':p.relative_to(PAYLOAD).as_posix(),'bytes':p.stat().st_size,'sha256':sha_file(p)})
    write_json(PAYLOAD/'MANIFEST.json',{'schema':'CPC6.external.manifest.v1','raiz':'CPC6_REVISION_EXTERNA','archivos':files,'excluye_autorreferencia':['MANIFEST.json','HASHES.sha256']})
    lines=[f"{r['sha256']}  {r['archivo']}" for r in files]+[f"{sha_file(PAYLOAD/'MANIFEST.json')}  MANIFEST.json"]
    (PAYLOAD/'HASHES.sha256').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    candidate=HERE/'CPC6_REVISION_EXTERNA.candidate.zip';assert not candidate.exists()
    with zipfile.ZipFile(candidate,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(PAYLOAD.rglob('*')):
            if not p.is_file():continue
            info=zipfile.ZipInfo('CPC6_REVISION_EXTERNA/'+p.relative_to(PAYLOAD).as_posix(),date_time=(1980,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED;info.extra=b'';info.comment=b'';info.external_attr=0o100644<<16
            z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    verify(candidate)
    write_json(HERE/'CANDIDATO_VERIFICADO.json',{'sha256':sha_file(candidate),'bytes':candidate.stat().st_size,'audit':audit})

def audit_tree(root):
    blocked={'raw','clock','clocks','s_reg','direction','directions','coordinate','coordinates','site','geometry','recipe','recipes','snapshots','snapshot','physical','local_windows','neighborhood','phase','kernel_modulus','reducer_cap','semantic','packing','source_code','command','argv','stderr','traceback'}
    def walk(v):
        if isinstance(v,dict):
            for k,x in v.items():assert k.lower() not in blocked,(k,'blocked field');walk(x)
        elif isinstance(v,list):
            for x in v:walk(x)
        elif isinstance(v,str):
            assert not re.search(r'[A-Za-z]:[\\/]|\\Users\\|site-packages|trabajo_codex|MEASUREMENTS\.json|\.deetsnap|\.whl\b|\.pyd\b',v,re.I), 'Private/implementation reference'
            assert not re.search(r'\[\s*-?\d+\s*,\s*-?\d+\s*,\s*-?\d+\s*\]',v),'Numeric spatial tuple'
    checked=[]
    for p in sorted(root.rglob('*')):
        if not p.is_file() or p.name in ('MANIFEST.json','HASHES.sha256','REVISION_EXPORTACION.json'):continue
        assert p.suffix in ('.json','.jsonl','.md','.py')
        blob=p.read_bytes();text=blob.decode('utf-8');assert not blob.startswith((b'MZ',b'PK\x03\x04'))
        if p.suffix=='.json':walk(json.loads(text))
        elif p.suffix=='.jsonl':
            for line in text.splitlines():walk(json.loads(line))
        else:
            assert not re.search(r'[A-Za-z]:[\\/]|\\Users\\|site-packages|trabajo_codex',text,re.I)
        checked.append(p.relative_to(root).as_posix())
    return {'estado':'REVISADO_LISTA_BLANCA','archivos_revisados':checked,
        'solo_texto_utf8':True,'rutas_privadas_excluidas':True,'datos_de_estado_y_geometria_excluidos':True,
        'ids_originales_sustituidos':True,'metadatos_zip':'Fecha neutral, sin comentarios ni campos extra; no conserva tiempos del filesystem.',
        'segunda_revision_editorial':'Inspección independiente asistida por IA de archivos y metadatos; no certificación de un tercero externo. Se precisó el codominio de las formas y se retiraron nombres técnicos de campos del decoder.',
        'alcance':'Comprobación automática de campos/patrones y revisión editorial independiente por separado. No prueba ausencia de cualquier inferencia posible sobre el sistema.'}

def verify(path):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(set(z.namelist()))
        for n in z.namelist():
            assert n.startswith('CPC6_REVISION_EXTERNA/') and '..' not in n.split('/')
            assert not z.getinfo(n).extra and not z.getinfo(n).comment
        manifest=json.loads(z.read('CPC6_REVISION_EXTERNA/MANIFEST.json'))
        for row in manifest['archivos']:
            blob=z.read('CPC6_REVISION_EXTERNA/'+row['archivo']);assert len(blob)==row['bytes'] and sha_bytes(blob)==row['sha256']
        expected={r['archivo']:r['sha256'] for r in manifest['archivos']};expected['MANIFEST.json']=sha_bytes(z.read('CPC6_REVISION_EXTERNA/MANIFEST.json'))
        actual={line.split('  ',1)[1]:line.split('  ',1)[0] for line in z.read('CPC6_REVISION_EXTERNA/HASHES.sha256').decode().splitlines()}
        assert actual==expected
        assert set(z.namelist())=={'CPC6_REVISION_EXTERNA/'+n for n in expected}|{'CPC6_REVISION_EXTERNA/HASHES.sha256'}
    assert sha_file(CASES/SOURCE)==SOURCE_SHA

def publish():
    candidate=HERE/'CPC6_REVISION_EXTERNA.candidate.zip';verify(candidate)
    destination=CASES/NAME;assert not destination.exists(),'Protect any existing delivery'
    identity=sha_file(candidate);os.rename(candidate,destination);assert sha_file(destination)==identity
    with zipfile.ZipFile(destination) as z:expanded=sum(i.file_size for i in z.infolist());members=len(z.namelist())
    write_json(HERE/'PUBLICACION.json',{'archivo':str(destination),'sha256':identity,'bytes':destination.stat().st_size,'expandido_bytes':expanded,'miembros':members,'original_inalterado':sha_file(CASES/SOURCE)==SOURCE_SHA})
    print(json.dumps({'name':NAME,'sha256':identity,'bytes':destination.stat().st_size,'expanded_bytes':expanded,'members':members}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['build','seal','verify','publish']);a=p.parse_args()
    if a.action=='build':build()
    elif a.action=='seal':seal()
    elif a.action=='verify':verify(HERE/'CPC6_REVISION_EXTERNA.candidate.zip')
    else:publish()
