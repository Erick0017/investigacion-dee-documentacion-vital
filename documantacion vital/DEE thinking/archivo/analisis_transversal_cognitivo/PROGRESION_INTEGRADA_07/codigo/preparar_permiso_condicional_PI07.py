"""Prepare only: exact administrative successor permissions for Root review.

No apply mode, C/S7 writes, Native imports or contract activation. Root may
include these explicit deltas in a later gated full-world adoption decision.
"""
from pathlib import Path
import ast,hashlib,json
P=Path(__file__).resolve().parents[1];H=P/'codigo';S=P/'estados/candidato/sistema';C=P.parents[2]/'DEE Cognitive 2.0';DEST=H/'PI07_ADOPCION_PERMISOS_PREPARADA'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_CAND_01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,value):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
 if DEST.exists():raise FileExistsError('Preserve prior conditional delta')
 DEST.mkdir();rows=[]
 # The old administrative adapter's parser/Store API is preserved; one exact
 # successor identity and its permitted previous current leaf are narrowed.
 oldfile=S/'app/pi05_identidad_c2c.py';old=oldfile.read_text('utf8');new=old.replace('PI05','PI07')
 new=new.replace('ECI02_PI03_REPRO_PI04_PI07_MAIN_01',LIFE)
 new=new.replace("or not source_life.startswith('ECI02_PI03_REPRO_PI04_')","or source_life!=LIFE")
 new=new.replace("if not isinstance(metadata.get('life_id'),str)or any","if metadata.get('life_id')not in('ECI02_PI03_REPRO_PI04_PI05_MAIN_01',LIFE)or any")
 ast.parse(new);adapter=H/'pi07_identidad_c2c.py'
 if adapter.exists():raise FileExistsError('Adapter already prepared')
 adapter.write_text(new,encoding='utf8')
 for source,relative in((adapter,'app/pi07_identidad_c2c.py'),(H/'pi07_permiso_principal_R01.py','capacidades/pi07_permiso_principal_R01.py')):
  data=source.read_bytes();ast.parse(data);target=DEST/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);rows.append({'file':relative,'source':str(source),'sha256':sha(target),'bytes':len(data),'must_be_absent_in_product':True})
 source=S/'capacidades/pi04_dispatcher.py';old=source.read_text('utf8');oldline="return _load('pi05_permiso_principal_R01').configure(component,a)"
 if old.count(oldline)!=2:raise ValueError('Exact old permission call sites required')
 new=old.replace(oldline,"return _load('pi07_permiso_principal_R01').configure(_load('pi05_permiso_principal_R01').configure(component,a),a)")
 oldlist="paths.append(root/'pi05_permiso_principal_R01.py')"
 if old.count(oldlist)!=1:raise ValueError('Exact old code locator required')
 new=new.replace(oldlist,oldlist+"\n    paths.append(root/'pi07_permiso_principal_R01.py')")
 ast.parse(new);target=DEST/'capacidades/pi04_dispatcher.py';target.write_text(new,encoding='utf8');rows.append({'file':'capacidades/pi04_dispatcher.py','source':str(source),'source_before_sha256':sha(source),'product_before_sha256':sha(C/'sistema/capacidades/pi04_dispatcher.py'),'sha256':sha(target),'bytes':target.stat().st_size,'scope':'Two nested fixed permission call sites and code-file locator only; no actor, phase, payload, Native function or expected result changes.'})
 template={'schema':'DEE.PI07.exact_adopted_permission.v1','status':'DRAFT_NOT_AUTHORITY','life_id':LIFE,'profile':'fisica_directa','protocol_sha256':'f69e8558799558a1ccceb70e0684a061a971b9521ad8985205d1662aea55d269','allowed_modes':['eci01-pi07-r03-episodio','eci01-pi07-r03-estado'],'C2C_use':{'allowed_modes':['eci01-pi04-c2c-oportunidad','eci01-pi04-c2c-estado'],'requires_environment30':True,'protocol_sha256':'5dda50c36fa72ea3932eded545e0bb673b40202d0d553cfa97a50ab31c67d1bc','current_C2C_life_id':LIFE},'adoption_decision_sha256':None,'preparation_readmission_calibration_and_cuts_forbidden_on_selected':True,'ordering':'Only after real Store.promote COMMITTED witness, immediately before first selected Owner; never install this draft as authority.'}
 save(DEST/'PI07_REGULACION_USO_PRINCIPAL_01.PLANTILLA_NO_ACTIVA.json',template)
 plan={'schema':'DEE.PI07.conditional_exact_principal_permission_delta.v1','status':'PREPARADO_NO_APLICADO_GATES_PENDIENTES','target_life_id':LIFE,'files':rows,'preserved_dependencies':{str(file.relative_to(S)):sha(file)for file in(S/'capacidades/pi04_coordinacion_central_C2C.py',S/'capacidades/pi05_c2c_ofertas_R01.py',S/'capacidades/PROTOCOLO_PI05_C2C_30_R01.json',S/'capacidades/PROTOCOLO_PI05_C2C_EXTENSION_R01.json',S/'capacidades/pi05_permiso_principal_R01.py')},'one_administrative_metadata_leaf':{'KEY':'DEE.Cognitive.PI04.C2C.coordination.R01','pointer':'/life_id','from':'ECI02_PI03_REPRO_PI04_PI05_MAIN_01','to':LIFE,'only_after_full_pair_import':True,'all_other_metadata_and_Native_causal_prefix_must_be_exact':True},'required_order':['Root checks actual scientific/conservation/continuity gates and current-main CAS; no anticipated promotion.','Preserve complete S7 source and product parent; full paired import unselected target, exact files only.','Root may call app.pi07_identidad_c2c.rebind_imported_C2C_identity(store,target_life,source_life); both target/source world IDs are exact CAND_01; old inherited C2C current leaf remains recorded as PI05_MAIN.','Prove complete Native physical and causal-prefix equality and all other nonadministrative metadata identical; reopen unselected0ticks.','Only after actual Store.promote COMMITTED, install exact permission contract with that actual adoption decision SHA before any selected Owner starts.','Selected state/opportunity only; preparation/admission/calibration/cuts remain refused.','If any gate fails, do not apply delta or activate permission.'],
 'resupply_analysis':{'existing_30to32_command':None,'old26to30_reinvocation_forbidden':True,'current_offers':'ordinal28/30; two offers at the protected source before any conservation consumption','gap':'A new prospective external extension requires a new immutable appended protocol, manifest/KEY/journal, effective-component layer, resource transaction, tests and actual isolated use. Merely appending files or resetting counters is invalid.'},'Native_executed':False,'S7_or_product_modified':False}
 output=P/'control/PI07_PERMISOS_CONDICIONALES_PREPARADOS_R01.json';save(output,plan)
 print(json.dumps({'plan':str(output),'sha256':sha(output),'files':len(rows),'Native_executed':False,'product_modified':False}))
if __name__=='__main__':main()
