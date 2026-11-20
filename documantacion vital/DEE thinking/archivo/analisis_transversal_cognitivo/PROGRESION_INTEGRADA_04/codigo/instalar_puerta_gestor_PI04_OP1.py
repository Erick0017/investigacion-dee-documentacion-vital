"""Install only reviewed transport entrypoints in the isolated S2 code."""
from pathlib import Path
import hashlib,json,shutil,datetime
P=Path(__file__).resolve().parents[1];code=P/'codigo';S=P/'estados/candidato_R02/sistema';src=code/'PUERTA_GESTOR_PI04_OP1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(S/'gestionar.py')==sha(src/'gestionar_ANTES_PRODUCTO.py'),'Source manager changed; never overwrite another delta'
backup=code/'revisiones/ANTES_PUERTA_GESTOR_OP1';backup.mkdir(exist_ok=False);shutil.copy2(S/'gestionar.py',backup/'gestionar.py')
assert not(S/'app/pi04_cliente_acotado.py').exists()
for source,target in[(src/'gestionar.py',S/'gestionar.py'),(src/'pi04_cliente_acotado.py',S/'app/pi04_cliente_acotado.py')]:shutil.copy2(source,target);assert sha(source)==sha(target)
proof={'local':datetime.datetime.now().astimezone().isoformat(),'scope':'Isolated S2 only, no Native or product/selector changes','files':{str(t.relative_to(S)):sha(t)for t in(S/'gestionar.py',S/'app/pi04_cliente_acotado.py')},'new_Native_ticks':0}
with(P/'control/PUERTA_GESTOR_INSTALADA_S2_OP1.json').open('x',encoding='utf8')as f:json.dump(proof,f,indent=2)
print(json.dumps(proof))
