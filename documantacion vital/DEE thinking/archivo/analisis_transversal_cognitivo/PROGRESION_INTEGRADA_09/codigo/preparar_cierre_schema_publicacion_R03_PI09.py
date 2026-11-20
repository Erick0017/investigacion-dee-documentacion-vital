"""Compatibilidad exacta R01/R02 de publicación1.38, mismos bytes/filas."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
rows=[]
for src,dst in(('cerrar_presupuesto_y_estado_PI09_R02.py','cerrar_presupuesto_y_estado_PI09_R03.py'),('sincronizar_cierre_actual_PI09_R03.py','sincronizar_cierre_actual_PI09_R04.py')):
 source=H/src;target=H/dst
 if target.exists():raise FileExistsError('Revisión nueva anterior conservada')
 text=source.read_text('utf8');old="get('schema')=='DEE.PI09.actual_complete_DOCX_publication.R01'";new="get('schema')in('DEE.PI09.actual_complete_DOCX_publication.R01','DEE.PI09.actual_complete_DOCX_publication.R02')"
 if text.count(old)!=1:raise ValueError('Comparación única de publicación esperada')
 text=text.replace(old,new)
 if src.startswith('cerrar'):
  text=text.replace("sync.get('schema')=='DEE.PI09.final_current_metadata.applied.R03'","sync.get('schema')in('DEE.PI09.final_current_metadata.applied.R03','DEE.PI09.final_current_metadata.applied.R04')").replace("H/'sincronizar_cierre_actual_PI09_R03.py'","H/'sincronizar_cierre_actual_PI09_R04.py'")
 else:text=text.replace('CAS_plan.R03','CAS_plan.R04').replace('applied.R03','applied.R04').replace('SINCRONIZACION_FINAL_ACTUAL_PI09_R03.json','SINCRONIZACION_FINAL_ACTUAL_PI09_R04.json').replace('SINCRONIZACION_FINAL_PI09_R03','SINCRONIZACION_FINAL_PI09_R04')
 ast.parse(text);target.write_text(text,'utf8');rows.append({'file':dst,'sha256':sha(target),'source_preserved_sha256':sha(source)})
print(json.dumps({'files':rows,'only_publication_schema_alias_and_new_revision_outputs':True,'Native_executed':False,'product_writes':False}))
