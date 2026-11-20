"""Copy closed APD02 mechanism evidence without dense worlds; never create a Runtime."""
import argparse,hashlib,json,shutil,subprocess,sys,tempfile,zlib
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf8',newline='\n')as f:f.write(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--stage',type=Path,required=True);p.add_argument('--system',type=Path,required=True);args=p.parse_args();here=Path(__file__).parent
    if args.stage.exists():raise FileExistsError('New closed stage only')
    if args.stage.resolve().is_relative_to(args.evidencia.resolve()):raise ValueError('Stage must not become its own source')
    args.stage.mkdir(parents=True);omitted=[];included=[]
    for file in sorted(args.evidencia.rglob('*')):
        if not file.is_file():continue
        rel=file.relative_to(args.evidencia).as_posix()
        if file.name.endswith('.deetsnap.gz'):
            omitted.append({'file':rel,'local_locator':str(file.resolve()),'bytes':file.stat().st_size,'sha256':sha(file),'reason':'Complete native world retained locally; not reconstructed from compact telemetry'})
            continue
        target=args.stage/'EVIDENCIA'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(file,target);included.append({'source':str(file.resolve()),'file':target.relative_to(args.stage).as_posix(),'sha256':sha(target)})
    for file in sorted(here.glob('*.py'))+sorted(here.glob('PROTOCOLO*.json')):
        target=args.stage/'CODIGO_Y_PROTOCOLOS'/file.name;target.parent.mkdir(exist_ok=True);shutil.copyfile(file,target)
    for name,target in(('recalcular_mecanismo_apd02.py','RECALCULO/recalcular_mecanismo_apd02.py'),('RECALCULO_MECANISMO_APD02_R01.json','RECALCULO/REFERENCIA.json'),('INFORME_MECANISMO_APD02.md','INFORME_MECANISMO_APD02.md')):
        dest=args.stage/target;dest.parent.mkdir(exist_ok=True);shutil.copyfile(here/name,dest)
    root=args.system.parent;lab=args.evidencia.parent.parent.parent.parent/'laboratorio'
    # These two immutable parent preflight artifacts are explanatory N0 inputs,
    # not dependencies of the portable arithmetic/RAW recalculation.
    campaign=root/'laboratorio/campanas/APD02_CONTINUIDAD_CALIDAD_ADAPTACION'
    for source in(campaign/'preflight_ruta_r04_n0.py',root/'evidencia/campanas/APD02_CONTINUIDAD_CALIDAD_ADAPTACION/PREFLIGHT_R04_N0.json'):
        if not source.is_file():raise FileNotFoundError(source)
        target=args.stage/'GEOMETRIA_N0'/source.name;target.parent.mkdir(exist_ok=True);shutil.copyfile(source,target)
    emit(args.stage/'INDICE_FUENTES_Y_OMISIONES.json',{'included_original_files':included,'omitted_dense_worlds':omitted,'dense_worlds_omitted':len(omitted),'scope':'All compact source primaries, successes, negative controls and instrumental errors retained byte-exact. Complete worlds stay at private local locators; no motor, WHL, service SQLite, promotion or imported learned contents. Source preimages explicitly named NO_EJECUTADO were not native tests.'})
    emit(args.stage/'PLAN_RECALCULO.json',{'jobs':[{'id':'MECANISMO_APD02_TODOS','name':'MECANISMO_APD02_TODOS','base':'.','script':'RECALCULO/recalcular_mecanismo_apd02.py','args':['--evidencia','EVIDENCIA','--salida','{output}'],'reference':'RECALCULO/REFERENCIA.json'}],'runtime_required':False,'native_ticks':0})
    # One new relocated stdlib check; the evidence is copied, not re-run natively.
    test=Path(tempfile.mkdtemp(prefix='apd02_mechanism_n0_'));copied=test/'STAGE';shutil.copytree(args.stage,copied);output=test/'RECALCULADO.json'
    completed=subprocess.run([sys.executable,'-I','-B',str(copied/'RECALCULO/recalcular_mecanismo_apd02.py'),'--evidencia',str(copied/'EVIDENCIA'),'--salida',str(output)],capture_output=True,text=True,encoding='utf8')
    equal=output.is_file()and output.read_bytes()==(args.stage/'RECALCULO/REFERENCIA.json').read_bytes()
    emit(args.stage/'PRUEBA_PORTABLE.json',{'scope':'Fresh relocated copy; stdlib archived recalculation, no Runtime/import of DEE','exit_code':completed.returncode,'reference_sha256':sha(args.stage/'RECALCULO/REFERENCIA.json'),'recomputed_sha256':sha(output)if output.is_file()else None,'byte_identical':equal,'stdout':completed.stdout,'stderr':completed.stderr,'command':['python','-I','-B','RECALCULO/recalcular_mecanismo_apd02.py','--evidencia','EVIDENCIA','--salida','OUTSIDE/RESULTADOS.json'],'original_system_or_lab_required':False,'native_ticks':0})
    if completed.returncode or not equal:raise RuntimeError('Portable check failed; stage remains adversarial/not CLOSED')
    emit(args.stage/'CERRADO.json',{'status':'CLOSED','native_experiments_finished':True,'portable_recalculation_byte_identical':True,'new_native_ticks_in_build':0,'operational_MAIN_not_advanced':True,'limitations':'This stage is physical AUX research, not a cloned service or replacement active individual.'})
    files=[{'file':f.relative_to(args.stage).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)}for f in sorted(args.stage.rglob('*'))if f.is_file()]
    emit(args.stage/'MANIFIESTO.json',{'files':files,'file_count_excluding_manifest':len(files),'no_self_hash':True})
    allfiles=[f for f in args.stage.rglob('*')if f.is_file()]
    print(json.dumps({'stage':str(args.stage),'manifest_sha256':sha(args.stage/'MANIFIESTO.json'),'files':len(allfiles),'expanded_bytes':sum(f.stat().st_size for f in allfiles),'individual_zlib6_bytes_estimate':sum(len(zlib.compress(f.read_bytes(),6))for f in allfiles),'portable_byte_identical':equal},sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
