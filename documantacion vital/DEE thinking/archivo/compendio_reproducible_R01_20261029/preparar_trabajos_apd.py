"""Rutas y controles históricos APD seleccionados, sin evolución nueva."""
from pathlib import Path
import json,hashlib,shutil,gzip
W=Path(__file__).resolve().parent;R=W.parents[1];ARCH=R/'archivo/DEE Cognitive System 1.1';S=W/'sector_apd/stage'
sources=json.loads((W/'sector_apd/seleccion.json').read_text(encoding='utf8'))
def add(f,rel):
    f=Path(f);target=S/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,target)
    sources['sources'].append(dict(original=str(f),relative=rel,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),bytes=f.stat().st_size));return rel
def parent(name):
    p=ARCH/'sistema/estado/checkpoints'/name
    if not p.exists():p=R/'DEE Cognitive 2.0/sistema/estado/checkpoints'/name
    return add(p,'padres/'+name)
def native_job(id,script,kind,parents,**extra):return dict(id=id,script=script,kind=kind,parents=parents,**extra)
def find(suffix):
    rows=[p for p in S.rglob(suffix) if p.is_file()]
    if not rows:raise FileNotFoundError(suffix)
    return rows[0].relative_to(S).as_posix()
jobs=[]
p=parent('APD01_BASE_LEXICA.T104472.db3d0d26687b.deetsnap.gz')
source=ARCH/'laboratorio/campanas/ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01/aritmetica'
for name in ['ejecutar_perfil_delta_r1.py','traslacion_acumulativa_core06_candidata.py','PROTOCOLO_TRASLACION_ACUMULATIVA_R1.json']:add(source/name,'protocolos/delta/'+name)
jobs.append(native_job('M302','protocolos/delta/ejecutar_perfil_delta_r1.py','system_out',[p],argv=['--parent','APD01_BASE_LEXICA','--max-seconds','300'],reference='archivo/APD01/MECANISMO/EVIDENCIA/PERFIL_DELTA_R1',output='nativo',comparison='delta'))
p=parent('APD02_MAIN.T361114.97439697e3b9.deetsnap.gz')
jobs.append(native_job('M303',find('ensayar_acumulador_r01.py'),'patched_globals',[p],output='nativo',comparison='accumulator',reference='archivo/APD02/ACUMULADOR_LEXICO/EVIDENCIA/ACUMULADOR/R01',global_paths={'SOURCE':p},deadline=True))
p=parent('APD01_LEX_R03_paired.T108212.8a2d055fcf82.deetsnap.gz')
jobs.append(native_job('M301','protocolos/lexico/ensayar_lexico_r04.py','patched_globals',[p],output='evidencia/campanas/ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01/lenguaje/APD01_LEX_R04',comparison='lexical',reference='archivo/APD01/APD_P01_P26/CURRICULO_LEXICO_R04',budget_file=True))
p=parent('APD02_MAIN.T391957.8b146c72922f.deetsnap.gz')
jobs.append(native_job('M304','protocolos/ruta04/ejecutar_r04_abab.py','system_out',[p],output='nativo',comparison='r04',reference='archivo/APD02/MECANISMO',argv=[]))
p=parent('APD02_MAIN.T548407.1175587c1ab9.deetsnap.gz')
jobs.append(native_job('M305','protocolos/sensor03/cribar_sensor_balanceado_apd03_r02.py','system_out',[p],output='nativo',comparison='sensor',reference='archivo/APD03/DEE_APD03_ANALISIS/MECANISMO/EVIDENCIA/SENSOR_BALANCEADO_R02',argv=['--root-go','APD03_SENSOR_AUX_R02_ONLY']))
jobs.append(native_job('M309','protocolos/calidad/probar_calidad_apd02.py','pure_quality',[],output='calidad',comparison='quality',reference='archivo/APD02/CALIDAD',argv=[]))
(S/'native_jobs.json').write_text(json.dumps(jobs,ensure_ascii=False,indent=2),encoding='utf8')
(W/'sector_apd/seleccion.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf8')
print('APD historical jobs',[(j['id'],j['kind'])for j in jobs])
