"""Prepare separate Root D administrative supervisors; no state/Native read."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;NATIVE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01';DISCOVERY='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01';A='ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,t):
 if p.exists():raise FileExistsError('Prior revision preserved')
 ast.parse(t);p.write_text(t,'utf8')
def main():
 rows=[];source=H/'comprobar_procesos_afectados_PI09_R01.py';target=H/'comprobar_procesos_adopcion_D_PI09_R01.py';text=source.read_text('utf-8-sig').replace("SOURCE=P/'estados/NATIVE/sistema'","SOURCE=P/'estados/DISCOVERY/sistema'").replace(NATIVE,DISCOVERY).replace(A,NATIVE);save(target,text);rows.append({'file':target.name,'source_sha256':sha(source),'sha256':sha(target)})
 source=H/'ejecutar_administracion_con_tope_PI09_R05.py';target=H/'ejecutar_administracion_D_con_tope_PI09_R01.py';text=source.read_text('utf-8-sig').replace(NATIVE,DISCOVERY).replace(A,NATIVE).replace('incorporar_PI09_misma_identidad_R05.py','incorporar_D_PI09_misma_identidad_R01.py').replace('PREPARACION_TRASLADO_PRODUCTO_PI09.json','PREPARACION_TRASLADO_D_PRODUCTO_PI09.json').replace('ADOPCION_PRODUCTO_PI09.json','ADOPCION_D_PRODUCTO_PI09.json').replace("'ADMINISTRACION_'+a.accion.upper()+'_512M_PI09_R01.json'","'ADMINISTRACION_D_'+a.accion.upper()+'_512M_PI09_R01.json'").replace('DEE.PI09.owned_admin512.v1','DEE.PI09.D.owned_admin512.R01');save(target,text);rows.append({'file':target.name,'source_sha256':sha(source),'sha256':sha(target)})
 result={'schema':'DEE.PI09.D.adoption_Root_tools.prepared.R01','Native_executed':False,'conditional_on_six_actual_gates_and_Root_approval':True,'files':rows};(H/'HERRAMIENTAS_ADOPCION_D_PI09_R01.json').write_text(json.dumps(result,indent=2)+'\n','utf8');print(json.dumps(result))
if __name__=='__main__':main()
