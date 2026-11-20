"""Bounded immutable-source/product code delta. No deployment, Native or state."""
from pathlib import Path
import argparse,ast,hashlib,json
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';N=P/'estados/NATIVE/sistema'
SELECTORS=('PROYECTO.json','CONTINUIDAD_DEE_COGNITIVE_2_0.json','sistema/estado/ACTIVO.json','sistema/estado/genesis/SELECCION_PERSONAL.json','aplicacion/GENESIS/SELECCION_CANDIDATA.json','sistema/capacidades/CATALOGO_CAPACIDADES.json')
MANDATORY={'app/mundo_genesis_apd05.py','app/cola_local.py','app/usar_dee.py','app/pi09_identidad_c2c_R01.py','capacidades/pi04_dispatcher.py','capacidades/pi09_permiso_operativo_R01.py','capacidades/pi09_transporte_heredado_R02.py','capacidades/PI09_TRANSPORTE_HEREDADO_R02.json','capacidades/pi09_dispatcher_R02.py','capacidades/PI09_PLUGINS_R02.json','capacidades/pi09_consulta_selectiva_R02.py','capacidades/PROTOCOLO_PI09_CONSULTA_R01.json','capacidades/SELLO_PI09_CONSULTA_R02.json','contratos/PI09_CONSULTA_OPERATIVA_R01.json'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def require(ok,msg):
 if not ok:raise ValueError(msg)
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--decision',type=Path);ap.add_argument('--salida',type=Path,default=H/'DELTA_OPERATIVO_PI09_R01.json');a=ap.parse_args()
 output=a.salida.resolve();require(output.is_relative_to(H.resolve())and not output.exists(),'Salida nueva sólo bajo codigo PI09')
 manifest=P/'estados/NATIVE/SISTEMA_CODIGO_PI09.json';source=read(manifest);mapping={r['file']:N/r['file']for r in source['files']}
 for row in source['files']:require(sha(mapping[row['file']])==row['sha256'],'Cambió la fuente canónica congelada: '+row['file'])
 override=H/'PERMISO_OPERATIVO_PI09_R01_PROPUESTO';plan=read(override/'PLAN.json')
 for row in plan['code_files']:require(sha(Path(row['source']))==row['sha256'],'Cambió el permiso preparado');mapping[row['file']]=Path(row['source'])
 approval=False
 if a.decision:
  file=a.decision.resolve(strict=True);require(file.is_relative_to((P/'control').resolve()),'Decisión real dentro del control PI09');d=read(file)
  require(d.get('life_id')=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01'and d.get('approved_for_adoption')is True,'La decisión Root aún no aprueba este candidato')
  contract=d['new_contract'];target=output.with_name(output.stem+'_CONTRATO_PREPARADO.json');write(target,contract);mapping['contratos/PI09_CONSULTA_OPERATIVA_R01.json']=target;approval=True
  if contract['public_arithmetic_policy']=='P0_phase19_fixed':
   require(contract.get('arithmetic_guard_actual_gate_met')is True,'No hay guardia pública P0 sin evidencia real')
   mapping['capacidades/pi09_aritmetica_temporal_P0_R01.py']=H/'pi09_aritmetica_temporal_P0_R01.py'
 rows=[];unchanged=[]
 for name,file in sorted(mapping.items()):
  require(not name.startswith(('estado/','runtime/'))and '..'not in Path(name).parts,'No se despliegan estado/motor')
  target=S/name;digest=sha(file);before=sha(target)if target.is_file()else None
  if file.suffix=='.py':ast.parse(file.read_bytes())
  elif file.suffix=='.json':read(file)
  if digest!=before or name in MANDATORY:rows.append({'file':name,'source':str(file),'bytes':file.stat().st_size,'sha256':digest,'before_sha256':before})
  else:unchanged.append({'file':name,'sha256':digest})
 require(MANDATORY<=set(r['file']for r in rows),'Falta un transporte o permiso obligatorio')
 result={'schema':'DEE.PI09.bounded_product_source_delta.R01','Native_executed':False,'source_state_read':False,'product_modified':False,'approved_decision_supplied':approval,'approved_code_files':rows,'unchanged_current_dependencies':unchanged,'bounded_source_manifest_sha256':sha(manifest),'selectors_cas':{name:sha(C/name)for name in SELECTORS},'Root_review_required':True,'prepared_contract_is_not_COMMITTED':True}
 write(output,result);print(json.dumps({'prepared':str(output),'sha256':sha(output),'changed_or_required_files':len(rows),'unchanged_dependencies':len(unchanged),'Native_executed':False,'approval':approval}))
if __name__=='__main__':main()
