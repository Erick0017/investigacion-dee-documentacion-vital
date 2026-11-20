"""One compact service contribution for the parent analysis, no DEE/ticks.

Closed primaries, failures, exact code and portable arithmetic are retained;
native snapshots/SQLite pairs remain local and in the collaboration package.
"""
import argparse,hashlib,json,shutil,subprocess,sys,tempfile,zipfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
EV=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/servicio'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def prepare(stage):
    stage.mkdir(parents=True,exist_ok=False);members=[];omitted=[]
    def put(source,member):
        target=stage/member;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        if sha(source)!=sha(target):raise ValueError('Copied source bytes changed')
        members.append({'file':member.as_posix(),'bytes':target.stat().st_size,'sha256':sha(target),'source':str(source)})
    for source in sorted(EV.rglob('*')):
        if not source.is_file()or'__pycache__'in source.parts:continue
        if source.suffix in('.zip','.whl','.exe','.pyd','.dll','.sqlite3')or'.deetsnap'in source.name:
            omitted.append({'source':str(source),'bytes':source.stat().st_size,'sha256':sha(source),'reason':'Complete operational snapshot/transport or engine remains local; not needed for archived calculations.'});continue
        put(source,Path('EVIDENCIA')/source.relative_to(EV))
    for source in sorted(HERE.rglob('*')):
        if not source.is_file()or'__pycache__'in source.parts:continue
        if source.suffix not in('.py','.md','.json'):continue
        put(source,Path('CODIGO')/source.relative_to(HERE))
    plans=[
      ('recalcular_piloto.py',['--primario','EVIDENCIA/PILOTO_R01/PILOTO.json.gz'],'EVIDENCIA/PILOTO_R01/RECALCULO_PILOTO.json','PILOTO.json'),
      ('recalcular_emparejado.py',['--primario','EVIDENCIA/EMPAREJADO_R03/EMPAREJADO.json.gz'],'EVIDENCIA/EMPAREJADO_R03/RECALCULO_EMPAREJADO.json','EMPAREJADO.json'),
      ('recalcular_servicio_a.py',['--evidencia','EVIDENCIA'],'EVIDENCIA/RECALCULO_SERVICIO_A.json','SERVICIO_A.json'),
      ('recalcular_interrupcion.py',['--evidencia','EVIDENCIA/INTERRUPCION_REAL_R09'],'EVIDENCIA/INTERRUPCION_REAL_R09/RECALCULO_INTERRUPCION.json','INTERRUPCION.json'),
      ('recalcular_ensayo_60min.py',['--evidencia','EVIDENCIA/SERVICIO_60MIN_FINAL_R11'],'EVIDENCIA/SERVICIO_60MIN_FINAL_R11/RECALCULO_60MIN.json','SERVICIO_60MIN.json'),
      ('recalcular_tiempo_suplementario.py',['--evidencia','EVIDENCIA'],'EVIDENCIA/RECALCULO_TIEMPO_TOTAL.json','TIEMPO_TOTAL.json'),
      ('resumir_funciones_servicio.py',['--evidencia','EVIDENCIA/SERVICIO_60MIN_FINAL_R11'],'EVIDENCIA/SERVICIO_60MIN_FINAL_R11/PANELES_Y_FUNCIONES.json','PANELES_Y_FUNCIONES.json')]
    runs=[]
    for script,args,reference,output in plans:
        source=HERE/script
        if not source.is_file()or not(stage/reference).is_file():raise ValueError('Final calculation/reference missing; do not substitute an earlier or partial result: '+script)
        put(source,Path('RECALCULO')/script)
        runs.append({'script':'RECALCULO/'+script,'args':[*args,'--salida','RECALCULADO/'+output],'reference':reference,'reference_sha256':sha(stage/reference)})
    (stage/'PLAN_RECALCULO.json').write_text(json.dumps(runs,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (stage/'OMISIONES.json').write_text(json.dumps({'omitted':omitted,'full_snapshots_are_not_replaced_by_arrays':True,'scope':'All new service primaries and failures retained. Stored reports of complete snapshot compaction/pair validation are not rerun from omitted snapshots by these arithmetic scripts.'},sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (stage/'LEER.md').write_text('# Servicio persistente MUFI\n\nPrimarios positivos y negativos, fuentes exactas y siete recálculos sin motor. Los protocolos CANDIDATO R01/R02/R03 NO ejecutados no se cuentan como vidas ni como resultados físicos. R03 FINAL de3605s y el tramo suplementario tienen registros separados.\n\nLa copia emparejada preserva mundo, agenda, colas, artefactos y resultados inciertos. Este análisis no contiene esos respaldos completos y no sirve para continuar una vida por sí solo. El paquete operativo de colaboración sí contiene el corte seleccionado.\n\nLos planes usan rutas relativas y referencias byte a byte. No son reproducción nativa ni entrenamiento nuevo. Las pruebas de interrupción real y los errores del harness anteriores están incluidos sin borrarlos. Las fichas JSON de compactación acreditan una comprobación local sobre snapshots omitidos, no una nueva prueba de esa igualdad desde este reducido.\n',encoding='utf8')
    # Freeze staged content; the proof added below is deliberately outside this manifest.
    manifest=[{'file':f.relative_to(stage).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)}for f in sorted(stage.rglob('*'))if f.is_file()]
    (stage/'MANIFIESTO.json').write_text(json.dumps({'members':manifest,'sources':members,'omissions':omitted,'self_hash_absent':True},sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return runs
def probe(stage,runs):
    temp=Path(tempfile.mkdtemp(prefix='MUFI-service-portable-'));copy=temp/'SERVICIO';shutil.copytree(stage,copy);checks=[]
    for row in runs:
        out=copy/row['args'][-1];args=[str(copy/row['script']),*row['args']];r=subprocess.run([sys.executable,'-I','-B','-X','utf8',*args],cwd=copy,capture_output=True,text=True,encoding='utf8',timeout=120)
        equal=out.is_file()and out.read_bytes()==(copy/row['reference']).read_bytes();checks.append({'script':row['script'],'args':row['args'],'reference':row['reference'],'reference_sha256':row['reference_sha256'],'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'byte_identical':equal})
        if r.returncode or not equal:raise RuntimeError('Portable archived calculation differs: '+json.dumps(checks[-1]))
    result={'schema':'DEE.unified.service.portable_staging.v1','new_native_ticks':0,'DEE_imports':False,'temporary_copy':str(copy),'all_byte_identical':all(q['byte_identical']for q in checks),'checks':checks,'scope':'Separate-path archived arithmetic; code inspection confirms stdlib only. Final combined audit adds its no-DEE/no-network/history-access guard. Not native reproduction or a second computer.'}
    (stage/'PRUEBA_PORTABLE.json').write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'stage':str(stage),'files':sum(f.is_file()for f in stage.rglob('*')),'bytes':sum(f.stat().st_size for f in stage.rglob('*')if f.is_file()),'runs':len(checks),'all_byte_identical':result['all_byte_identical']}))
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();runs=prepare(a.salida);probe(a.salida,runs)
if __name__=='__main__':main()
