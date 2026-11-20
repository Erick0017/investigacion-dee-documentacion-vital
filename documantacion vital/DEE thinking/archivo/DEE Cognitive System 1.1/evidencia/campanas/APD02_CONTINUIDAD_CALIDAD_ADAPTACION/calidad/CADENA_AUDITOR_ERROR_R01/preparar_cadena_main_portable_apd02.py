"""Copy exact closed first-chain evidence and actual effects; no native replay."""
import argparse,gzip,hashlib,json,shutil,subprocess,sys
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def write(p,x):
    with p.open('x',encoding='utf8')as f:json.dump(x,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--origen',type=Path,required=True);p.add_argument('--efectos',type=Path,required=True);p.add_argument('--stage',type=Path,required=True);p.add_argument('--portable',type=Path,required=True);a=p.parse_args()
    source=a.origen.resolve();effects=a.efectos.resolve();stage=a.stage.resolve();portable=a.portable.resolve()
    if stage.exists()or portable.exists():raise FileExistsError('New destinations only; closed evidence is never overwritten')
    stage.mkdir(parents=True);ev=stage/'EVIDENCIA';ev.mkdir();recalc=stage/'RECALCULO';recalc.mkdir()
    names=['ADMISIONES.jsonl','CODIGO_EJECUTADO.py','FUENTES_ANTES_TICKS.json','OWNER_ERR.txt','OWNER_OUT.txt','PROTOCOLO.json','REGISTROS_VENTANA.json.gz','RESUMEN.json']
    for name in names:shutil.copy2(source/name,ev/name)
    shutil.copytree(source/'codigo',stage/'FUENTES')
    captured=read(source/'FUENTES_ANTES_TICKS.json')
    for row in captured:
        f=stage/'FUENTES'/row['file']
        if f.stat().st_size!=row['bytes']or sha(f)!=row['sha256']:raise ValueError('Executed source copy mismatch: '+row['file'])
    x=read(source/'REGISTROS_VENTANA.json.gz');index={'by_slot':{},'source_primary_sha256':sha(source/'REGISTROS_VENTANA.json.gz'),'scope':'Exact actual JSON files copied only from the matching executed event directory, never from another life or an equal-name artifact elsewhere.'}
    for identifier,transport in x['records'].items():
        if identifier.endswith('_parsed'):continue
        parsed=json.loads(transport['result'])
        for slot,row in enumerate(parsed.get('result',{}).get('rows',[])):
            if row.get('kind')!='APD02_quality_request':continue
            folder=Path(row['effect_directory']).resolve()
            if not folder.is_relative_to(effects):raise ValueError('Actual effect directory outside this declared life')
            artifact=row['committed_effect']['artifact'];relative=Path('ARTEFACTOS')/(identifier+'_'+str(slot));dest=ev/relative;dest.mkdir(parents=True)
            item={'directory':relative.as_posix(),'source_directory_locator':str(folder),'artifact':artifact,'copied_actual_file':False}
            if artifact:
                path=folder/artifact['relative_path']
                if not path.resolve().is_relative_to(folder):raise ValueError('Unsafe actual receipt path')
                if path.stat().st_size!=artifact['bytes']or sha(path)!=artifact['sha256']:raise ValueError('Actual committed effect bytes disagree: '+str(path))
                shutil.copy2(path,dest/artifact['relative_path']);item['copied_actual_file']=True
            index['by_slot'][identifier+':'+str(slot)]=item
    write(ev/'ARTEFACTOS.json',index)
    calculator=Path(__file__).with_name('recalcular_cadena_main_apd02.py');shutil.copy2(calculator,recalc/calculator.name)
    args=['--evidencia','EVIDENCIA','--evaluador','FUENTES/capacidades/evaluador_calidad_apd02.py','--salida','{output}'];reference=stage/'REFERENCIA_CADENA_MAIN.json'
    run=subprocess.run([sys.executable,'-I','-B','-X','utf8','RECALCULO/'+calculator.name,*[str(reference)if x=='{output}'else x for x in args]],cwd=stage,capture_output=True,text=True,encoding='utf8',timeout=60)
    if run.returncode:print(run.stdout);print(run.stderr);return run.returncode
    plan={'jobs':[{'name':'CADENA_MAIN_APD02_R01_RAW_CALIDAD_FIFO','base':'.','script':'RECALCULO/'+calculator.name,'args':args,'reference':reference.name}],'scope':'Archived exact records and actual exported effects only; no Runtime or native reproduction. Private reference arithmetic is external auditing and never fed back.'};write(stage/'PLAN_RECALCULO.json',plan)
    shutil.copytree(stage,portable);out=portable/'RECALCULADO.json'
    second=subprocess.run([sys.executable,'-I','-B','-X','utf8','RECALCULO/'+calculator.name,*[str(out)if x=='{output}'else x for x in args]],cwd=portable,capture_output=True,text=True,encoding='utf8',timeout=60)
    proof={'returncode':second.returncode,'stdout':second.stdout,'stderr':second.stderr,'byte_identical':out.exists()and sha(out)==sha(reference),'reference_sha256':sha(reference),'native_ticks':0,'actual_effect_files':sum(v['copied_actual_file']for v in index['by_slot'].values())};write(stage/'PRUEBA_PORTABLE.json',proof)
    files=[{'file':p.relative_to(stage).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(stage.rglob('*'))if p.is_file()];write(stage/'MANIFIESTO.json',{'files':files,'scope':'Manifest excludes only itself; exact closed sources/primary/effects and portable proof included. Complete native checkpoints and full persistent database remain local and are not claims of this arithmetic/file recalculation.'})
    print(json.dumps({'stage':str(stage),'reference':str(reference),'byte_identical':proof['byte_identical'],'issues':read(reference)['issues'],'files':len(files)+1}));return second.returncode or not proof['byte_identical']
if __name__=='__main__':raise SystemExit(main())
