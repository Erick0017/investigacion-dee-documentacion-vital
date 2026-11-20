"""Export a CLOSED hour, not a live queue; copy only exact referenced real files."""
import argparse,hashlib,importlib.util,json,shutil,subprocess,sys
from pathlib import Path
def read(p):
    import gzip
    return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):
    with p.open('x',encoding='utf8')as f:json.dump(x,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--origen',type=Path,required=True);p.add_argument('--sistema',type=Path,required=True);p.add_argument('--helper-objetivo',type=Path,required=True);p.add_argument('--fuentes-complementarias',type=Path,required=True);p.add_argument('--stage',type=Path,required=True);p.add_argument('--portable',type=Path,required=True);p.add_argument('--par-poststop',type=Path);p.add_argument('--corte-poststop',type=Path);a=p.parse_args();stage=a.stage.resolve();portable=a.portable.resolve();source=a.origen.resolve();system=a.sistema.resolve()
    if stage.exists()or portable.exists():raise FileExistsError('Preserve every preceding stage or failed attempt')
    if not(source/'RESUMEN.json').is_file():raise ValueError('Window must be CLOSED; do not open live journal')
    x=read(source/'REGISTROS_VENTANA.json.gz')
    if x.get('owner_final',{}).get('running'):raise ValueError('Owner not stopped')
    stage.mkdir(parents=True);ev=stage/'EVIDENCIA';ev.mkdir();rc=stage/'RECALCULO';rc.mkdir()
    for name in('REGISTROS_VENTANA.json.gz','PROTOCOLO.json','ADMISIONES.jsonl','CODIGO_EJECUTADO.py','FUENTES_ANTES_TICKS.json','RESUMEN.json','OWNER_OUT.txt','OWNER_ERR.txt'):shutil.copy2(source/name,ev/name)
    shutil.copytree(source/'codigo',stage/'FUENTES')
    for r in read(source/'FUENTES_ANTES_TICKS.json'):
        actual=stage/'FUENTES'/r['file']
        if actual.stat().st_size!=r['bytes']or sha(actual)!=r['sha256']:raise ValueError('Captured executed-source hash mismatch')
    dependency=system/'capacidades/mente_unificada_01.py';expected=x['owner_initial']['source_sha256']['native_capability_source']
    if sha(dependency)!=expected or x['owner_final']['source_sha256']['native_capability_source']!=expected:raise ValueError('Additional executed session source changed; never capture a different revision as original')
    target=stage/'FUENTES_DEPENDENCIAS';target.mkdir();shutil.copy2(dependency,target/dependency.name);write(target/'PROVENIENCIA.json',{'file':dependency.name,'sha256':expected,'bytes':dependency.stat().st_size,'scope':'Exact session source hash recorded by this owner before/after. Captured after STOP with the same bytes, not falsely included in the original narrower FUENTES_ANTES_TICKS map.'})
    complementary=a.fuentes_complementarias.resolve();capture=read(complementary/'MANIFIESTO.json');comparison=[]
    for row in capture['files']:
        archived=complementary/'codigo'/row['file'];current=system/row['file']
        if archived.stat().st_size!=row['bytes']or sha(archived)!=row['sha256']:raise ValueError('Complementary capture bytes do not match its original manifest')
        comparison.append({'file':row['file'],'captured_sha256':row['sha256'],'STOP_sha256':sha(current),'equal_at_STOP':current.stat().st_size==row['bytes']and sha(current)==row['sha256']})
    shutil.copytree(complementary,stage/'FUENTES_COMPLEMENTARIAS');write(ev/'COMPARACION_FUENTES_COMPLEMENTARIAS_POSTSTOP.json',{'capture_manifest_sha256':sha(complementary/'MANIFIESTO.json'),'files':comparison,'all_equal_at_STOP':all(r['equal_at_STOP']for r in comparison),'not_a_startup_global_attestation':True,'scope':'Complementary source capture made DURING the running reserve, after load; its original UTC/manifest is preserved. Comparison to STOP is read-only. The original startup32 map remains separate, and the owner module hash has its own before/after witness.'})
    for name in('recalcular_cadena_main_apd02.py','recalcular_ruta04_main_apd02.py','auditar_efecto_apd02_r02.py','auditar_archivo_ventana_apd02.py','recalcular_reserva_continua_apd02.py','recalcular_tiempo_reserva_apd02.py','probar_tiempo_reserva_apd02_n0.py'):shutil.copy2(Path(__file__).with_name(name),rc/name)
    shutil.copy2(a.helper_objetivo,rc/'auditar_evento_objetivo_apd02_r03.py')
    export=x.get('export',{}).get('paired_export');manifest=None;members={};export_root=None
    if export:
        export_root=Path(export['directory']);mp=export_root/'EXPORTACION_SERVICIO.json'
        if sha(mp)!=export['manifest_sha256']:raise ValueError('Closed paired-export manifest changed')
        manifest=read(mp);members={r['file']:r for r in manifest['members']};shutil.copy2(mp,ev/mp.name)
    primary_export_sha=export['manifest_sha256']if export else None
    if a.par_poststop:
        if not a.corte_poststop:raise ValueError('Explicit postSTOP pair requires its exact separate stopped-cut witness')
        stopped=read(a.corte_poststop);mp=a.par_poststop.resolve()/'EXPORTACION_SERVICIO.json'
        if sha(mp)!=stopped['paired_export']['manifest_sha256']:raise ValueError('Explicit postSTOP manifest differs from its stopped-cut witness')
        if manifest is not None:shutil.copy2(ev/'EXPORTACION_SERVICIO.json',ev/'EXPORTACION_SERVICIO_PRESTOP.json')
        export_root=a.par_poststop.resolve();manifest=read(mp);members={r['file']:r for r in manifest['members']};shutil.copy2(mp,ev/'EXPORTACION_SERVICIO.json');shutil.copy2(a.corte_poststop,ev/'CORTE_HORA_POSTSTOP.json')
        if stopped['main']['snapshot_sha256']!=x['final']['snapshot_sha256']:raise ValueError('The supplied postSTOP cut is not this hour final, never substitute a later operational life')
    index={'by_node':{},'primary_sha256':sha(source/'REGISTROS_VENTANA.json.gz'),'paired_manifest_sha256':sha(export_root/'EXPORTACION_SERVICIO.json')if export_root else None,'primary_preSTOP_export_manifest_sha256':primary_export_sha,'explicit_postSTOP_export_used':bool(a.par_poststop),'scope':'Actual files from this immutable manifest-validated hour export only. The original primary still records its preSTOP export and snapshot; an explicit postSTOP package has a distinct exact manifest/native container and is preserved separately. No later MAIN cut is substituted. Episode directory follows captured MU.session and its actual cumulative counter; not a filename search, Base64 reconstruction or another life.'}
    def bind(label,receipt,dirname,episode):
        relative=Path('ARTEFACTOS')/label.replace(':','_');artifact=receipt.get('artifact')if receipt else None;item={'directory':relative.as_posix(),'artifact':artifact,'copied_actual_file':False,'episode_inferred_from_exact_session_counter':episode,'relative_export_directory':'artefactos_trabajador/'+dirname}
        if artifact:
            if manifest is None:raise ValueError('A real effect requires its closed paired-export manifest, not a reconstructed artifact')
            rel='artefactos_trabajador/'+dirname+'/'+artifact['relative_path'];m=members[rel];actual=export_root/rel
            if not actual.resolve().is_relative_to(export_root.resolve())or m['bytes']!=artifact['bytes']or m['sha256']!=artifact['sha256']or actual.stat().st_size!=m['bytes']or sha(actual)!=m['sha256']:raise ValueError('Actual effect file disagrees with export member or receipt')
            destination=ev/relative;destination.mkdir(parents=True);shutil.copy2(actual,destination/artifact['relative_path']);item['copied_actual_file']=True;item['relative_export_member']=rel
        index['by_node'][label]=item
    for identifier,t in x['records'].items():
        if identifier.endswith('_parsed')or not t.get('result'):continue
        parsed=json.loads(t['result']);result=parsed.get('result',{});rows=result.get('rows',[])
        if not rows:continue
        last_episode=result['final']['operational']['episodes'];situations=json.loads(t['payload'])['situaciones']
        for slot,(request,row)in enumerate(zip(situations,rows)):
            episode=last_episode-(len(rows)-slot-1);label=identifier+':'+str(slot);mode=request['modo']
            if row.get('kind')=='APD02_quality_request':bind(label,row['committed_effect'],'apd02_'+str(episode),episode)
            elif row.get('kind')=='APD02_assisted_quality_sequence':
                for j,step in enumerate(row['rows']):bind(label+':stage:'+str(j),step['committed_effect'],'apd02_composition_'+str(episode)+'/stage_'+str(j),episode)
            elif row.get('kind')=='APD02_native_goal_opportunities':
                dirname=('apd02_goal_'if mode=='apd02-meta'else'apd02_goal_resume_')+str(episode)+'/world'
                for j,op in enumerate(row['result']['opportunities']):bind(label+':goal:'+str(j),op['environment_effect'].get('committed_effect'),dirname,episode)
    write(ev/'ARTEFACTOS.json',index)
    jobs=[{'name':'RESERVE_FUNCTIONS_RAW_REAL_EFFECTS_42EVENTS','base':'.','script':'RECALCULO/recalcular_reserva_continua_apd02.py','args':['--evidencia','EVIDENCIA','--evaluador','FUENTES/capacidades/evaluador_calidad_apd02.py','--fuente-ruta','FUENTES/capacidades/ruta_adaptativa_apd02_04.py','--salida','{output}'],'reference':'REFERENCIA_FUNCIONES_RESERVA.json'},
          {'name':'RESERVE_ONE_OWNER_DURATION_AND_SEPARATE_CLEAN_CLOSE','base':'.','script':'RECALCULO/recalcular_tiempo_reserva_apd02.py','args':['--evidencia','EVIDENCIA','--salida','{output}'],'reference':'REFERENCIA_TIEMPO_RESERVA.json'},
          {'name':'TIME_AUDITOR9_SYNTHETIC_NEGATIVE_FIXTURES_ONLY','base':'.','script':'RECALCULO/probar_tiempo_reserva_apd02_n0.py','args':['--salida','{output}'],'reference':'REFERENCIA_FIXTURES_TIEMPO_N0.json'}]
    for job in jobs:
        command=[sys.executable,'-I','-B','-X','utf8',str(stage/job['script'])]
        for value in job['args']:
            if value=='{output}':command.append(str(stage/job['reference']))
            elif value.startswith(('RECALCULO/','EVIDENCIA','FUENTES/')):command.append(str(stage/value))
            else:command.append(value)
        first=subprocess.run(command,capture_output=True,text=True,encoding='utf8',timeout=120)
        if first.returncode:print(first.stdout);print(first.stderr);return first.returncode
    write(stage/'PLAN_RECALCULO.json',{'jobs':jobs,'scope':'Only archived RAW/receipt/actual-file/temporal computation and9 synthetic auditor fixtures. No engine, provider, live queue, native reproduction or new tick.'})
    shutil.copytree(stage,portable);proof=[]
    for j,job in enumerate(jobs):
        out=portable/('RECALCULADO_'+str(j)+'.json');command=[sys.executable,'-I','-B','-X','utf8',job['script'],*[str(out)if value=='{output}'else value for value in job['args']]];run=subprocess.run(command,cwd=portable,capture_output=True,text=True,encoding='utf8',timeout=120);proof.append({'name':job['name'],'returncode':run.returncode,'stdout':run.stdout,'stderr':run.stderr,'reference_sha256':sha(stage/job['reference']),'byte_identical':out.exists()and sha(out)==sha(stage/job['reference'])})
    write(stage/'PRUEBA_PORTABLE.json',{'cases':proof,'new_native_ticks':0,'new_provider_calls':0,'live_SQLite_reads':0});write(stage/'MANIFIESTO.json',{'files':[{'file':f.relative_to(stage).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)}for f in sorted(stage.rglob('*'))if f.is_file()],'scope':'All exact closed primaries/executed code/real selected effect files/references/proof. Full original snapshots and operational journals remain local; no analysis file is a resumable native life. Manifest excludes itself.'})
    print(json.dumps({'stage':str(stage),'jobs':len(jobs),'byte_identical':all(r['byte_identical']for r in proof),'actual_files':sum(r['copied_actual_file']for r in index['by_node'].values()),'new_native_ticks':0}));return any(r['returncode']or not r['byte_identical']for r in proof)
if __name__=='__main__':raise SystemExit(main())
