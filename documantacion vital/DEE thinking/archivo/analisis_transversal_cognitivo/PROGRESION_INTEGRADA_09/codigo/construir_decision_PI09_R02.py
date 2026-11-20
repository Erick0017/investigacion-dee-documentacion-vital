"""Root-only reasoned adoption proposal; approval requires explicit --aprobar.

Actual gates and named source/replay/conservation proofs are mandatory.
Prepares codigo only. The source bodies, selected product and state stay still.
"""
from pathlib import Path
import argparse,copy,hashlib,importlib.util,json
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0'
GATES=('functional_gain','conservation','causal_controls','source_reopening','new_function_at_final_cut','decisive_recipe_replay')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def ref(p):return {'path':str(p.resolve(strict=True)),'sha256':sha(p)}
def require(ok,msg):
 if not ok:raise ValueError(msg)
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--evaluacion',type=Path,required=True);ap.add_argument('--referencias',type=Path,required=True);ap.add_argument('--process-proof',type=Path,required=True);ap.add_argument('--salida',type=Path,required=True);ap.add_argument('--aprobar',action='store_true');a=ap.parse_args()
 out=a.salida.resolve();require(out.is_relative_to((P/'control').resolve())and not out.exists(),'Comprobante nuevo sólo bajo control PI09')
 evaluation=read(a.evaluacion);require(evaluation.get('schema')=='DEE.PI09.consultation.combined_actual_gates.R01'and set(evaluation['gates'])==set(GATES),'Evaluación científica final única requerida')
 refs=read(a.referencias);required={'PI09_actual_closed_arms','PI09_source_full_pair','PI09_reproduction_result','PI09_reproduction_comparison','PI09_conservation_proof','scope','gains','losses','uncertainties','assistance','regression_coverage','catalog_entry','PI09_source_reopening_proof'};require(required<=set(refs),'Complete las referencias reales, la entrada de catálogo existente y el alcance razonado')
 gates=copy.deepcopy(evaluation['gates'])
 if a.aprobar:require(all(g.get('satisfied')is True for g in gates.values()),'No se aprueba una ganancia sin los seis criterios actuales')
 delta=read(H/'DELTA_OPERATIVO_PI09_R01.json');contract=read(H/'PERMISO_OPERATIVO_PI09_R01_PROPUESTO/contratos/PI09_CONSULTA_OPERATIVA_R01.json')
 contract.update(all_adoption_gates_met=bool(a.aprobar),prepared_is_not_operational_approval=not a.aprobar)
 if refs.get('public_arithmetic_policy')=='P0_phase19_fixed':
  evidence=refs.get('arithmetic_guard_actual_evidence',[]);require(len(evidence)>=2 and refs.get('arithmetic_guard_actual_gate_met')is True,'La nueva ruta aritmética exige pareja/reserva materiales reales')
  contract.update(public_arithmetic_policy='P0_phase19_fixed',arithmetic_guard_actual_gate_met=True,arithmetic_guard_actual_evidence=evidence)
 prepared_contract=H/(out.stem+'_CONTRATO_PREPARADO.json');require(not prepared_contract.exists(),'Contrato propuesto anterior preservado');prepared_contract.write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n','utf8')
 rows=copy.deepcopy(delta['approved_code_files'])
 for row in rows:
  if row['file']=='contratos/PI09_CONSULTA_OPERATIVA_R01.json':row.update(source=str(prepared_contract),sha256=sha(prepared_contract),bytes=prepared_contract.stat().st_size)
 if contract['public_arithmetic_policy']=='P0_phase19_fixed':
  source=H/'pi09_aritmetica_temporal_P0_R01.py';target=C/'sistema/capacidades'/source.name
  if not any(r['file']=='capacidades/'+source.name for r in rows):rows.append({'file':'capacidades/'+source.name,'source':str(source),'sha256':sha(source),'bytes':source.stat().st_size,'before_sha256':sha(target)if target.is_file()else None})
 pair=Path(refs['PI09_source_full_pair']['path']);manifest=read(pair/'EXPORTACION_SERVICIO.json');source_reopening=read(Path(refs['PI09_source_reopening_proof']['path']))
 d={'schema':'DEE.PI09.reasoned_actual_adoption_decision.R01','decision_id':'PI09_ADOPCION_CONSULTA_NATIVE_01','approved_for_adoption':bool(a.aprobar),'life_id':'ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01','source_tick':manifest['physical']['tick'],'source_snapshot_sha256':source_reopening['snapshot_sha256'],'gates':gates,'approved_code_files':rows,'selectors_cas':{rel:sha(C/rel)for rel in delta['selectors_cas']},'new_contract':contract,'catalog_entry':refs.get('catalog_entry',{'id':'PI09_CONSULTA_REGISTRADA_NATIVE_R02','type':'integracion_native_adquirida','status':'ACTUAL_GATES_PASSED_PENDING_ROOT_COMMIT','scope':refs['scope'],'limitations':refs['losses']+refs['uncertainties']}),'process_proof':str(a.process_proof.resolve(strict=True)),'evidence':[ref(a.evaluacion),ref(a.referencias),ref(a.process_proof)],**{key:refs[key]for key in required}}
 require(manifest['life_id']==d['life_id'],'El prefijo pertenece a otra vida')
 if a.aprobar:
  sp=importlib.util.spec_from_file_location('PI09_conditional_adopter_validator',H/'incorporar_PI09_misma_identidad_R03.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
  temporary=H/(out.stem+'_REVISION_DECISION.json');require(not temporary.exists(),'Revisión anterior preservada');temporary.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
  m.decision(temporary);m.code(d);m.selector_cas(d)
 with out.open('x',encoding='utf8')as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'decision':str(out),'sha256':sha(out),'approved_for_adoption':d['approved_for_adoption'],'Native_executed':False,'product_modified':False,'Root_explicit_approval_argument':bool(a.aprobar)}))
if __name__=='__main__':main()
