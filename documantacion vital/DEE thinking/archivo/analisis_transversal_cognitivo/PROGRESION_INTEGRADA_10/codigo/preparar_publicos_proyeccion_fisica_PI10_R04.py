"""Pure explicit physical4/card8 projection fix; all R03 sources preserved."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def exact(p,text):
 ast.parse(text)
 if p.exists():assert p.read_text('utf8')==text
 else:
  with p.open('x',encoding='utf8')as f:f.write(text)
old=H/'pi10_gestor_publico_R03.py';helper=H/'pi10_gestor_publico_R04.py';t=old.read_text('utf8');anchor="v['physical']==card['physical']and v['encoded_sha256']==card['snapshot_sha256']";assert t.count(anchor)==1;t=t.replace(anchor,"all(v['physical'][k]==card['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256'))and v['encoded_sha256']==card['snapshot_sha256']").replace("VERSION='DEE.PI10.exact_public_manager.R03'","VERSION='DEE.PI10.exact_public_manager.R04'");exact(helper,t)
t=(H/'pi10_publico_acotado_comun_R03.py').read_text('utf8');anchor="v['physical']==card['physical']";assert t.count(anchor)==1;t=t.replace(anchor,"all(v['physical'][k]==card['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256'))");common=H/'pi10_publico_acotado_comun_R04.py';exact(common,t)
t=(H/'reabrir_producto_PI10_0_R03.py').read_text('utf8').replace('pi10_publico_acotado_comun_R03.py','pi10_publico_acotado_comun_R04.py').replace('PRODUCTO_PI10_SELECCIONADA_0_R03','PRODUCTO_PI10_SELECCIONADA_0_R04').replace('PRODUCTO_PI10_PREPARADA_0_R03','PRODUCTO_PI10_PREPARADA_0_R04').replace('PI10_PRODUCT0_SELECTED_R03','PI10_PRODUCT0_SELECTED_R04').replace('PI10_PRODUCT0_PREPARED_R03','PI10_PRODUCT0_PREPARED_R04');zero=H/'reabrir_producto_PI10_0_R04.py';exact(zero,t)
t=(H/'usar_principal_PI10_EP13_publico_R03.py').read_text('utf8').replace('pi10_publico_acotado_comun_R03.py','pi10_publico_acotado_comun_R04.py').replace('pi10_gestor_publico_R03.py','pi10_gestor_publico_R04.py').replace('b6a5a0aac2258825ed7bfb8ef4d70bb6aebcdddf480873272fecc49ca138441e',sha(helper)).replace('DEE.PI10.exact_public_manager.R03','DEE.PI10.exact_public_manager.R04').replace('PI10_PUBLIC_EP13_R03','PI10_PUBLIC_EP13_R04');public=H/'usar_principal_PI10_EP13_publico_R04.py';exact(public,t)
generator=(H/'preparar_gestor_publico_PI10_R02.py').read_text('utf8').replace('GESTOR_PUBLICO_PI10_R02_PREPARADO','GESTOR_PUBLICO_PI10_R04_PREPARADO').replace('pi10_gestor_publico_R02.py','pi10_gestor_publico_R04.py').replace('DEE.PI10.public_manager.staged_exact_delta.R02','DEE.PI10.public_manager.staged_exact_delta.R04');ast.parse(generator);namespace={'__file__':str(H/'preparar_gestor_publico_PI10_R02.py'),'__name__':'PI10_R04_projection_stage_only'};exec(compile(generator,'PI10_R04_public_fixed_physical4_projection','exec'),namespace)
print(json.dumps({'common_sha256':sha(common),'zero_sha256':sha(zero),'public_sha256':sha(public),'Native':0}))
