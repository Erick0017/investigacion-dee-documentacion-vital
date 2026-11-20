"""Propuesta/decisión D Root-only a partir de pruebas cerradas y seis criterios.

Sólo escribe una decisión y un contrato preparados bajo P9. --aprobar es una
decisión explícita de Root; sin los seis criterios actuales no se permite.
No abre Native, no mueve estados y no modifica el producto.
"""
from pathlib import Path
import argparse,copy,hashlib,importlib.util,json
H=Path(__file__).resolve().parent;P=H.parent;C=P.parents[2]/'DEE Cognitive 2.0'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def need(ok,msg):
 if not ok:raise ValueError(msg)
def ref(p):return {'path':str(Path(p).resolve(strict=True)),'sha256':sha(p)}
def write(p,v):
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def load():
 sp=importlib.util.spec_from_file_location('D_adopter_for_actual_closed_decision',H/'incorporar_D_PI09_misma_identidad_R03.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--evaluacion',type=Path,required=True);ap.add_argument('--referencias',type=Path,required=True);ap.add_argument('--delta',type=Path,required=True);ap.add_argument('--process-proof',type=Path,required=True);ap.add_argument('--salida',type=Path,required=True);ap.add_argument('--aprobar',action='store_true');a=ap.parse_args()
 out=a.salida.resolve();need(out.is_relative_to((P/'control').resolve())and not out.exists(),'Salida nueva sólo dentro de control PI09')
 evaluation=read(a.evaluacion);m=load();need(evaluation.get('schema')=='DEE.PI09.D.combined_actual_gates.R01'and set(evaluation.get('gates',{}))==set(m.GATES),'Se exigen los seis criterios D combinados actuales')
 refs=read(a.referencias);required={'first_milestone_adoption','D_actual_closed_arms','D_conservation_proof','D_source_reopening_function_proof','D_source_zero_reopening_proof','D_reproduction_result','D_reproduction_comparison','D_new_frontdoor_CLI_replay_verified','scope','gains','losses','uncertainties','assistance','regression_coverage','catalog_entry'};need(required<=set(refs),'Complete todas las referencias reales y el alcance razonado D')
 gates=copy.deepcopy(evaluation['gates'])
 if a.aprobar:need(all(g.get('satisfied')is True for g in gates.values()),'No se aprueba D con un criterio fallido o pendiente')
 zero=m.evidence(refs['D_source_zero_reopening_proof']);need(zero.get('schema')=='DEE.PI09.D.mature_source.public_reopening0.R01'and zero.get('closed')is True,'La Source0 debe estar cerrada antes de proponer su corte')
 delta=read(a.delta);need(delta.get('schema')=='DEE.PI09.D.operational_delta.conditional_CAS_plan.R01','Se exige el delta operativo D explícito')
 contract=copy.deepcopy(delta['new_contract']);contract.update(all_adoption_gates_met=bool(a.aprobar),prepared_is_not_approval=not a.aprobar)
 prepared=H/(out.stem+'_CONTRATO_PREPARADO.json');need(not prepared.exists(),'Contrato preparado anterior conservado');write(prepared,contract)
 rows=copy.deepcopy(delta['approved_code_files']);changed=0
 for row in rows:
  if row['file']=='contratos/PI09_D_USO_OPERATIVO_R02.json':row.update(source=str(prepared),sha256=sha(prepared),bytes=prepared.stat().st_size);changed+=1
 need(changed==1,'Se exige un único contrato D separado')
 parent=read(C/'sistema/estado/vidas'/m.m.PARENT/'VIDA.json');need(parent['physical']['tick']==903603,'El principal NATIVE ancestral debe seguir quieto')
 d={'schema':'DEE.PI09.D.reasoned_actual_adoption_decision.R01','decision_id':'PI09_ADOPCION_D_ADQUIRIDA_01','approved_for_adoption':bool(a.aprobar),'life_id':m.LIFE,'profile':'fisica_directa','source_tick':zero['final_tick'],'source_snapshot_sha256':zero['snapshot_sha256'],'source_D_ordinal':zero['stock_after']['D']['ordinal'],'protected_parent_snapshot_sha256':parent['snapshot_sha256'],'gates':gates,'approved_code_files':rows,'selectors_cas':{rel:sha(C/rel)for rel in m.base().SELECTORS},'new_contract':contract,'process_proof':str(a.process_proof.resolve(strict=True)),'evidence':[ref(a.evaluacion),ref(a.referencias),ref(a.process_proof),ref(a.delta)],**{key:refs[key]for key in required}}
 m.validate_source_zero(d)
 if a.aprobar:
  temp=H/(out.stem+'_REVISION_DECISION.json');need(not temp.exists(),'Revisión previa conservada');write(temp,d);m.decision(temp);m.code(d);m.base().selector_cas(d)
 write(out,d);print(json.dumps({'decision':str(out),'sha256':sha(out),'approved_for_adoption':bool(a.aprobar),'Native_executed':False,'product_modified':False}))
if __name__=='__main__':main()
