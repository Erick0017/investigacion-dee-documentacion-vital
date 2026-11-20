"""Pure EXT physical4 projection and matching provenance; no Native."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent
def exact(path,text):
 ast.parse(text)
 if path.exists():assert path.read_text('utf8')==text
 else:
  with path.open('x',encoding='utf8')as f:f.write(text)
text=(H/'continuidad_EXT_post_COMMITTED_PI10_R05.py').read_text('utf8');old="v['physical']==card['physical']and v['encoded_sha256']==a.snapshot_sha256";assert text.count(old)==1;text=text.replace(old,"all(v['physical'][k]==card['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256'))and v['encoded_sha256']==a.snapshot_sha256");cloner=H/'continuidad_EXT_post_COMMITTED_PI10_R06.py';exact(cloner,text)
text=(H/'sellar_EXT_desde_MAIN14_actual_PI10_R05.py').read_text('utf8').replace('continuidad_EXT_post_COMMITTED_PI10_R05.py','continuidad_EXT_post_COMMITTED_PI10_R06.py').replace('Clone preparerR05 accepts','Clone preparerR06 accepts');old="'physical':card['physical'],'full_pair_manifest'";assert text.count(old)==1;text=text.replace(old,"'physical':view['physical'],'full_pair_manifest'");seal=H/'sellar_EXT_desde_MAIN14_actual_PI10_R06.py';exact(seal,text)
text=(H/'preparar_plan_EXT2_PI10_R05.py').read_text('utf8').replace('continuidad_EXT_post_COMMITTED_PI10_R05.py','continuidad_EXT_post_COMMITTED_PI10_R06.py');plan=H/'preparar_plan_EXT2_PI10_R06.py';exact(plan,text);print(json.dumps({'cloner_sha256':hashlib.sha256(cloner.read_bytes()).hexdigest(),'seal_sha256':hashlib.sha256(seal.read_bytes()).hexdigest(),'plan_sha256':hashlib.sha256(plan.read_bytes()).hexdigest(),'Native':0}))
