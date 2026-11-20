"""Export the exact-archive operational evidence, including its failed harness.

No native execution. Reads only closed proof records and actual bytes produced
by those explicit extraction copies. Full worlds/engine/archives remain local.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prueba-final',type=Path,required=True);p.add_argument('--fallo',type=Path,required=True);p.add_argument('--continuacion',type=Path,required=True)
    p.add_argument('--extraido-final',type=Path,required=True);p.add_argument('--protocolo',type=Path,required=True);p.add_argument('--salida',type=Path,required=True)
    a=p.parse_args();out=a.salida.resolve();out.mkdir(parents=True,exist_ok=False);here=Path(__file__).resolve().parent
    evidence=out/'EVIDENCIA';code=out/'CODIGO_EJECUTADO';calc=out/'RECALCULO';sources=[]
    def copy(src,name):
        target=out/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target)
        sources.append({'file':name,'source':str(src),'bytes':src.stat().st_size,'sha256':sha(src)})
    final=read(a.prueba_final);failed=read(a.fallo);continued=read(a.continuacion)
    if final['status']!='COMPLETED_WITH_RECORDED_SCOPE':raise ValueError('Final exact archive proof is not completed')
    if failed['status']!='FAILED_WITH_STATE_PRESERVED'or continued['status']!='COMPLETED':raise ValueError('First failed attempt and its explicit continuation must remain distinct')
    for source,name in((a.prueba_final,'VERIFICACION_FULLZIP_EXACTO_R3.json'),(a.fallo,'PRIMER_INTENTO_FALLO_ESPERA.json'),(a.continuacion,'CONTINUACION_MISMA_COPIA.json')):copy(source,'EVIDENCIA/'+name)
    copy(a.fallo.parent/'DIAGNOSTICO_TIMEOUT_HARNESS.md','EVIDENCIA/DIAGNOSTICO_TIMEOUT_HARNESS.md')
    copy(a.protocolo,'CODIGO_EJECUTADO/PROTOCOLO_PRUEBA_ZIP_EXACTO_R03.json')
    seen=set();files=[]
    for label,record in(('first_copy',continued),('final_exact_archive_copy',final)):
        for row in record['service_sequence']['actual_new_worker_files']:
            source=Path(row['file']);key=(row['name'],row['sha256'])
            if sha(source)!=row['sha256']or source.stat().st_size!=row['bytes']:raise ValueError('Actual new worker file changed')
            if key in seen:continue
            seen.add(key);name='EVIDENCIA/ARCHIVOS/'+label+'/'+source.name;copy(source,name)
            files.append({**{k:row[k]for k in('name','bytes','sha256','worker','accepted','commit')},'file':Path(name).relative_to('EVIDENCIA').as_posix()})
    write(evidence/'ARCHIVOS_REALES.json',{'files':files,'scope':'Exact bytes generated in the two declared operational copies; not regenerated and not historical originals.'})
    # All Python helpers actually used by the outer runner are included from the
    # exact final extraction, not reconstructed from the mutable source tree.
    for name in('arrancar.py','probar_servicio_distribuido.py','verificar_entrega_independiente.py','actualizar.py'):
        copy(a.extraido_final/'actualizaciones'/name,'CODIGO_EJECUTADO/ENTREGA_R02/'+name)
    for name in('probar_servicio_distribuido_R01.py','verificar_entrega_independiente_R01.py','OWNER_1.txt'):
        copy(a.fallo.parent/name,'CODIGO_EJECUTADO/PRIMER_INTENTO/'+name)
    copy(here/'continuar_prueba_zip_r01.py','CODIGO_EJECUTADO/continuar_prueba_zip_r01.py')
    copy(here/'recalcular_entrega_mufi.py','RECALCULO/recalcular_entrega_mufi.py')
    # Relevant manager, ownership, capability and local-worker sources. The
    # manifest states omitted engine/world dependencies, not self-sufficiency.
    paths=['gestionar.py','app/lives.py','app/native_tools.py','app/access_guard.py','app/cola_local.py','app/servicio_persistente.py','app/cliente_mente_unificada.py','app/importacion_emparejada.py','app/compactar_historia_operativa.py','app/finalizar_protocolo.py','capacidades/mente_unificada_01.py','capacidades/mente_acumulativa_r02.py','capacidades/percepcion_cruda_fi01.py','capacidades/acceso_nativo_mufi01.py']
    for name in paths:copy(a.extraido_final/'sistema'/name,'CODIGO_EJECUTADO/S_PORTABLE/'+name)
    worker=a.extraido_final/'sistema/capacidades'
    for source in sorted(worker.rglob('eo02_trabajador_local.py')):copy(source,'CODIGO_EJECUTADO/S_PORTABLE/'+source.relative_to(a.extraido_final/'sistema').as_posix())
    cases=[]
    for label,name,expected in(('ENTREGA_FINAL','VERIFICACION_FULLZIP_EXACTO_R3.json','completed'),('PRIMER_INTENTO','PRIMER_INTENTO_FALLO_ESPERA.json','instrument_timeout'),('CONTINUACION','CONTINUACION_MISMA_COPIA.json','continued')):
        reference='REFERENCIAS/'+label+'.json';args=['--evidencia','EVIDENCIA','--prueba',name,'--esperado',expected,'--salida',reference]
        command=[sys.executable,'-I','-B','RECALCULO/recalcular_entrega_mufi.py',*args]
        result=subprocess.run(command,cwd=out,text=True,capture_output=True,encoding='utf8')
        if result.returncode:raise RuntimeError('Portable proof recalculation failed: '+label+' '+result.stdout+' '+result.stderr)
        cases.append({'id':label,'script':'RECALCULO/recalcular_entrega_mufi.py','args':['--evidencia','EVIDENCIA','--prueba',name,'--esperado',expected],'reference':reference,'reference_sha256':sha(out/reference),'comparison':'all_output_bytes_identical','execution':'Archived arithmetic only, no native replay.'})
    write(out/'PLAN_RECALCULO.json',{'schema':'DEE.portable.plan.v1','cases':cases})
    # Re-run from a separate short tree, with no source-directory imports.
    checks=[]
    with tempfile.TemporaryDirectory(prefix='mufi_proof_',dir=out.parent)as t:
        isolated=Path(t)/'copy';shutil.copytree(out,isolated)
        for case in cases:
            target=Path(t)/(case['id']+'.json');result=subprocess.run([sys.executable,'-I','-B',case['script'],*case['args'],'--salida',str(target)],cwd=isolated,text=True,capture_output=True,encoding='utf8')
            ok=result.returncode==0 and sha(target)==case['reference_sha256'];checks.append({'case':case['id'],'exit_code':result.returncode,'identical_reference_bytes':ok,'output_sha256':sha(target)if target.exists()else None})
            if not ok:raise ValueError('Isolated proof recalculation differs: '+case['id']+' '+result.stdout+result.stderr)
    write(out/'PRUEBA_PORTABLE.json',{'native_ticks':0,'DEE_imports':0,'results':checks,'all_identical':all(x['identical_reference_bytes']for x in checks)})
    previous_zip=Path(final['zip']).parent/'cognitive_sistem_colaborador.anterior.20261025T152024Z.zip'
    if sha(previous_zip)!=failed['zip_sha256']:raise ValueError('First exact archive is not preserved at its declared recoverable locator')
    write(out/'FUENTES_Y_OMISIONES.json',{'sources':sources,'omissions':[{'kind':'full_collaboration_ZIP','file':final['zip'],'bytes':final['zip_bytes'],'sha256':final['zip_sha256']},{'kind':'first_exact_ZIP','file':str(previous_zip),'sha256':failed['zip_sha256'],'bytes':failed['zip_bytes'],'recoverable_bytes_rechecked':True},{'kind':'operational_worlds_and_SQLite','location':str(a.extraido_final/'trabajo_personal/estado'),'reason':'Complete worlds/transport/bridge files remain locally; analysis stage is not a continuation backup.'}],'scope':'First timeout and its same-copy continuation are one trajectory. The second exact-archive copy is another operational trajectory, never an independent acquisition.'})
    (out/'LEER_PRIMERO.md').write_text('# Comprobación operativa de la entrega exacta\n\nEl primer ZIP se importó correctamente; su cliente dejó de esperar una exportación completa a los40s, aunque terminó a los49.78s. Se preservó el fallo y se continuó esa misma copia sin reenviar FINISH. Después se revisó sólo el harness (export120s/safety420s), se selló otro ZIP y se comprobó desde otra extracción. Ningún resultado de las copias se atribuye a MAIN original.\n\nPLAN_RECALCULO.json describe tres recálculos estándar con Python, sin importar DEE ni avanzar ticks. Son aritmética de RAW/lectores/recibos y verificación de archivos reales exportados; no reproducen la física ni el ZIP omitido. La reproducción nativa necesita el paquete completo y sus estados. PRUEBA_PORTABLE.json acredita comparación byte a byte desde otro directorio.\n\nLos comandos y sus salidas físicas, incluidos el negativo instrumental y los resultados de los dos participantes separados, están íntegros en EVIDENCIA/. El código ejecutado relevante está en CODIGO_EJECUTADO/.\n',encoding='utf8')
    members=[{'file':f.relative_to(out).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)}for f in sorted(out.rglob('*'))if f.is_file()]
    write(out/'MANIFIESTO.json',{'members':members,'no_self_hash':True})
    print(json.dumps({'stage':str(out),'files':len(members)+1,'bytes':sum(x['bytes']for x in members),'manifest_sha256':sha(out/'MANIFIESTO.json'),'portable_cases':len(cases)}))

if __name__=='__main__':main()
