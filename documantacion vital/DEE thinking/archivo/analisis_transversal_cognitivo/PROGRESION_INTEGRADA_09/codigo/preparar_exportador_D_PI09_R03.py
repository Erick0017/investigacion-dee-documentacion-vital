"""New export companion: only the bundled documentary reader changes to R03."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;src=H/'EXPORTAR_D_PI09_R02.py';dst=H/'EXPORTAR_D_PI09_R03.py'
assert hashlib.sha256(src.read_bytes()).hexdigest()=='dd5984203f2bbaf480667c992b439809b655f2f8b2afca6167ff40ac136c4d97'
text=src.read_text('utf8');old="for name in('RECALCULAR_D_PI09_R02.py','RECALCULAR_CONSULTA_PI09_R01.py'";new="for name in('RECALCULAR_D_PI09_R03.py','RECALCULAR_D_PI09_R02.py','RECALCULAR_CONSULTA_PI09_R01.py'";assert text.count(old)==1;text=text.replace(old,new);ast.parse(text)
with dst.open('x',encoding='utf8',newline='\n')as f:f.write(text)
print(json.dumps({'file':str(dst),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'Native_executed':False,'R02_exporter_preserved':True}))
