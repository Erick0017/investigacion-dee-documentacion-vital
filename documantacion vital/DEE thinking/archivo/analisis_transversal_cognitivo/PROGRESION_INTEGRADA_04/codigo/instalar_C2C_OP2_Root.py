"""Reviewed administrative guard and empty-directory fix, isolated S2 only."""
from pathlib import Path
import hashlib,json,shutil,ast
P=Path(__file__).resolve().parents[1];S=P/'estados/candidato_R02/sistema';code=P/'codigo'
assert not list((S/'estado/locks').glob('*.lock')),'Preserve and inspect any world lock; no blind removal'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=code/'PI04_C2C_SCAFFOLD_OP2/pi04_coordinacion_central_C2C.py'
assert sha(source)=='51c27c6bf9cfd58f53f812268a855e2a47d458450141d585cf098939b5c27ab4'
assert sha(S/'capacidades/pi04_coordinacion_central_C2C.py')=='0b3f2f72cbcd461561555c1168295f6d08c43a48ddeb4835791528df92632607'
e3=code/'PI04_GUARDS_OPERATIVOS_CANDIDATOS/C2C_OP1/pi04_e3_contingencia.py'
assert sha(S/'capacidades/pi04_e3_contingencia.py')=='5d20c4887633ea96bb5da693848a777a913d5f24fd86aeeb93dd3345ac485b4e'
proofs=['C2C_SCAFFOLD_OP2_PRUEBAS_PURAS.json','PI04_C2C_REAL_RET2_R01.json','C2C_CTX1_FALLO_INFRAESTRUCTURA_R01.json']
assert json.loads((P/'control'/proofs[1]).read_text(encoding='utf8'))['owner_closed']
backup=code/'revisiones/ANTES_C2C_OP2_ROOT';backup.mkdir(exist_ok=False)
files={}
for src,target in[(source,S/'capacidades/pi04_coordinacion_central_C2C.py'),(e3,S/'capacidades/pi04_e3_contingencia.py')]:
 ast.parse(src.read_text(encoding='utf-8-sig'));shutil.copy2(target,backup/target.name);shutil.copy2(src,target);assert sha(target)==sha(src);files[target.name]=sha(target)
proof={'scope':'Isolated S2 code; no kernel/WHL/source state edits','files':files,'new_Native_ticks':0,'preserved_before':str(backup),'evidence':{n:sha(P/'control'/n)for n in proofs},'source_physics_or_decoder_changed':False,'technical_schema_creates_empty_fixed_folders_only_before_material':True,'old_CTX1_not_retried':True}
with(P/'control/INSTALACION_C2C_OP2_ROOT.json').open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2)
print(json.dumps(proof))
