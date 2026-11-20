"""Close the R04-specific trace-cut addendum; preserve the earlier closed stages."""
import argparse,hashlib,json,shutil,subprocess,sys,tempfile,zlib
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8',newline='\n')as f:f.write(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--stage',type=Path,required=True);a=p.parse_args();here=Path(__file__).parent
    if a.stage.exists():raise FileExistsError('Do not rewrite prior history')
    summary=json.loads((a.evidencia/'RESULTADOS.json').read_bytes());a.stage.mkdir(parents=True);omitted=[]
    for f in sorted(a.evidencia.rglob('*')):
        if not f.is_file():continue
        rel=f.relative_to(a.evidencia)
        if f.name.endswith('.deetsnap.gz'):
            omitted.append({'file':rel.as_posix(),'local_locator':str(f.resolve()),'bytes':f.stat().st_size,'sha256':sha(f)});continue
        dst=a.stage/'EVIDENCIA'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,dst)
    recalc=a.stage/'RECALCULO/recalcular_mecanismo_apd02.py';recalc.parent.mkdir();shutil.copyfile(here/'recalcular_mecanismo_apd02.py',recalc)
    src=a.stage/'CODIGO_CIERRE'/Path(__file__).name;src.parent.mkdir();shutil.copyfile(Path(__file__),src)
    output=a.stage/'REFERENCIA.json';run=subprocess.run([sys.executable,'-I','-B',str(recalc),'--evidencia',str(a.stage/'EVIDENCIA'),'--salida',str(output)],capture_output=True,text=True,encoding='utf8')
    if run.returncode:raise RuntimeError('Archive recalculation failed: '+run.stdout+run.stderr)
    tmp=Path(tempfile.mkdtemp(prefix='apd02_r04cut_n0_'));copy=tmp/'COPIA';shutil.copytree(a.stage,copy);second=tmp/'RECALCULADO.json'
    run2=subprocess.run([sys.executable,'-I','-B',str(copy/'RECALCULO/recalcular_mecanismo_apd02.py'),'--evidencia',str(copy/'EVIDENCIA'),'--salida',str(second)],capture_output=True,text=True,encoding='utf8');equal=second.is_file()and second.read_bytes()==output.read_bytes()
    emit(a.stage/'PRUEBA_PORTABLE.json',{'exit_code':run2.returncode,'byte_identical':equal,'reference_sha256':sha(output),'recomputed_sha256':sha(second)if second.is_file()else None,'stdout':run2.stdout,'stderr':run2.stderr,'native_ticks':0,'scope':'Fresh relocated archive-only stdlib recalculation, no Runtime'})
    if run2.returncode or not equal:raise RuntimeError('Portable R04 cut check failed')
    rows=summary['outcomes'];by={r['mode']:r for r in rows};valid=all(k in by and'error'not in by[k]for k in('retain','cut','sham'))
    effect=valid and by['retain']['later']==-1 and by['sham']['later']==-1 and by['cut']['later']==0
    emit(a.stage/'INDICE_Y_ALCANCE.json',{'status':'CLOSED','earlier_closed_stages_unchanged':True,'native_addendum_source_parent':summary['parent']['snapshot_sha256'],'prior_source_tick':391960,'complete_worlds_retained_locally':omitted,'actual_result_rows':rows,'specific_R04_trace_dependence_supported':effect,'new_native_ticks_in_this_builder':0,'scope':'This is an R04-specific causal diagnostic on complete AUX forks, not MAIN learning or a service clone. The intervention happens after the first action is formed and does not replace the task or the generic consequence.'})
    text='# Addendum causal específico R04\n\nTres bifurcaciones del mismo estado preparado sin semilla, T391960 SHA5e0dd9fa3983cc5fbed26969db74610010403dd7db005c86b941c383559b1f1f, conservaron/cortaron/desacoplaron espacialmente la traza de una acción ya formada. No se modificó MAIN ni sistema/.\n\n'
    for row in rows:text+='- '+json.dumps(row,ensure_ascii=False,sort_keys=True)+'\n'
    text+='\nLa primera acción, efecto real de archivo y consecuencia externa se registran por separado; tres puntos de corte fijos cubren las tres trayectorias sin consultar el signo. Las entradas inactivas SEM4 son intervenciones físicas legales sobre RAW0 y no ediciones del campo. Un corte rechazado no acreditaría ablación. El sham conserva dosis. El primer uso posterior no recibe docencia, y seis consultas anteriores comprueban función no paralizada.\n\n'
    text+='El patrón R04 específico de dependencia de la traza '+('se observó'if effect else'NO se acredita por la regla fijada')+'. No es válido atribuirle automáticamente al R04 todos los resultados del R03: este addendum conserva evidencia propia. La regla de selección, la anatomía, el calendario y el mapeo de0 material a externo siguen siendo P0; la dependencia de consecuencias es local, no autonomía o regulación general.\n\nUn caso stdlib verifica RAW/clocks/lectores, proveedor único, bytes reales y proyección de calidad desde esta exportación. Los mundos completos y futuros de cada rama quedan locales con hashes; este addendum no reemplaza el respaldo operativo. Los stages6eef… y18ef… anteriores permanecen inalterados.\n'
    with(a.stage/'ADDENDUM_CORTE_R04.md').open('x',encoding='utf8',newline='\n')as f:f.write(text)
    emit(a.stage/'PLAN_RECALCULO.json',{'jobs':[{'id':'CORTE_ESPECIFICO_R04','name':'CORTE_ESPECIFICO_R04','base':'.','script':'RECALCULO/recalcular_mecanismo_apd02.py','args':['--evidencia','EVIDENCIA','--salida','{output}'],'reference':'REFERENCIA.json'}]})
    emit(a.stage/'MANIFIESTO.json',{'files':[{'file':f.relative_to(a.stage).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)}for f in sorted(a.stage.rglob('*'))if f.is_file()],'no_self_hash':True})
    files=[f for f in a.stage.rglob('*')if f.is_file()];print(json.dumps({'stage':str(a.stage),'manifest_sha256':sha(a.stage/'MANIFIESTO.json'),'files':len(files),'expanded_bytes':sum(f.stat().st_size for f in files),'zlib6_estimate':sum(len(zlib.compress(f.read_bytes(),6))for f in files),'specific_R04_trace_dependence_supported':effect}));return 0
if __name__=='__main__':raise SystemExit(main())
