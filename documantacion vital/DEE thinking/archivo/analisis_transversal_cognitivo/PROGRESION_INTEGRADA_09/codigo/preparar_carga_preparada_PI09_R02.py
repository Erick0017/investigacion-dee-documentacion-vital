"""New exact full-payload administrative gate. Preserves failed R01/R03 uses."""
from pathlib import Path
import ast,hashlib,json,shutil
H=Path(__file__).resolve().parent;P=H.parent;C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';OUT=H/'CARGA_PREPARADA_PI09_R02_PROPUESTA'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def once(t,a,b):
 if t.count(a)!=1:raise ValueError('Exact administrative anchor changed '+a[:80])
 return t.replace(a,b)
def main():
 if OUT.exists():raise FileExistsError('Preserve prior revision')
 OUT.mkdir();old=H/'pi09_carga_preparada_R01.py';helper=old.read_text('utf-8-sig');start=helper.index('def guard_external(');end=helper.index('def install():',start)
 helper=helper[:start]+'''def guard_external(a,row,*,payload=None):
 from capacidades import pi09_permiso_operativo_R01 as permission
 identity=permission._identity(a)
 if identity.get('life_id')!=LIFE or permission._selected()==LIFE:return
 prepared(a,identity)
 need(isinstance(payload,dict),'Se requiere la petición completa para la carga administrativa')
 operation=payload.get('operacion')
 if operation in {'reanudar','pausar','guardar','detener'}:
  need(set(payload)=={'operacion'}and row is None,'Control administrativo exacto sin datos ni ticks');return
 need(operation=='sesion'and set(payload)<={'operacion','situaciones','actuador','retorno'}and payload.get('actuador','closed')=='closed'and payload.get('retorno','real')=='omit','La fase PREPARED sólo admite controles y STATE omit/closed')
 situations=payload.get('situaciones');need(isinstance(situations,list)and len(situations)==1 and situations[0]==row and isinstance(row,dict)and set(row)=={'modo'}and row.get('modo')in STATES,'Sólo una de las tres STATE registradas; ningún episodio, FI, aritmética ni memoria material')
''' +helper[end:]
 helper=helper.replace('DEE.PI09.exact_prepared_unselected_load.R01','DEE.PI09.exact_prepared_unselected_load.R02');ast.parse(helper);(OUT/'pi09_carga_preparada_R02.py').write_text(helper,'utf8')
 permission=S/'capacidades/pi09_permiso_operativo_R01.py';text=permission.read_text('utf-8-sig');text=once(text,'def validate_selected_external(a,row):','def validate_selected_external(a,row,*,payload=None):');text=text.replace('pi09_carga_preparada_R01','pi09_carga_preparada_R02');text=once(text,' prepared_load.guard_external(a,row)',' prepared_load.guard_external(a,row,payload=payload)');ast.parse(text);(OUT/permission.name).write_text(text,'utf8')
 world=S/'app/mundo_genesis_apd05.py';text=world.read_text('utf-8-sig');before='pi09_permission.validate_selected_external(self.a,row)'
 if text.count(before)!=2:raise ValueError('Exact two public validation/execute calls required')
 text=text.replace(before,'pi09_permission.validate_selected_external(self.a,row,payload=payload)');ast.parse(text);(OUT/world.name).write_text(text,'utf8')
 prior=P/'control/CARGA_PREPARADA_PI09_APLICADA_R01.json';prepared=P/'control/PREPARACION_TRASLADO_PRODUCTO_PI09.json';prep=json.loads(prepared.read_text('utf-8-sig'))
 rows=[{'file':rel,'source':str(OUT/name),'sha256':sha(OUT/name),'before_sha256':sha(S/rel)if(S/rel).exists()else None}for rel,name in(('capacidades/pi09_permiso_operativo_R01.py',permission.name),('app/mundo_genesis_apd05.py',world.name),('capacidades/pi09_carga_preparada_R02.py','pi09_carga_preparada_R02.py'))]
 plan={'schema':'DEE.PI09.prepared_load.administrative_supplement.CAS_plan.R02','Native_executed':False,'applied':False,'preparation':{'path':str(prepared),'sha256':sha(prepared)},'decision':prep['decision'],'prior_supplement':{'path':str(prior),'sha256':sha(prior)},'files':rows,'only_full_payload_admin_controls_or_single_STATE':True,'pending_exact_STATE_id_preserved':'PI09_PRODUCT0_UNSELECTED_R03_PI09','no_automatic_existing_request_resubmit':True,'failed_R01_and_R03_sources_and_queues_preserved':True}
 (OUT/'PLAN.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'plan':str(OUT/'PLAN.json'),'sha256':sha(OUT/'PLAN.json'),'files':rows}))
if __name__=='__main__':main()
