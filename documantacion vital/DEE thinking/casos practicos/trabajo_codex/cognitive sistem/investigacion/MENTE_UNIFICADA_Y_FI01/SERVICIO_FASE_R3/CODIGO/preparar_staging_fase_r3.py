"""Closed R3 contribution, separate from immutable SERVICIO/R11; zero ticks."""
import argparse, hashlib, json, shutil, subprocess, sys, tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
EV=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/servicio'
TRIAL='SERVICIO_60MIN_FASE_R17'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def prepare(stage):
    if not(EV/TRIAL/'CORTE_PARA_MANUAL.json').is_file():raise ValueError('Actual post-STOP cut required; do not seal predictions')
    stage.mkdir(parents=True,exist_ok=False);copied=[];omitted=[]
    def put(src,rel):
        dest=stage/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
        if sha(src)!=sha(dest):raise ValueError('Source moved during closed-stage copying')
        copied.append({'file':rel.as_posix(),'bytes':dest.stat().st_size,'sha256':sha(dest),'source':str(src)})
    def evidence(src):
        if not src.is_file()or'__pycache__'in src.parts:return
        rel=src.relative_to(EV)
        is_package=bool({'PAQUETE_PADRE_FINAL_R11','PAQUETE_FINAL_POSTSTOP'}&set(rel.parts))
        if is_package and src.name!='EXPORTACION_SERVICIO.json' or src.suffix in('.zip','.whl','.exe','.pyd','.dll','.sqlite3')or'.deetsnap'in src.name:
            omitted.append({'source':str(src),'bytes':src.stat().st_size,'sha256':sha(src),'reason':'Complete operational parent/native/journal assets remain locally and in the operational collaboration package; compact analysis retains exact manifests/receipts, not another backup.'});return
        put(src,Path('EVIDENCIA')/rel)
    for folder in('FASE_R3_PREPARACION_R01','FASE_R3_PREPARACION_R02',TRIAL):
        for src in sorted((EV/folder).rglob('*')):evidence(src)
    for name in('PROTOCOLO_60MIN_FASE_R3_R04.json','PROTOCOLO_PRUEBA_ZIP_EXACTO_R01.json','PROTOCOLO_PRUEBA_ZIP_EXACTO_R02.json','PROTOCOLO_PRUEBA_ZIP_EXACTO_R03.json','VERIFICACION_PROTOCOLO_R04_0TICKS.json','RECALCULO_PREPARACION_R3.json','DISTRIBUCION_STDLIB_R02.json'):
        evidence(EV/name)
    source_names=('ensayo_servicio_fase_r3_r04.py','preparar_fork_emparejado_r3.py','exportar_ensayo_fase_r3.py','recalcular_preparacion_r3.py','recalcular_ensayo_fase_r3.py','resumir_funciones_fase_r3.py','recalcular_tiempo_fase_r3.py','documentar_corte_final_fase_r3.py','preparar_staging_fase_r3.py','verificar_guardas_distribucion_r3.py')
    for name in source_names:put(HERE/name,Path('CODIGO')/name)
    for src in sorted((HERE/'distribucion').iterdir()):
        if src.is_file()and src.suffix in('.py','.md'):put(src,Path('CODIGO/distribucion')/src.name)
    plans=[
      ('recalcular_preparacion_r3.py',['--evidencia','EVIDENCIA'],'EVIDENCIA/RECALCULO_PREPARACION_R3.json','PREPARACION_R3.json'),
      ('recalcular_ensayo_fase_r3.py',['--evidencia','EVIDENCIA/'+TRIAL],'EVIDENCIA/'+TRIAL+'/RECALCULO_FASE_R3.json','FASE_R3.json'),
      ('recalcular_tiempo_fase_r3.py',['--evidencia','EVIDENCIA/'+TRIAL],'EVIDENCIA/'+TRIAL+'/RECALCULO_TIEMPO_FASE_R3.json','TIEMPO_FASE_R3.json'),
      ('resumir_funciones_fase_r3.py',['--evidencia','EVIDENCIA/'+TRIAL],'EVIDENCIA/'+TRIAL+'/PANELES_Y_FUNCIONES.json','PANELES_Y_FUNCIONES_R3.json')]
    runs=[]
    for script,args,ref,out in plans:
        if not(stage/ref).is_file():raise ValueError('Final reference absent: '+ref)
        put(HERE/script,Path('RECALCULO')/script)
        runs.append({'script':'RECALCULO/'+script,'args':[*args,'--salida','RECALCULADO/'+out],'reference':ref,'reference_sha256':sha(stage/ref)})
    write(stage/'PLAN_RECALCULO.json',runs)
    write(stage/'OMISIONES.json',{'omitted':omitted,'all_new_R17_positive_and_negative_transport_rows_retained':True,'source_R11_staging_separate_and_unchanged':True,'scope':'Native arrays, admissions and exact actual worker files in R17 are included. Complete operational snapshots, SQLite and outbox copies are not duplicated in this analysis and are necessary for continuation. Their archived hash receipts do not mean the portable arithmetic reopens those omitted sources.'})
    (stage/'LEER.md').write_text('# Servicio y protección temporal R3P0\n\nEste bloque conserva la reserva R04/R17 de3720s, sin reescribir R11. La vida R3 procede de importación emparejada explícita, una enseñanza B0 declarada y protección temporal P0; no es regulación aprendida ni un nuevo individuo deT0. Los resultados funcionales, silencios y rechazos proceden de los registros completos, no de lo previsto en el protocolo.\n\nLa revisión beta de+ a− es enseñanza explícita del operador. La ausencia de sondas de auditoría no retira las consultas funcionales. Las cadenas son dos peticiones asistidas con archivos de trabajador reales; no un planificador autónomo.\n\n`PLAN_RECALCULO.json` contiene cuatro recálculos estándar sin motor: preparación0ticks archivada, lectores/RAW/entradas/bytes reales, tiempo descontando pausas y tablas funcionales. Se ejecutan desde esta carpeta y se comparan byte a byte con referencias finales. No reproducen física ni una instalación en otro equipo.\n\nEl manifiesto emparejado postSTOP es un índice de los respaldos operativos locales: este análisis reducido no continúa vidas por sí solo. La prueba independiente del ZIP operativo se informa aparte y no repite la reserva larga. R01/R02 de prueba ZIP no ejecutados quedan señalados como sustituidos; R03 fija estímulos nuevos antes de extraer/usar el ZIP final.\n',encoding='utf8')
    manifest=[{'file':f.relative_to(stage).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)}for f in sorted(stage.rglob('*'))if f.is_file()]
    write(stage/'MANIFIESTO.json',{'members':manifest,'sources':copied,'omissions':omitted,'self_hash_absent':True})
    return runs

def probe(stage,runs):
    temp=Path(tempfile.mkdtemp(prefix='MUFI-phase-R3-portable-'));copy=temp/'SERVICIO_FASE_R3';shutil.copytree(stage,copy);checks=[]
    for row in runs:
        out=copy/row['args'][-1];r=subprocess.run([sys.executable,'-I','-B','-X','utf8',str(copy/row['script']),*row['args']],cwd=copy,capture_output=True,text=True,encoding='utf8',timeout=120)
        same=out.is_file()and out.read_bytes()==(copy/row['reference']).read_bytes()
        checks.append({**row,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'byte_identical':same})
        if r.returncode or not same:raise RuntimeError('Portable result differs: '+json.dumps(checks[-1]))
    write(stage/'PRUEBA_PORTABLE.json',{'schema':'DEE.unified.R3.portable_stage.v1','new_native_ticks':0,'DEE_imports':False,'temporary_copy':str(copy),'all_byte_identical':all(x['byte_identical']for x in checks),'checks':checks,'scope':'Four archived stdlib calculations from a separate path. No native replay, policy training or claim of independent physical replication.'})
    print(json.dumps({'stage':str(stage),'files':sum(p.is_file()for p in stage.rglob('*')),'bytes':sum(p.stat().st_size for p in stage.rglob('*')if p.is_file()),'runs':len(checks),'manifest_sha256':sha(stage/'MANIFIESTO.json'),'portable_sha256':sha(stage/'PRUEBA_PORTABLE.json')}))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();runs=prepare(a.salida);probe(a.salida,runs)

if __name__=='__main__':main()
