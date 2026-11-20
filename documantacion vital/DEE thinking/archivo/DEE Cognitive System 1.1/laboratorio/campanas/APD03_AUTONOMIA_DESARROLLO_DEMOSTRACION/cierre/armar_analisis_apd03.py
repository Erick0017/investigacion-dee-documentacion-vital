"""Assemble an unsealed APD03 analysis candidate. No ZIP, Native or originals edits.

Only existing closed compact stages, exact source deltas and documents are
copied. Full remains explicitly pending unless a separately closed proof is
provided. Source stages are never patched to make a recalculation succeed.
"""
import argparse,hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path

EXPORTS={
    'MAIN':'main/exportacion/CIERRE_MAIN_APD03_R01',
    'MECANISMO':'mecanismo/exportacion/CIERRE_MECANISMO_APD03_R01',
    'CURVAS':'comparacion/exportacion/CIERRE_CURVAS_LEXICO_APD03_R02',
    'R04':'comparacion/exportacion/CIERRE_HISTORIA_ACCESO_APD03_R04',
    'REFERENCIAS':'comparacion/exportacion/CIERRE_REFERENCIAS_APD03_R01',
    'WSLS_ESTANDAR':'comparacion/exportacion/CIERRE_WSLS_ESTANDAR_APD03_R01',
    'ENTRADA_UI':'entrada/CIERRE_ENTRADA_UI_R03',
    'SERVICIO_MAIN':'entrada/CIERRE_SERVICIO_MAIN_R01',
}
DELTA=['gestionar.py','app/usar_dee.py','app/cola_local.py','app/protocolo_apd03.py','app/validation.py',
    'app/servicio_persistente.py','capacidades/mente_unificada_01.py',
    'capacidades/asistente_apd03.py','capacidades/entorno_compartido_apd03.py',
    'capacidades/lexico_generico_apd03_r02.py','capacidades/sensor_balanceado_apd03_r02.py']
DENIED_SUFFIXES=('.whl','.pyd','.dll','.zip','.deetsnap','.deetsnap.gz')


def read(path):return json.loads(Path(path).read_bytes())


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb')as stream:
        for block in iter(lambda:stream.read(1048576),b''):h.update(block)
    return h.hexdigest()


def emit(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf8')as stream:
        json.dump(value,stream,ensure_ascii=False,sort_keys=True,indent=2);stream.write('\n')


def text(path,value):
    with Path(path).open('x',encoding='utf8')as stream:stream.write(value)


def safe(root,name):
    name=Path(name)
    if name.is_absolute():raise ValueError('Absolute member rejected')
    result=(root/name).resolve()
    if not result.is_relative_to(root.resolve()):raise ValueError('Member escapes component')
    return result


def verify_component(folder):
    manifest=folder/'MANIFIESTO.json'
    if not manifest.is_file():raise ValueError('Closed component without manifest: '+str(folder))
    value=read(manifest);members=value.get('files',value.get('members'))
    if not isinstance(members,list)or not members:raise ValueError('Missing actual member list')
    count=0
    for row in members:
        name=row.get('file',row.get('path'))
        if not name or 'sha256'not in row:raise ValueError('Bad component member')
        path=safe(folder,name)
        if path.stat().st_size!=row['bytes']or sha(path)!=row['sha256']:raise ValueError('Closed component member differs: '+str(path))
        count+=1
    return {'manifest_sha256':sha(manifest),'listed_members_verified':count}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lab',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--out',type=Path,default=Path(__file__).resolve().parent/'ANALISIS_APD03_R01')
    parser.add_argument('--full-stage',type=Path,help='Optional separately closed compact Full proof, never the Full ZIP')
    parser.add_argument('--entry-docs',type=Path,help='Optional final Root-approved user dossier/script directory')
    parser.add_argument('--run-recalculation',action='store_true')
    parser.add_argument('--proof-out',type=Path,help='External candidate proof directory; no writes into originals')
    args=parser.parse_args();lab=args.lab.resolve();out=args.out.resolve();closing=Path(__file__).resolve().parent
    project=lab.parents[2];system=project/'sistema'
    if out.exists():raise FileExistsError('Never replace an assembled candidate; select a fresh --out')
    if not out.is_relative_to(closing):raise ValueError('Candidate must stay under LAB/cierre')
    out.mkdir(parents=True);copied=[];omitted=[];components=[]
    def copy_file(source,target,kind):
        source=Path(source);target=Path(target)
        if source.is_symlink():raise ValueError('Symlink source not admitted')
        if source.name.lower().endswith(DENIED_SUFFIXES):raise ValueError('Engine/archive/dense checkpoint forbidden in analysis: '+str(source))
        digest=sha(source);size=source.stat().st_size;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,target)
        if sha(source)!=digest or sha(target)!=digest or target.stat().st_size!=size:raise ValueError('Source changed while copying')
        copied.append({'source':str(source),'file':target.relative_to(out).as_posix(),'bytes':size,'sha256':digest,'kind':kind})
    for name,relative in EXPORTS.items():
        source=lab/relative;verification=verify_component(source)
        before={str(p):sha(p)for p in source.rglob('*')if p.is_file()}
        for path in sorted(source.rglob('*')):
            if not path.is_file():continue
            if path.suffix=='.pyc'or'__pycache__'in path.parts:continue
            copy_file(path,out/name/path.relative_to(source),'closed_scientific_component')
        if any(sha(path)!=digest for path,digest in before.items()):raise ValueError('An original component changed')
        components.append({'name':name,'source':str(source),'status':'EXACT_CLOSED_COPY',**verification})
    # Root's resource capture is not a second Main and its accounting is
    # nested. Preserve its exact raw samples and calculator separately.
    for path in sorted((closing/'RECURSOS_TOTAL_MAIN_R01').rglob('*')):
        if path.is_file():copy_file(path,out/'RECURSOS/TOTAL_TREE'/path.relative_to(closing/'RECURSOS_TOTAL_MAIN_R01'),'outer_total_resource_proof')
    for name in('INFORME_CIENTIFICO_APD03.md','COBERTURA_FRENTES_APD03.json',
        'COMPARACION_FUNCIONAL_Y_COSTE_MAIN_REFERENCIAS.md','COMPARACION_FUNCIONAL_Y_COSTE_MAIN_REFERENCIAS.json'):
        copy_file(closing/name,out/name,'scientific_report_not_final_Full_claim')
    for path in sorted((closing/'complementos').rglob('*')):
        if path.is_file():copy_file(path,out/'COMPLEMENTOS'/path.relative_to(closing/'complementos'),'closed_scientific_attribution_and_omission_tables')
    if args.entry_docs:
        docs=args.entry_docs.resolve()
        selected=sorted(docs.glob('*FINAL_R02.md'))
        if len(selected)!=3:raise ValueError('Require exactly three closed FINAL_R02 documentary files, not antecedent drafts')
        for path in selected:
            copy_file(path,out/'DEMOSTRACION_Y_DOSSIER'/path.name,'final_documentary_demonstration_not_a_new_human_or_video_test')
    for path in(closing/'generar_comparacion_funcional_n0.py',closing/'probar_analisis_portable_frontera_n0.py',Path(__file__)):
        copy_file(path,out/'CODIGO_DE_CIERRE'/path.name,'N0_analysis_source')
    for path in sorted((closing/'finalizacion').glob('*')):
        if path.is_file()and path.suffix in('.py','.md'):
            copy_file(path,out/'CODIGO_DE_CIERRE/finalizacion'/path.name,'explicit_final_sealing_instrument_not_yet_a_result')
    for name in('NOTA_REVISION_REFERENCIAS_N0.md',):
        path=lab/'entrada'/name
        if path.is_file():copy_file(path,out/'REVISIONES_N0'/name,'independent_scope_review')
    for name in('MEDICION_IO_REFERENCIAS_N0.json','MEDICIONES_CUATRO_REFERENCIAS_N0.json',
        'explicar_io_referencias_apd03_n0.py','resumir_mediciones_referencias_apd03_n0.py'):
        copy_file(lab/'comparacion'/name,out/'RECURSOS/REFERENCIAS'/name,'reference_resource_scope')
    incorporation=lab/'incorporacion/COMPROBACION_INCORPORACION_APD03_N0.json'
    copy_file(incorporation,out/'INCORPORACION'/incorporation.name,'closed_operational_incorporation')
    copy_file(lab/'incorporacion/verificar_incorporacion_apd03_n0.py',out/'INCORPORACION/verificar_incorporacion_apd03_n0.py','N0_local_incorporation_source_not_portable_state')
    for relative in DELTA:copy_file(system/relative,out/'CODIGO_DELTA/sistema'/relative,'system_source_delta_not_engine')
    for relative in('documentacion/GUIA_USO_APD03.md','capacidades/CATALOGO_CAPACIDADES.json'):
        copy_file(system/relative,out/'CODIGO_DELTA/sistema'/relative,'operational_guide_or_catalog_not_individual_memory')
    for path in sorted((system/'contratos').glob('*APD03*')):
        if path.is_file():copy_file(path,out/'CODIGO_DELTA/sistema/contratos'/path.name,'affected_capacity_contract')
    for path in sorted((system/'contratos').glob('*apd03*')):
        if path.is_file()and not(out/'CODIGO_DELTA/sistema/contratos'/path.name).exists():copy_file(path,out/'CODIGO_DELTA/sistema/contratos'/path.name,'affected_capacity_contract')
    continuity=project/'CONTINUIDAD_APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION.json'
    copy_file(continuity,out/'CONTINUIDAD'/continuity.name,'actual_life_continuity_localizers')
    for name in('REANUDACION.json','LEER_PRIMERO.md'):
        copy_file(project/name,out/'CODIGO_DELTA/raiz_proyecto'/name,'current_project_continuation_instruction')
    distributed_identity=project/'entregas/IDENTIDAD_PAR_DISTRIBUIDO_APD03_R01.json'
    if distributed_identity.is_file():copy_file(distributed_identity,out/'INCORPORACION'/distributed_identity.name,'closed_distributed_pair_identity_N0_not_new_continuation')
    collaborator=project.parent/'cognitive sistem'
    for relative in('actualizaciones/arrancar.py','actualizaciones/SELECCION.json'):
        copy_file(collaborator/relative,out/'CODIGO_DELTA/cognitive_sistem'/relative,'collaboration_launcher_or_update_selection_not_Full_proof')
    edition=read(lab/'manual/EDICION_MANUAL_APD03.json');word=Path(edition['document'])
    if sha(word)!=edition['sha256']:raise ValueError('Current Word differs from its edition proof')
    copy_file(word,out/'MANUAL'/word.name,'actual_updated_Word_visual_validation_not_claimed')
    copy_file(lab/'manual/EDICION_MANUAL_APD03.json',out/'MANUAL/EDICION_MANUAL_APD03.json','editorial_structure_and_failed_render_proof')
    for name in('actualizar_manual_apd03.py','CONTENIDO_APROBADO_MANUAL_APD03.json'):
        path=lab/'manual'/name
        if path.is_file():copy_file(path,out/'MANUAL'/name,'editorial_source_not_render_validation')
    # Typed frontend mocks are informative but never replace Native UI proof.
    for path in sorted((lab/'entrada/CIERRE_UI_TYPED_R07').iterdir()):
        if path.is_file():copy_file(path,out/'ENTRADA_TIPADA_N0'/path.name,'mock_frontend_only_not_Native_proof')
    full_status='PENDING_EXACT_FULL_PROOF'
    if args.full_stage:
        full=args.full_stage.resolve();proof=verify_component(full)
        for path in sorted(full.rglob('*')):
            if path.is_file():copy_file(path,out/'VALIDACION_FULL'/path.relative_to(full),'separately_closed_Full_verification')
        full_status='SEPARATE_CLOSED_PROOF_INCLUDED_NOT_REEXECUTED_BY_ASSEMBLER'
        components.append({'name':'VALIDACION_FULL','source':str(full),**proof})
    else:
        emit(out/'VALIDACION_FULL/ESTADO.json',{'status':full_status,'Full_ZIP_verified_by_this_assembly':False,
            'scope':'Explicit pending slot, not an empty success file. Add only actual sealed-Full verification after Root GO; analysis is not operational backup.'})
    # Normalise the two existing PLAN spellings without modifying them.
    jobs=[{'name':'MAIN','base':'MAIN','script':'CODIGO_Y_RECALCULO/recalcular_main_integrado_n0.py',
        'args':['--evidence','EVIDENCIA_MAIN','--io-evidence','RECURSOS_OS_NATIVE','--quality-artifacts','ARCHIVOS_CALIDAD_REALES','--out','{output}'],
        'expected':'RESULTADOS/RECALCULO_MAIN_FINAL.json'}]
    for name in list(EXPORTS)+(['VALIDACION_FULL']if args.full_stage else[]):
        plan=out/name/'PLAN_RECALCULO.json'
        if not plan.is_file():continue
        value=read(plan)
        for row in value.get('jobs',value.get('cases',[])):
            jobs.append({'name':name+'_'+row.get('name',row.get('id')),
                'base':str(Path(name)/row.get('base','.')),'script':row['script'],'args':row['args'],
                'expected':row.get('reference',row.get('expected'))})
    jobs.append({'name':'SERVICIO_MAIN','base':'SERVICIO_MAIN','script':'RECALCULO/recalcular_servicio_hora_apd03_n0.py',
        'args':['--evidencia','EVIDENCIA','--salida','{output}','--requiere-cierre'],'expected':'RECALCULO_SERVICIO_CERRADO.json'})
    jobs.append({'name':'ARCHIVOS_GOAL_REALES','base':'COMPLEMENTOS/ARCHIVOS_GOAL_REALES',
        'script':'desnormalizar_goal_archivos_apd03_n0.py',
        'args':['recalcular','--evidence','.','--out','{output}'],'expected':'RECALCULO_ARCHIVOS_GOAL.json'})
    resource_reference=out/'RECURSOS/REFERENCIA_TOTAL.json';resource_reference.parent.mkdir(exist_ok=True)
    resource_command=[sys.executable,'-I','-B',str(out/'RECURSOS/TOTAL_TREE/recalcular_recursos_apd03_n0.py'),
        '--evidence',str(out),'--out',str(resource_reference)]
    run=subprocess.run(resource_command,cwd=tempfile.gettempdir(),capture_output=True,text=True,encoding='utf8',timeout=90)
    if run.returncode:
        emit(out/'FALLO_RECURSOS_N0.json',{'command':resource_command,'exit_code':run.returncode,'stdout':run.stdout,'stderr':run.stderr})
        raise ValueError('Actual resource CLI failed; do not seal this partial candidate')
    jobs.append({'name':'RECURSOS_TOTAL','base':'.','script':'RECURSOS/TOTAL_TREE/recalcular_recursos_apd03_n0.py',
        'args':['--evidence','.','--out','{output}'],'expected':'RECURSOS/REFERENCIA_TOTAL.json'})
    copy_file(closing/'recalcular_comparacion_portable_apd03_n0.py',out/'RECALCULO/recalcular_comparacion_portable_apd03_n0.py','explicit_portable_adapter_provenance_only_no_original_reads')
    jobs.append({'name':'COMPARACION_FUNCIONAL','base':'.','script':'RECALCULO/recalcular_comparacion_portable_apd03_n0.py',
        'args':['--evidence','.','--out','{output}'],'expected':'COMPARACION_FUNCIONAL_Y_COSTE_MAIN_REFERENCIAS.json'})
    for job in jobs:
        base=safe(out,job['base']);expected=safe(base,job['expected']);script=safe(base,job['script'])
        if not script.is_file()or not expected.is_file():raise ValueError('Actual CLI/reference missing: '+job['name'])
        job['expected_sha256']=sha(expected);job['script_sha256']=sha(script)
    (out/'RECALCULO').mkdir(exist_ok=True)
    copy_file(closing/'recalcular_analisis_apd03_n0.py',out/'RECALCULO/recalcular_todo_apd03.py','global_relative_N0_recalculation')
    emit(out/'RECALCULO/PLAN_GLOBAL.json',{'schema':'APD03.global_relative_recalculation_plan.R01','jobs':jobs,
        'full_status':full_status,'new_native_ticks':0,'not_a_scientific_or_Full_PASS':True})
    emit(out/'INDICE_FUENTES_Y_OMISIONES.json',{'schema':'APD03.analysis_unsealed_source_index.R01','copied':copied,
        'omitted':omitted,'original_component_omissions':'Each exact component retains its own source/omission index; complete local snapshots, Runtime, WHL and Full ZIP are intentionally absent.',
        'scope':'Candidate analysis, not historical archive, operational backup or Full distribution.'})
    text(out/'LEER_PRIMERO.md','# APD03 — análisis candidato no sellado\n\nEste directorio conserva ocho expedientes compactos cerrados, fuentes, positivos y negativos. No contiene motor ni los snapshots completos para continuar vidas. El Word incluido declara su validación visual pendiente.\n\nEl estado del Full exacto está en VALIDACION_FULL/ESTADO.json cuando permanece pendiente; no se anticipa éxito. No se creó un ZIP.\n\nRecálculo archivado sin motor desde cualquier ubicación: `python -I -B RECALCULO/recalcular_todo_apd03.py --out RUTA_EXTERNA_NUEVA`. Ejecuta CLIs reales y exige resultados idénticos byte a byte a referencias conservadas. No ejecuta Native, otra adquisición ni el Full.\n\nCODIGO_DELTA es material de estudio de la capa1.1, no instalador ni kernel; no transfiere memorias. CONTINUIDAD contiene localizadores locales, no mundos completos.\n')
    inventory=[{'file':p.relative_to(out).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(out.rglob('*'))if p.is_file()]
    emit(out/'RECALCULO/ENTRADAS_ESPERADAS.json',{'files':inventory,'excludes_own_hash':True,'candidate_not_final_manifest':True})
    groups={}
    for row in inventory:groups.setdefault(row['sha256'],[]).append(row)
    emit(out/'CANDIDATO_NO_SELLADO.json',{'schema':'APD03.analysis_unsealed_candidate.R01','status':'UNSEALED_NO_ZIP',
        'components':components,'full_status':full_status,'files_before_inventory':len(inventory),
        'expanded_bytes_before_inventory':sum(r['bytes']for r in inventory),'global_jobs':len(jobs),
        'exact_duplicate_bytes_retained_for_relative_paths':sum(sum(r['bytes']for r in group[1:])for group in groups.values()),
        'no_original_modified':True,'new_native_ticks':0,'final_ZIP_created':False})
    if args.run_recalculation:
        proof=args.proof_out.resolve()if args.proof_out else closing/'PRUEBA_ANALISIS_APD03_N0_R01'
        command=[sys.executable,'-I','-B',str(out/'RECALCULO/recalcular_todo_apd03.py'),'--root',str(out),'--out',str(proof)]
        result=subprocess.run(command,cwd=tempfile.gettempdir(),capture_output=True,text=True,encoding='utf8',timeout=600)
        if result.returncode:raise ValueError('Global archived recalculation failed: '+result.stdout+result.stderr)
        print(result.stdout)
    print(json.dumps({'candidate':str(out),'global_jobs':len(jobs),'status':'UNSEALED_NO_ZIP','Full':full_status}))


if __name__=='__main__':main()
