"""PLAN default. Root static CAS publication of the PI11 readonly RP R02.

Preserves every R01 capsule byte and recipe. A new R02 capsule changes only
the documented owner bootstrap hooks, adds the exact non-REAL readonly shim
and updates its code registry. Native actor/environment/protocol are literal.
No Native, importer, owner, state or experiment is executed by this updater.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ast,copy,hashlib,importlib.util,json,os,shutil
H=Path(__file__).resolve().parent;P=H.parent;C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad'
OLD='pi11_habitat16_familia_desde_REAL2_R01';NEW='pi11_habitat16_familia_desde_REAL2_R02'
OLDCAP='PI11_HABITAT16_FAMILIA_R01';NEWCAP='PI11_HABITAT16_FAMILIA_R02'
NEWREL='reproducibilidad/codigo_preservado/'+NEWCAP
SHIM='capacidades/pi11_identidad_diagnostica_R02.py';OWNER='app/mundo_genesis_apd05.py';REGISTRY='capacidades/PI11_PLUGINS_R01.json'

def need(ok,msg):
    if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def encoded(v):return(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def regular(p):
    p=Path(p).absolute()
    for n in(p,*p.parents):need(not n.is_symlink()and(not n.exists()or not(getattr(n.lstat(),'st_file_attributes',0)&1024)),'No linked/reparse source/target')
    return p
def load(name,p):
    sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def new(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb')as f:f.write(encoded(v));f.flush();os.fsync(f.fileno())
def copy_new(source,target,digest=None):
    regular(source);regular(target);need(source.is_file()and not target.exists(),'Existing exact source/new target only')
    if digest is not None:need(sha(source)==digest,'Source changed before copy')
    target.parent.mkdir(parents=True,exist_ok=True)
    with source.open('rb')as inp,target.open('xb')as out:shutil.copyfileobj(inp,out);out.flush();os.fsync(out.fileno())
    need(sha(source)==sha(target),'Copy integrity')
def cas(p,digest,data):
    need(sha(p)==digest,'Concurrent mutation; original not overwritten');tmp=p.with_name(p.name+'.PI11_RP_R02_WRITING');need(not tmp.exists(),'Partial write preserved')
    with tmp.open('xb')as f:f.write(data);f.flush();os.fsync(f.fileno())
    need(sha(p)==digest,'Concurrent mutation before replace');os.replace(tmp,p)

def proposed_manifest(oldmanifest,oldroot,shimbytes,patcher):
    """Pure proposed code delta; no original code/role/state edits."""
    owner=patcher((oldroot/OWNER).read_text('utf-8-sig')).encode('utf8');ast.parse(owner)
    registry=read(oldroot/REGISTRY);registry['files_sha256'][Path(SHIM).name]=hashlib.sha256(shimbytes).hexdigest()
    blobs={OWNER:owner,REGISTRY:encoded(registry),SHIM:shimbytes};rows={row['file']:copy.deepcopy(row)for row in oldmanifest['files']}
    need(SHIM not in rows,'Readonly shim already present; preserve previous revision')
    for name,data in blobs.items():rows[name]={'file':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
    return blobs,{'schema':'DEE.PI11.stable_code_capsule.R02','source_R01_manifest_sha256':sha(oldroot/'SISTEMA_CODIGO.json'),
                  'instrumental_readonly_bootstrap_revision':'R02','Native_actor_environment_protocol_changed':False,
                  'state_or_engine_included':False,'files':[rows[name]for name in sorted(rows)]}

def main(apply=False):
    resources=RP/'RECURSOS.json';frontdoor=RP/'reproducir.py';oldrecipefile=RP/'recetas'/(OLD+'.json')
    for path in(resources,frontdoor,oldrecipefile,H/'pi11_identidad_diagnostica_R02.py'):regular(path)
    cfg=read(resources);oldrecipe=read(oldrecipefile);oldentry=cfg['code_capsules'][OLDCAP];oldroot=C/oldentry['product_relative'];mf=oldroot/oldentry.get('manifest','SISTEMA_CODIGO.json')
    need(sha(mf)==oldentry['manifest_sha256'],'Original R01 capsule identity differs')
    oldmanifest=read(mf)
    for row in oldmanifest['files']:need((oldroot/row['file']).stat().st_size==row['bytes']and sha(oldroot/row['file'])==row['sha256'],'Original R01 capsule changed: '+row['file'])
    need(oldrecipe['id']==OLD and oldrecipe['code_capsule_key']==OLDCAP and oldrecipe['diagnostic_identity_binding']['schema']=='DEE.PI11.diagnostic_family.identity_binding.R01','Actual registered original R01 recipe')
    # No R01 family may have reached material import; otherwise investigate its
    # real future separately instead of silently replacing that recipe.
    for recordfile in(RP/'EJECUCIONES').glob('*.json'):
        need(read(recordfile).get('recipe')!=OLD,'R01 already materially registered; preserve/reconcile before a different revision')
    tools=('pi11_vinculo_reproduccion_R02.py','pi11_guardia_reproduccion_R02.py')
    for name in(*tools,'pi11_adaptar_frontdoor_R02.py','pi11_identidad_diagnostica_R02.py','aplicar_identidad_control_PI11_R02.py'):
        ast.parse((H/name).read_text('utf-8-sig'))
    patcher=load('PI11_exact_control_readonly_patch',H/'aplicar_identidad_control_PI11_R02.py').patch_owner
    blobs,manifest=proposed_manifest(oldmanifest,oldroot,(H/'pi11_identidad_diagnostica_R02.py').read_bytes(),patcher)
    patched_front=load('PI11_pure_R02_frontdoor_delta',H/'pi11_adaptar_frontdoor_R02.py').adapt_frontdoor(frontdoor.read_text('utf-8-sig'))
    newroot=C/NEWREL;newrecipefile=RP/'recetas'/(NEW+'.json');backup=P/'control/PUBLICACION_REPRODUCCION_READONLY_PI11_R02'
    advisorydir=RP/'verificaciones'/OLD;advisoryfile=advisorydir/'DEPENDENCIA_READONLY_SUPERADA_R02.json'
    for path in(newroot,newrecipefile,backup,advisoryfile,*(RP/name for name in tools)):regular(path);need(not path.exists(),'Previous/partial publication preserved: '+str(path))
    before={'resources':sha(resources),'frontdoor':sha(frontdoor),'old_recipe':sha(oldrecipefile),'old_capsule_manifest':sha(mf),'ACTIVO':sha(C/'sistema/estado/ACTIVO.json')}
    recipe=copy.deepcopy(oldrecipe);recipe.update(id=NEW,revision='R02_READONLY_NONREAL_BOOTSTRAP_BEFORE_FIRST_NATIVE_REPLAY',code_capsule_key=NEWCAP)
    recipe['diagnostic_identity_binding'].update(schema='DEE.PI11.diagnostic_family.identity_binding.R02',helper_sha256=sha(H/tools[0]))
    recipe['material_supervisor']['sha256']=sha(H/tools[1])
    recipe['verification']={'status':'PREPARED_READONLY_R02_PENDING_ACTUAL_PUBLIC_NATIVE_REPLAY','new_Native_ticks_by_updater':0,'R01_material_executed':False}
    recipe['supersedes_instrumental_recipe']=OLD;recipe['public_retention_enabled']=False
    for key,text in recipe.get('usage',{}).items():
        if isinstance(text,str):recipe['usage'][key]=text.replace(OLD,NEW)
    recipe['limitations'].append('R02 only fixes non-REAL readonly C2C bootstrap. Role stays reproduction and public retention remains disabled. Actor, Native decoder, environment, phases and expected errors remain the original protocol.')
    plan={'schema':'DEE.PI11.prospective_readonly_RP_publication.R02','recorded_utc':datetime.now(timezone.utc).isoformat(),
          'mode':'APPLY_STATIC_ONLY'if apply else'PLAN_ONLY','Native_ticks':0,'DEE_imports':0,'Native_inputs':0,
          'old_recipe':OLD,'new_recipe':NEW,'original_hashes':before,'R01_material_executed':False,'role_reproduction_preserved':True,'public_retention_enabled':False,
          'old_capsule':str(oldroot),'new_capsule':str(newroot),'changed_code_files':{name:{'source_R01_sha256':next((row['sha256']for row in oldmanifest['files']if row['file']==name),None),'R02_sha256':hashlib.sha256(data).hexdigest()}for name,data in blobs.items()},
          'unchanged_critical_scientific_files':['capacidades/pi11_actor_R01.py','capacidades/pi11_habitat_persistente_R01.py','capacidades/PROTOCOLO_PI11_R01.json','capacidades/pi10_dos_trazas_legales_R01.py'],
          'Native_bound':32256,'episode_batches':[8,8],'memory_limit_bytes':536870912}
    if not apply:print(json.dumps(plan,ensure_ascii=False,indent=2));return
    need(not(P/'PI11_ROOT_NATIVE_WRITER.lock').exists()and not(RP/'EJECUCION_MATERIAL.lock').exists(),'Coordinator writer must be closed/reconciled before publication')
    backup.mkdir();new(backup/'INTENCION.json',plan)
    copy_new(resources,backup/'RECURSOS_ANTES.json',before['resources']);copy_new(frontdoor,backup/'reproducir_ANTES.py',before['frontdoor']);copy_new(oldrecipefile,backup/(OLD+'.json'),before['old_recipe'])
    newroot.mkdir(parents=True)
    for row in oldmanifest['files']:
        if row['file']in blobs:
            target=newroot/row['file'];target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('xb')as f:f.write(blobs[row['file']]);f.flush();os.fsync(f.fileno())
        else:copy_new(oldroot/row['file'],newroot/row['file'],row['sha256'])
    (newroot/SHIM).write_bytes(blobs[SHIM]);new(newroot/'SISTEMA_CODIGO.json',manifest)
    for name in tools:copy_new(H/name,RP/name)
    new(newrecipefile,recipe)
    updated=copy.deepcopy(cfg);need(NEWCAP not in updated['code_capsules'],'R02 capsule key already used')
    updated['code_capsules'][NEWCAP]={'product_relative':NEWREL,'manifest':'SISTEMA_CODIGO.json','manifest_sha256':sha(newroot/'SISTEMA_CODIGO.json')}
    cas(resources,before['resources'],encoded(updated));cas(frontdoor,before['frontdoor'],patched_front.encode('utf8'))
    new(advisoryfile,{'schema':'DEE.reproduction.static_dependency_advisory.v1','recipe':OLD,'status':'DOCUMENTED_DEPENDENCY_BLOCK_SUPERSEDED','use_replacement_recipe':NEW,
        'actual_native_execution_completed':False,'new_native_ticks':0,'reason':'Non-REAL reproduction bootstrap called REAL-only C2C enumeration. No R01 material attempt; R02 readonly identity fixes that technical dependency without granting public retention.'})
    need(sha(mf)==before['old_capsule_manifest']and sha(oldrecipefile)==before['old_recipe']and sha(C/'sistema/estado/ACTIVO.json')==before['ACTIVO'],'Original R01 or selected life changed')
    for row in oldmanifest['files']:need(sha(oldroot/row['file'])==row['sha256'],'Original R01 member changed')
    for row in manifest['files']:need(sha(newroot/row['file'])==row['sha256'],'New R02 capsule incomplete')
    plan.update(mode='REGISTERED_STATIC_READONLY_R02_PENDING_NATIVE',new_capsule_manifest_sha256=sha(newroot/'SISTEMA_CODIGO.json'),
        files_after={'resources':sha(resources),'frontdoor':sha(frontdoor),'recipe_R02':sha(newrecipefile)},old_R01_literal_preserved=True,selected_principal_unchanged=True)
    new(backup/'REGISTRO_COMPLETADO.json',plan);print(json.dumps(plan,ensure_ascii=False,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--aplicar',action='store_true');main(p.parse_args().aplicar)
