"""New additive IDs after Root already registered the incomplete R02 capsule.
Never edits its recipe, manifest or source. Root-only registrar is generated.
"""
from pathlib import Path
import hashlib
H=Path(__file__).resolve().parent;source=H/'incorporar_RP_R03_PI07_R03.py';target=H/'incorporar_RP_R03_PI07_R04.py'
if target.exists():raise FileExistsError('Prepared revision preserved')
s=source.read_text('utf-8-sig')
for old,new in [('PI07_R03_LOCAL_FI_PRE34_R02','PI07_R03_LOCAL_FI_PRE34_R03'),('pi07_r03_uso_adquirido_post4_R02','pi07_r03_uso_adquirido_post4_R03'),('PI07_R03_ANALISIS_POST4_R01','PI07_R03_ANALISIS_POST4_R03'),('RP_R03_DOCUMENTAL_STAGE_R02','RP_R03_DOCUMENTAL_STAGE_R03'),('RP_RECURSOS_ANTES_R03_PI07_R02.json','RP_RECURSOS_ANTES_R03_PI07_R03.json'),('RP_R03_INCORPORADA_PI07_R03.json','RP_R03_INCORPORADA_PI07_R04.json')]:s=s.replace(old,new)
s=s.replace("'revision':'R01_NATIVE_REFERENCE_VERIFIED_CLI_REPLAY_PENDING'", "'revision':'R03_PRE34_FULL_CPC_DEPENDENCIES_CLI_REPLAY_PENDING','supersedes_incomplete_recipe':'pi07_r03_uso_adquirido_post4_R02'")
needle="recipe=build_recipe();files=snapshot_sources();pre34=pre34_validation(files);source_manifest="
replacement="""oldrecipe=RP/'recetas/pi07_r03_uso_adquirido_post4_R02.json';oldcaps=RP/'codigo_preservado/PI07_R03_LOCAL_FI_PRE34_R02/SISTEMA_CODIGO.json'
 oldhashes={str(file):sha(file)for file in(oldrecipe,oldcaps)}
 recipe=build_recipe();files=snapshot_sources();pre34=pre34_validation(files);source_manifest="""
if needle not in s:raise ValueError('Expected exact registrar preflight')
s=s.replace(needle,replacement)
needle="if any(sha(Path(path))!=v for path,v in critical.items()):raise RuntimeError('Protected principal metadata changed')"
replacement=needle+"""
 if any(sha(Path(path))!=digest for path,digest in oldhashes.items()):raise RuntimeError('Historical incomplete R02recipe/capsule modified')
 advisory=RP/'verificaciones/pi07_r03_uso_adquirido_post4_R02/ADVERTENCIA_DEPENDENCIAS_CPC_R03.json'
 put(advisory,{'schema':'DEE.reproduction.static_dependency_advisory.v1','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'recipe':'pi07_r03_uso_adquirido_post4_R02','status':'DOCUMENTED_DEPENDENCY_BLOCK_SUPERSEDED','actual_native_execution_completed':False,'new_native_ticks':0,'reason':'The original frozen manifest omitted44organizaciones/cpc9 Python sources required by app/lives.py legacy_class and the inherited .eventos file. Generic byte checks alone cannot prove dependency closure. Do not execute the old R02recipe.','use_replacement_recipe':RECIPE,'old_literals_preserved':oldhashes,'new_frontdoor_Native_verified':False,'transport_note':'Additive advisory visible in listar/verificar actual_registered_verifications; the old immutable recipe has not been silently rewritten or retroactively marked verified.'})
"""
if needle not in s:raise ValueError('Expected exact preservation checkpoint')
s=s.replace(needle,replacement)
s=s.replace("'source_native_reference_executed':True,'new_frontdoor_CLI_material_replay_executed':False", "'old_incomplete_recipe_literals_preserved':oldhashes,'dependency_advisory':{'path':str(advisory),'sha256':sha(advisory)},'source_native_reference_executed':True,'new_frontdoor_CLI_material_replay_executed':False")
compile(s,str(target),'exec');target.write_text(s,encoding='utf8');print(str(target));print(hashlib.sha256(target.read_bytes()).hexdigest())
