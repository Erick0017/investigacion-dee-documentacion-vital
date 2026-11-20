"""Pure prospective pre-write README-anchor check; original R02 preserved."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;src=H/'registrar_replay_Native_estable_PI10_R02.py';out=H/'registrar_replay_Native_estable_PI10_R03.py';text=src.read_text('utf8');anchor="before_recipe=sha(recipefile);before_readme=sha(readme)";assert text.count(anchor)==1;text=text.replace(anchor,anchor+";need(readme.read_text('utf-8-sig').count('Esta incorporación conserva los medios, no acredita todavía el replay Native ni la adopción.')==1,'Exact prior README anchor must be valid before ANY write')");ast.parse(text)
if out.exists():assert out.read_text('utf8')==text
else:
 with out.open('x',encoding='utf8')as f:f.write(text)
print(json.dumps({'file':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'Native':0}))
