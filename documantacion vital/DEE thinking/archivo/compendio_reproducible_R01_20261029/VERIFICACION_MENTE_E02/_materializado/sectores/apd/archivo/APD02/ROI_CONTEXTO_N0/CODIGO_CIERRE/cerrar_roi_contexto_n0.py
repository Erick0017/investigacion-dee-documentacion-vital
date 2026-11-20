"""Close only the passive contextual ROI addendum; no engine import."""
import argparse,hashlib,json,shutil,subprocess,sys,tempfile,zlib
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8',newline='\n')as f:f.write(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidence',type=Path,required=True);p.add_argument('--stage',type=Path,required=True);a=p.parse_args();here=Path(__file__).parent
 if a.stage.exists():raise FileExistsError('Immutable earlier stages preserved')
 a.stage.mkdir(parents=True)
 for f in a.evidence.rglob('*'):
  if f.is_file():
   dst=a.stage/'EVIDENCIA'/f.relative_to(a.evidence);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,dst)
 for f,directory in((here/'recalcular_roi_contexto_n0.py','RECALCULO'),(Path(__file__),'CODIGO_CIERRE')):
  dst=a.stage/directory/f.name;dst.parent.mkdir(exist_ok=True);shutil.copyfile(f,dst)
 shutil.copyfile(here/'RECALCULO_ROI_N0_R01.json',a.stage/'REFERENCIA.json')
 temp=Path(tempfile.mkdtemp(prefix='apd02_ROI_context_N0_'));copy=temp/'COPIA';shutil.copytree(a.stage,copy);output=temp/'RESULTADO.json'
 run=subprocess.run([sys.executable,'-I','-B',str(copy/'RECALCULO/recalcular_roi_contexto_n0.py'),'--evidence',str(copy/'EVIDENCIA'),'--output',str(output)],capture_output=True,text=True,encoding='utf8');same=output.is_file()and output.read_bytes()==(a.stage/'REFERENCIA.json').read_bytes()
 emit(a.stage/'PRUEBA_PORTABLE.json',{'exit_code':run.returncode,'byte_identical':same,'reference_sha256':sha(a.stage/'REFERENCIA.json'),'actual_sha256':sha(output)if output.is_file()else None,'stdout':run.stdout,'stderr':run.stderr,'new_native_ticks':0})
 if run.returncode or not same:raise RuntimeError('Passive archived field reconstruction not exact')
 text='''# ROI pasiva contextual — cero ticks

Se cargaron de uno en uno cuatro snapshots completos ya alcanzados en el cribado, al mismo tick454893. No se llamó run/step/update. RAW/clocks antes y después de observar fueron idénticos. Se verificó el orden de coordenadas mediante la API oficial sobre TODOS los RAW no nulos: z es el eje rápido, luego y, luego x; se exportó además la ROI fija E+[-4..4]×[-3..4]×[-4..4],648sitios por mundo, incluyendo state0/RAW0.

Los campos RAW completos (dispersos) y los clocks completos (RLE) se reconstruyen sin motor y reproducen sus SHAexactos. No son un snapshot operativo: no contienen todas las interfaces, colas, recibos, entorno o progreso y nunca deben usarse para restaurar una vida. Los snapshots completos originales permanecen en los localizadores y SHA de los primarios.

Sensor lateral0 frente1: difieren tres RAW globales y ningún clock. [24,13,53] contiene el propio sensor0/1; [23,15,53] tiene el producto−X,+Y,s_reg5 sólo para0; [25,15,53] tiene el producto0,+Y,s_reg5 sólo para1. El lector3gates original sí daba una acción válida distinta. El anclaje posterior impidió recibir la actualización siguiente, como documenta el cribado; aquí no se repara ni se reenseña.

Sensor superiorFI01: el bit1 NO produjo un portador alternativo oculto fuera de los seis gates al corte observado. Los RAW completos0/1 difieren sólo en [23,15,53]: bit0 tiene RAW1161647250359713793, dirección[-1,1,0],s_reg5; bit1tieneRAW0. Todos los demás RAW y todos los clocks son idénticos. Por tanto hubo supresión del producto de consulta en ese corte, no un éxito recuperado cambiando el lector. La ausencia sigue siendo una diferencia física distinguible por el auditor; no se transforma desde Python en una acción QUERY inteligente ni se declara convergencia de todos los estados causales o destrucción universal de información.

El soporteSEM4 existente en E+(0,1,1) es un candidato a interceptar una salida con componente+Z inducida por el sensor superior, pero no hay registro suficiente de q3/q4 para demostrar esa colisión. No se atribuye una genealogía única ni se simula retrospectivamente un tramo nuevo. El resultado distingue un observador fijo que falla de una supuesta salida alternativa: no aparece tal salida en el campo RAW completo registrado, aunque la causa intermedia necesita otra resolución.

Este addendum es una herramienta del auditor y una delimitación de interfaz, no una capacidad adquirida por MAIN. No modifica los lectores fijados, no añade una tercera familia, no ejecuta aprendizaje, acción ambiental ni calidad y no cambia las fuentes del servicio. El exceso anterior194.448s frente a180s sigue declarado en el stage de sensibilidad, sin reinterpretarlo como presupuesto cumplido.
'''
 with(a.stage/'INFORME_ROI_CONTEXTO_N0.md').open('x',encoding='utf8',newline='\n')as f:f.write(text)
 emit(a.stage/'CERRADO.json',{'status':'CLOSED','new_native_ticks':0,'new_runtime_evolution':False,'readers_unchanged':True,'source_system_or_MAIN_modified':False,'complete_sparse_fields_not_complete_operational_snapshots':True,'scope':'Passive retrospective read of reached AUX snapshots and exact archived field reconstruction only'})
 emit(a.stage/'PLAN_RECALCULO.json',{'jobs':[{'name':'ROI_CONTEXTO_N0_CAMPOS_COMPLETOS','base':'.','script':'RECALCULO/recalcular_roi_contexto_n0.py','args':['--evidence','EVIDENCIA','--output','{output}'],'reference':'REFERENCIA.json'}]})
 emit(a.stage/'MANIFIESTO.json',{'files':[{'file':f.relative_to(a.stage).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)}for f in sorted(a.stage.rglob('*'))if f.is_file()],'no_self_hash':True})
 files=[f for f in a.stage.rglob('*')if f.is_file()];print(json.dumps({'stage':str(a.stage),'manifest_sha256':sha(a.stage/'MANIFIESTO.json'),'files':len(files),'expanded_bytes':sum(f.stat().st_size for f in files),'zlib6_estimate':sum(len(zlib.compress(f.read_bytes(),6))for f in files),'new_native_ticks':0}));return 0
if __name__=='__main__':raise SystemExit(main())
