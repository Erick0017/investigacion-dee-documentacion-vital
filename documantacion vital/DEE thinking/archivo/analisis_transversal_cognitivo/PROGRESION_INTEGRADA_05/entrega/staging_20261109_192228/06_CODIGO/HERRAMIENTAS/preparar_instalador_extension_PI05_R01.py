from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;p=H/'aplicar_fuentes_PI05_R01.py';t=p.read_text('utf8')
t=t.replace("PATCH=HERE/'FUENTES_PI05_R01_SELLADAS'","PATCH=HERE/'FUENTES_EXTENSION30_PI05_R01_PREPARADAS'")
t=t.replace("PATCH/'capacidades/PROTOCOLO_PI05_TRANSITO_R01.json'","PATCH/'capacidades/PROTOCOLO_PI05_C2C_EXTENSION_R01.json'")
t=t.replace("['status']!='SEALED'","['status']!='SEALED_BEFORE_NEW_RESERVES'")
t=t.replace("'DEE.PI05.isolated_source_CAS_install.v1'","'DEE.PI05.environment30_isolated_source_CAS_install.v1'")
t=t.replace("'FUENTES_PI05_R01_'","'EXTENSION30_PI05_R01_'")
ast.parse(t);o=H/'aplicar_extension_PI05_R01.py';assert not o.exists();o.write_text(t,encoding='utf8')
print(json.dumps({'file':str(o),'sha256':hashlib.sha256(o.read_bytes()).hexdigest(),'Native_executed':False}))
