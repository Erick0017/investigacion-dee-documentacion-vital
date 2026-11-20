"""Package the finished bounded context sensitivity, not a completed new learner."""
import argparse,hashlib,json,shutil,subprocess,sys,tempfile,zlib
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8',newline='\n')as f:f.write(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidence',type=Path,required=True);p.add_argument('--stage',type=Path,required=True);a=p.parse_args();here=Path(__file__).parent
 if a.stage.exists():raise FileExistsError('Preserve original stages')
 result=json.loads((a.evidence/'RESULTADOS.json').read_bytes());a.stage.mkdir(parents=True);omitted=[]
 for f in sorted(a.evidence.rglob('*')):
  if not f.is_file():continue
  relative=f.relative_to(a.evidence)
  if f.name.endswith('.deetsnap.gz'):
   omitted.append({'file':relative.as_posix(),'local_locator':str(f.resolve()),'bytes':f.stat().st_size,'sha256':sha(f)});continue
  dst=a.stage/'EVIDENCIA'/relative;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,dst)
 for f in(here/'recalcular_contexto_r01.py',here/'recalcular_contexto_r00_PRE_SYNTAX_N0.py',here/'ERROR_RECALCULO_R00_N0.json',Path(__file__)):
  dst=a.stage/('RECALCULO'if f.name=='recalcular_contexto_r01.py'else'CODIGO_N0')/f.name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,dst)
 shutil.copyfile(here/'RECALCULO_CONTEXTO_R01.json',a.stage/'REFERENCIA.json')
 tmp=Path(tempfile.mkdtemp(prefix='apd02_context_n0_'));copy=tmp/'COPIA';shutil.copytree(a.stage,copy);output=tmp/'RESULTADO.json'
 run=subprocess.run([sys.executable,'-I','-B',str(copy/'RECALCULO/recalcular_contexto_r01.py'),'--evidence',str(copy/'EVIDENCIA'),'--output',str(output)],capture_output=True,text=True,encoding='utf8');equal=output.is_file()and output.read_bytes()==(a.stage/'REFERENCIA.json').read_bytes()
 emit(a.stage/'PRUEBA_PORTABLE.json',{'exit_code':run.returncode,'byte_identical':equal,'reference_sha256':sha(a.stage/'REFERENCIA.json'),'actual_sha256':sha(output)if output.is_file()else None,'stdout':run.stdout,'stderr':run.stderr,'native_ticks':0})
 if run.returncode or not equal:raise RuntimeError('Archived calculation did not reproduce exactly')
 emit(a.stage/'INDICE_Y_LIMITES.json',{'status':'CLOSED_BOUNDED_SENSITIVITY_ONLY','no_new_MAIN_or_service_capacity_claimed':True,'omitted_complete_physical_AUX_worlds_retained_locally':omitted,'declared_budget_seconds':result['protocol']['budget_seconds'],'actual_seconds':result['elapsed_seconds'],'declared_overshoot_seconds':max(0,result['elapsed_seconds']-result['protocol']['budget_seconds']),'budget_guard_limit':'Executed guard was between opportunities, so the last query finished beyond180s; recorded194.448s is not relabeled as180. No new Native run is performed here.','scope':'Two source/readout geometries declared before data, shared complete parentf296T454808, maximum8materialqueries; source anatomy/interface active flags are P0, not learned semantics or policy. All responses, rejections and zero-output cases retained. Source system, MAIN, live SQLite and source R04 are untouched.'})
 text='# Contexto sensorial nativo: primer corte APD02\n\n'
 text+='Se bifurcó físicamente el snapshot completo f296ea9389b22e2d02520f641052b214c8333db11eb5de30d242775888aabf93, T454808, mediante el adaptador oficial; no se clonó SQLite ni se registró una supuesta continuación operativa del servicio. No se escribió sistema/ ni MAIN.\n\n'
 text+='Un único canal fijo recibe el bit público de falta de observación:0=segundo dato observado,1=ausente. Ambos son materia state1SEM1 con dirección0; no se entrega la acción correcta, un operando privado o una referencia docente. Dos historias opuestas parten del mismo RAW/clocks/tick y sólo difieren en los bits de sus entradas futuras declaradas.\n\n'
 text+='S lateral [24,13,53], lector fijo3gates: primeras entradas0/1 APPLIED produjeron−1/0 material. Eso demuestra uso físico inicial del dato en la selección, dado el estado de referencia heredado, no aprendizaje de la noción de ausencia. El sensor permaneció activo y acreció; las dos entradas siguientes fueron REJECTED_OCCUPIED, y las respuestas−1/0 perseveraron sin recibir el nuevo bit. No se limpiaron ni reasignaron los sensores.\n\n'
 text+='S superiorFI01 [24,13,54], lector fijo6gates: los cuatro bits fueron APPLIED, y el sitio de entrada se vació nativamente. Las secuencias0→1 y1→0 produjeron[−1,None] y[None,−1]. Para1, los seis RAW del lector fueron0, no una elección de otro acceso a posteriori. No se demuestra allí una emisiónQUERY utilizable; tampoco se atribuye automáticamente una clasez−1 que no se observó. El snapshot completo conserva el posible producto fuera de esa cobertura.\n\n'
 text+='Denominadores:8consultas materiales solicitadas,6entradas sensoriales APPLIED y2rechazadas;6lecturas válidas en total, pero2son respuestas posteriores a entradas rechazadas y no prueban uso del dato nuevo. Entre las6entradas aplicadas hubo4lecturas válidas y2sin salida del lector. No se ejecutó tarea ambiental, actor de archivo, docencia ni consecuencia de calidad. El calendario común omitido sólo finaliza recursos genéricos y no se cuenta comoSUCCESS aprendido.\n\n'
 text+='Resultado acotado: percepción contextual inicial nativa positiva, reutilización lateral bloqueada por ocupación/anclaje; sensor superior reutilizable pero conexión de su bit1 a una acción utilizable no acreditada. No se inició currículo ni se declara política contextual aprendida, P2/R2 o regulación. Falta un enlace físico reutilizable entre observación y acción/retorno, no una actualización correcta calculada porPython.\n\n'
 text+='El corte Native registró194.44801309984177s: excedió14.44801309984177s su guardia180s, que se comprobaba entre consultas y terminó la última ya iniciada. Se declara la desviación, sin rehacer fuente o estados. Pico223350784B, un Job512MiB/OMP1. No hay Runtime propio vivo. El recálculo N0 inspecciona2682observacionesRAW/48lectores con0discrepancias; los recuentos son ocurrencias, no réplicas.\n'
 with(a.stage/'INFORME_CONTEXTO_SENSORIAL.md').open('x',encoding='utf8',newline='\n')as f:f.write(text)
 emit(a.stage/'PLAN_RECALCULO.json',{'jobs':[{'name':'SENSIBILIDAD_CONTEXTO_NATIVO','base':'.','script':'RECALCULO/recalcular_contexto_r01.py','args':['--evidence','EVIDENCIA','--output','{output}'],'reference':'REFERENCIA.json'}]})
 emit(a.stage/'MANIFIESTO.json',{'files':[{'file':f.relative_to(a.stage).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)}for f in sorted(a.stage.rglob('*'))if f.is_file()],'no_self_hash':True})
 fs=[f for f in a.stage.rglob('*')if f.is_file()];print(json.dumps({'stage':str(a.stage),'manifest_sha256':sha(a.stage/'MANIFIESTO.json'),'files':len(fs),'expanded_bytes':sum(f.stat().st_size for f in fs),'zlib6_estimate':sum(len(zlib.compress(f.read_bytes(),6))for f in fs),'native_ticks':0}));return 0
if __name__=='__main__':raise SystemExit(main())
