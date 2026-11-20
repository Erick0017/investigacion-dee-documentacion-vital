"""Genera revisión del supervisor D apuntando sólo al incorporador Source0 R02."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source=H/'ejecutar_administracion_D_con_tope_PI09_R01.py';target=H/'ejecutar_administracion_D_con_tope_PI09_R02.py'
if target.exists():raise FileExistsError('Supervisor R02 previo conservado')
text=source.read_text('utf8');old='incorporar_D_PI09_misma_identidad_R01.py'
if text.count(old)!=1:raise ValueError('Ancla del supervisor cambió')
text=text.replace(old,'incorporar_D_PI09_misma_identidad_R02.py').replace("'_512M_PI09_R01.json'","'_512M_PI09_R02.json'").replace('DEE.PI09.D.owned_admin512.R01','DEE.PI09.D.owned_admin512.R02')
ast.parse(text);target.write_text(text,'utf8');print(json.dumps({'source_sha256':sha(source),'target':str(target),'sha256':sha(target),'Native_executed':False,'product_writes':False}))
