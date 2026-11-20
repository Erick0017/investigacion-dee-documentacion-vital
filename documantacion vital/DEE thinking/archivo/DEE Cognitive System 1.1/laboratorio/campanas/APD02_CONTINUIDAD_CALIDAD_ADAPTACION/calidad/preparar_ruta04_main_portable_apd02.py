"""Copy a closed R04 window once, including its exact selected real JSON files."""
import argparse,hashlib,importlib.util,json,shutil,subprocess,sys
from pathlib import Path
def read(p):
    import gzip
    return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):
    with p.open('x',encoding='utf8')as f:json.dump(x,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--origen',type=Path,required=True);p.add_argument('--efectos',type=Path,required=True);p.add_argument('--historia-r03',type=Path,required=True);p.add_argument('--stage',type=Path,required=True);p.add_argument('--portable',type=Path,required=True);a=p.parse_args();stage=a.stage.resolve();portable=a.portable.resolve();source=a.origen.resolve();effects=a.efectos.resolve()
    if stage.exists()or portable.exists():raise FileExistsError('Never overwrite a preceding audit, stage or adverse future')
    if not(source/'RESUMEN.json').is_file():raise ValueError('The executed window is not closed; do not read a live journal instead')
    stage.mkdir(parents=True);ev=stage/'EVIDENCIA';ev.mkdir();rc=stage/'RECALCULO';rc.mkdir()
    for name in('REGISTROS_VENTANA.json.gz','PROTOCOLO.json','ADMISIONES.jsonl','CODIGO_EJECUTADO.py','FUENTES_ANTES_TICKS.json','RESUMEN.json','OWNER_OUT.txt','OWNER_ERR.txt'):shutil.copy2(source/name,ev/name)
    shutil.copytree(source/'codigo',stage/'FUENTES')
    for row in read(source/'FUENTES_ANTES_TICKS.json'):
        file=stage/'FUENTES'/row['file']
        if file.stat().st_size!=row['bytes']or sha(file)!=row['sha256']:raise ValueError('Frozen executed-source mismatch')
    shutil.copy2(a.historia_r03,ev/'HISTORIA_R03.json.gz')
    for name in('recalcular_cadena_main_apd02.py','recalcular_ruta04_main_apd02.py'):shutil.copy2(Path(__file__).with_name(name),rc/name)
    x=read(source/'REGISTROS_VENTANA.json.gz');index={'by_slot':{},'source_primary_sha256':sha(source/'REGISTROS_VENTANA.json.gz'),'scope':'Only exact files from the matched executed event directory. Original directories are localizers, never consulted by the portable calculator. No artifact is reconstructed from a target or another life.'}
    for identifier,transport in x['records'].items():
        if identifier.endswith('_parsed'):continue
        parsed=json.loads(transport['result'])
        for slot,row in enumerate(parsed.get('result',{}).get('rows',[])):
            if row.get('kind')!='APD02_quality_request':continue
            folder=Path(row['effect_directory']).resolve()
            if not folder.is_relative_to(effects):raise ValueError('Effect outside declared actual-life tree')
            relative=Path('ARTEFACTOS')/(identifier+'_'+str(slot));artifact=row['committed_effect']['artifact'];item={'directory':relative.as_posix(),'source_directory_locator':str(folder),'copied_actual_file':False,'artifact':artifact}
            if artifact:
                actual=folder/artifact['relative_path']
                if not actual.resolve().is_relative_to(folder)or actual.stat().st_size!=artifact['bytes']or sha(actual)!=artifact['sha256']:raise ValueError('Real archived effect bytes/hash differ')
                dest=ev/relative;dest.mkdir(parents=True);shutil.copy2(actual,dest/artifact['relative_path']);item['copied_actual_file']=True
            index['by_slot'][identifier+':'+str(slot)]=item
    write(ev/'ARTEFACTOS.json',index)
    script='RECALCULO/recalcular_ruta04_main_apd02.py';evaluator='FUENTES/capacidades/evaluador_calidad_apd02.py';route='FUENTES/capacidades/ruta_adaptativa_apd02_04.py';ref=stage/'REFERENCIA_RUTA04_MAIN.json';args=['--evidencia','EVIDENCIA','--evaluador',evaluator,'--fuente-ruta',route,'--salida','{output}']
    first=subprocess.run([sys.executable,'-I','-B','-X','utf8',str(stage/script),'--evidencia',str(ev),'--evaluador',str(stage/evaluator),'--fuente-ruta',str(stage/route),'--salida',str(ref)],capture_output=True,text=True,encoding='utf8',timeout=90)
    if first.returncode:print(first.stdout);print(first.stderr);return first.returncode
    write(stage/'PLAN_RECALCULO.json',{'jobs':[{'name':'MAIN_RUTA04_ABAB_RAW_EFECTOS_CALIDAD','base':'.','script':script,'args':args,'reference':ref.name}],'scope':'Archived RAW/receipt/real-effect/quality calculation, no engine or new native tick.'})
    shutil.copytree(stage,portable);out=portable/'RECALCULADO.json';second=subprocess.run([sys.executable,'-I','-B','-X','utf8',script,*[str(out)if v=='{output}'else v for v in args]],cwd=portable,capture_output=True,text=True,encoding='utf8',timeout=90)
    proof={'returncode':second.returncode,'stdout':second.stdout,'stderr':second.stderr,'byte_identical':out.exists()and sha(out)==sha(ref),'reference_sha256':sha(ref),'new_native_ticks':0,'new_provider_calls':0,'actual_artifact_files':sum(i['copied_actual_file']for i in index['by_slot'].values())};write(stage/'PRUEBA_PORTABLE.json',proof)
    files=[{'file':f.relative_to(stage).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)}for f in sorted(stage.rglob('*'))if f.is_file()];write(stage/'MANIFIESTO.json',{'files':files,'scope':'All exact closed primary/code/actual JSON effects, reference and portable proof; complete operational native snapshots/journal remain local. Manifest excludes itself.'})
    print(json.dumps({'stage':str(stage),'files':len(files)+1,'byte_identical':proof['byte_identical'],'issues':read(ref)['issues'],'native_ticks':0}));return second.returncode or not proof['byte_identical']
if __name__=='__main__':raise SystemExit(main())
