"""Nuevo tag/archivo para reapertura D tras CAS, sin reenvío de ningún ID."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
rows=[]
for src,dst in(('reabrir_producto_D_PI09_0_R01.py','reabrir_producto_D_PI09_0_R02.py'),('ejecutar_administracion_D_con_tope_PI09_R03.py','ejecutar_administracion_D_con_tope_PI09_R04.py')):
 source=H/src;target=H/dst
 if target.exists():raise FileExistsError('Nueva revisión anterior conservada')
 text=source.read_text('utf8')
 if src.startswith('reabrir'):
  text=text.replace('REAPERTURA_SELECCIONADA_D_PRODUCTO_PI09.json','REAPERTURA_SELECCIONADA_D_PRODUCTO_PI09_R02.json').replace('REAPERTURA_D_PRODUCTO_PI09.json','REAPERTURA_D_PRODUCTO_PI09_R02.json').replace('PI09_D_PRODUCT0_SELECTED_R01','PI09_D_PRODUCT0_SELECTED_R02').replace('PI09_D_PRODUCT0_UNSELECTED_R01','PI09_D_PRODUCT0_UNSELECTED_R02')
 else:text=text.replace('incorporar_D_PI09_misma_identidad_R03.py','incorporar_D_PI09_misma_identidad_R04.py').replace('_512M_PI09_R03.json','_512M_PI09_R04.json').replace('DEE.PI09.D.owned_admin512.R03','DEE.PI09.D.owned_admin512.R04')
 ast.parse(text);target.write_text(text,'utf8');rows.append({'file':dst,'sha256':sha(target),'source_preserved_sha256':sha(source)})
print(json.dumps({'files':rows,'Native_executed':False,'product_writes':False}))
