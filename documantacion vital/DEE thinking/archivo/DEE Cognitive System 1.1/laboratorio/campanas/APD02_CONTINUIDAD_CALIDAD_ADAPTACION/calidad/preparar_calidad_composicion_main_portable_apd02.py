"""Export one closed APD02 quality/composition window and its exact real files."""
import argparse,hashlib,importlib.util,json,shutil,subprocess,sys
from pathlib import Path

def read(p):
    import gzip
    return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,value):
    with p.open('x',encoding='utf8')as f:json.dump(value,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
def walk(value,path='$'):
    yield path,value
    if isinstance(value,dict):
        for k,v in value.items():yield from walk(v,path+'.'+k)
    elif isinstance(value,list):
        for k,v in enumerate(value):yield from walk(v,path+'['+str(k)+']')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--origen',type=Path,required=True);p.add_argument('--efectos',type=Path,required=True);p.add_argument('--stage',type=Path,required=True);p.add_argument('--portable',type=Path,required=True);a=p.parse_args();stage=a.stage.resolve();portable=a.portable.resolve();source=a.origen.resolve();effects=a.efectos.resolve()
    if stage.exists()or portable.exists():raise FileExistsError('Preserve all earlier attempts and stages')
    if not(source/'RESUMEN.json').is_file():raise ValueError('Only a closed window may be exported, never a live SQLite journal')
    stage.mkdir(parents=True);ev=stage/'EVIDENCIA';ev.mkdir();rc=stage/'RECALCULO';rc.mkdir()
    for name in('REGISTROS_VENTANA.json.gz','PROTOCOLO.json','ADMISIONES.jsonl','CODIGO_EJECUTADO.py','FUENTES_ANTES_TICKS.json','RESUMEN.json','OWNER_OUT.txt','OWNER_ERR.txt'):shutil.copy2(source/name,ev/name)
    shutil.copytree(source/'codigo',stage/'FUENTES')
    for row in read(source/'FUENTES_ANTES_TICKS.json'):
        file=stage/'FUENTES'/row['file']
        if file.stat().st_size!=row['bytes']or sha(file)!=row['sha256']:raise ValueError('Frozen exact-source mismatch')
    for name in('recalcular_cadena_main_apd02.py','recalcular_ruta04_main_apd02.py','auditar_efecto_apd02.py','recalcular_calidad_composicion_main_apd02.py'):shutil.copy2(Path(__file__).with_name(name),rc/name)
    x=read(source/'REGISTROS_VENTANA.json.gz');index={'by_node':{},'primary_sha256':sha(source/'REGISTROS_VENTANA.json.gz'),'scope':'Exact event/nested-stage directories and existing real files only; not reconstructed values, filename search, another life, or a currently active journal.'}
    for identifier,t in x['records'].items():
        if identifier.endswith('_parsed'):continue
        parsed=json.loads(t['result'])
        for slot,row in enumerate(parsed.get('result',{}).get('rows',[])):
            material=[(identifier+':'+str(slot),row)]if row.get('kind')=='APD02_quality_request'else[(identifier+':'+str(slot)+':stage:'+str(j),r)for j,r in enumerate(row.get('rows',[]))if r.get('kind')=='APD02_quality_request']
            for label,actual_row in material:
                folder=Path(actual_row['effect_directory']).resolve()
                if not folder.is_relative_to(effects):raise ValueError('Actual effect outside declared original life tree')
                relative=Path('ARTEFACTOS')/label.replace(':','_');artifact=actual_row['committed_effect']['artifact'];item={'directory':relative.as_posix(),'source_directory_locator':str(folder),'artifact':artifact,'copied_actual_file':False}
                if artifact:
                    original=folder/artifact['relative_path']
                    if not original.resolve().is_relative_to(folder)or original.stat().st_size!=artifact['bytes']or sha(original)!=artifact['sha256']:raise ValueError('Actual archived file differs from the committed receipt')
                    dest=ev/relative;dest.mkdir(parents=True);shutil.copy2(original,dest/artifact['relative_path']);item['copied_actual_file']=True
                index['by_node'][label]=item
    write(ev/'ARTEFACTOS.json',index)
    script='RECALCULO/recalcular_calidad_composicion_main_apd02.py';evaluator='FUENTES/capacidades/evaluador_calidad_apd02.py';route='FUENTES/capacidades/ruta_adaptativa_apd02_04.py';ref=stage/'REFERENCIA_CALIDAD_COMPOSICION_MAIN.json';args=['--evidencia','EVIDENCIA','--evaluador',evaluator,'--fuente-ruta',route,'--salida','{output}']
    first=subprocess.run([sys.executable,'-I','-B','-X','utf8',str(stage/script),'--evidencia',str(ev),'--evaluador',str(stage/evaluator),'--fuente-ruta',str(stage/route),'--salida',str(ref)],capture_output=True,text=True,encoding='utf8',timeout=90)
    if first.returncode:print(first.stdout);print(first.stderr);return first.returncode
    write(stage/'PLAN_RECALCULO.json',{'jobs':[{'name':'MAIN_QUALITY_COMPOSITION_FIXED_RAW_REAL_FILES','base':'.','script':script,'args':args,'reference':ref.name}],'scope':'Archived RAW/receipt/actual-file/post-action-quality computation only; no Runtime/provider/new native tick.'})
    shutil.copytree(stage,portable);out=portable/'RECALCULADO.json';second=subprocess.run([sys.executable,'-I','-B','-X','utf8',script,*[str(out)if v=='{output}'else v for v in args]],cwd=portable,capture_output=True,text=True,encoding='utf8',timeout=90)
    proof={'returncode':second.returncode,'stdout':second.stdout,'stderr':second.stderr,'byte_identical':out.exists()and sha(out)==sha(ref),'reference_sha256':sha(ref),'new_native_ticks':0,'new_provider_calls':0,'actual_file_count':sum(i['copied_actual_file']for i in index['by_node'].values())};write(stage/'PRUEBA_PORTABLE.json',proof)
    files=[{'file':f.relative_to(stage).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)}for f in sorted(stage.rglob('*'))if f.is_file()];write(stage/'MANIFIESTO.json',{'files':files,'scope':'All exact primaries, captured executed sources, real files and portable proof. The manifest excludes itself. Full native snapshots and operational journal remain local.'})
    print(json.dumps({'stage':str(stage),'files':len(files)+1,'byte_identical':proof['byte_identical'],'issues':read(ref)['issues'],'native_ticks':0}));return second.returncode or not proof['byte_identical']
if __name__=='__main__':raise SystemExit(main())
