"""Freeze new zero-tick auditor policy references without editing a closed stage."""
import argparse,hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def copy(p,q):
    q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
    if sha(p)!=sha(q):raise ValueError('Copy mismatch or source changed')
def emit(p,v):
    if p.exists():raise FileExistsError(str(p))
    p.write_text(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in('code','o2','reversal','system','evidence','stage','check_root'):ap.add_argument('--'+key.replace('_','-'),dest=key,type=Path,required=True)
    a=ap.parse_args()
    if a.evidence.exists()or a.stage.exists():raise FileExistsError('New supplemental directories only')
    a.evidence.mkdir(parents=True);a.stage.mkdir(parents=True);inputs=[]
    sources=[(a.code/'PROTOCOLO_RUTA_O2_R3.json','PROTOCOLO_RUTA_O2_R3.json'),
             (a.code/'PROTOCOLO_REVERSION_O2_R3.json','PROTOCOLO_REVERSION_O2_R3.json'),
             *[(a.o2/name/'03_RESULTADO_COMPLETO.json.gz','O2_'+name+'.json.gz')for name in('real','omit','sham')],
             *[(a.reversal/name/'03_RESULTADO_COMPLETO.json.gz','REV_'+name+'.json.gz')for name in('SAME_LAW','REVERSE')]]
    for source,name in sources:
        copy(source,a.evidence/name);inputs.append({'source_local_locator':str(source.resolve()),'file':name,'sha256':sha(source),'bytes':source.stat().st_size,'exact_original_container_bytes_copied':True})
    emit(a.evidence/'PROCEDENCIA.json',{'schema':'APD01.analytical_policy_reference.inputs.v1','native_ticks':0,'inputs':inputs,'originals_modified':False})
    script=a.code/'recalcular_referencias_politicas_r1.py'
    command=[sys.executable,'-I','-B','-X','utf8',str(script),'--evidencia',str(a.evidence),'--salida',str(a.evidence/'RECALCULO_REFERENCIAS_POLITICAS_R1.json')]
    result=subprocess.run(command,capture_output=True,text=True,encoding='utf8',timeout=60)
    if result.returncode:raise ValueError(result.stdout+result.stderr)
    for p in sorted(a.evidence.iterdir()):copy(p,a.stage/'EVIDENCIA'/p.name)
    copy(script,a.stage/'RECALCULO'/script.name)
    for name in('REFERENCIAS_POLITICAS_Y_COBERTURA.md','COBERTURA_FUNCIONAL_ACOTADA.csv'):
        copy(a.code/name,a.stage/name)
    copy(Path(__file__),a.stage/'CODIGO_Y_CONTEXTO'/Path(__file__).name)
    operation_source=a.system/'capacidades/asistente_proposito_01.py'
    copy(operation_source,a.stage/'CODIGO_Y_CONTEXTO/asistente_proposito_01_LEIDO_R04.py')
    emit(a.stage/'CODIGO_Y_CONTEXTO/ALCANCE_LECTURA_DSL.json',{'native_ticks':0,'source_local_locator':str(operation_source.resolve()),'source_sha256':sha(operation_source),'function_inspected':'compose','scope':'Static operational-interface inspection only. Concrete MAIN composition runs/reserves remain in the Root primary evidence; this supplemental policy reference does not certify them.'})
    copy(a.evidence/'RECALCULO_REFERENCIAS_POLITICAS_R1.json',a.stage/'REFERENCIAS/RESULTADO.json')
    plan={'schema':'APD01.policy_reference.portable_plan.v1','native_ticks':0,'jobs':[{'name':'POLITICAS_ANALITICAS_Y_LIMITES','base':'.','script':'RECALCULO/recalcular_referencias_politicas_r1.py','args':['--evidencia','EVIDENCIA','--salida','{output}'],'reference':'REFERENCIAS/RESULTADO.json'}]}
    emit(a.stage/'PLAN_RECALCULO.json',plan)
    with tempfile.TemporaryDirectory(prefix='_apd_policies_',dir=a.check_root)as folder:
        target=Path(folder)/'extraido';shutil.copytree(a.stage,target);output=Path(folder)/'resultado.json'
        cmd=[sys.executable,'-I','-B','-X','utf8',str(target/'RECALCULO'/script.name),'--evidencia','EVIDENCIA','--salida',str(output)]
        check=subprocess.run(cmd,cwd=target,capture_output=True,text=True,encoding='utf8',timeout=60)
        equal=check.returncode==0 and output.exists()and output.read_bytes()==(a.stage/'REFERENCIAS/RESULTADO.json').read_bytes()
        if not equal:raise ValueError(check.stdout+check.stderr)
        emit(a.stage/'COMPROBACION_PORTABLE.json',{'native_ticks':0,'returncode':check.returncode,'byte_identical_reference':equal,'stdout':check.stdout,'stderr':check.stderr})
    emit(a.stage/'MANIFIESTO.json',{'schema':'SHA256.members.no_self_reference.v1','members':[{'file':p.relative_to(a.stage).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(a.stage.rglob('*'))if p.is_file()]})
    print(result.stdout,end='');print(json.dumps({'stage':str(a.stage),'native_ticks':0,'portable_byte_identical':True,'manifest_sha256':sha(a.stage/'MANIFIESTO.json')}))

if __name__=='__main__':main()
