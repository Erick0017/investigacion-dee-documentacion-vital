"""Exportación N0 acotada de la prueba UI ya realizada; no motor ni nuevos ticks."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(p,x):
    with Path(p).open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--sistema',type=Path,required=True);parser.add_argument('--primarios',type=Path,required=True);parser.add_argument('--salida',type=Path,required=True);a=parser.parse_args()
    source=a.primarios.resolve(strict=True);root=a.sistema.resolve(strict=True);out=a.salida.resolve();out.mkdir(parents=True,exist_ok=False);ev=out/'EVIDENCIA';ev.mkdir();members=[];omitted=[]
    def copy(path,name,compress=False):
        path=Path(path);target=ev/name;target.parent.mkdir(parents=True,exist_ok=True);b=path.read_bytes()
        target.write_bytes(gzip.compress(b,compresslevel=9,mtime=0)if compress else b)
        row={'file':name,'bytes':target.stat().st_size,'sha256':sha(target),'original':str(path),'original_bytes':len(b),'original_sha256':hashlib.sha256(b).hexdigest()}
        if compress:row['compression']='gzip_exact_original_bytes'
        else:row['compression']='none_exact_original_bytes'
        members.append(row);return target
    # Todas las solicitudes, éxitos, resultados y controles, no un resumen elegido.
    copy(source/'SESIONES_ORIGINALES.jsonl','SESIONES_ORIGINALES.jsonl.gz',True)
    for filename in('ANTES_DEL_PRIMER_TICK.json','EJECUCION_0.json','EJECUCION_1.json','CORTE_0.json','CORTE_1.json','RESULTADOS_OPERATIVOS.json'):
        copy(source/filename,filename)
    for i in(0,1):
        copy(source/('UI_'+str(i)+'.stdout.txt'),'UI_'+str(i)+'.stdout.txt.gz',True)
        copy(source/('UI_'+str(i)+'.stderr.txt'),'UI_'+str(i)+'.stderr.txt')
    before=read(source/'ANTES_DEL_PRIMER_TICK.json')
    for row in before['sources']:
        path=source/row['file']
        if path.stat().st_size!=row['bytes']or sha(path)!=row['sha256']:raise ValueError('Frozen source mismatch: '+row['file'])
        copy(path,'CODIGO_EJECUTADO/'+path.name)
    history=root/'evidencia/campanas/APD02_CONTINUIDAD_CALIDAD_ADAPTACION/CALIDAD_REVERSIBLE_R01/REGISTROS_VENTANA.json.gz'
    copy(history,'HISTORIA_APD02/REGISTROS_VENTANA.json.gz')
    rows=[json.loads(line)for line in(source/'SESIONES_ORIGINALES.jsonl').read_text(encoding='utf8').splitlines()if line]
    first=next(row for row in rows if row['event']=='literal_material_result');trial=json.loads(first['result']['request']['result'])['result']['rows'][0]
    relative=trial['committed_effect']['artifact']['relative_path'];artifact=(Path(trial['effect_directory'])/relative).resolve(strict=True)
    if not artifact.is_relative_to(root/'sistema/estado/servicios_locales/DIAG_APD03_UI_R01'):raise ValueError('Artifact outside the tested stopped diagnostic life')
    if sha(artifact)!=trial['committed_effect']['artifact']['sha256']:raise ValueError('Committed artifact changed')
    copy(artifact,'ARTEFACTOS/'+relative)
    # Verificación local N0 de snapshots sin distribuirlos ni cargar un Runtime.
    for i in(0,1):
        path=source/('CORTE_'+str(i)+'_COMPLETO.deetsnap.gz');cut=read(source/('CORTE_'+str(i)+'.json'));storage=cut['record']['storage']
        encoded=path.read_bytes();decoded=gzip.decompress(encoded)
        if len(encoded)!=storage['encoded_bytes']or hashlib.sha256(encoded).hexdigest()!=storage['encoded_sha256']or len(decoded)!=storage['decoded_bytes']or hashlib.sha256(decoded).hexdigest()!=storage['decoded_sha256']:raise ValueError('Snapshot storage bytes/hash/CRC differ')
        omitted.append({'source':str(path),'bytes':len(encoded),'sha256':hashlib.sha256(encoded).hexdigest(),'decoded_sha256':hashlib.sha256(decoded).hexdigest(),'local_crc_and_hash_verified_N0':True,'reason':'Full operational snapshot retained locally; sparse RAW gates and exact fingerprint/identity witnesses exported, not a continuation backup.'})
    write(ev/'INDICE_PRIMARIOS.json',{'schema':'APD03.UI.archived_export.v1','new_native_ticks':0,'members':members,'omitted':omitted,'scope':'Exact originals or lossless gzip. No original artifact is edited; histories are not merged.'})
    code=out/'CODIGO_Y_RECALCULO';code.mkdir()
    for filename in('recalcular_ui_apd03_n0.py','preparar_evidencia_ui_apd03_n0.py'):
        shutil.copyfile(Path(__file__).parent/filename,code/filename)
    command=[sys.executable,'-I','-B',str(code/'recalcular_ui_apd03_n0.py'),'--evidencia',str(ev),'--salida',str(out/'REFERENCIA_UI_APD03.json')]
    proof=subprocess.run(command,cwd=Path(sys.executable).parent,capture_output=True,text=True,encoding='utf8')
    write(out/'EJECUCION_RECALCULO_LOCAL.json',{'command':command,'returncode':proof.returncode,'stdout':proof.stdout,'stderr':proof.stderr,'new_native_ticks':0})
    if proof.returncode:raise RuntimeError('Archived recalculation found differences: '+proof.stdout+proof.stderr)
    # Repetición portable desde copia distinta: no Native ni importaciones de S.
    with tempfile.TemporaryDirectory(prefix='apd03-ui-archived-')as temporary:
        elsewhere=Path(temporary)/'copied';shutil.copytree(ev,elsewhere/'EVIDENCIA');shutil.copytree(code,elsewhere/'CODIGO_Y_RECALCULO');result=elsewhere/'actual.json'
        portable=subprocess.run([sys.executable,'-I','-B',str(elsewhere/'CODIGO_Y_RECALCULO/recalcular_ui_apd03_n0.py'),'--evidencia',str(elsewhere/'EVIDENCIA'),'--salida',str(result)],cwd=Path(sys.executable).parent,capture_output=True,text=True,encoding='utf8')
        if portable.returncode or result.read_bytes()!=(out/'REFERENCIA_UI_APD03.json').read_bytes():raise RuntimeError('Portable N0 result differs')
    write(out/'PLAN_RECALCULO.json',{'schema':'APD03.archived_recalculation_plan.v1','status':'CLOSED_ARCHIVED_EVIDENCE_ONLY','cases':[{'id':'UI_SINGLE_TERMINAL_OPERATIONAL','script':'CODIGO_Y_RECALCULO/recalcular_ui_apd03_n0.py','args':['--evidencia','EVIDENCIA','--salida','{output}'],'expected':'REFERENCIA_UI_APD03.json','recalculation_portable_byte_identical':True,'new_native_ticks':0}],'not_native_reproduction':True})
    files=[{'file':p.relative_to(out).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(out.rglob('*'))if p.is_file()]
    write(out/'MANIFIESTO.json',{'schema':'APD03.UI.compact_recalculation_stage.v1','members':files,'member_count_excluding_this_manifest':len(files),'bytes_excluding_this_manifest':sum(r['bytes']for r in files),'new_native_ticks':0,'not_operational_backup':True})
    print(json.dumps({'out':str(out),'files':len(files)+1,'recalculation_byte_identical':True,'new_native_ticks':0}))
if __name__=='__main__':main()
