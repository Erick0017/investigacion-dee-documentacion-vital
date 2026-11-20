"""Pure seal-helper provenance update to final EXT cloner; no execution."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;src=H/'sellar_EXT_desde_MAIN14_actual_PI10_R04.py';out=H/'sellar_EXT_desde_MAIN14_actual_PI10_R05.py';text=src.read_text('utf8').replace('continuidad_EXT_post_COMMITTED_PI10_R04.py','continuidad_EXT_post_COMMITTED_PI10_R05.py').replace('Clone preparerR04 accepts','Clone preparerR05 accepts');ast.parse(text)
if out.exists():assert out.read_text('utf8')==text
else:
 with out.open('x',encoding='utf8')as f:f.write(text)
print(json.dumps({'file':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'Native':0}))
