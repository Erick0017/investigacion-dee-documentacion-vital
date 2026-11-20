"""Pure prospective stable-path fix; R03/R04 and their incident stay intact."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;src=H/'incorporar_reproducibilidad_estable_PI10_R04.py';out=H/'incorporar_reproducibilidad_estable_PI10_R05.py';text=src.read_text('utf8');old="analysis=RP/'analisis_por_receta'/ANALYSIS";new="analysis=RP/'evidencia'/ANALYSIS";assert text.count(old)==1;text=text.replace(old,new)
anchor="resources=read(resourcesfile);need(PREFIX not in resources['pairs']and CAP not in resources['code_capsules'],'Do not overwrite old resource identities');";assert text.count(anchor)==1;text=text.replace(anchor,"need(all(t.parent.is_dir()for t in targets),'Every stable-store parent must already exist; no implicit new root');"+anchor);ast.parse(text)
if out.exists():assert out.read_text('utf8')==text
else:
 with out.open('x',encoding='utf8')as f:f.write(text)
print(json.dumps({'file':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'Native':0}))
