from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from datetime import datetime,timezone
import sys,json,hashlib,shutil,subprocess,time
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];WORKSPACE=ROOT.parents[4];STAGE=WORKSPACE/'_ic01_analysis_stage_20261021';EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01';SYSTEM=ROOT/'sistema'
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
budget=read(LAB/'PRESUPUESTO_Y_PADRE.json')
if time.monotonic()>budget['monotonic_deadline_seconds']-1200:raise TimeoutError('Preserve independent verification time')
index=read(STAGE/'INDICE_FUENTES_Y_OMISIONES.json');sources=index['included_original_sources'];by={r['member']:r for r in sources}
def include(src,name,kind):
    src=Path(src);dst=STAGE/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);by[name]={'member':name,'original':str(src),'original_bytes':src.stat().st_size,'original_sha256':sha(src),'kind':kind,'byte_identical_to_source':True}
for p in (LAB/'entrega_analisis').iterdir():
    if p.is_file():include(p,p.name,'scientific_report_table_or_continuity')
for name in('recalcular.py','resumir_ciencia.py','reproducir_entorno.py','verificar_testigos.py','finalizar_paquete.py','verificar_zip.py'):
    include(LAB/name,'CODIGO_Y_RECALCULO/'+name,'recalculation_or_sealing_verification_source')
include(LAB/'VERIFICACION_TABLAS_ARTIFACT.json','CONFIGURACION_Y_VERIFICACION/VERIFICACION_TABLAS_ARTIFACT.json','exact_table_roundtrip_verification')
def call(argv):
    r=subprocess.run(argv,cwd=STAGE,capture_output=True,text=True,encoding='utf8',timeout=240)
    if r.returncode:raise RuntimeError(r.stdout+'\n'+r.stderr)
    return{'argv':argv,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
checks=[];checks.append(call([sys.executable,'-B',str(STAGE/'CODIGO_Y_RECALCULO/recalcular.py'),'--out',str(STAGE/'CALCULOS.json')]))
checks.append(call([sys.executable,'-B',str(STAGE/'CODIGO_Y_RECALCULO/resumir_ciencia.py')]))
checks.append(call([sys.executable,'-B',str(STAGE/'CODIGO_Y_RECALCULO/verificar_testigos.py'),'--package',str(STAGE),'--out',str(STAGE/'VERIFICACION_TESTIGOS.json')]))
original=read(EV/'CALCULOS.json');exported=read(STAGE/'CALCULOS.json')
for key in('trial_metrics','physical_checks','common_history_opportunities','main140_collision_window','selected_physical_results'):
    if original[key]!=exported[key]:raise AssertionError('Compact extraction changed principal metric: '+key)
write(STAGE/'CONFIGURACION_Y_VERIFICACION/RECORTE_METRICAS.json',{'equal_principal_metrics_to_local_complete_primary_set':True,'keys':['trial_metrics','physical_checks','common_history_opportunities','main140_collision_window','selected_physical_results'],'record_count_may_differ_because_duplicated_aggregates_are_indexed_not_copied':True,'native_ticks':0,'commands':checks})
index['included_original_sources']=list(by.values());index['source_bytes_included_before_ZIP']=sum(r['original_bytes']for r in by.values());write(STAGE/'INDICE_FUENTES_Y_OMISIONES.json',index)
# Verify current originals against staged copies before recording their identity.
for row in by.values():
    if sha(STAGE/row['member'])!=row['original_sha256']:raise AssertionError('Staged source mismatch '+row['member'])
members=[]
for p in sorted(STAGE.rglob('*')):
    if p.is_file()and p.name!='MANIFIESTO_HASHES.json':members.append({'member':p.relative_to(STAGE).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
write(STAGE/'MANIFIESTO_HASHES.json',{'schema':'IC01.sealed.member.hashes.v1','members':members,'excluded_self':'MANIFIESTO_HASHES.json does not contain its own hash','archive_hash':'Only in external verification, never inside this container','expanded_bytes_without_manifest':sum(r['bytes']for r in members)})
target=ROOT/'entregas/DEE_COGNITIVE_1_1_INTEGRACION_COGNITIVA_SITUADA_E1_01_ANALISIS.zip';target.parent.mkdir(exist_ok=True)
if target.exists():raise FileExistsError('Do not overwrite a sealed canonical archive; inspect existing external verification')
with ZipFile(target,'w',compression=ZIP_DEFLATED,compresslevel=9,allowZip64=True)as z:
    for p in sorted(STAGE.rglob('*')):
        if p.is_file():z.write(p,p.relative_to(STAGE).as_posix())
if target.stat().st_size>16000000:raise ValueError('Candidate exceeds absolute transfer limit; do not publish it')
with ZipFile(target)as z:
    if z.testzip():raise AssertionError('ZIP CRC failure')
record={'archive':str(target),'bytes':target.stat().st_size,'sha256':sha(target),'members':len(members)+1,'stage':str(STAGE),'expanded_bytes':sum(r['bytes']for r in members),'sealing_utc':datetime.now(timezone.utc).isoformat(),'elapsed_monotonic_seconds':time.monotonic()-budget['monotonic_start_seconds'],'external_verification_still_required':True}
write(LAB/'CANDIDATO_SELLADO.json',record);print(json.dumps(record))
