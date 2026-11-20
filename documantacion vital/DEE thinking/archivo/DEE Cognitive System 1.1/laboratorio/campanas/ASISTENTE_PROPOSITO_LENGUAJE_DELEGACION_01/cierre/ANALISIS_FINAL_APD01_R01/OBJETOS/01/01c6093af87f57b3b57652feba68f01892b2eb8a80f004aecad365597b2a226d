"""Build a small independent archived-cost stage; no native Runtime, no ZIP."""
import argparse,hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf8'))
def emit(p,v):
 if p.exists():raise FileExistsError(str(p))
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
def copy(p,q):
 q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
 if sha(p)!=sha(q):raise ValueError('Bytes changed on copy')
def main():
 ap=argparse.ArgumentParser(description=__doc__)
 for k in('main_stage','mechanism_stage','recalculator','out','check_root'):ap.add_argument('--'+k.replace('_','-'),type=Path,required=True)
 a=ap.parse_args()
 if a.out.exists():raise FileExistsError('Fresh stage required')
 origins=[]
 def cp(p,rel):
  copy(p,a.out/'EVIDENCIA'/rel);origins.append({'included_relative':'EVIDENCIA/'+rel,'original_local_locator':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p)})
 for n in('P16_DOCENTE_CALCULO_MAIN.json.gz','P17_NOVEDAD_SIN_DOCENTE_MAIN.json.gz'):cp(a.main_stage/'PRIMARIOS'/n,'MAIN/'+n)
 for h in('T','U','D','H','CUT','SHAM'):cp(a.mechanism_stage/'EVIDENCIA/PERFIL_DELTA_R1'/h/'05_RESULTADO_COMPLETO.json.gz','CONTROLES/'+h+'/05_RESULTADO_COMPLETO.json.gz')
 cp(a.mechanism_stage/'EVIDENCIA/PERFIL_DELTA_R1/RESULTADOS.json','CONTROLES/RESULTADOS.json')
 cp(a.mechanism_stage/'EVIDENCIA/RUTA_O2_R3/COMPARACION_PASIVA/DELTA_RECIBOS_FINALES_COMPLETOS.json.gz','CONTROLES/DELTA_RECIBOS_FINALES_COMPLETOS.json.gz')
 index=read(a.main_stage/'INDICE_FUENTES_Y_OMISIONES.json');selected=[]
 for row in index['exact_code_revisions']:
  if row['primary'] in('P16_DOCENTE_CALCULO_MAIN.json.gz','P17_NOVEDAD_SIN_DOCENTE_MAIN.json.gz') and Path(row['included']).name in('experimento_inicial.py','asistente_proposito_01.py','acumulador_adquirido_apd_01.py'):
   old=a.main_stage/row['included'];rel=row['included'].removeprefix('FUENTES/')
   if sha(old)!=row['sha256']:raise ValueError('Executed source differs')
   target=a.out/'EVIDENCIA/FUENTES'/rel
   if not target.exists():cp(old,'FUENTES/'+rel)
   selected.append({**row,'original_included':row['included'],'included':rel})
 emit(a.out/'EVIDENCIA/FUENTES/REVISIONES_MAIN.json',selected)
 copy(a.recalculator,a.out/'RECALCULO/recalcular_coste_acumulador_apd.py')
 copy(Path(__file__),a.out/'CODIGO/preparar_stage_coste_acumulador_apd_n0.py')
 reference=a.out/'REFERENCIAS/COSTE_ACUMULADOR.json';reference.parent.mkdir()
 run=subprocess.run([sys.executable,'-I','-B','-X','utf8',str(a.recalculator),'--evidencia',str(a.out/'EVIDENCIA'),'--salida',str(reference)],capture_output=True,text=True,encoding='utf8',timeout=60)
 if run.returncode:raise ValueError(run.stdout+run.stderr)
 result=read(reference);m=result['main']
 report='''# Coste registrado del acumulador adquirido — APD01 N0

Extracción retrospectiva de P16/P17 y seis controles existentes; cero ticks nuevos. No se estima una ventaja de CPU ni se equipara el acumulador a SUM genérica.

## MAIN

| Fase | Tick inicial→final | Ticks | Entradas físicas | Calculadora externa | Tiempo host registrado |
|---|---|---:|---:|---:|---:|
| P16 enseñanza |112220→112227|7|2 solicitadas/aplicadas|1 docente inline|9.449938999954611 s|
| P17 cinco usos |112227→112269|42|10 solicitadas/aplicadas|0 en evaluación|7.4815540998242795 s|

La preparación de interfaces avanza0 ticks y no inserta contenido adquirido. La enseñanza recibe x=7 y el resultado17 de la calculadora externa para SUM[7,10]; se forma la diferencia física10. Los incrementos posteriores1,4,0,7,2 producen11,15,15,22,24. Son acumulación contextual y cinco oportunidades preparadas, no cinco llamadas independientes n+δ ni un operador binario aprendido. Cada uso requiere2 entradas (incremento y giro genérico): primer uso10 ticks después de enseñanza; siguientes8 ticks cada uno. La evaluación no vuelve a invocar la calculadora docente.

Los tiempos son dos comandos supervisados completos: importación, carga, observación, guardado e I/O incluidos. No son tiempos puros de cálculo. Su suma16.93149309977889 s no es una sesión continua ni una medición de CPU. La única llamada docente registra además1.6998965293169022e-06 s de pared interna; no debe usarse para extrapolar rendimiento.

## Controles

Cada rama empieza enT104472, termina enseñanzaT104479, cinco usosT104521 y panel antiguoT104929:7+42+408=457 ticks por rama. No se suman como una vida ni se consideran réplicas independientes.

| Historia | Entradas enseñanza | Entradas cinco usos | Entradas panel antiguo | Total |
|---|---:|---:|---:|---:|
| T emparejada |2|10|42|54|
| U sin docente |1|10|42|53|
| D desacoplada |2|10|42|54|
| H historia opuesta |2|10|42|54|
| CUT |3|10|42|55|
| SHAM |3|10|42|55|

Total325 entradas. En los recibos tempranos CUT y SHAM conservan cada uno una entrada scheduled, sin reescritura retrospectiva. El testigo completo posterior acredita325/325 aplicadas y ninguna pendiente. Los pares docentes de los controles son entradas preparadas declaradas, no llamadas a la calculadora externa de P16. Todos sus usos posteriores omiten nuevas referencias docentes. El supervisor conjunto de seis ramas registra62.80290630017407 s incluyendo sus paneles y guardados; no existen tiempos separados exactos por fase/control en esos primarios.

T/SHAM producen4,8,8,15,17; H produce−2,2,2,9,11; U/D/CUT emiten cinco abstenciones. El alcance de esas diferencias está en sus primarios originales; este informe sólo añade contabilidad del coste observado.

## Lo que no se concluye

El ahorro amortizado es indeterminado: no hay comparación de dominio y recursos equivalente. El SUM preparado procesa dos operandos; el acumulador conserva una diferencia adquirida y suma incrementos en una trayectoria finita. Cinco usos ensayados no demuestran borrado físico, un máximo universal de cinco, un sexto uso ni reutilización indefinida. No se miden energía ni metabolismo.

REFERENCIAS/COSTE_ACUMULADOR.json conserva cada fuente/SHA256 y sus localizadores JSON. PLAN_RECALCULO.json repite sólo esta extracción stdlib desde los primarios incluidos, sin importar el motor. Los snapshots completos quedan en las ubicaciones ya indexadas por las dos campañas de origen; este stage no los sustituye.
'''
 if (m['teaching']['tick_delta'],m['five_uses']['tick_delta'],m['five_uses']['native_inputs']['requested_unique_within_this_world_phase'])!=(7,42,10):raise ValueError('Human summary needs a declared new revision')
 (a.out/'INFORME_COSTE_ACUMULADOR.md').write_text(report,encoding='utf8')
 plan={'schema':'APD01.accumulator_recorded_cost.closed_stdlib_plan.v1','native_ticks':0,'jobs':[{'name':'COSTE_REGISTRADO_ENSENANZA_Y_CINCO_USOS','base':'.','script':'RECALCULO/recalcular_coste_acumulador_apd.py','args':['--evidencia','EVIDENCIA','--salida','{output}'],'reference':'REFERENCIAS/COSTE_ACUMULADOR.json'}]}
 emit(a.out/'PLAN_RECALCULO.json',plan)
 emit(a.out/'INDICE_FUENTES.json',{'native_ticks':0,'sources':origins,'dense_snapshots_included':False,'originals_modified':False,'scope':'Exact existing primary/code bytes copied. Sources already present in other analysis namespaces may share a CAS object without deleting their original aliases.'})
 with tempfile.TemporaryDirectory(prefix='_apd_offset_cost_',dir=a.check_root)as directory:
  tree=Path(directory)/'extraido';shutil.copytree(a.out,tree);output=Path(directory)/'out.json'
  trial=subprocess.run([sys.executable,'-I','-B','-X','utf8',str(tree/'RECALCULO/recalcular_coste_acumulador_apd.py'),'--evidencia','EVIDENCIA','--salida',str(output)],cwd=tree,capture_output=True,text=True,encoding='utf8',timeout=60)
  exact=trial.returncode==0 and output.exists()and output.read_bytes()==reference.read_bytes()
  if not exact:raise ValueError(trial.stdout+trial.stderr)
 emit(a.out/'PRUEBA_PORTABLE.json',{'native_ticks':0,'returncode':trial.returncode,'exact_reference_bytes':exact,'stdout':trial.stdout,'stderr':trial.stderr})
 emit(a.out/'MANIFIESTO.json',{'schema':'SHA256.members.no_self_reference.v1','members':[{'file':p.relative_to(a.out).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(a.out.rglob('*'))if p.is_file()]})
 files=[p for p in a.out.rglob('*')if p.is_file()]
 print(json.dumps({'stage':str(a.out),'files':len(files),'bytes':sum(p.stat().st_size for p in files),'manifest_sha256':sha(a.out/'MANIFIESTO.json'),'portable_exact':exact,'native_ticks':0}))
if __name__=='__main__':main()

