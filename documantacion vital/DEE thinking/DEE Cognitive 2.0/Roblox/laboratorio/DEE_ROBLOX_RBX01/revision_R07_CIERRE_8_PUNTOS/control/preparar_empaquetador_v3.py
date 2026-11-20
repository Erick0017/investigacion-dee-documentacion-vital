"""Version the checked R06 small-evidence packager. No final ZIP is built."""
from pathlib import Path
import ast,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
source=ROOT.parent/'revision_R06_INTEGRAL_V2/control/expediente_compacto_R06.py'
raw=source.read_bytes();text=raw.decode('utf8').replace('R06 evidence packager','R07 evidence packager')
text=text.replace('DEE.INTEGRAL.V2.','DEE.INTEGRAL.V3.').replace('CRITICOS_ANTES_R06.json','CRITICOS_ANTES_R07.json')
text=text.replace("if root!=HERE.parent/'revision_R05_C02':", "if root not in (HERE.parent/'revision_R05_C02',HERE.parent/'revision_R06_INTEGRAL_V2'):")
ast.parse(text);target=ROOT/'control/expediente_compacto_v3.py'
with target.open('x',encoding='utf8')as f:f.write(text)
proof={'schema':'DEE.R07.packager.prepared.R01','Native_calls':0,'ZIPs_built':0,'source':str(source),'source_sha256':hashlib.sha256(raw).hexdigest(),
 'changes':['R07 schemas','R07 eleven-critical baseline','exact R05 and R06 sibling historical sources allowed'],
 'target':str(target),'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
 'limit_bytes':15000000,'original_states_and_model_not_embedded':True,'final_plan_not_frozen_yet':True}
with(ROOT/'control/EMPAQUETADOR_V3_PREPARADO.json').open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2)
print(json.dumps(proof,ensure_ascii=False))
