"""Archive CLOSED MAIN/OMIT windows once and verify portable stdlib replay."""
import argparse,gzip,hashlib,json,shutil,subprocess,sys
from pathlib import Path

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def write(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
def copy_file(src,dst):dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
def closed_window(source,dest,permitted_effects):
    if not(source/'RESUMEN.json').is_file():raise ValueError('Window not CLOSED; never inspect its live database')
    x=read(source/'REGISTROS_VENTANA.json.gz')
    if x.get('owner_final',{}).get('running',True):raise ValueError('Original owner still running')
    dest.mkdir(parents=True)
    for name in('REGISTROS_VENTANA.json.gz','PROTOCOLO.json','ADMISIONES.jsonl','CODIGO_EJECUTADO.py','FUENTES_ANTES_TICKS.json','RESUMEN.json','OWNER_OUT.txt','OWNER_ERR.txt'):copy_file(source/name,dest/name)
    frozen=read(source/'FUENTES_ANTES_TICKS.json')
    for row in frozen:
        path=source/'codigo'/row['file']
        if path.stat().st_size!=row['bytes']or sha(path)!=row['sha256']:raise ValueError('Executed source mismatch: '+row['file'])
        copy_file(path,dest/'CODIGO_EJECUTADO'/row['file'])
    index={'by_slot':{},'source_primary_sha256':sha(source/'REGISTROS_VENTANA.json.gz'),'scope':'Exact actual committed files from the declared execution. No regeneration from references, expected values or another life.'}
    for identifier,t in x['records'].items():
        if identifier.endswith('_parsed')or not t.get('result'):continue
        parsed=json.loads(t['result'])
        for slot,row in enumerate(parsed.get('result',{}).get('rows',[])):
            if row.get('kind')!='APD02_quality_request':continue
            folder=Path(row['effect_directory']).resolve();artifact=row['committed_effect']['artifact'];relative=Path('ARTEFACTOS')/(identifier+'_'+str(slot))
            if not any(folder.is_relative_to(root)for root in permitted_effects):raise ValueError('Undeclared actual effect directory: '+str(folder))
            item={'directory':relative.as_posix(),'source_directory_locator':str(folder),'artifact':artifact,'copied_actual_file':False}
            if artifact:
                src=(folder/artifact['relative_path']).resolve()
                if not src.is_relative_to(folder)or src.stat().st_size!=artifact['bytes']or sha(src)!=artifact['sha256']:raise ValueError('Actual effect bytes no longer match committed receipt')
                copy_file(src,dest/relative/artifact['relative_path']);item['copied_actual_file']=True
            index['by_slot'][identifier+':'+str(slot)]=item
    write(dest/'ARTEFACTOS.json',index);return x,frozen

def main():
    p=argparse.ArgumentParser();p.add_argument('--main',type=Path,required=True);p.add_argument('--control-run',type=Path,required=True);p.add_argument('--binding',type=Path,required=True);p.add_argument('--efectos',type=Path,action='append',required=True);p.add_argument('--calidad-helpers',type=Path,required=True);p.add_argument('--stage',type=Path,required=True);p.add_argument('--portable',type=Path,required=True);a=p.parse_args()
    stage=a.stage.resolve();portable=a.portable.resolve();control=a.control_run.resolve();binding=a.binding.resolve();here=Path(__file__).parent;helpers=a.calidad_helpers.resolve();allowed=[v.resolve()for v in a.efectos]
    if stage.exists()or portable.exists():raise FileExistsError('Preserve every prior stage and proof')
    execution=read(control/'EJECUCION.json')
    if execution.get('error'):raise ValueError('Execution instrument failed; preserve it, do not certify a successful comparison')
    stage.mkdir(parents=True);ev=stage/'EVIDENCIA';rc=stage/'RECALCULO';rc.mkdir(parents=True)
    real,rs=closed_window(a.main.resolve(),ev/'MAIN',allowed);omit,os=closed_window(control/'VENTANA_OMIT',ev/'OMIT',allowed)
    for name in('VINCULACION_N0.json','MATERIAL_ROOT_FIJO.json','PROTOCOLO_MAIN_RESUELTO.json','PROTOCOLO_OMIT.json','CONFIG_EJECUCION.json','EJECUTOR_ORIGINAL.py'):copy_file(binding/name,ev/'BINDING'/name)
    for name in('PROTOCOLO_EJECUTADO_POSTIMPORT.json','VINCULACION_POSTIMPORT_N0.json','EJECUCION.json','CONFIG_EJECUTADA.json','FUENTE_CONTROL_EJECUTADA.py','01_IMPORTAR_PAR.stdout','01_IMPORTAR_PAR.stderr','02_VENTANA_ORIGINAL.stdout','02_VENTANA_ORIGINAL.stderr'):copy_file(control/name,ev/'BINDING'/name)
    for rel in('capacidades/ruta_adaptativa_apd02_04.py','capacidades/evaluador_calidad_apd02.py'):
        first=ev/'MAIN/CODIGO_EJECUTADO'/rel;second=ev/'OMIT/CODIGO_EJECUTADO'/rel
        if sha(first)!=sha(second):raise ValueError('Actor/evaluator revision differs between paired branches')
        copy_file(first,ev/'FUENTES'/Path(rel).name)
    for name in('recalcular_cadena_main_apd02.py','recalcular_ruta04_main_apd02.py','auditar_archivo_ventana_apd02.py','auditar_efecto_apd02_r02.py'):copy_file(helpers/name,rc/name)
    copy_file(here/'recalcular_calidad_reversible.py',rc/'recalcular_calidad_reversible.py')
    for file in here.glob('*.py'):copy_file(file,stage/'CODIGO_PREPARACION'/file.name)
    copy_file(here/'PLAN_CONTROL_OMIT_N0.md',stage/'PLAN_CONTROL_OMIT_N0.md')
    if(here/'PRUEBA_BINDER_N0_R01.json').is_file():copy_file(here/'PRUEBA_BINDER_N0_R01.json',stage/'PRUEBA_BINDER_N0_R01.json')
    for file in here.glob('ERROR_*_N0.json'):copy_file(file,stage/'INSTRUMENTACION_N0'/file.name)
    preceding=here/'CIERRE_CALIDAD_REVERSIBLE_R01'
    if preceding.is_dir():
        for name in('REFERENCIA_CALIDAD_REVERSIBLE.json','MANIFIESTO.json','PRUEBA_PORTABLE.json'):copy_file(preceding/name,stage/'INSTRUMENTACION_N0/R01_PRE_BINARY_CATEGORY'/name)
    script='RECALCULO/recalcular_calidad_reversible.py';args=['--evidencia','EVIDENCIA','--salida','{output}'];reference=stage/'REFERENCIA_CALIDAD_REVERSIBLE.json'
    first=subprocess.run([sys.executable,'-I','-B','-X','utf8',str(stage/script),'--evidencia',str(ev),'--salida',str(reference)],capture_output=True,text=True,encoding='utf8',timeout=120)
    write(stage/'PRIMER_RECALCULO.json',{'returncode':first.returncode,'stdout':first.stdout,'stderr':first.stderr,'native_ticks':0})
    if first.returncode:raise RuntimeError('Archived calculator failed; stage attempt preserved, no Native repeated')
    result=read(reference);lines=['# Calidad reversible a precios iguales: MAIN y control OMIT','','Dos continuaciones del mismo padre emparejado completo posthora; una sola historia prospectiva por brazo, no siete réplicas independientes. Anatomía, lector, proveedor, leyes y oportunidades preparados. Los números correctos privados se calculan únicamente después de los archivos comprometidos. El retorno al ente es sólo SUCCESS/FAILURE común, sin respuesta ni ruta recomendada.','','| Brazo | Evento | Ruta física | Proveedor | Categoría de calidad | Categoría al ente | D antes → después |','|---|---|---:|---|---|---|---|']
    for arm in('MAIN','OMIT'):
        for row in result[arm]['effects']:
            r=row['native_references'];change=str(r['before']['difference'])+' → '+str(r['after']['difference'])if r else'no retorno';lines.append('| '+arm+' | '+row['event']+':'+str(row['slot'])+' | '+str(row['route_choice'])+' | '+str(row['selected_procedure'])+' | '+row['category']+' | '+row['actor_feedback_category']+' | '+change+' |')
    lines+=['','La señal0 es una salida material +Y y se transduce a externo; no es silencio. Las siete oportunidades de tratamiento son2/3/2, seguidas por un commonprobe sin retorno y seis usos de formas anteriores:14 efectos APD por brazo. Los dos paneles de seis memorias, funciones nuevas y δ no inflan ese denominador. Beta fue enseñada+ deliberadamente durante la hora y se separa de los otros cinco contenidos.','']
    for arm in('MAIN','OMIT'):
        a=result[arm]['aggregate'];training=[r for r in result[arm]['effects']if r['trial_group']=='treatment'];lines+=['- '+arm+': calidad útil tratamiento '+str(sum(r['task_success_under_limits']is True for r in training))+'/'+str(len(training))+'; total '+str(a['quality_success'])+'/'+str(a['requested_APD_effects'])+'; archivos válidos '+str(a['actual_valid_files'])+'/'+str(a['requested_APD_effects'])+'.']
    ages=result['matched_opportunities'];lines+=['','Igualdad de edad en consultas nativas de ruta: '+str(sum(r['route_query_same_exact_age']for r in ages))+'/'+str(len(ages))+'. Las diferencias de tick antes de la llamada completa se conservan separadamente. No se igualan retroactivamente clocks ni futuros interactivos.','','Resultado local de selección dependiente de consecuencias, compatible con P2 local dentro de la anatomía de cambio preparada. No acredita R2 general, aprendizaje de suma/resta, comprensión de missing-data, política óptima, iniciativa de tarea, planificación general ni una nueva primitiva NSM. Las estrategias y el lector no se seleccionaron después de ver aciertos. Los números correctos anteriores al fault y los números efectivamente escritos se mantienen separados.','','Las fuentes exactas, todos los resultados negativos y la preimagen del error N0 de categoría detallada/binaria se conservan. No hubo repetición nativa por ese error del auditor. El padre postSTOP y los snapshots completos/SQLite continúan localmente; este stage no es un respaldo operativo.']
    (stage/'INFORME_CALIDAD_REVERSIBLE.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    write(stage/'PLAN_RECALCULO.json',{'jobs':[{'id':'CALIDAD_REVERSIBLE_MAIN_OMIT_RAW_ARCHIVOS','name':'CALIDAD_REVERSIBLE_MAIN_OMIT_RAW_ARCHIVOS','base':'.','script':script,'args':args,'reference':reference.name}],'scope':'One retrospective paired comparison, not independent native reruns. All14 actual effects per branch, RAW readers, exact real files and category-only feedback are recomputed.'})
    shutil.copytree(stage,portable);output=portable/'RECALCULADO_PORTABLE.json'
    second=subprocess.run([sys.executable,'-I','-B','-X','utf8',script,*[str(output)if v=='{output}'else v for v in args]],cwd=portable,capture_output=True,text=True,encoding='utf8',timeout=120)
    proof={'returncode':second.returncode,'stdout':second.stdout,'stderr':second.stderr,'reference_sha256':sha(reference),'byte_identical':output.exists()and sha(output)==sha(reference),'native_ticks':0,'new_provider_calls':0}
    write(stage/'PRUEBA_PORTABLE.json',proof)
    if second.returncode or not proof['byte_identical']:raise RuntimeError('Portable check not exact; attempted stage preserved')
    write(stage/'OMISIONES.json',{'complete_snapshots_and_transport':'Complete operational service exports, checkpoints and journals stay in their declared local paired-parent/branch paths. This analysis contains original closed primary rows, source revisions and every selected real artifact, not an operational backup.','parent':read(ev/'BINDING/VINCULACION_N0.json')['paired_parent'],'MAIN_final':real['final'],'OMIT_final':omit['final'],'no_primary_success_or_failure_omitted':True,'observational_scope':'RAW/clock observations are complete for the registered readers/windows, not a full all-tick spatial lineage atlas. Imported identity is not causal equality of all metadata. No old context is forced to an expected sign.'})
    files=[{'file':f.relative_to(stage).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)}for f in sorted(stage.rglob('*'))if f.is_file()]
    write(stage/'MANIFIESTO.json',{'status':'CLOSED','files':files,'scope':'Exact original MAIN and paired OMIT primary/code/actual artifacts, portable reference and proof. Manifest excludes itself; no new engine execution.'})
    print(json.dumps({'stage':str(stage),'files':len(files)+1,'manifest_sha256':sha(stage/'MANIFIESTO.json'),'jobs':1,'byte_identical':True,'issues':read(reference)['issues'],'native_ticks':0},ensure_ascii=False))
if __name__=='__main__':main()
