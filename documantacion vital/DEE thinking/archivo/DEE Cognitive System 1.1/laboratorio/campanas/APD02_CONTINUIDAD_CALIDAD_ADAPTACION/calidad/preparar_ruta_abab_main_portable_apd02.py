"""Export exact closed R03 route records and read-only full-field projections."""
import argparse,collections,gzip,hashlib,importlib.util,json,shutil,subprocess,sys
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def write(p,x):
    with p.open('x',encoding='utf8')as f:json.dump(x,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sistema',type=Path,required=True);p.add_argument('--origen',type=Path,required=True);p.add_argument('--historia',type=Path,required=True);p.add_argument('--stage',type=Path,required=True);p.add_argument('--portable',type=Path,required=True);a=p.parse_args();stage=a.stage.resolve();portable=a.portable.resolve();source=a.origen.resolve();system=a.sistema.resolve()
    if stage.exists()or portable.exists():raise FileExistsError('New destinations only')
    stage.mkdir(parents=True);ev=stage/'EVIDENCIA';ev.mkdir();recalc=stage/'RECALCULO';recalc.mkdir()
    for name in('REGISTROS_VENTANA.json.gz','PROTOCOLO.json','ADMISIONES.jsonl','CODIGO_EJECUTADO.py','FUENTES_ANTES_TICKS.json','RESUMEN.json','OWNER_OUT.txt','OWNER_ERR.txt'):shutil.copy2(source/name,ev/name)
    shutil.copytree(source/'codigo',stage/'FUENTES')
    for row in read(source/'FUENTES_ANTES_TICKS.json'):
        f=stage/'FUENTES'/row['file']
        if sha(f)!=row['sha256']or f.stat().st_size!=row['bytes']:raise ValueError('Executed-source mismatch')
    shutil.copy2(a.historia,ev/'HISTORIA_MAIN_CADENA_R01.json.gz')
    for name in('recalcular_cadena_main_apd02.py','recalcular_ruta_abab_main_apd02.py'):shutil.copy2(Path(__file__).with_name(name),recalc/name)
    observer_source=system/'capacidades/observador_causal_retrospectivo_01.py';shutil.copy2(observer_source,recalc/observer_source.name)
    spec=importlib.util.spec_from_file_location('read_only_complete_snapshot',observer_source);observer=importlib.util.module_from_spec(spec);spec.loader.exec_module(observer)
    x=read(source/'REGISTROS_VENTANA.json.gz');projection={'snapshots':{},'observer_sha256':sha(observer_source),'native_ticks':0,'scope':'Read-only full snapshot v2 parsing, encoded SHA and FNV checksum verified before exporting complete sparse RAW+clocks. No Runtime or metadata execution. Actual full checkpoints remain local.'}
    for label,key in(('INITIAL','initial'),('FINAL','final')):
        record=x[key];path=system/record['snapshot'];s=observer.Snapshot(path)
        if s.encoded_sha256!=record['snapshot_sha256']:raise ValueError('Wrong exact snapshot')
        for field,values in(('RAW_sha256',s.raw),('clocks_sha256',s.clocks)):
            if observer.sha(observer.pbytes(values))!=record['physical'][field]:raise ValueError('Full physical vector SHA differs from closed primary')
        default=collections.Counter(s.clocks).most_common(1)[0][0];routekey='DEE.Cognitive.System.1.1.APD02.delayed_action_trace.R03'
        route=json.loads(s.metadata[routekey])if routekey in s.metadata else None
        projection['snapshots'][label]={'snapshot_locator':record['snapshot'],'snapshot_sha256':s.encoded_sha256,'snapshot_bytes':s.encoded_bytes,'checksum_valid':s.checksum_valid,'N':s.N,'tick':s.tick,'RAW_sha256':observer.sha(observer.pbytes(s.raw)),'clocks_sha256':observer.sha(observer.pbytes(s.clocks)),'raw_nonzero':[[i,str(v)]for i,v in enumerate(s.raw)if v],'clock_default':str(default),'clock_exceptions':[[i,str(v)]for i,v in enumerate(s.clocks)if v!=default],'native_pending':s.pending,'selected_metadata':{'route':route},'selected_channels':{name:c for name,c in s.channels.items()if name.startswith('APD02.trace.R03.')},'final_receipt_table_locator':'Complete exact receipt table remains in local snapshot; per-intervention status copies are exported in the primary.'}
    with gzip.GzipFile(filename=str(ev/'PROYECCION_SNAPSHOTS.json.gz'),mode='wb',mtime=0)as f:f.write((json.dumps(projection,sort_keys=True,ensure_ascii=False,indent=2)+'\n').encode())
    artifacts={'by_slot':{},'source_primary_sha256':sha(source/'REGISTROS_VENTANA.json.gz'),'scope':'No tool was invoked and no artifact receipt was formed in these twelve no-route opportunities; no synthetic substitute files are created.'}
    for identifier,row in x['records'].items():
        if identifier.endswith('_parsed'):continue
        parsed=json.loads(row['result'])
        for slot,result in enumerate(parsed.get('result',{}).get('rows',[])):
            if result.get('kind')=='APD02_quality_request':
                if result['committed_effect'].get('artifact')is not None:raise ValueError('New actual effect exists: this negative-only export must not omit it')
                artifacts['by_slot'][identifier+':'+str(slot)]={'artifact':None,'copied_actual_file':False,'effect_directory_locator':result['effect_directory']}
    write(ev/'ARTEFACTOS.json',artifacts)
    script='RECALCULO/recalcular_ruta_abab_main_apd02.py';args=['--evidencia','EVIDENCIA','--evaluador','FUENTES/capacidades/evaluador_calidad_apd02.py','--salida','{output}'];ref=stage/'REFERENCIA_RUTA_ABAB.json'
    first=subprocess.run([sys.executable,'-I','-B','-X','utf8',str(stage/script),'--evidencia',str(ev),'--evaluador',str(stage/'FUENTES/capacidades/evaluador_calidad_apd02.py'),'--salida',str(ref)],capture_output=True,text=True,encoding='utf8',timeout=60)
    if first.returncode:print(first.stdout);print(first.stderr);return first.returncode
    write(stage/'PLAN_RECALCULO.json',{'jobs':[{'name':'RUTA_ABAB_MAIN_R03_NEGATIVO','base':'.','script':script,'args':args,'reference':ref.name}],'scope':'Archived full-field SHA reconstruction, per-request receipt resolutions, fixed RAW decoders and post-action no-response quality only; no native replay.'})
    shutil.copytree(stage,portable);out=portable/'RECALCULADO.json';second=subprocess.run([sys.executable,'-I','-B','-X','utf8',script,*[str(out)if v=='{output}'else v for v in args]],cwd=portable,capture_output=True,text=True,encoding='utf8',timeout=60)
    proof={'returncode':second.returncode,'stdout':second.stdout,'stderr':second.stderr,'byte_identical':out.exists()and sha(out)==sha(ref),'reference_sha256':sha(ref),'native_ticks':0,'engine_imported':False};write(stage/'PRUEBA_PORTABLE.json',proof)
    files=[{'file':f.relative_to(stage).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)}for f in sorted(stage.rglob('*'))if f.is_file()];write(stage/'MANIFIESTO.json',{'files':files,'scope':'Manifest excludes itself only. Whole local snapshots omitted with encoded SHA and full physical projections; journal is not replaced by this analysis.'})
    print(json.dumps({'stage':str(stage),'files':len(files)+1,'byte_identical':proof['byte_identical'],'issues':read(ref)['issues'],'native_ticks':0}));return second.returncode or not proof['byte_identical']
if __name__=='__main__':raise SystemExit(main())
