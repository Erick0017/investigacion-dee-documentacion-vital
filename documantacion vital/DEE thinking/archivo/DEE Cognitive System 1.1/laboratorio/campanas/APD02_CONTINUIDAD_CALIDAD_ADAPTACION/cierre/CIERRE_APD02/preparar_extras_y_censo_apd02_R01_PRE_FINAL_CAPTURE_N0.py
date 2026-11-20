"""Explicit pinned APD02 analysis extras and existing-receipt census; no Native.

Does not scan sistema, states, SQLite, checkpoints or historical folders.
Closed-stage manifests identify every metadata document examined below.
"""
import argparse,datetime as dt,hashlib,json,re,time
from pathlib import Path

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(p,v):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
def scalars(x,path='',depth=0):
    if depth>3:return []
    out=[]
    if isinstance(x,dict):
        for k,v in x.items():
            p=path+'/'+str(k)
            if isinstance(v,(str,int,float,bool))or v is None:
                if re.search(r'(elapsed|seconds|wall_|cpu_|memory|working_set|private_bytes|committed_bytes|job_active|job_total|returncode|forced|pid|timeout|limit_bytes)',str(k),re.I):out.append({'json_pointer':p,'recorded_value':v})
            elif isinstance(v,dict)and k in('resources','job','job_before_cleanup','job_final','owner_initial','owner_final','initial','final'):out+=scalars(v,p,depth+1)
            elif isinstance(v,list)and k=='steps':
                for n,item in enumerate(v):out+=scalars(item,p+'/'+str(n),depth+1)
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);p.add_argument('--closure-utc');a=p.parse_args();config=read(a.config);root=Path(config['source_root']).resolve();lab=Path('laboratorio/campanas/APD02_CONTINUIDAD_CALIDAD_ADAPTACION');ev=Path('evidencia/campanas/APD02_CONTINUIDAD_CALIDAD_ADAPTACION');continuity=read(root/'CONTINUIDAD_APD02_CONTINUIDAD_CALIDAD_ADAPTACION.json');contract=read(root/'sistema/contratos/APD02_CONTINUIDAD_CALIDAD.json');out=a.salida.resolve()
    if out.exists():raise FileExistsError('Keep every capture; this never edits a final proposal in place')
    aliases={};selected=[];resource_docs=[];omission_indexes=[]
    for st in config['stages']:
        stage=root/st['source'];manifest=stage/st.get('manifest','MANIFIESTO.json')
        if sha(manifest)!=st['manifest_sha256']:raise ValueError('Pinned closed manifest changed')
        rows=read(manifest);rows=rows.get('files',rows.get('members'));selected.append({'namespace':st['namespace'],'source':st['source'],'manifest_sha256':st['manifest_sha256'],'plan_sha256':sha(stage/st.get('plan','PLAN_RECALCULO.json'))})
        for row in rows:
            name=row.get('file',row.get('path'));aliases.setdefault(row['sha256'],[]).append({'namespace':st['namespace'],'path':name})
            base=Path(name).name.upper()
            if any(key in base for key in('OMISION','INDICE','LOCALIZ','SNAPSHOT'))and base.endswith('.JSON'):omission_indexes.append({'namespace':st['namespace'],'logical_path':name,'bytes':row['bytes'],'sha256':row['sha256'],'reason':'Already exported index is the authority for the omitted local complete data; targets are not rehashed or read here.'})
            if base in('RECURSOS.JSON','RESUMEN.JSON','RESULTADOS.JSON','EJECUCION.JSON')and name.startswith('EVIDENCIA/')and row['bytes']<=2000000:
                file=stage/name
                if sha(file)!=row['sha256']:raise ValueError('Existing metadata bytes changed: '+name)
                observed=scalars(read(file))
                if observed:resource_docs.append({'namespace':st['namespace'],'logical_path':name,'sha256':row['sha256'],'bytes':row['bytes'],'recorded_scalars':observed,'scope':'Existing archived per-process/window measurements; not independent samples, new measurement, aggregate host RAM, cognition score, native energy or one summed continuous session.'})
    public=[]
    def add(source,target,role):
        f=(root/source).resolve(strict=True)
        if not f.is_relative_to(root)or not f.is_file():raise ValueError('Explicit regular source inside research root required')
        digest=sha(f);public.append({'source':f.relative_to(root).as_posix(),'to':target,'sha256':digest,'bytes':f.stat().st_size,'role':role,'identical_bytes_already_in_closed_namespaces':aliases.get(digest,[])})
    for source,target in[
        (continuity['manual']['file'],'DOCUMENTOS/MANUAL_MAESTRO_1_16.docx'),
        (str(lab/'documentos/EDICION_MANUAL_APD02.json'),'DOCUMENTOS/EDICION_MANUAL_APD02.json'),
        (str(lab/'documentos/CONTENIDO_APROBADO_MANUAL_APD02.json'),'DOCUMENTOS/CONTENIDO_APROBADO_MANUAL_APD02.json'),
        (str(lab/'documentos/actualizar_manual_apd02.py'),'CODIGO_EDITORIAL/actualizar_manual_apd02.py'),
        (str(lab/'documentos/preparar_contenido_manual_apd02.py'),'CODIGO_EDITORIAL/preparar_contenido_manual_apd02.py'),
        (str(lab/'documentos/PRESERVACION_CATALOGO_APD02_R01.json'),'DOCUMENTOS/PRESERVACION_CATALOGO_APD02_R01.json'),
        (str(lab/'documentos/comprobar_actualizacion_catalogo_apd02.py'),'CODIGO_EDITORIAL/comprobar_actualizacion_catalogo_apd02.py'),
        ('CONTINUIDAD_APD02_CONTINUIDAD_CALIDAD_ADAPTACION.json','DOCUMENTOS/CONTINUIDAD_APD02_CONTINUIDAD_CALIDAD_ADAPTACION.json'),
        ('LEER_PRIMERO.md','DOCUMENTOS/LEER_PRIMERO_COGNITIVE.md'),('PROYECTO.json','DOCUMENTOS/PROYECTO.json'),('REANUDACION.json','DOCUMENTOS/REANUDACION.json'),
        (str(ev/'CORTE_POSTSTOP_FINAL_R01/CORTE_OPERATIVO_APD02.json'),'DOCUMENTOS/CORTE_OPERATIVO_APD02.json'),
        (str(lab/'documentar_corte_poststop_apd02.py'),'CODIGO_CIERRE/documentar_corte_poststop_apd02.py'),
        (str(lab/'documentos/LEER_ANALISIS_APD02.md'),'LEER_ANALISIS_APD02.md'),
        (str(lab/'documentos/DELTA_OPERATIVO_Y_REPRODUCCION.md'),'DELTA_SISTEMA/LEER_PRIMERO.md')]:add(source,target,'Root closed documentary/operational-cut source; no Native executed by capture')
    # Explicit implementation list from the closed contract; never glob sistema.
    implementation=list(dict.fromkeys(contract['implementation']+['app/cola_local.py','gestionar.py','app/importacion_emparejada.py','app/process_control.py','app/lives.py','app/native_tools.py','app/cliente_mente_unificada.py']))
    for name in implementation:add('sistema/'+name,'DELTA_SISTEMA/'+name,'Actual Cognitive implementation/delta, not an engine or acquired individual state')
    for source,target in [('sistema/contratos/APD02_CONTINUIDAD_CALIDAD.json','DELTA_SISTEMA/contratos/APD02_CONTINUIDAD_CALIDAD.json'),('sistema/documentacion/GUIA_ASISTENTE_APD02.md','DELTA_SISTEMA/documentacion/GUIA_ASISTENTE_APD02.md'),('sistema/capacidades/CATALOGO_CAPACIDADES.json','DELTA_SISTEMA/capacidades/CATALOGO_CAPACIDADES.json'),('sistema/estado/vidas/APD02_MAIN/VIDA.json','DOCUMENTOS/VIDA_APD02_MAIN.json'),('sistema/estado/ACTIVO.json','DOCUMENTOS/ACTIVO_PROTEGIDO.json')]:add(source,target,'Actual metadata; code/document availability is not knowledge transferred to a life')
    here=Path(__file__).parent
    for name in('ensamblar_analisis_apd02_cas.py','ensamblar_analisis_apd02_cas_R02_PRE_README_LINK_N0.py','repetir_todo_apd02_cas.py','sellar_probar_zip_analisis_apd02.py','preparar_extras_y_censo_apd02_n0.py'):add((here/name).relative_to(root).as_posix(),'CODIGO_CIERRE/'+name,'Exact N0 packaging/documentation source, not a DEE function')
    if len({r['to'].casefold()for r in public})!=len(public):raise ValueError('Public target collision')
    actualword=next(r for r in public if r['to']=='DOCUMENTOS/MANUAL_MAESTRO_1_16.docx')
    if actualword['sha256']!=continuity['manual']['sha256']:raise ValueError('Word bytes differ from closed continuity')
    now=dt.datetime.now(dt.timezone.utc);start=dt.datetime.fromisoformat('2026-10-26T03:17:43+00:00');deadline=dt.datetime.fromisoformat('2026-10-26T11:17:43+00:00');end=dt.datetime.fromisoformat(a.closure_utc.replace('Z','+00:00'))if a.closure_utc else None
    budget={'root_first_command_utc':start.isoformat(),'unchanged_campaign_deadline_utc':deadline.isoformat(),'maximum_total_wall_seconds':28800,'monotonic_start_estimated_from_first_command':1163605.970752,'monotonic_start_is_estimated_not_an_initial_capture':True,'capture_utc':now.isoformat(),'capture_monotonic':time.monotonic(),'wall_elapsed_seconds_at_capture':(now-start).total_seconds(),'campaign_end_utc':end.isoformat()if end else None,'campaign_end_not_asserted_by_this_capture':end is None,'nominal_native_process_caps_as_declared_by_Root':{'main_owners_max':1,'auxiliary_owners_max':2,'per_owned_job_bytes':536870912,'maximum_nominal_combined_native_cap_bytes':1610612736,'not_measured_aggregate_RAM':True,'host_archiving_workers_are_separate':True},'initial_policy_snapshot_is_retained_without_rewrite':{'source':str(ev/'PRESUPUESTO_E_IDENTIDAD_INICIAL.json'),'note':'Initial record specified one auxiliary owner; Root later declared a maximum of two auxiliary owners. This capture does not fabricate the time of that authorization or claim simultaneous observed occupancy.'},'continuous_service_is_separate':'The one-owner 3600.095529s proof is its own archived temporal case; no separate auxiliary/process windows are summed to establish it.'}
    known=[{'namespace':'CONTEXTO_R01','logical_source':'EVIDENCIA/RESULTADOS.json','intended_seconds':180,'actual_seconds':194.44801309984177,'excess_seconds':14.44801309984177,'reason':'Guard checked between material queries and completed an already-started final query; preserved protocol deviation, no Native rerun.'},{'namespace':'MECANISMO_AUX','logical_source':'EVIDENCIA/TRAZA_DEMORADA_R03/RESULTADOS.json','intended_seconds':300,'actual_seconds':305.3372899000533,'excess_seconds':5.3372899000533,'reason':'Already-started bounded native operation completed before stopping; retained deviation, not a rewritten300s success.'}]
    out.mkdir(parents=True)
    census={'schema':'APD02.closed_analysis.omissions_and_recorded_resources.N0.v1','status':'CANDIDATE_NOT_FINAL_SEAL','native_ticks':0,'new_current_SQLite_or_snapshot_reads':0,'source_config_sha256':sha(a.config),'selected_stages':selected,'omitted_local_complete_data_indexes':omission_indexes,'recorded_resource_documents':resource_docs,'known_time_bound_deviations':known,'budget':budget,'not_in_analysis':[{'kind':'Complete native snapshots, SQLite journals/outboxes and full paired export trees','locator_policy':'Use exact paths/SHA in the included stage indexes, closed continuity and operational cut; no empty-world fallback or incomplete-RAW restoration.'},{'kind':'Kernel, officialWHL and binary dependencies','locator_policy':'Provided only by the independent operational collaborator Full package; no engine duplication or recompilation here.'},{'kind':'Superseded whole staging trees and deep redundant telemetry','locator_policy':'Original local directories remain; selected preferred stage contains physical primaries, exact revision sources, negatives and instrumental-error preimages. No unique physical failure is omitted for a favorable conclusion.'}], 'scope':'Index/receipt census only. Omitted data targets are neither rehashed nor loaded. Per-process counters have distinct definitions; they are not summed into continuous lifespan, cognitive effort, thermodynamic energy, global speed or a statistical sample count.'}
    write(out/'CENSO_OMISIONES_Y_RECURSOS_APD02_N0.json',census)
    proposal={'schema':'APD02.explicit_analysis_extras.pinned_candidate.v1','status':'CANDIDATE_AWAITING_ROOT_REVIEW_AND_FULL','base_config':a.config.name,'base_config_sha256':sha(a.config),'current_closed_case_count':config['expected_case_count'],'current_closed_namespace_count':len(config['stages']),'public_files':public,'pending_public_items':['Root final scientific report','Three final approved CSVs','Approved scalar table-inputJSON+actual builder+VERIFICACION_TABLAS_ARTIFACT','Actual CLOSED exact Full proof stage; one additional archived job','Root final protected-state/external ZIP proof when available; no self-hash cycle'],'final_root_go_required':True,'will_not_assemble_or_seal':True}
    write(out/'EXTRAS_Y_FUENTES_CANDIDATOS.json',proposal)
    (out/'LEER_CENSO.md').write_text('# Captura documental, no cierre de campaña\n\nLos hashes fijan archivos explícitos actuales. No se exploró todo sistema ni se volvió a verificar el corpus histórico. Los datos locales excluidos se localizan mediante los índices originales ya incluidos en los namespaces. Las medidas de recursos proceden de recibos archivados, no de repetir Native. El final de campaña no se inventa antes del Full y de los recálculos del ZIP exacto.\n\nEl máximoAPD02 es8h desde03:17:43UTC hasta11:17:43UTC; la estimación monotónica inicial se identifica como estimación. No se suman las distintas sesiones para afirmar una hora continua. Las desviaciones180→194.448 y300→305.337 siguen visibles. El Word sí está editado y estructuralmente comprobado; su render visual falló por ausencia de soffice.exe.\n',encoding='utf8')
    write(out/'REGISTRO_CAPTURA_N0.json',{'native_ticks':0,'copied_operational_or_scientific_files':0,'source_bytes_are_not_copied_by_this_proposal':True,'captured_documents':[{'file':f.name,'bytes':f.stat().st_size,'sha256':sha(f)}for f in sorted(out.iterdir())if f.is_file()],'self_hash_excluded':True})
    print(json.dumps({'out':str(out),'explicit_public_files':len(public),'explicit_public_bytes':sum(r['bytes']for r in public),'resource_documents':len(resource_docs),'omission_indexes':len(omission_indexes),'native_ticks':0,'assembly_or_ZIP_created':False},ensure_ascii=False))
if __name__=='__main__':main()
