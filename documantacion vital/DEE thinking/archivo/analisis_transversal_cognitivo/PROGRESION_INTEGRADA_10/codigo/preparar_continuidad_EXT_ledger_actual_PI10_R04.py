"""Pure ledger-aware update for optional EXT; no Native/source writes."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;src=H/'continuidad_EXT_post_COMMITTED_PI10_R03.py';out=H/'continuidad_EXT_post_COMMITTED_PI10_R04.py';text=src.read_text('utf8');old="H/'ledger_PI10_R01.py','55ec5b9b131f251a7b452b19adc2df38a07eaf54ab049804f2205359631a3ff3'";new="H/'ledger_PI10_traslado_integral_R02.py','cd936262b101943b2a6013322609500690e129624ce57a1a172dbd530f00a52e'";assert text.count(old)==1;text=text.replace(old,new);ast.parse(text)
def exact(p,t):
 if p.exists():assert p.read_text('utf8')==t
 else:
  with p.open('x',encoding='utf8')as f:f.write(t)
exact(out,text);plan=H/'preparar_plan_EXT2_PI10_R04.py';pt=(H/'preparar_plan_EXT2_PI10_R03.py').read_text('utf8');old='continuidad_EXT_post_COMMITTED_PI10_R03.py';assert pt.count(old)==1;pt=pt.replace(old,'continuidad_EXT_post_COMMITTED_PI10_R04.py');ast.parse(pt);exact(plan,pt);print(json.dumps({'cloner':str(out),'cloner_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'plan_builder':str(plan),'plan_builder_sha256':hashlib.sha256(plan.read_bytes()).hexdigest(),'Native':0}))
