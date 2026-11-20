"""Select only existing CLOSED baseline/lexical records and their exact source."""
import argparse,hashlib,json,shutil,subprocess,sys
from pathlib import Path

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(p,v):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
def cp(a,b):b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(a,b)
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--stage',type=Path,required=True);p.add_argument('--portable',type=Path,required=True);a=p.parse_args();root=a.root.resolve();stage=a.stage.resolve();portable=a.portable.resolve();lab=root/'laboratorio/campanas/APD02_CONTINUIDAD_CALIDAD_ADAPTACION';ev=root/'evidencia/campanas/APD02_CONTINUIDAD_CALIDAD_ADAPTACION';base=ev/'BASELINE_R01';lex=ev/'LENGUAJE_R01'
    if stage.exists()or portable.exists():raise FileExistsError('Preserve all preparation revisions')
    closed=read(base/'RESUMEN.json')
    if closed.get('pending')or closed.get('owner_final',{}).get('running',True)or closed.get('owner_returncode')!=0:raise ValueError('Baseline is not the existing CLOSED operational window')
    stage.mkdir(parents=True);dest=stage/'EVIDENCIA';rc=stage/'RECALCULO';rc.mkdir();sources=[]
    for name in('REGISTROS_VENTANA.json.gz','PROTOCOLO.json','RESUMEN.json','ADMISIONES.jsonl','FUENTES_ANTES_TICKS.json','CODIGO_EJECUTADO.py','OWNER_OUT.txt','OWNER_ERR.txt'):cp(base/name,dest/'BASELINE'/name)
    for row in read(base/'FUENTES_ANTES_TICKS.json'):
        f=base/'codigo'/row['file']
        if f.stat().st_size!=row['bytes']or sha(f)!=row['sha256']:raise ValueError('Original baseline source bytes differ')
        cp(f,dest/'BASELINE/CODIGO_EJECUTADO'/row['file']);sources.append({'relative':row['file'],'sha256':row['sha256'],'bytes':row['bytes']})
    for name in('PRIMARIOS_COMPLETOS.json.gz','PROTOCOLO.json','lexico_apd02_01.py','probar_lenguaje_apd02_r01.py','PROGRESO.json'):cp(lex/name,dest/'LENGUAJE_R01'/name)
    cp(ev/'RECALCULO_REPERTORIO_R01.json',dest/'ORIGINAL_RECALCULO_REPERTORIO_R01.json');cp(lab/'recalcular_repertorio_apd02.py',rc/'ORIGINAL_recalcular_repertorio_apd02.py')
    cp(ev/'PRESUPUESTO_E_IDENTIDAD_INICIAL.json',dest/'PRESUPUESTO_E_IDENTIDAD_INICIAL.json')
    for life in('APD02_MAIN','APD02_BASELINE'):cp(root/'sistema/estado/servicios_persistentes'/life/'IMPORTACION.json',dest/'RECIBOS_IMPORTACION'/(life+'.json'))
    cp(Path(__file__).with_name('repetir_baseline_original_n0.py'),rc/'repetir_baseline_original_n0.py');cp(Path(__file__),stage/'CODIGO_CIERRE'/Path(__file__).name)
    descriptor={key:{'file':path.relative_to(stage).as_posix(),'bytes':path.stat().st_size,'sha256':sha(path)}for key,path in(('original_script',rc/'ORIGINAL_recalcular_repertorio_apd02.py'),('original_reference',dest/'ORIGINAL_RECALCULO_REPERTORIO_R01.json'),('baseline_primary',dest/'BASELINE/REGISTROS_VENTANA.json.gz'),('language_primary',dest/'LENGUAJE_R01/PRIMARIOS_COMPLETOS.json.gz'))};descriptor['baseline_exact_source_inventory']=sources;descriptor['native_ticks']=0
    write(dest/'FUENTES_DEL_AUDITOR_ORIGINAL.json',descriptor)
    script='RECALCULO/repetir_baseline_original_n0.py';args=['--evidencia','EVIDENCIA','--salida','{output}'];ref=stage/'REFERENCIA_BASELINE_ORIGINAL_PORTABLE.json'
    first=subprocess.run([sys.executable,'-I','-B','-X','utf8',str(stage/script),'--evidencia',str(dest),'--salida',str(ref)],capture_output=True,text=True,encoding='utf8',timeout=120);write(stage/'PRIMER_RECALCULO_N0.json',{'returncode':first.returncode,'stdout':first.stdout,'stderr':first.stderr,'native_ticks':0})
    if first.returncode:raise RuntimeError('Original archived auditor check failed; attempted stage remains preserved')
    write(stage/'PLAN_RECALCULO.json',{'jobs':[{'name':'EXISTING_BASELINE_AND_LEXICAL_R01_ORIGINAL_AUDITOR','base':'.','script':script,'args':args,'reference':ref.name}],'scope':'One archived N0 job using the exact original auditor and existing inputs. No Native experiment, new learner or historical suite.'})
    (stage/'LEER_BASELINE.md').write_text('# Baseline original y procedencia\n\nEste namespace conserva el diagnóstico material APD02_BASELINE desdeT361114: seis contextos y seis formas numéricas, más COUNT. La vida es una copia diagnóstica; sus usos no se suman como experiencia de MAIN. Los recibos emparejados conservan el origen0046 y los distintos encodings c93a…/3216…; la igualdad se limita a los campos físicos y padre registrados, no a toda identidad documental.\n\nEl auditor original se conserva byte por byte y se ejecuta con su misma CLI. El wrapper normaliza únicamente las dos cadenas documentales de localización de sus entradas y exige igualdad del resto del resultado original. Se incluyen también sus seis historias léxicas R01, con los fallos, porque son la segunda entrada real de aquel recálculo. No se repite física ni se cambian sus resultados.\n',encoding='utf8')
    write(stage/'OMISIONES.json',{'complete_worlds_and_SQLite':'Retained locally at paths and SHA in original baseline summary/import receipts and budget identity. No complete snapshot, SQLite journal, engine or wheel is included here.','exact_original_sources_selected_from_inventory':len(sources),'no_raw_primary_or_original_recalc_input_omitted':True,'no_historical_states_rehashed_or_evolved':True})
    shutil.copytree(stage,portable);out=portable/'RECALCULADO_BASELINE.json';second=subprocess.run([sys.executable,'-I','-B','-X','utf8',script,*[str(out)if v=='{output}'else v for v in args]],cwd=portable,capture_output=True,text=True,encoding='utf8',timeout=120);proof={'returncode':second.returncode,'stdout':second.stdout,'stderr':second.stderr,'reference_sha256':sha(ref),'byte_identical':out.exists()and sha(out)==sha(ref),'new_native_ticks':0,'new_provider_calls':0};write(stage/'PRUEBA_PORTABLE.json',proof)
    if second.returncode or not proof['byte_identical']:raise RuntimeError('Portable original-auditor output not byte identical')
    rows=[{'file':f.relative_to(stage).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)}for f in sorted(stage.rglob('*'))if f.is_file()];write(stage/'MANIFIESTO.json',{'status':'CLOSED','files':rows,'scope':'Existing closed baseline and original lexical physical primaries, original source/reference, declared import receipts and one portable N0 calculation. Manifest excludes itself.'});print(json.dumps({'stage':str(stage),'manifest_sha256':sha(stage/'MANIFIESTO.json'),'files':len(rows)+1,'bytes':sum(f.stat().st_size for f in stage.rglob('*')if f.is_file()),'jobs':1,'native_ticks':0,'issues':read(ref)['issues']}))
if __name__=='__main__':main()
