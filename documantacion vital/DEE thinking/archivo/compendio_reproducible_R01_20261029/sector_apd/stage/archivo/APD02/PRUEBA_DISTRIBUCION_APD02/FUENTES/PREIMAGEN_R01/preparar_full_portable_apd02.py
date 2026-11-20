"""Export a completed exact-Full proof and its own real selected files; no Native."""
import argparse,gzip,hashlib,json,shutil,subprocess,sys
from pathlib import Path
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
def native(value):return json.loads((value.get('request')or value)['result'])['result']
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prueba',type=Path,required=True);p.add_argument('--verificacion',type=Path,required=True);p.add_argument('--protocolo',type=Path,required=True);p.add_argument('--extraido',type=Path,required=True);p.add_argument('--stage',type=Path,required=True);p.add_argument('--portable',type=Path,required=True);a=p.parse_args();stage=a.stage.resolve();portable=a.portable.resolve();extracted=a.extraido.resolve();proof=read(a.prueba);protocol=read(a.protocolo)
    if stage.exists()or portable.exists():raise FileExistsError('Preserve every attempted stage and exact proof')
    if 'continued_state'not in proof or proof.get('forced_owned_job_cleanup')or len(proof.get('owned_close',[]))!=2:raise ValueError('This complete-run exporter cannot impute missing execution or a clean owner close')
    for close in proof['owned_close']:
        if close['resources'].get('job_active_processes')!=0:raise ValueError('Owned process closure not established')
    stage.mkdir(parents=True);ev=stage/'EVIDENCIA';ev.mkdir();rc=stage/'RECALCULO';rc.mkdir();source=stage/'FUENTES';source.mkdir()
    original=a.prueba.read_bytes();(ev/'PRUEBA_SERVICIO_APD02.json.gz').write_bytes(gzip.compress(original,mtime=0));shutil.copy2(a.verificacion,ev/'VERIFICACION_FULL_EXACTO.json');shutil.copy2(a.protocolo,ev/'PROTOCOLO_LIGADO.json');write(ev/'PROVENIENCIA_PROYECCION.json',{'original_json_sha256':hashlib.sha256(original).hexdigest(),'original_json_bytes':len(original),'original_localizer':str(a.prueba),'exported_gzip_sha256':sha(ev/'PRUEBA_SERVICIO_APD02.json.gz'),'scope':'Lossless gzip of the complete original proof bytes, not JSON reserialization. Native outputs, failures, literal requests and own cleanup records are preserved.'})
    files=('recalcular_full_apd02.py','recalcular_cadena_main_apd02.py','recalcular_ruta04_main_apd02.py','auditar_efecto_apd02_r02.py','auditar_evento_objetivo_apd02_r03.py')
    for name in files:shutil.copy2(Path(__file__).with_name(name),rc/name)
    for relative in('actualizaciones/probar_servicio_distribuido.py','actualizaciones/probar_asistente2_distribuido.py','actualizaciones/verificar_entrega_independiente.py','actualizaciones/arrancar.py','sistema/capacidades/evaluador_calidad_apd02.py','sistema/capacidades/ruta_adaptativa_apd02_04.py','sistema/app/protocolo_apd02.py','sistema/app/process_control.py'):
        destination=source/relative;destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(extracted/relative,destination)
    shutil.copy2(Path(__file__),source/Path(__file__).name)
    life=proof['exact_import']['life_id'];service=extracted/'trabajo_personal/estado/servicios_locales'/life;index={'by_node':{},'life_id':life,'world_id':proof['exact_import']['world_id'],'scope':'Only actual effect files from this exact extraction and this personal life. No Base64 reconstruction, history search, other life, engine or snapshot export.'}
    def bind(label,receipt,directory):
        relative=Path('ARTEFACTOS')/label.replace(':','_');artifact=receipt.get('artifact')if receipt else None;entry={'directory':relative.as_posix(),'artifact':artifact,'copied_actual_file':False}
        if artifact:
            directory=Path(directory).resolve(strict=True)
            if not directory.is_relative_to(service.resolve()):raise ValueError('Effect directory outside exact extracted personal life')
            actual=(directory/artifact['relative_path']).resolve(strict=True)
            if not actual.is_relative_to(directory)or actual.stat().st_size!=artifact['bytes']or sha(actual)!=artifact['sha256']:raise ValueError('Actual selected file differs from real terminal receipt')
            destination=ev/relative/artifact['relative_path'];destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(actual,destination);entry.update(copied_actual_file=True,source_relative_to_extraction=actual.relative_to(extracted).as_posix())
        index['by_node'][label]=entry
    for i,_ in enumerate(protocol['service_protocol']['new_apd']):
        label='new_apd_'+str(i);row=native(proof['results'][label])['rows'][0];bind(label,row['committed_effect'],row['effect_directory'])
    row=native(proof['results']['new_composition'])['rows'][0]
    for j,part in enumerate(row['rows']):bind('new_composition:stage:'+str(j),part['committed_effect'],part['effect_directory'])
    for label in('goal_first_one','goal_continue'):
        body=native(proof['results'][label]);episode=body['final']['operational']['episodes'];row=body['rows'][0];directory=service/('apd02_goal_resume_'+str(episode))/'world'
        for j,op in enumerate(row['result']['opportunities']):bind(label+':goal:'+str(j),op['environment_effect'].get('committed_effect'),directory)
    write(ev/'ARTEFACTOS.json',index)
    job={'name':'EXACT_EXTRACTED_APD02_RAW_REALFILES_AND_PAIRED_CONTINUATION','base':'.','script':'RECALCULO/recalcular_full_apd02.py','args':['--evidencia','EVIDENCIA','--evaluador','FUENTES/sistema/capacidades/evaluador_calidad_apd02.py','--fuente-ruta','FUENTES/sistema/capacidades/ruta_adaptativa_apd02_04.py','--salida','{output}'],'reference':'REFERENCIA_FULL_APD02.json'}
    command=[sys.executable,'-I','-B','-X','utf8',str(stage/job['script'])]
    for value in job['args']:command.append(str(stage/job['reference'])if value=='{output}'else str(stage/value)if value.startswith(('EVIDENCIA','FUENTES/'))else value)
    run=subprocess.run(command,capture_output=True,text=True,encoding='utf8',timeout=120)
    if run.returncode:print(run.stdout);print(run.stderr);return run.returncode
    write(stage/'PLAN_RECALCULO.json',{'jobs':[job],'scope':'One pure archived RAW/real-file/transport-state calculation. Native reproduction and exact ZIP extraction are distinct completed operations recorded in the primary verifier; this calculator never imports their engine.'})
    shutil.copytree(stage,portable);out=portable/'RECALCULADO_FULL_APD02.json';run=subprocess.run([sys.executable,'-I','-B','-X','utf8',job['script'],*[str(out)if v=='{output}'else v for v in job['args']]],cwd=portable,capture_output=True,text=True,encoding='utf8',timeout=120);proof2={'returncode':run.returncode,'stdout':run.stdout,'stderr':run.stderr,'reference_sha256':sha(stage/job['reference']),'byte_identical':out.exists()and sha(out)==sha(stage/job['reference']),'new_native_ticks':0,'new_provider_calls':0}
    write(stage/'PRUEBA_PORTABLE.json',proof2);write(stage/'MANIFIESTO.json',{'files':[{'file':f.relative_to(stage).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)}for f in sorted(stage.rglob('*'))if f.is_file()],'scope':'Manifest includes the independent portable proof and all selected actual artifacts; excludes only itself. Full ZIP, Runtime, native complete snapshots/journal and pending operational bundle remain outside this scientific stage with original localizers in verifier.'});print(json.dumps({'stage':str(stage),'manifest_sha256':sha(stage/'MANIFIESTO.json'),'jobs':1,'actual_files':sum(v['copied_actual_file']for v in index['by_node'].values()),**proof2}));return run.returncode or not proof2['byte_identical']
if __name__=='__main__':raise SystemExit(main())

